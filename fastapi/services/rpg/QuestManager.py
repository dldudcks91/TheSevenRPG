import logging
from database import SessionLocal
from models import User, Material
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

# 시설 해금 비트
FACILITY_QUEST_BOARD = 1  # 비트 1: 퀘스트 게시판 (Ch2 클리어)

# 퀘스트 목록 (폴백 상수, 기획 미확정)
# quest_id → {name, desc, required: [(material_type, material_id, amount)], reward: {gold, exp_bonus, materials: [(type, id, amount)]}}
QUEST_LIST = {
    1: {
        "name": "광석 납품 (소)",
        "desc": "광석 10개를 납품하세요.",
        "required": [("ore", 1, 10)],
        "reward": {"gold": 500, "materials": []},
    },
    2: {
        "name": "광석 납품 (대)",
        "desc": "광석 30개를 납품하세요.",
        "required": [("ore", 1, 30)],
        "reward": {"gold": 2000, "materials": []},
    },
    3: {
        "name": "포션 공급",
        "desc": "하급 포션 5개를 납품하세요.",
        "required": [("potion", 1, 5)],
        "reward": {"gold": 800, "materials": [("ore", 1, 10)]},
    },
}


class QuestManager:
    """퀘스트 게시판 — 재료 납품 (API 4003, 4004)"""

    @classmethod
    async def get_quests(cls, user_no: int, data: dict):
        """API 4004: 퀘스트 목록 조회"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if not cls._is_facility_unlocked(user.unlocked_facilities, FACILITY_QUEST_BOARD):
                return error_response(ErrorCode.INVALID_REQUEST, "퀘스트 게시판이 아직 해금되지 않았습니다. (Ch2 클리어 필요)")

            # 유저의 현재 재료 보유량 조회
            materials = db.query(Material).filter(
                Material.user_no == user_no,
                Material.amount > 0,
            ).all()
            mat_map = {}
            for m in materials:
                mat_map[(m.material_type, m.material_id)] = m.amount

        except Exception as e:
            logger.error(f"[QuestManager] get_quests 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "퀘스트 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

        quest_list = []
        for qid, q in QUEST_LIST.items():
            completable = all(
                mat_map.get((mt, mi), 0) >= amt
                for mt, mi, amt in q["required"]
            )
            quest_list.append({
                "quest_id": qid,
                "name": q["name"],
                "desc": q["desc"],
                "required": [
                    {"material_type": mt, "material_id": mi, "amount": amt, "owned": mat_map.get((mt, mi), 0)}
                    for mt, mi, amt in q["required"]
                ],
                "reward": q["reward"],
                "completable": completable,
            })

        return {
            "success": True,
            "message": f"퀘스트 {len(quest_list)}건 조회",
            "data": {"quests": quest_list},
        }

    @classmethod
    async def submit_quest(cls, user_no: int, data: dict):
        """API 4003: 퀘스트 재료 납품 → 보상"""
        # ── [1] 입력 추출 ──
        quest_id = data.get("quest_id")
        if quest_id is None:
            return error_response(ErrorCode.INVALID_REQUEST, "quest_id가 필요합니다.")
        quest_id = int(quest_id)

        # ── [2] 메타데이터 검증 ──
        quest = QUEST_LIST.get(quest_id)
        if not quest:
            return error_response(ErrorCode.INVALID_REQUEST, f"존재하지 않는 퀘스트: {quest_id}")

        # ── [3] DB 세션 + 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            if not cls._is_facility_unlocked(user.unlocked_facilities, FACILITY_QUEST_BOARD):
                return error_response(ErrorCode.INVALID_REQUEST, "퀘스트 게시판이 아직 해금되지 않았습니다.")

            # 재료 검증 + 차감 준비
            materials_to_consume = []
            for mat_type, mat_id, required_amount in quest["required"]:
                mat = db.query(Material).filter(
                    Material.user_no == user_no,
                    Material.material_type == mat_type,
                    Material.material_id == mat_id,
                ).with_for_update().first()
                if not mat or mat.amount < required_amount:
                    owned = mat.amount if mat else 0
                    return error_response(
                        ErrorCode.MATERIAL_NOT_FOUND,
                        f"재료가 부족합니다. ({mat_type}/{mat_id}: 필요 {required_amount}, 보유 {owned})"
                    )
                materials_to_consume.append((mat, required_amount))

            # ── [4] 비즈니스 로직 ──
            # 재료 차감
            for mat, amount in materials_to_consume:
                mat.amount -= amount
                if mat.amount <= 0:
                    db.delete(mat)

            # 보상 지급
            reward = quest["reward"]
            gold_reward = reward.get("gold", 0)
            if gold_reward > 0:
                user.gold += gold_reward

            # 재료 보상
            for mat_type, mat_id, amount in reward.get("materials", []):
                cls._upsert_material(db, user_no, mat_type, mat_id, amount)

            remaining_gold = user.gold

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[QuestManager] submit_quest (user_no={user_no}, quest_id={quest_id}, gold_reward={gold_reward})")

        except Exception as e:
            db.rollback()
            logger.error(f"[QuestManager] submit_quest 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "퀘스트 납품 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"퀘스트 '{quest['name']}' 완료!",
            "data": {
                "quest_id": quest_id,
                "gold_reward": gold_reward,
                "material_rewards": reward.get("materials", []),
                "gold_remaining": remaining_gold,
            },
        }

    # ── 헬퍼 ──

    @classmethod
    def _upsert_material(cls, db, user_no: int, material_type: str, material_id: int, amount: int):
        existing = db.query(Material).filter(
            Material.user_no == user_no,
            Material.material_type == material_type,
            Material.material_id == material_id,
        ).first()
        if existing:
            existing.amount += amount
        else:
            db.add(Material(
                user_no=user_no,
                material_type=material_type,
                material_id=material_id,
                amount=amount,
            ))

    @staticmethod
    def _is_facility_unlocked(bitmask: int, facility_bit: int) -> bool:
        return bool((bitmask or 0) & (1 << facility_bit))
