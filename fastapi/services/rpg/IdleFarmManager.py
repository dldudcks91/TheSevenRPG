import time
import logging
from database import SessionLocal
from models import User, Item
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

MAX_IDLE_SECONDS = 86400   # 최대 누적 24시간
MIN_COLLECT_SECONDS = 60   # 최소 수령 시간 1분
KILLS_PER_5MIN = 1         # 5분당 킬 수 (임시 — 미확정 기획)
GOLD_PER_KILL = 10         # 킬당 골드 (임시 — 미확정 기획)


class IdleFarmManager:
    """방치 파밍 ON/OFF + 보상 수령 (API 3005~3006)"""

    @classmethod
    async def toggle_idle(cls, user_no: int, data: dict):
        """API 3005: 방치 파밍 ON/OFF 토글"""
        idle_key = f"user:{user_no}:idle_farm"

        # ── [1] Redis 상태 확인 (필수 의존) ──
        try:
            current = await RedisManager.hgetall(idle_key)
        except RedisUnavailable:
            return error_response(ErrorCode.REDIS_ERROR, "서버 점검 중입니다.")

        # 이미 활성 → OFF
        if current:
            try:
                await RedisManager.delete(idle_key)
            except RedisUnavailable:
                logger.warning(f"[IdleFarmManager] idle_farm 삭제 실패 - Redis 장애 (user_no={user_no})")
                return error_response(ErrorCode.REDIS_ERROR, "서버 점검 중입니다.")

            return {
                "success": True,
                "message": "방치 파밍이 중지되었습니다.",
                "data": {"idle_active": False},
            }

        # ── OFF → ON ──
        # ── [1] 입력 추출 ──
        stage_id = data.get("stage_id")
        if not stage_id:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        # ── [3] DB 세션 + 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if stage_id > user.current_stage:
                return error_response(ErrorCode.STAGE_NOT_UNLOCKED, "해금되지 않은 스테이지입니다.")

            item_count = db.query(Item).filter(Item.user_no == user_no).count()
            if item_count >= user.max_inventory:
                return error_response(ErrorCode.INVENTORY_FULL, "인벤토리가 가득 찼습니다.")
        except Exception as e:
            logger.error(f"[IdleFarmManager] toggle_idle 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "방치 파밍 시작 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [5] Redis 타이머 시작 ──
        try:
            await RedisManager.hmset(idle_key, {
                "stage_id": str(stage_id),
                "start_time": str(int(time.time())),
            })
        except RedisUnavailable:
            return error_response(ErrorCode.REDIS_ERROR, "서버 점검 중입니다.")

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"스테이지 {stage_id}에서 방치 파밍을 시작합니다.",
            "data": {"idle_active": True, "stage_id": stage_id},
        }

    @classmethod
    async def collect_idle(cls, user_no: int, data: dict):
        """API 3006: 방치 파밍 보상 수령"""
        idle_key = f"user:{user_no}:idle_farm"

        # ── [1] Redis 상태 확인 (필수 의존) ──
        try:
            idle_data = await RedisManager.hgetall(idle_key)
        except RedisUnavailable:
            return error_response(ErrorCode.REDIS_ERROR, "서버 점검 중입니다.")

        if not idle_data:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "방치 파밍이 활성화되어 있지 않습니다.")

        start_time = int(idle_data["start_time"])
        stage_id = int(idle_data["stage_id"])
        elapsed = min(int(time.time()) - start_time, MAX_IDLE_SECONDS)

        if elapsed < MIN_COLLECT_SECONDS:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "최소 1분 이상 경과해야 수령 가능합니다.")

        # ── [4] 보상 계산 ──
        kill_count = max(1, elapsed // 300 * KILLS_PER_5MIN)
        gold_reward = kill_count * GOLD_PER_KILL

        # ── [3] DB 세션 + 골드 지급 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            user.gold += gold_reward
            total_gold = user.gold

            # ── [5] 커밋 ──
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"[IdleFarmManager] collect_idle 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "보상 지급 중 오류가 발생했습니다.")
        finally:
            db.close()

        # 타이머 리셋 (파밍 계속 유지)
        try:
            await RedisManager.hmset(idle_key, {
                "stage_id": str(stage_id),
                "start_time": str(int(time.time())),
            })
        except RedisUnavailable:
            logger.warning(f"[IdleFarmManager] 타이머 리셋 실패 - Redis 장애 (user_no={user_no})")

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"방치 파밍 보상을 수령했습니다. ({elapsed // 60}분 경과)",
            "data": {
                "elapsed_minutes": elapsed // 60,
                "kill_count": kill_count,
                "gold_reward": gold_reward,
                "total_gold": total_gold,
            },
        }
