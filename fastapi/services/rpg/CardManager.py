import logging
from database import SessionLocal
from models import UserStat, Collection, Card, Material
from services.system.GameDataManager import GameDataManager
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

# 스킬 슬롯 해금 레벨
SKILL_SLOT_UNLOCK = {1: 1, 2: 5, 3: 15, 4: 30}
MAX_SKILL_SLOTS = 4

# 카드 레벨 관련 상수
MAX_CARD_LEVEL = 3

# 레벨업 소모량 (폴백 상수, CSV 미확정)
# key: 현재 레벨 → (필요 동일 카드 수, 필요 카드 영혼 수)
LEVELUP_COST = {
    1: (2, 3),    # Lv1→2: 동일 카드 2장 + 영혼 3개
    2: (4, 8),    # Lv2→3: 동일 카드 4장 + 영혼 8개
}

# 분해 시 카드 영혼 획득량
DISASSEMBLE_SOUL = {
    1: 1,
    2: 3,
    3: 7,
}

# 카드 영혼 material 식별
CARD_SOUL_TYPE = "card_soul"
CARD_SOUL_ID = 1


class CardManager:
    """카드 인벤토리 + 도감 시스템 (API 2007~2009, 2012~2014)"""

    # ══════════════════════════════════════════════
    # API 2007: 도감 목록 조회
    # ══════════════════════════════════════════════

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

    # ══════════════════════════════════════════════
    # API 2008: 카드 스킬 장착 (Cards 테이블 기반)
    # ══════════════════════════════════════════════

    @classmethod
    async def equip_skill(cls, user_no: int, data: dict):
        """API 2008: 카드를 스킬 슬롯에 장착"""
        # ── [1] 입력 추출 ──
        card_uid = data.get("card_uid")
        slot_number = data.get("slot_number")

        if not card_uid:
            return error_response(ErrorCode.INVALID_REQUEST, "card_uid가 필요합니다.")
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

            # 장착할 카드 검증
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).with_for_update().first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            # 같은 monster_idx 카드가 이미 다른 슬롯에 장착 중인지 검증
            same_monster_equipped = db.query(Card).filter(
                Card.user_no == user_no,
                Card.monster_idx == card.monster_idx,
                Card.is_equipped == True,
                Card.card_uid != card_uid,
            ).first()
            if same_monster_equipped:
                return error_response(
                    ErrorCode.SKILL_SLOT_INVALID,
                    "같은 몬스터의 카드가 이미 장착되어 있습니다. 먼저 해제하세요."
                )

            # 이미 장착 중인 카드면 슬롯 변경
            if card.is_equipped and card.skill_slot == slot_number:
                return error_response(ErrorCode.SKILL_SLOT_INVALID, "이미 해당 슬롯에 장착되어 있습니다.")

            # 기존 슬롯에서 해제
            if card.is_equipped:
                card.is_equipped = False
                card.skill_slot = None

            # 해당 슬롯 점유자 해제
            occupant = db.query(Card).filter(
                Card.user_no == user_no,
                Card.is_equipped == True,
                Card.skill_slot == slot_number,
            ).with_for_update().first()
            if occupant:
                occupant.is_equipped = False
                occupant.skill_slot = None

            # ── [4] 비즈니스 로직 ──
            card.is_equipped = True
            card.skill_slot = slot_number

            monster_idx = card.monster_idx

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[CardManager] equip_skill (user_no={user_no}, card_uid={card_uid}, slot={slot_number})")

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] equip_skill 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스킬 장착 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"슬롯 {slot_number}에 카드를 장착했습니다.",
            "data": {
                "card_uid": card_uid,
                "monster_idx": monster_idx,
                "slot_number": slot_number,
            },
        }

    # ══════════════════════════════════════════════
    # API 2009: 카드 스킬 해제 (Cards 테이블 기반)
    # ══════════════════════════════════════════════

    @classmethod
    async def unequip_skill(cls, user_no: int, data: dict):
        """API 2009: 카드 스킬 슬롯에서 해제"""
        # ── [1] 입력 추출 ──
        card_uid = data.get("card_uid")
        if not card_uid:
            return error_response(ErrorCode.INVALID_REQUEST, "card_uid가 필요합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).with_for_update().first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            if not card.is_equipped:
                return error_response(ErrorCode.SKILL_SLOT_INVALID, "장착되어 있지 않은 카드입니다.")

            old_slot = card.skill_slot

            # ── [4] 비즈니스 로직 ──
            card.is_equipped = False
            card.skill_slot = None

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[CardManager] unequip_skill (user_no={user_no}, card_uid={card_uid}, old_slot={old_slot})")

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] unequip_skill 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스킬 해제 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"슬롯 {old_slot}의 카드를 해제했습니다.",
            "data": {"card_uid": card_uid},
        }

    # ══════════════════════════════════════════════
    # API 2012: 카드 인벤토리 조회
    # ══════════════════════════════════════════════

    @classmethod
    async def get_cards(cls, user_no: int, data: dict):
        """API 2012: 카드 인벤토리 전체 조회"""
        card_skills = GameDataManager.REQUIRE_CONFIGS.get("card_skills", {})

        db = SessionLocal()
        try:
            cards = db.query(Card).filter(Card.user_no == user_no).all()

            card_list = []
            for c in cards:
                skill_info = card_skills.get(c.monster_idx, {})
                card_list.append({
                    "card_uid": c.card_uid,
                    "monster_idx": c.monster_idx,
                    "card_level": c.card_level,
                    "card_stats": c.card_stats or {},
                    "is_equipped": c.is_equipped,
                    "skill_slot": c.skill_slot,
                    "skill_info": {
                        "skill_id": skill_info.get("skill_id", ""),
                        "skill_name": skill_info.get("skill_name", ""),
                        "trigger_type": skill_info.get("trigger_type", ""),
                        "effect_type": skill_info.get("effect_type", ""),
                    } if skill_info else None,
                })

        except Exception as e:
            logger.error(f"[CardManager] get_cards 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

        return {
            "success": True,
            "message": f"카드 {len(card_list)}장 조회",
            "data": {"cards": card_list},
        }

    # ══════════════════════════════════════════════
    # API 2013: 카드 분해
    # ══════════════════════════════════════════════

    @classmethod
    async def disassemble_card(cls, user_no: int, data: dict):
        """API 2013: 카드 분해 → 카드 영혼 획득"""
        # ── [1] 입력 추출 ──
        card_uid = data.get("card_uid")
        if not card_uid:
            return error_response(ErrorCode.INVALID_REQUEST, "card_uid가 필요합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).with_for_update().first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            if card.is_equipped:
                return error_response(ErrorCode.CARD_EQUIPPED, "장착 중인 카드는 분해할 수 없습니다. 먼저 해제하세요.")

            # ── [4] 비즈니스 로직 ──
            soul_gain = DISASSEMBLE_SOUL.get(card.card_level, 1)

            # 카드 삭제
            db.delete(card)

            # 카드 영혼 UPSERT
            soul_total = cls._upsert_card_soul(db, user_no, soul_gain)

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[CardManager] disassemble_card (user_no={user_no}, card_uid={card_uid}, soul_gain={soul_gain})")

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] disassemble_card 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 분해 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"카드를 분해하여 카드 영혼 {soul_gain}개를 획득했습니다.",
            "data": {
                "card_uid": card_uid,
                "card_soul_gained": soul_gain,
                "card_soul_total": soul_total,
            },
        }

    # ══════════════════════════════════════════════
    # API 2014: 카드 레벨업
    # ══════════════════════════════════════════════

    @classmethod
    async def level_up_card(cls, user_no: int, data: dict):
        """API 2014: 카드 레벨업 (동일 카드 N장 + 카드 영혼 N개 소모)"""
        # ── [1] 입력 추출 ──
        card_uid = data.get("card_uid")
        if not card_uid:
            return error_response(ErrorCode.INVALID_REQUEST, "card_uid가 필요합니다.")

        # ── [3] DB 세션 + 소유권/상태 검증 ──
        db = SessionLocal()
        try:
            card = db.query(Card).filter(
                Card.card_uid == card_uid,
                Card.user_no == user_no,
            ).with_for_update().first()
            if not card:
                return error_response(ErrorCode.CARD_NOT_FOUND, "카드를 찾을 수 없습니다.")

            if card.card_level >= MAX_CARD_LEVEL:
                return error_response(ErrorCode.CARD_MAX_LEVEL, f"이미 최대 레벨({MAX_CARD_LEVEL})입니다.")

            # 레벨업 비용 확인
            cost = LEVELUP_COST.get(card.card_level)
            if not cost:
                return error_response(ErrorCode.CARD_MAX_LEVEL, "레벨업할 수 없는 레벨입니다.")
            required_cards, required_souls = cost

            # 소모용 동일 monster_idx 카드 조회 (장착 중 제외, 대상 카드 제외)
            fodder_cards = db.query(Card).filter(
                Card.user_no == user_no,
                Card.monster_idx == card.monster_idx,
                Card.card_uid != card_uid,
                Card.is_equipped == False,
            ).limit(required_cards).all()

            if len(fodder_cards) < required_cards:
                return error_response(
                    ErrorCode.CARD_INSUFFICIENT,
                    f"동일 카드가 부족합니다. (필요: {required_cards}장, 보유: {len(fodder_cards)}장)"
                )

            # 카드 영혼 보유량 확인
            soul_mat = db.query(Material).filter(
                Material.user_no == user_no,
                Material.material_type == CARD_SOUL_TYPE,
                Material.material_id == CARD_SOUL_ID,
            ).with_for_update().first()

            soul_amount = soul_mat.amount if soul_mat else 0
            if soul_amount < required_souls:
                return error_response(
                    ErrorCode.CARD_SOUL_INSUFFICIENT,
                    f"카드 영혼이 부족합니다. (필요: {required_souls}개, 보유: {soul_amount}개)"
                )

            # ── [4] 비즈니스 로직 ──
            # 소모 카드 삭제
            for fc in fodder_cards:
                db.delete(fc)

            # 카드 영혼 차감
            soul_mat.amount -= required_souls
            if soul_mat.amount <= 0:
                db.delete(soul_mat)
                soul_remaining = 0
            else:
                soul_remaining = soul_mat.amount

            # 카드 레벨업 + stats 갱신
            card.card_level += 1
            card.card_stats = cls._calc_card_stats_for_level(card.monster_idx, card.card_level)

            new_level = card.card_level
            new_stats = card.card_stats

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[CardManager] level_up_card (user_no={user_no}, card_uid={card_uid}, new_level={new_level}, consumed_cards={required_cards}, consumed_souls={required_souls})")

        except Exception as e:
            db.rollback()
            logger.error(f"[CardManager] level_up_card 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "카드 레벨업 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"카드가 Lv.{new_level}로 레벨업되었습니다.",
            "data": {
                "card_uid": card_uid,
                "new_level": new_level,
                "new_card_stats": new_stats,
                "cards_consumed": required_cards,
                "souls_consumed": required_souls,
            },
        }

    # ══════════════════════════════════════════════
    # 내부 전용: 도감 등록
    # ══════════════════════════════════════════════

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

    # ══════════════════════════════════════════════
    # 헬퍼 메서드
    # ══════════════════════════════════════════════

    @staticmethod
    def _get_unlocked_slot_count(level: int) -> int:
        """플레이어 레벨에 따른 해금된 스킬 슬롯 수"""
        count = 0
        for slot, req_level in SKILL_SLOT_UNLOCK.items():
            if level >= req_level:
                count = slot
        return count

    @classmethod
    def _upsert_card_soul(cls, db, user_no: int, amount: int) -> int:
        """카드 영혼 UPSERT, 변경 후 총량 반환 (commit 하지 않음)"""
        mat = db.query(Material).filter(
            Material.user_no == user_no,
            Material.material_type == CARD_SOUL_TYPE,
            Material.material_id == CARD_SOUL_ID,
        ).first()

        if mat:
            mat.amount += amount
            return mat.amount
        else:
            new_mat = Material(
                user_no=user_no,
                material_type=CARD_SOUL_TYPE,
                material_id=CARD_SOUL_ID,
                amount=amount,
            )
            db.add(new_mat)
            return amount

    @classmethod
    def _calc_card_stats_for_level(cls, monster_idx: int, level: int) -> dict:
        """카드 레벨에 따른 card_stats 계산"""
        card_skills = GameDataManager.REQUIRE_CONFIGS.get("card_skills", {})
        skill = card_skills.get(monster_idx, {})
        if not skill:
            return {"trigger_rate": 0.0}

        rate_lv1 = skill.get("trigger_rate_lv1", 0.0)
        rate_lv2 = skill.get("trigger_rate_lv2", 0.0)

        if level == 1:
            trigger_rate = rate_lv1
        elif level == 2:
            trigger_rate = round((rate_lv1 + rate_lv2) / 2, 4)
        else:  # level 3
            trigger_rate = rate_lv2

        return {"trigger_rate": trigger_rate}

    @classmethod
    def generate_card_stats(cls, monster_idx: int) -> dict:
        """카드 드롭 시 랜덤 card_stats 생성 (외부에서 호출 가능)"""
        card_skills = GameDataManager.REQUIRE_CONFIGS.get("card_skills", {})
        skill = card_skills.get(monster_idx, {})
        if not skill:
            return {"trigger_rate": 0.0}

        import random
        base_rate = skill.get("trigger_rate_lv1", 0.0)
        # ±10% 랜덤 변동
        variation = base_rate * 0.1
        trigger_rate = round(random.uniform(base_rate - variation, base_rate + variation), 4)
        trigger_rate = max(0.01, trigger_rate)  # 최소 1%

        return {"trigger_rate": trigger_rate}
