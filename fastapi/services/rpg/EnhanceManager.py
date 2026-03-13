import logging
from database import SessionLocal
from models import User, Item
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

# 강화 비용 = base × item_level
ENHANCE_BASE_COST = 100
MAX_ITEM_LEVEL = 20

# 강화 시 스탯 증가율 (레벨당 10% 복리)
ENHANCE_STAT_MULTIPLIER = 0.10


class EnhanceManager:
    """아이템 강화 시스템 (API 2006)"""

    @classmethod
    async def enhance_item(cls, user_no: int, data: dict):
        """API 2006: 아이템 강화 — 골드 소비 → item_level 증가 → dynamic_options 스케일링"""
        # ── [1] 입력 추출 ──
        item_uid = data.get("item_uid")
        if not item_uid:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "item_uid가 필요합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).with_for_update().first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")

            if item.item_level >= MAX_ITEM_LEVEL:
                return error_response(ErrorCode.ENHANCE_FAILED, f"최대 강화 레벨({MAX_ITEM_LEVEL})에 도달했습니다.")

            cost = ENHANCE_BASE_COST * item.item_level

            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if user.gold < cost:
                return error_response(ErrorCode.INSUFFICIENT_GOLD, f"골드가 부족합니다. (필요: {cost}, 보유: {user.gold})")

            # ── [4] 비즈니스 로직 ──
            user.gold -= cost
            item.item_level += 1

            if item.dynamic_options:
                scaled = {}
                for key, val in item.dynamic_options.items():
                    if isinstance(val, (int, float)):
                        scaled[key] = round(val * (1 + ENHANCE_STAT_MULTIPLIER), 4)
                    else:
                        scaled[key] = val
                item.dynamic_options = scaled

            was_equipped = item.equip_slot is not None

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()

            if was_equipped:
                try:
                    await RedisManager.delete(f"user:{user_no}:battle_stats")
                except RedisUnavailable:
                    logger.warning(f"[EnhanceManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

        except Exception as e:
            db.rollback()
            logger.error(f"[EnhanceManager] enhance_item 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "아이템 강화 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"강화 성공! (Lv.{item.item_level - 1} → Lv.{item.item_level})",
            "data": {
                "item_uid": item_uid,
                "item_level": item.item_level,
                "dynamic_options": item.dynamic_options,
                "cost": cost,
                "total_gold": user.gold,
            },
        }
