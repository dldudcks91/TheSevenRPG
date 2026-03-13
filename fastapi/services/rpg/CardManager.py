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
        except Exception as e:
            logger.error(f"[CardManager] get_cards 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

        return {
            "success": True,
            "message": f"카드 {len(card_list)}개 조회",
            "data": {"cards": card_list},
        }

    @classmethod
    async def equip_card(cls, user_no: int, data: dict):
        """API 2008: 카드를 장비에 장착"""
        # ── [1] 입력 추출 ──
        card_uid = data.get("card_uid")
        item_uid = data.get("item_uid")

        if not card_uid:
            return error_response(ErrorCode.CARD_NOT_FOUND, "card_uid가 필요합니다.")
        if not item_uid:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "item_uid가 필요합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).with_for_update().first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            if card.equipped_item is not None:
                return error_response(ErrorCode.CARD_ALREADY_EQUIPPED, "이미 장착 중인 카드입니다. 먼저 해제하세요.")

            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).with_for_update().first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")

            existing_card = db.query(Card).filter(
                Card.equipped_item == item_uid,
                Card.user_no == user_no,
            ).first()
            if existing_card:
                return error_response(ErrorCode.CARD_ALREADY_EQUIPPED, "해당 장비에 이미 카드가 장착되어 있습니다.")

            # ── [4] 비즈니스 로직 ──
            card.equipped_item = item_uid
            was_equipped = item.equip_slot is not None

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()

            if was_equipped:
                try:
                    await RedisManager.delete(f"user:{user_no}:battle_stats")
                except RedisUnavailable:
                    logger.warning(f"[CardManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] equip_card 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 장착 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "카드를 장비에 장착했습니다.",
            "data": {"card_uid": card_uid, "item_uid": item_uid},
        }

    @classmethod
    async def unequip_card(cls, user_no: int, data: dict):
        """API 2009: 카드 해제"""
        # ── [1] 입력 추출 ──
        card_uid = data.get("card_uid")
        if not card_uid:
            return error_response(ErrorCode.CARD_NOT_FOUND, "card_uid가 필요합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).with_for_update().first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            if card.equipped_item is None:
                return error_response(ErrorCode.CARD_NOT_FOUND, "장착되어 있지 않은 카드입니다.")

            item = db.query(Item).filter(Item.item_uid == card.equipped_item).first()
            was_equipped = item and item.equip_slot is not None

            # ── [4] 비즈니스 로직 ──
            card.equipped_item = None

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()

            if was_equipped:
                try:
                    await RedisManager.delete(f"user:{user_no}:battle_stats")
                except RedisUnavailable:
                    logger.warning(f"[CardManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] unequip_card 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 해제 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "카드를 해제했습니다.",
            "data": {"card_uid": card_uid},
        }
