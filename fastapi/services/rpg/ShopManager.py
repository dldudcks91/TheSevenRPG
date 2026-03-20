import logging
from database import SessionLocal
from models import User, Material
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

# 시설 해금 비트
FACILITY_SHOP = 2  # 비트 2: 상인 (Ch3 클리어)

# 상점 상품 목록 (폴백 상수, CSV 미확정)
# shop_id → {name, material_type, material_id, amount, gold_price}
SHOP_ITEMS = {
    1: {"name": "하급 포션", "material_type": "potion", "material_id": 1, "amount": 1, "gold_price": 100},
    2: {"name": "중급 포션", "material_type": "potion", "material_id": 2, "amount": 1, "gold_price": 300},
    3: {"name": "상급 포션", "material_type": "potion", "material_id": 3, "amount": 1, "gold_price": 800},
    4: {"name": "광석 ×5", "material_type": "ore", "material_id": 1, "amount": 5, "gold_price": 200},
    5: {"name": "광석 ×20", "material_type": "ore", "material_id": 1, "amount": 20, "gold_price": 700},
}


class ShopManager:
    """상인 시스템 — 골드로 재료 구매 (API 4002)"""

    @classmethod
    async def get_shop(cls, user_no: int, data: dict):
        """API 4005: 상점 목록 조회"""
        # 시설 해금 검증
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if not cls._is_facility_unlocked(user.unlocked_facilities, FACILITY_SHOP):
                return error_response(ErrorCode.INVALID_REQUEST, "상인이 아직 해금되지 않았습니다. (Ch3 클리어 필요)")

            gold = user.gold
        except Exception as e:
            logger.error(f"[ShopManager] get_shop 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "상점 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

        items = [
            {"shop_id": sid, **info}
            for sid, info in SHOP_ITEMS.items()
        ]

        return {
            "success": True,
            "message": f"상점 상품 {len(items)}종",
            "data": {"shop_items": items, "gold": gold},
        }

    @classmethod
    async def buy_item(cls, user_no: int, data: dict):
        """API 4002: 상인에서 아이템 구매"""
        # ── [1] 입력 추출 ──
        shop_id = data.get("shop_id")
        quantity = data.get("quantity", 1)
        if shop_id is None:
            return error_response(ErrorCode.INVALID_REQUEST, "shop_id가 필요합니다.")
        shop_id = int(shop_id)
        quantity = max(1, int(quantity))

        # ── [2] 메타데이터 검증 ──
        shop_item = SHOP_ITEMS.get(shop_id)
        if not shop_item:
            return error_response(ErrorCode.INVALID_REQUEST, f"존재하지 않는 상품: {shop_id}")

        total_price = shop_item["gold_price"] * quantity

        # ── [3] DB 세션 + 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if not cls._is_facility_unlocked(user.unlocked_facilities, FACILITY_SHOP):
                return error_response(ErrorCode.INVALID_REQUEST, "상인이 아직 해금되지 않았습니다.")

            if user.gold < total_price:
                return error_response(ErrorCode.INSUFFICIENT_GOLD, f"골드가 부족합니다. (필요: {total_price}, 보유: {user.gold})")

            # ── [4] 비즈니스 로직 ──
            user.gold -= total_price
            total_amount = shop_item["amount"] * quantity

            # 재료 UPSERT
            mat = db.query(Material).filter(
                Material.user_no == user_no,
                Material.material_type == shop_item["material_type"],
                Material.material_id == shop_item["material_id"],
            ).first()
            if mat:
                mat.amount += total_amount
            else:
                mat = Material(
                    user_no=user_no,
                    material_type=shop_item["material_type"],
                    material_id=shop_item["material_id"],
                    amount=total_amount,
                )
                db.add(mat)

            remaining_gold = user.gold
            mat_amount = mat.amount

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[ShopManager] buy_item (user_no={user_no}, shop_id={shop_id}, qty={quantity}, gold_spent={total_price})")

        except Exception as e:
            db.rollback()
            logger.error(f"[ShopManager] buy_item 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "구매 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"{shop_item['name']} ×{quantity} 구매 완료",
            "data": {
                "shop_id": shop_id,
                "item_name": shop_item["name"],
                "quantity": quantity,
                "gold_spent": total_price,
                "gold_remaining": remaining_gold,
                "material_amount": mat_amount,
            },
        }

    @staticmethod
    def _is_facility_unlocked(bitmask: int, facility_bit: int) -> bool:
        return bool((bitmask or 0) & (1 << facility_bit))
