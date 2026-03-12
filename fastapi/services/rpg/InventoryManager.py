import logging
from database import SessionLocal
from models import User, UserStat, Item, Card
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

VALID_EQUIP_SLOTS = {"weapon", "armor", "helmet", "gloves", "boots"}

# 아이템 판매 가격 배율 (rarity → 골드 배수)
SELL_PRICE_TABLE = {
    "normal": 10,
    "magic": 30,
    "rare": 100,
    "unique": 500,
}

# 인벤토리 확장
EXPAND_BASE_COST = 500   # 기본 비용
EXPAND_SLOTS = 10        # 한 번에 확장되는 칸 수
MAX_INVENTORY_CAP = 500  # 최대 인벤토리 상한


class InventoryManager:
    """인벤토리/장비 관리 (API 2001~2003)"""

    @classmethod
    async def equip_item(cls, user_no: int, data: dict):
        """API 2001: 장비 장착 — 슬롯 충돌 처리 + 코스트 검증 + Redis 무효화"""
        item_uid = data.get("item_uid")
        target_slot = data.get("equip_slot")

        if not item_uid:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "item_uid가 필요합니다.")
        if target_slot not in VALID_EQUIP_SLOTS:
            return error_response(ErrorCode.EQUIP_SLOT_MISMATCH, f"유효하지 않은 장착 부위: {target_slot}")

        db = SessionLocal()
        try:
            # 아이템 소유권 검증
            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")

            if item.equip_slot == target_slot:
                return {"success": True, "message": "이미 장착 중입니다.", "data": {"item_uid": item_uid, "equip_slot": target_slot}}

            # 코스트 검증
            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            max_cost = (stat.level * 1) + (stat.stat_cost * 2)

            equipped = db.query(Item).filter(
                Item.user_no == user_no,
                Item.equip_slot.isnot(None),
                Item.item_uid != item_uid,
            ).all()

            # 교체 대상 슬롯 비용 제외 + 새 아이템 비용 포함
            cost_after = sum(i.item_cost for i in equipped if i.equip_slot != target_slot) + item.item_cost
            if cost_after > max_cost:
                return error_response(ErrorCode.COST_EXCEEDED, f"코스트 초과 ({cost_after}/{max_cost})")

            # 같은 슬롯 기존 장비 해제
            for old in equipped:
                if old.equip_slot == target_slot:
                    old.equip_slot = None

            item.equip_slot = target_slot
            db.commit()

            try:
                await RedisManager.delete(f"user:{user_no}:battle_stats")
            except RedisUnavailable:
                pass

            return {
                "success": True,
                "message": f"{target_slot} 슬롯에 장비를 장착했습니다.",
                "data": {"item_uid": item_uid, "equip_slot": target_slot},
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[Inventory] 장착 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "장비 장착 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    async def unequip_item(cls, user_no: int, data: dict):
        """API 2002: 장비 해제"""
        item_uid = data.get("item_uid")
        if not item_uid:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "item_uid가 필요합니다.")

        db = SessionLocal()
        try:
            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")
            if item.equip_slot is None:
                return error_response(ErrorCode.EQUIP_SLOT_MISMATCH, "장착되어 있지 않은 아이템입니다.")

            old_slot = item.equip_slot
            item.equip_slot = None
            db.commit()

            try:
                await RedisManager.delete(f"user:{user_no}:battle_stats")
            except RedisUnavailable:
                pass

            return {
                "success": True,
                "message": f"{old_slot} 슬롯의 장비를 해제했습니다.",
                "data": {"item_uid": item_uid},
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[Inventory] 해제 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "장비 해제 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    async def get_inventory(cls, user_no: int, data: dict):
        """API 2003: 인벤토리 조회"""
        db = SessionLocal()
        try:
            items = db.query(Item).filter(Item.user_no == user_no).all()
            item_list = [
                {
                    "item_uid": i.item_uid,
                    "base_item_id": i.base_item_id,
                    "item_level": i.item_level,
                    "rarity": i.rarity,
                    "item_cost": i.item_cost,
                    "suffix_id": i.suffix_id,
                    "set_id": i.set_id,
                    "dynamic_options": i.dynamic_options,
                    "equip_slot": i.equip_slot,
                }
                for i in items
            ]
            return {
                "success": True,
                "message": f"아이템 {len(item_list)}개 조회",
                "data": {"items": item_list},
            }
        except Exception as e:
            logger.error(f"[Inventory] 조회 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "인벤토리 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

    # ── 아이템 판매 / 인벤 확장 ────────────────────────────

    @classmethod
    async def sell_item(cls, user_no: int, data: dict):
        """API 2004: 아이템 판매 — 장착 중 아이템 판매 차단, 카드 부착 시 카드도 삭제"""
        item_uid = data.get("item_uid")
        if not item_uid:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "item_uid가 필요합니다.")

        db = SessionLocal()
        try:
            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")

            # 장착 중인 아이템은 판매 불가
            if item.equip_slot is not None:
                return error_response(ErrorCode.EQUIP_SLOT_MISMATCH, "장착 중인 아이템은 판매할 수 없습니다. 먼저 해제하세요.")

            # 판매 가격 = 기본 배율 × 아이템 레벨
            base_price = SELL_PRICE_TABLE.get(item.rarity, 10)
            sell_price = base_price * item.item_level

            # 카드가 부착되어 있으면 카드도 같이 삭제
            attached_card = db.query(Card).filter(Card.equipped_item == item_uid).first()
            if attached_card:
                db.delete(attached_card)

            user = db.query(User).filter(User.user_no == user_no).first()
            user.gold += sell_price
            db.delete(item)
            db.commit()

            return {
                "success": True,
                "message": f"아이템을 {sell_price} 골드에 판매했습니다.",
                "data": {
                    "item_uid": item_uid,
                    "sell_price": sell_price,
                    "total_gold": user.gold,
                },
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[Inventory] 판매 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "아이템 판매 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    async def expand_inventory(cls, user_no: int, data: dict):
        """API 2005: 인벤토리 확장 — 골드 소비로 max_inventory 증가"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if user.max_inventory >= MAX_INVENTORY_CAP:
                return error_response(ErrorCode.INVENTORY_FULL, f"인벤토리가 최대치({MAX_INVENTORY_CAP})입니다.")

            # 비용 = base × (현재 최대칸 / 초기칸) — 확장할수록 비싸짐
            cost = EXPAND_BASE_COST * (user.max_inventory // 100 + 1)

            if user.gold < cost:
                return error_response(ErrorCode.INSUFFICIENT_GOLD, f"골드가 부족합니다. (필요: {cost}, 보유: {user.gold})")

            user.gold -= cost
            user.max_inventory = min(user.max_inventory + EXPAND_SLOTS, MAX_INVENTORY_CAP)
            db.commit()

            return {
                "success": True,
                "message": f"인벤토리를 {EXPAND_SLOTS}칸 확장했습니다.",
                "data": {
                    "max_inventory": user.max_inventory,
                    "cost": cost,
                    "total_gold": user.gold,
                },
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[Inventory] 확장 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "인벤토리 확장 중 오류가 발생했습니다.")
        finally:
            db.close()
