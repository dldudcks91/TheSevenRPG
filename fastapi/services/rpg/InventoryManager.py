import logging
from database import SessionLocal
from models import User, UserStat, Item, Material
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

VALID_EQUIP_SLOTS = {"weapon", "armor", "helmet", "gloves", "boots"}

# 아이템 판매 가격 배율 (rarity → 골드 배수)
SELL_PRICE_TABLE = {
    "magic": 30,
    "rare": 100,
    "craft": 300,
    "unique": 500,
}

# 인벤토리 확장
EXPAND_BASE_COST = 500   # 기본 비용
EXPAND_SLOTS = 10        # 한 번에 확장되는 칸 수
MAX_INVENTORY_CAP = 500  # 최대 인벤토리 상한

# 장비 분해 — 등급별 광석 회수 배율
DISASSEMBLE_ORE_TABLE = {
    "magic": 1,    # item_level × 1
    "rare": 2,     # item_level × 2
    "craft": 3,    # item_level × 3
    "unique": 5,   # item_level × 5
}
DISASSEMBLE_GOLD_PER_LEVEL = 20  # item_level × 20 골드 회수
ORE_TYPE = "ore"
ORE_BASE_ID = 1


class InventoryManager:
    """인벤토리/장비 관리 (API 2001~2005)"""

    @classmethod
    async def equip_item(cls, user_no: int, data: dict):
        """API 2001: 장비 장착 — 슬롯 충돌 처리 + 코스트 검증 + Redis 무효화"""
        # ── [1] 입력 추출 ──
        item_uid = data.get("item_uid")
        target_slot = data.get("equip_slot")

        if not item_uid:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "item_uid가 필요합니다.")
        if target_slot not in VALID_EQUIP_SLOTS:
            return error_response(ErrorCode.EQUIP_SLOT_MISMATCH, f"유효하지 않은 장착 부위: {target_slot}")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).with_for_update().first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")

            if item.equip_slot == target_slot:
                return {"success": True, "message": "이미 장착 중입니다.", "data": {"item_uid": item_uid, "equip_slot": target_slot}}

            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            max_cost = (stat.level * 1) + (stat.stat_cost * 2)

            equipped = db.query(Item).filter(
                Item.user_no == user_no,
                Item.equip_slot.isnot(None),
                Item.item_uid != item_uid,
            ).with_for_update().all()

            cost_after = sum(i.item_cost for i in equipped if i.equip_slot != target_slot) + item.item_cost
            if cost_after > max_cost:
                return error_response(ErrorCode.COST_EXCEEDED, f"코스트 초과 ({cost_after}/{max_cost})")

            # ── [4] 비즈니스 로직 ──
            for old in equipped:
                if old.equip_slot == target_slot:
                    old.equip_slot = None

            item.equip_slot = target_slot

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()

            try:
                await RedisManager.delete(f"user:{user_no}:battle_stats")
            except RedisUnavailable:
                logger.warning(f"[InventoryManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

        except Exception as e:
            db.rollback()
            logger.error(f"[InventoryManager] equip_item 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "장비 장착 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"{target_slot} 슬롯에 장비를 장착했습니다.",
            "data": {"item_uid": item_uid, "equip_slot": target_slot},
        }

    @classmethod
    async def unequip_item(cls, user_no: int, data: dict):
        """API 2002: 장비 해제"""
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
            if item.equip_slot is None:
                return error_response(ErrorCode.EQUIP_SLOT_MISMATCH, "장착되어 있지 않은 아이템입니다.")

            # ── [4] 비즈니스 로직 ──
            old_slot = item.equip_slot
            item.equip_slot = None

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()

            try:
                await RedisManager.delete(f"user:{user_no}:battle_stats")
            except RedisUnavailable:
                logger.warning(f"[InventoryManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

        except Exception as e:
            db.rollback()
            logger.error(f"[InventoryManager] unequip_item 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "장비 해제 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"{old_slot} 슬롯의 장비를 해제했습니다.",
            "data": {"item_uid": item_uid},
        }

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
                    "item_score": i.item_score,
                    "item_cost": i.item_cost,
                    "prefix_id": i.prefix_id,
                    "suffix_id": i.suffix_id,
                    "set_id": i.set_id,
                    "dynamic_options": i.dynamic_options,
                    "is_equipped": i.is_equipped,
                    "equip_slot": i.equip_slot,
                }
                for i in items
            ]
        except Exception as e:
            logger.error(f"[InventoryManager] get_inventory 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "인벤토리 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

        return {
            "success": True,
            "message": f"아이템 {len(item_list)}개 조회",
            "data": {"items": item_list},
        }

    # ── 아이템 판매 / 인벤 확장 ────────────────────────────

    @classmethod
    async def sell_item(cls, user_no: int, data: dict):
        """API 2004: 아이템 판매 — 장착 중 아이템 판매 차단, 카드 부착 시 카드도 삭제"""
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

            if item.equip_slot is not None:
                return error_response(ErrorCode.EQUIP_SLOT_MISMATCH, "장착 중인 아이템은 판매할 수 없습니다. 먼저 해제하세요.")

            # ── [4] 비즈니스 로직 ──
            base_price = SELL_PRICE_TABLE.get(item.rarity, 30)
            sell_price = base_price * item.item_level

            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            user.gold += sell_price
            total_gold = user.gold
            db.delete(item)

            # ── [5] 커밋 ──
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"[InventoryManager] sell_item 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "아이템 판매 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"아이템을 {sell_price} 골드에 판매했습니다.",
            "data": {
                "item_uid": item_uid,
                "sell_price": sell_price,
                "total_gold": total_gold,
            },
        }

    @classmethod
    async def expand_inventory(cls, user_no: int, data: dict):
        """API 2005: 인벤토리 확장 — 골드 소비로 max_inventory 증가"""
        # ── [3] DB 세션 + 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if user.max_inventory >= MAX_INVENTORY_CAP:
                return error_response(ErrorCode.INVENTORY_FULL, f"인벤토리가 최대치({MAX_INVENTORY_CAP})입니다.")

            cost = EXPAND_BASE_COST * (user.max_inventory // 100 + 1)

            if user.gold < cost:
                return error_response(ErrorCode.INSUFFICIENT_GOLD, f"골드가 부족합니다. (필요: {cost}, 보유: {user.gold})")

            # ── [4] 비즈니스 로직 ──
            user.gold -= cost
            user.max_inventory = min(user.max_inventory + EXPAND_SLOTS, MAX_INVENTORY_CAP)
            new_max = user.max_inventory
            total_gold = user.gold

            # ── [5] 커밋 ──
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"[InventoryManager] expand_inventory 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "인벤토리 확장 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"인벤토리를 {EXPAND_SLOTS}칸 확장했습니다.",
            "data": {
                "max_inventory": new_max,
                "cost": cost,
                "total_gold": total_gold,
            },
        }

    # ── 장비 분해 ────────────────────────────────────

    @classmethod
    async def disassemble_item(cls, user_no: int, data: dict):
        """API 2010: 장비 분해 → 광석 + 골드 회수"""
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

            if item.equip_slot is not None:
                return error_response(ErrorCode.EQUIP_SLOT_MISMATCH, "장착 중인 장비는 분해할 수 없습니다. 먼저 해제하세요.")

            # ── [4] 비즈니스 로직 ──
            # 광석 회수량
            ore_mult = DISASSEMBLE_ORE_TABLE.get(item.rarity, 1)
            ore_gain = max(1, item.item_level * ore_mult)

            # 골드 회수량
            gold_gain = max(1, item.item_level * DISASSEMBLE_GOLD_PER_LEVEL)

            # 아이템 삭제
            db.delete(item)

            # 광석 UPSERT
            ore_mat = db.query(Material).filter(
                Material.user_no == user_no,
                Material.material_type == ORE_TYPE,
                Material.material_id == ORE_BASE_ID,
            ).first()
            if ore_mat:
                ore_mat.amount += ore_gain
                ore_total = ore_mat.amount
            else:
                ore_mat = Material(
                    user_no=user_no,
                    material_type=ORE_TYPE,
                    material_id=ORE_BASE_ID,
                    amount=ore_gain,
                )
                db.add(ore_mat)
                ore_total = ore_gain

            # 골드 지급
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            user.gold += gold_gain
            total_gold = user.gold

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[InventoryManager] disassemble_item (user_no={user_no}, item_uid={item_uid}, ore={ore_gain}, gold={gold_gain})")

        except Exception as e:
            db.rollback()
            logger.error(f"[InventoryManager] disassemble_item 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "장비 분해 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"장비를 분해하여 광석 {ore_gain}개 + {gold_gain} 골드를 획득했습니다.",
            "data": {
                "item_uid": item_uid,
                "ore_gained": ore_gain,
                "ore_total": ore_total,
                "gold_gained": gold_gain,
                "total_gold": total_gold,
            },
        }
