import uuid
import logging
from database import SessionLocal
from models import User, Item, Card
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")


class CardManager:
    """카드 시스템 (API 2007~2009)"""

    @classmethod
    async def get_cards(cls, user_no: int, data: dict):
        """API 2007: 보유 카드 목록 조회"""
        db = SessionLocal()
        try:
            cards = db.query(Card).filter(Card.user_no == user_no).all()
            card_list = [
                {
                    "card_uid": c.card_uid,
                    "monster_idx": c.monster_idx,
                    "equipped_item": c.equipped_item,
                }
                for c in cards
            ]
            return {
                "success": True,
                "message": f"카드 {len(card_list)}개 조회",
                "data": {"cards": card_list},
            }
        except Exception as e:
            logger.error(f"[Card] 조회 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    async def equip_card(cls, user_no: int, data: dict):
        """API 2008: 카드를 장비에 장착"""
        card_uid = data.get("card_uid")
        item_uid = data.get("item_uid")

        if not card_uid:
            return error_response(ErrorCode.CARD_NOT_FOUND, "card_uid가 필요합니다.")
        if not item_uid:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "item_uid가 필요합니다.")

        db = SessionLocal()
        try:
            # 카드 소유권 검증
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            # 이미 다른 장비에 장착 중인 카드
            if card.equipped_item is not None:
                return error_response(ErrorCode.CARD_ALREADY_EQUIPPED, "이미 장착 중인 카드입니다. 먼저 해제하세요.")

            # 아이템 소유권 검증
            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")

            # 해당 아이템에 이미 다른 카드가 장착되어 있는지 확인
            existing_card = db.query(Card).filter(
                Card.equipped_item == item_uid,
                Card.user_no == user_no,
            ).first()
            if existing_card:
                return error_response(ErrorCode.CARD_ALREADY_EQUIPPED, "해당 장비에 이미 카드가 장착되어 있습니다.")

            card.equipped_item = item_uid
            db.commit()

            # 장착 중인 장비라면 battle_stats 무효화
            if item.equip_slot is not None:
                try:
                    await RedisManager.delete(f"user:{user_no}:battle_stats")
                except RedisUnavailable:
                    pass

            return {
                "success": True,
                "message": "카드를 장비에 장착했습니다.",
                "data": {"card_uid": card_uid, "item_uid": item_uid},
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[Card] 장착 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 장착 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    async def unequip_card(cls, user_no: int, data: dict):
        """API 2009: 카드 해제"""
        card_uid = data.get("card_uid")
        if not card_uid:
            return error_response(ErrorCode.CARD_NOT_FOUND, "card_uid가 필요합니다.")

        db = SessionLocal()
        try:
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            if card.equipped_item is None:
                return error_response(ErrorCode.CARD_NOT_FOUND, "장착되어 있지 않은 카드입니다.")

            # 장착 해제 전에 해당 아이템이 장비 중인지 확인 (battle_stats 무효화 판단)
            item = db.query(Item).filter(Item.item_uid == card.equipped_item).first()
            was_equipped = item and item.equip_slot is not None

            card.equipped_item = None
            db.commit()

            if was_equipped:
                try:
                    await RedisManager.delete(f"user:{user_no}:battle_stats")
                except RedisUnavailable:
                    pass

            return {
                "success": True,
                "message": "카드를 해제했습니다.",
                "data": {"card_uid": card_uid},
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[Card] 해제 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 해제 중 오류가 발생했습니다.")
        finally:
            db.close()
