import logging
from database import SessionLocal
from models import UserStat, Collection
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

# 스킬 슬롯 해금 레벨
SKILL_SLOT_UNLOCK = {1: 1, 2: 5, 3: 15, 4: 30}
MAX_SKILL_SLOTS = 4


class CardManager:
    """도감 시스템 (API 2007~2009)"""

    @classmethod
    async def get_collection(cls, user_no: int, data: dict):
        """API 2007: 도감 목록 조회"""
        db = SessionLocal()
        try:
            entries = db.query(Collection).filter(Collection.user_no == user_no).all()
            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()

            unlocked_slots = cls._get_unlocked_slot_count(stat.level) if stat else 1

            collection_list = [
                {
                    "monster_idx": e.monster_idx,
                    "card_count": e.card_count,
                    "collection_level": e.collection_level,
                    "skill_slot": e.skill_slot,
                }
                for e in entries
            ]
        except Exception as e:
            logger.error(f"[CardManager] get_collection 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "도감 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

        return {
            "success": True,
            "message": f"도감 {len(collection_list)}종 조회",
            "data": {
                "collections": collection_list,
                "unlocked_slots": unlocked_slots,
            },
        }

    @classmethod
    async def equip_skill(cls, user_no: int, data: dict):
        """API 2008: 도감 스킬을 스킬 슬롯에 장착"""
        # ── [1] 입력 추출 ──
        monster_idx = data.get("monster_idx")
        slot_number = data.get("slot_number")

        if monster_idx is None:
            return error_response(ErrorCode.COLLECTION_NOT_FOUND, "monster_idx가 필요합니다.")
        if slot_number is None or slot_number not in (1, 2, 3, 4):
            return error_response(ErrorCode.SKILL_SLOT_INVALID, "slot_number는 1~4 중 하나여야 합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            if not stat:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯을 찾을 수 없습니다.")

            unlocked = cls._get_unlocked_slot_count(stat.level)
            if slot_number > unlocked:
                return error_response(
                    ErrorCode.SKILL_SLOT_INVALID,
                    f"슬롯 {slot_number}은 Lv.{SKILL_SLOT_UNLOCK[slot_number]}에 해금됩니다. (현재 Lv.{stat.level})"
                )

            entry = db.query(Collection).filter(
                Collection.user_no == user_no,
                Collection.monster_idx == monster_idx,
            ).with_for_update().first()
            if not entry:
                return error_response(ErrorCode.COLLECTION_NOT_FOUND, "도감에 등록되지 않은 몬스터입니다.")

            if entry.skill_slot is not None:
                return error_response(ErrorCode.SKILL_SLOT_INVALID, "이미 다른 슬롯에 장착 중입니다. 먼저 해제하세요.")

            occupant = db.query(Collection).filter(
                Collection.user_no == user_no,
                Collection.skill_slot == slot_number,
            ).with_for_update().first()
            if occupant:
                occupant.skill_slot = None

            # ── [4] 비즈니스 로직 ──
            entry.skill_slot = slot_number

            # ── [5] 커밋 ──
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] equip_skill 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스킬 장착 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"슬롯 {slot_number}에 스킬을 장착했습니다.",
            "data": {"monster_idx": monster_idx, "slot_number": slot_number},
        }

    @classmethod
    async def unequip_skill(cls, user_no: int, data: dict):
        """API 2009: 스킬 슬롯에서 해제"""
        # ── [1] 입력 추출 ──
        monster_idx = data.get("monster_idx")
        if monster_idx is None:
            return error_response(ErrorCode.COLLECTION_NOT_FOUND, "monster_idx가 필요합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            entry = db.query(Collection).filter(
                Collection.user_no == user_no,
                Collection.monster_idx == monster_idx,
            ).with_for_update().first()
            if not entry:
                return error_response(ErrorCode.COLLECTION_NOT_FOUND, "도감에 등록되지 않은 몬스터입니다.")

            if entry.skill_slot is None:
                return error_response(ErrorCode.SKILL_SLOT_INVALID, "장착되어 있지 않은 스킬입니다.")

            old_slot = entry.skill_slot

            # ── [4] 비즈니스 로직 ──
            entry.skill_slot = None

            # ── [5] 커밋 ──
            db.commit()

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] unequip_skill 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스킬 해제 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"슬롯 {old_slot}의 스킬을 해제했습니다.",
            "data": {"monster_idx": monster_idx},
        }

    @classmethod
    async def register_card(cls, user_no: int, monster_idx: int, db=None):
        """내부 전용: 카드 드롭 시 도감에 등록 (외부 트랜잭션에서 호출, commit하지 않음)"""
        owns_session = db is None
        if owns_session:
            db = SessionLocal()

        try:
            entry = db.query(Collection).filter(
                Collection.user_no == user_no,
                Collection.monster_idx == monster_idx,
            ).with_for_update().first()

            if entry:
                entry.card_count += 1
                is_new = False
            else:
                entry = Collection(
                    user_no=user_no,
                    monster_idx=monster_idx,
                    card_count=1,
                    collection_level=1,
                    skill_slot=None,
                )
                db.add(entry)
                is_new = True

            if owns_session:
                db.commit()

            return {
                "is_new": is_new,
                "monster_idx": monster_idx,
                "card_count": entry.card_count,
                "collection_level": entry.collection_level,
            }

        except Exception as e:
            if owns_session:
                db.rollback()
            logger.error(f"[CardManager] register_card 실패: {e}", exc_info=True)
            return None
        finally:
            if owns_session:
                db.close()

    # ── 헬퍼 ──

    @staticmethod
    def _get_unlocked_slot_count(level: int) -> int:
        """플레이어 레벨에 따른 해금된 스킬 슬롯 수"""
        count = 0
        for slot, req_level in SKILL_SLOT_UNLOCK.items():
            if level >= req_level:
                count = slot
        return count
