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
        # ── [1] 입력 추출 ──
        stage_id = data.get("stage_id")
        if stage_id is None:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        # ── [3] DB 세션 + 상태 검증 ──
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
        except Exception as e:
            logger.error(f"[StageManager] enter_stage 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스테이지 입장 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [5] Redis 진행 상태 저장 ──
        try:
            await RedisManager.hmset(f"user:{user_no}:stage_progress", {
                "stage_id": str(stage_id),
                "wave": "1",
                "kills": "0",
            })
            await RedisManager.expire(f"user:{user_no}:stage_progress", 86400)
        except RedisUnavailable:
            logger.warning(f"[StageManager] stage_progress 저장 실패 - Redis 장애 (user_no={user_no})")

        # ── [6] 응답 반환 ──
        monster_pool = cls._generate_monster_pool(stage_id)
        return {
            "success": True,
            "message": f"스테이지 {stage_id} 입장",
            "data": {"stage_id": stage_id, "monsters": monster_pool},
        }

    @classmethod
    async def clear_stage(cls, user_no: int, data: dict):
        """API 3004: 스테이지 클리어 — 다음 스테이지 해금"""
        # ── [1] 입력 추출 ──
        stage_id = data.get("stage_id")
        if stage_id is None:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        # ── [2] enter_stage 선행 확인 (Redis) ──
        progress_key = f"user:{user_no}:stage_progress"
        try:
            progress = await RedisManager.hgetall(progress_key)
            if not progress or int(progress.get("stage_id", 0)) != stage_id:
                return error_response(ErrorCode.INVALID_BATTLE_REQ, "해당 스테이지에 입장하지 않았습니다.")
        except RedisUnavailable:
            logger.warning(f"[StageManager] stage_progress 검증 실패 - Redis 장애 (user_no={user_no})")

        # ── [3] DB 세션 + 상태 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            # ── [4] 비즈니스 로직 ──
            unlocked = False
            if stage_id == user.current_stage and stage_id < MAX_STAGE:
                user.current_stage = stage_id + 1
                unlocked = True

            current_stage = user.current_stage

            # ── [5] 커밋 ──
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"[StageManager] clear_stage 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스테이지 클리어 처리 중 오류가 발생했습니다.")
        finally:
            db.close()

        # Redis 진행 정보 삭제
        try:
            await RedisManager.delete(progress_key)
        except RedisUnavailable:
            logger.warning(f"[StageManager] stage_progress 삭제 실패 - Redis 장애 (user_no={user_no})")

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"스테이지 {stage_id} 클리어!",
            "data": {
                "stage_id": stage_id,
                "unlocked_next": unlocked,
                "current_stage": current_stage,
            },
        }

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
