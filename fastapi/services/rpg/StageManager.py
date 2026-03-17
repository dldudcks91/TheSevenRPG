import logging
from database import SessionLocal
from models import User
from services.system.GameDataManager import GameDataManager
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

STAGES_PER_CHAPTER = 4  # stage_num 1~3 일반 + 4 챕터보스
TOTAL_CHAPTERS = 7
FIRST_STAGE = 101  # 최초 스테이지
LAST_STAGE = 704   # 최종 스테이지


class StageManager:
    """스테이지 진행 관리 (API 3003~3004)"""

    @classmethod
    async def enter_stage(cls, user_no: int, data: dict):
        """API 3003: 스테이지 입장 — 해금 검증 + 몬스터 풀 반환"""
        # ── [1] 입력 추출 ──
        stage_id = data.get("stage_id")
        if stage_id is None:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        # ── [2] 메타데이터 검증 ──
        stages = GameDataManager.REQUIRE_CONFIGS.get("stages", {})
        if stage_id not in stages:
            return error_response(ErrorCode.STAGE_NOT_FOUND, f"존재하지 않는 스테이지: {stage_id}")

        # ── [3] DB 세션 + 상태 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            # 해금 검증: current_stage 이하만 입장 가능
            if stage_id > user.current_stage:
                return error_response(ErrorCode.STAGE_NOT_UNLOCKED, "아직 해금되지 않은 스테이지입니다.")
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

            # ── [4] 비즈니스 로직: 다음 스테이지 해금 ──
            unlocked = False
            if stage_id == user.current_stage and stage_id < LAST_STAGE:
                next_stage = cls._next_stage_id(stage_id)
                if next_stage:
                    user.current_stage = next_stage
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
    def _next_stage_id(cls, stage_id: int) -> int | None:
        """현재 스테이지의 다음 스테이지 ID 계산
        101→102→103→104→201→202→...→704(마지막)
        """
        chapter = stage_id // 100
        stage_num = stage_id % 100

        if stage_num < STAGES_PER_CHAPTER:
            # 같은 챕터 다음 스테이지
            return stage_id + 1
        elif chapter < TOTAL_CHAPTERS:
            # 다음 챕터 첫 스테이지
            return (chapter + 1) * 100 + 1
        return None

    @classmethod
    def _generate_monster_pool(cls, stage_id: int) -> list:
        """
        스테이지 몬스터 풀 생성
        stage_info.csv의 wave별 monster_idx 기반
        웨이브 구조: [일반3+정예1] × 3웨이브 + 보스1(웨이브4) = 13마리
        스폰 순서: 종별 집중 (AAA→BBB→CCC)
        """
        stages = GameDataManager.REQUIRE_CONFIGS.get("stages", {})
        stage_info = stages.get(stage_id)

        if not stage_info:
            return []

        waves = stage_info.get("waves", {})
        if not waves:
            return []

        pool = []

        # 웨이브 1~3: 일반 몬스터 (일반3 + 정예1)
        for wave_num in range(1, 4):
            monster_idx = waves.get(wave_num)
            if not monster_idx:
                continue
            wave_data = []
            for _ in range(3):
                wave_data.append({"monster_idx": monster_idx, "spawn_type": "일반"})
            wave_data.append({"monster_idx": monster_idx, "spawn_type": "정예"})
            pool.append({"wave": wave_num, "monsters": wave_data})

        # 웨이브 4: 보스
        boss_idx = waves.get(4)
        if boss_idx:
            pool.append({"wave": 4, "monsters": [{"monster_idx": boss_idx, "spawn_type": "보스"}]})

        return pool
