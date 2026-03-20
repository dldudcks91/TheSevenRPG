import random
import logging
from database import SessionLocal
from models import User, Item, Material
from services.system.GameDataManager import GameDataManager
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

# 시설 해금 비트마스크
FACILITY_BLACKSMITH = 0      # 비트 0: 대장간 (Ch1 클리어)
FACILITY_QUEST_BOARD = 1     # 비트 1: 퀘스트 게시판 (Ch2 클리어)
FACILITY_SHOP = 2            # 비트 2: 상인 (Ch3 클리어)
FACILITY_ASPECT_COMBINER = 3 # 비트 3: 흔적 조합소 (Ch4 클리어)

# 크래프팅 비용 (폴백 상수, CSV 미확정)
ORE_COST_PER_LEVEL = 2       # item_level × 2 = 필요 광석 수
GOLD_COST_PER_LEVEL = 50     # item_level × 50 = 필요 골드

# 낙인 죄종 → material_id 매핑
SIN_TO_STIGMA_ID = {
    "wrath": 1, "envy": 2, "greed": 3, "sloth": 4,
    "gluttony": 5, "lust": 6, "pride": 7,
}

# 광석 material_type / material_id
ORE_TYPE = "ore"
ORE_BASE_ID = 1  # 기본 광석 (등급 체계 미확정 → tier 1 통일)


class CraftingManager:
    """크래프팅 시스템 — 대장간 (API 4001)"""

    @classmethod
    async def craft_item(cls, user_no: int, data: dict):
        """API 4001: 매직 장비 + 낙인 + 광석 + 골드 → 크래프트 장비"""
        # ── [1] 입력 추출 ──
        item_uid = data.get("item_uid")
        stigma_sin = data.get("stigma_sin")  # e.g. "wrath", "envy"

        if not item_uid:
            return error_response(ErrorCode.INVALID_REQUEST, "item_uid가 필요합니다.")
        if not stigma_sin or stigma_sin not in SIN_TO_STIGMA_ID:
            return error_response(ErrorCode.INVALID_REQUEST, f"유효하지 않은 낙인 죄종: {stigma_sin}")

        # ── [2] 메타데이터 검증 ──
        configs = GameDataManager.REQUIRE_CONFIGS
        stigma_mat_id = SIN_TO_STIGMA_ID[stigma_sin]

        # ── [3] DB 세션 + 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            # 시설 해금 검증 (대장간 = 비트 0)
            if not cls._is_facility_unlocked(user.unlocked_facilities, FACILITY_BLACKSMITH):
                return error_response(ErrorCode.INVALID_REQUEST, "대장간이 아직 해금되지 않았습니다. (Ch1 클리어 필요)")

            # 아이템 검증
            item = db.query(Item).filter(
                Item.item_uid == item_uid,
                Item.user_no == user_no,
            ).with_for_update().first()
            if not item:
                return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템을 찾을 수 없습니다.")

            if item.is_equipped:
                return error_response(ErrorCode.INVALID_REQUEST, "장착 중인 장비는 크래프팅할 수 없습니다.")

            if item.rarity != "magic":
                return error_response(ErrorCode.INVALID_REQUEST, "매직 등급 장비만 크래프팅할 수 있습니다.")

            # 접사 검증: 하나만 있어야 함
            has_prefix = bool(item.prefix_id)
            has_suffix = bool(item.suffix_id)
            if has_prefix and has_suffix:
                return error_response(ErrorCode.INVALID_REQUEST, "이미 접두사와 접미사가 모두 있는 장비입니다.")
            if not has_prefix and not has_suffix:
                return error_response(ErrorCode.INVALID_REQUEST, "접두사 또는 접미사가 하나는 있어야 합니다.")

            # 비용 계산
            ore_cost = max(1, item.item_level * ORE_COST_PER_LEVEL)
            gold_cost = max(1, item.item_level * GOLD_COST_PER_LEVEL)

            # 골드 검증
            if user.gold < gold_cost:
                return error_response(ErrorCode.INSUFFICIENT_GOLD, f"골드가 부족합니다. (필요: {gold_cost}, 보유: {user.gold})")

            # 낙인 검증
            stigma_mat = db.query(Material).filter(
                Material.user_no == user_no,
                Material.material_type == "stigma",
                Material.material_id == stigma_mat_id,
            ).with_for_update().first()
            if not stigma_mat or stigma_mat.amount <= 0:
                return error_response(ErrorCode.MATERIAL_NOT_FOUND, f"{stigma_sin} 낙인이 없습니다.")

            # 광석 검증
            ore_mat = db.query(Material).filter(
                Material.user_no == user_no,
                Material.material_type == ORE_TYPE,
                Material.material_id == ORE_BASE_ID,
            ).with_for_update().first()
            ore_amount = ore_mat.amount if ore_mat else 0
            if ore_amount < ore_cost:
                return error_response(ErrorCode.MATERIAL_NOT_FOUND, f"광석이 부족합니다. (필요: {ore_cost}, 보유: {ore_amount})")

            # ── [4] 비즈니스 로직 ──
            # 빈 쪽 접사 롤
            equip_slot = item.equip_slot or "weapon"
            if not has_prefix:
                new_affix = cls._roll_sin_affix(configs.get("prefixes", []), equip_slot, stigma_sin)
                if new_affix:
                    item.prefix_id = new_affix.get("prefix", new_affix.get("suffix", ""))
                    cls._apply_affix_to_options(item, new_affix)
            else:
                new_affix = cls._roll_sin_affix(configs.get("suffixes", []), equip_slot, stigma_sin)
                if new_affix:
                    item.suffix_id = new_affix.get("suffix", new_affix.get("prefix", ""))
                    cls._apply_affix_to_options(item, new_affix)

            # 등급 변경
            item.rarity = "craft"

            # set_id 설정
            item.set_id = stigma_sin

            # 코스트 재계산
            rarity_config = configs.get("rarity_config", {}).get("craft", {})
            base_cost = rarity_config.get("base_cost", 3)
            item.item_cost = int(base_cost * (1 + item.item_level * 0.1))

            # 자원 소모
            user.gold -= gold_cost
            stigma_mat.amount -= 1
            if stigma_mat.amount <= 0:
                db.delete(stigma_mat)
            ore_mat.amount -= ore_cost
            if ore_mat.amount <= 0:
                db.delete(ore_mat)

            # 결과 데이터 추출
            result_item = {
                "item_uid": item.item_uid,
                "base_item_id": item.base_item_id,
                "item_level": item.item_level,
                "rarity": item.rarity,
                "item_cost": item.item_cost,
                "prefix_id": item.prefix_id,
                "suffix_id": item.suffix_id,
                "set_id": item.set_id,
                "dynamic_options": item.dynamic_options,
                "equip_slot": item.equip_slot,
            }

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[CraftingManager] craft_item (user_no={user_no}, item_uid={item_uid}, sin={stigma_sin}, ore={ore_cost}, gold={gold_cost})")

        except Exception as e:
            db.rollback()
            logger.error(f"[CraftingManager] craft_item 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "크래프팅 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "크래프팅 완료! 장비가 크래프트 등급으로 승급되었습니다.",
            "data": {
                "item": result_item,
                "ore_consumed": ore_cost,
                "gold_consumed": gold_cost,
            },
        }

    # ── 헬퍼 ──

    @staticmethod
    def _is_facility_unlocked(bitmask: int, facility_bit: int) -> bool:
        """비트마스크로 시설 해금 여부 확인"""
        return bool((bitmask or 0) & (1 << facility_bit))

    @classmethod
    def _roll_sin_affix(cls, affix_list: list, equip_slot: str, sin: str) -> dict:
        """특정 죄종의 접사 중 랜덤 선택"""
        valid = [
            a for a in affix_list
            if a.get("equipment_type") == equip_slot
        ]
        # 해당 죄종 접사 우선 필터
        sin_affixes = [
            a for a in valid
            if a.get("prefix", a.get("suffix", "")).lower() == sin.lower()
        ]
        # 죄종 접사가 있으면 그 중에서, 없으면 전체에서
        pool = sin_affixes if sin_affixes else valid
        if not pool:
            return None
        return random.choice(pool)

    @classmethod
    def _apply_affix_to_options(cls, item: 'Item', affix: dict):
        """접사 수치를 아이템 dynamic_options에 추가"""
        options = dict(item.dynamic_options or {})

        for i in (1, 2):
            stat = affix.get(f"stat_{i}", "")
            if not stat or stat == "-":
                continue
            min_val = cls._parse_float(affix.get(f"min_stat_{i}", "0"))
            max_val = cls._parse_float(affix.get(f"max_stat_{i}", "0"))
            if max_val > min_val:
                val = round(random.uniform(min_val, max_val), 2)
            elif min_val > max_val:
                val = round(random.uniform(max_val, min_val), 2)
                val = -abs(val)
            else:
                val = min_val
            options[stat] = options.get(stat, 0) + val

        item.dynamic_options = options

    @staticmethod
    def _parse_float(val) -> float:
        try:
            s = str(val).strip()
            if not s or s == "-":
                return 0.0
            return float(s)
        except (ValueError, TypeError):
            return 0.0
