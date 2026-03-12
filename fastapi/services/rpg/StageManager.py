import random
import logging
from database import SessionLocal
from models import User
from services.system.GameDataManager import GameDataManager
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

STAGES_PER_CHAPTER = 3
TOTAL_CHAPTERS = 7
MAX_STAGE = TOTAL_CHAPTERS * STAGES_PER_CHAPTER  # 21


class StageManager:
    """스테이지 진행 관리 (API 3003~3004)"""

    @classmethod
    async def enter_stage(cls, user_no: int, data: dict):
        """API 3003: 스테이지 입장 — 해금 검증 + 몬스터 풀 반환"""
        stage_id = data.get("stage_id")
        if stage_id is None:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            # 일반 스테이지 해금 검증
            if 1 <= stage_id <= MAX_STAGE:
                if stage_id > user.current_stage:
                    return error_response(ErrorCode.STAGE_NOT_UNLOCKED, "아직 해금되지 않은 스테이지입니다.")
            # 챕터 보스 (101~107): 해당 챕터 3스테이지 모두 클리어 필요
            elif 101 <= stage_id <= 100 + TOTAL_CHAPTERS:
                chapter = stage_id - 100
                chapter_last = chapter * STAGES_PER_CHAPTER
                if user.current_stage <= chapter_last:
                    return error_response(ErrorCode.STAGE_NOT_UNLOCKED, "해당 챕터를 모두 클리어해야 합니다.")
            else:
                return error_response(ErrorCode.STAGE_NOT_FOUND, f"존재하지 않는 스테이지: {stage_id}")

            # Redis에 진행 상태 저장 (포탈 귀환 지원)
            try:
                await RedisManager.hmset(f"user:{user_no}:stage_progress", {
                    "stage_id": str(stage_id),
                    "wave": "1",
                    "kills": "0",
                })
                await RedisManager.expire(f"user:{user_no}:stage_progress", 86400)
            except RedisUnavailable:
                pass

            # 몬스터 풀 생성
            monster_pool = cls._generate_monster_pool(stage_id)

            return {
                "success": True,
                "message": f"스테이지 {stage_id} 입장",
                "data": {"stage_id": stage_id, "monsters": monster_pool},
            }
        except Exception as e:
            logger.error(f"[Stage] 입장 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스테이지 입장 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    async def clear_stage(cls, user_no: int, data: dict):
        """API 3004: 스테이지 클리어 — 다음 스테이지 해금"""
        stage_id = data.get("stage_id")
        if stage_id is None:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        # enter_stage 선행 확인
        progress_key = f"user:{user_no}:stage_progress"
        try:
            progress = await RedisManager.hgetall(progress_key)
            if not progress or int(progress.get("stage_id", 0)) != stage_id:
                return error_response(ErrorCode.INVALID_BATTLE_REQ, "해당 스테이지에 입장하지 않았습니다.")
        except RedisUnavailable:
            pass  # Redis 장애 시 검증 스킵 (graceful degradation)

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            unlocked = False
            # 현재 최고 진행 스테이지를 클리어한 경우에만 다음 해금
            if stage_id == user.current_stage and stage_id < MAX_STAGE:
                user.current_stage = stage_id + 1
                unlocked = True

            db.commit()

            # 진행 정보 삭제
            try:
                await RedisManager.delete(progress_key)
            except RedisUnavailable:
                pass

            return {
                "success": True,
                "message": f"스테이지 {stage_id} 클리어!",
                "data": {
                    "stage_id": stage_id,
                    "unlocked_next": unlocked,
                    "current_stage": user.current_stage,
                },
            }
        except Exception as e:
            db.rollback()
            logger.error(f"[Stage] 클리어 처리 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스테이지 클리어 처리 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    def _generate_monster_pool(cls, stage_id: int) -> list:
        """
        스테이지 몬스터 풀 생성
        웨이브 구조: [일반4+정예1] × 2 + [일반4+정예1+보스1] = 16마리
        """
        monsters = GameDataManager.REQUIRE_CONFIGS.get("monsters", {})
        if not monsters:
            return []

        monster_ids = list(monsters.keys())
        pool = []

        for wave in range(1, 4):
            wave_data = []
            for _ in range(4):
                wave_data.append({"monster_idx": random.choice(monster_ids), "spawn_type": "일반"})
            wave_data.append({"monster_idx": random.choice(monster_ids), "spawn_type": "정예"})
            if wave == 3:
                wave_data.append({"monster_idx": random.choice(monster_ids), "spawn_type": "보스"})
            pool.append({"wave": wave, "monsters": wave_data})

        return pool
