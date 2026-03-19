import random
import logging
from services.system.GameDataManager import GameDataManager

logger = logging.getLogger("RPG_SERVER")


# ── 챕터별 죄종 영문 키 매핑 ──
CHAPTER_SIN_MAP = {
    1: "wrath",
    2: "envy",
    3: "greed",
    4: "sloth",
    5: "gluttony",
    6: "lust",
    7: "pride",
}

# ── 죄종 고유 특성 (7종) ──
# 전투 루프 내에서 동적으로 처리되는 특성은 trait_id로 식별
SIN_TRAITS = {
    "wrath": {
        "trait_id": "wrath_rage",
        "name_kr": "격분",
        "description": "HP 30% 이하 시: 공격력×2, 공속+50%",
        # 스탯 보정 없음 — 전투 루프에서 HP 조건 체크 후 동적 적용
    },
    "envy": {
        "trait_id": "envy_deprive",
        "name_kr": "박탈",
        "description": "치명타/회피 발동 시 무효화",
    },
    "sloth": {
        "trait_id": "sloth_lazy",
        "name_kr": "태만",
        "description": "공속-50%, 공격력×2",
        "stat_mods": {"atk_mult": 2.0, "aspd_mult": 0.5},
    },
    "lust": {
        "trait_id": "lust_seduce",
        "name_kr": "유혹",
        "description": "타격 시 플레이어 공격력 10% 흡수 (스택)",
    },
    "pride": {
        "trait_id": "pride_invincible",
        "name_kr": "불가침",
        "description": "모든 상태이상 면역",
        # Phase 16(상태이상) 구현 후 활성화
    },
    "gluttony": {
        "trait_id": "gluttony_devour",
        "name_kr": "탐식",
        "description": "매 타격 공격력 +2% 영구 누적",
    },
    "greed": {
        "trait_id": "greed_gamble",
        "name_kr": "도박",
        "description": "피해 0.2~1.8배 랜덤, 처치 시 드롭+1",
    },
}

# ── 공통 특성 풀 (16종) ──
COMMON_TRAITS = {
    # 스탯 강화 (8종) — 전투 시작 전 스탯에 곱/가산
    "robust": {
        "trait_id": "robust",
        "name_kr": "강인한",
        "stat_mods": {"hp_mult": 1.5},
    },
    "fortified": {
        "trait_id": "fortified",
        "name_kr": "단단한",
        "stat_mods": {"def_mult": 1.5},
    },
    "gigantic": {
        "trait_id": "gigantic",
        "name_kr": "거대한",
        "stat_mods": {"hp_mult": 1.2},  # 사이즈+1은 Phase 16 사이즈 보정에서 처리
    },
    "swift": {
        "trait_id": "swift",
        "name_kr": "날랜",
        "stat_mods": {"aspd_mult": 1.3},
    },
    "ferocious": {
        "trait_id": "ferocious",
        "name_kr": "흉포한",
        "stat_mods": {"atk_mult": 1.3},
    },
    "nimble": {
        "trait_id": "nimble",
        "name_kr": "민첩한",
        "stat_mods": {"eva_add": 0.3},
    },
    "precise": {
        "trait_id": "precise",
        "name_kr": "정확한",
        "stat_mods": {"acc_add": 0.3},
    },
    "deadly": {
        "trait_id": "deadly",
        "name_kr": "치명적인",
        "stat_mods": {"crit_chance_add": 0.2, "crit_dmg_add": 0.5},
    },
    # 전투 규칙 (8종) — 전투 루프 내에서 동적 처리
    "regenerating": {
        "trait_id": "regenerating",
        "name_kr": "재생하는",
        "description": "매초 최대HP의 1% 회복",
    },
    "thorned": {
        "trait_id": "thorned",
        "name_kr": "가시의",
        "description": "받은 피해의 15% 반사",
    },
    "hardening": {
        "trait_id": "hardening",
        "name_kr": "경화의",
        "description": "피격마다 DEF +1% 영구 누적",
    },
    "first_strike": {
        "trait_id": "first_strike",
        "name_kr": "선제의",
        "description": "전투 시작 시 선공 1회 (100% 명중)",
    },
    "retaliatory": {
        "trait_id": "retaliatory",
        "name_kr": "보복의",
        "description": "피격 시 30% 확률 즉시 반격 1회",
    },
    "exploding": {
        "trait_id": "exploding",
        "name_kr": "폭발하는",
        "description": "사망 시 최대HP 50% 범위 폭발",
    },
    "cursed": {
        "trait_id": "cursed",
        "name_kr": "저주받은",
        "description": "타격 시 30% 확률 랜덤 디버프",
        # Phase 16(상태이상) 구현 후 활성화
    },
    "vampiric": {
        "trait_id": "vampiric",
        "name_kr": "흡혈의",
        "description": "피해의 20% HP 회복",
    },
}

COMMON_TRAIT_KEYS = list(COMMON_TRAITS.keys())


class EliteManager:
    """정예 몬스터 특성 생성 (Phase 15)"""

    @classmethod
    def generate_elite(cls, stage_id: int, monster_data: dict, grade: dict) -> tuple[dict, list]:
        """
        정예 몬스터 생성: 기본 스탯에 등급 배율 + 특성 효과 적용

        Args:
            stage_id: 스테이지 ID (챕터 판별용)
            monster_data: 기본 몬스터 메타데이터 (monsters CSV)
            grade: 스폰 등급 배율 (elite)

        Returns:
            (elite_stats, traits): 특성 적용된 스탯 dict, 특성 목록
        """
        chapter = stage_id // 100

        # 1. 죄종 고유 특성 결정
        sin_key = CHAPTER_SIN_MAP.get(chapter, "wrath")
        sin_trait = SIN_TRAITS.get(sin_key, SIN_TRAITS["wrath"])

        # 2. 공통 특성 2개 랜덤 선택
        common_keys = random.sample(COMMON_TRAIT_KEYS, 2)
        common_trait_list = [COMMON_TRAITS[k] for k in common_keys]

        traits = [sin_trait] + common_trait_list

        # 3. 기본 스탯에 등급 배율 적용
        base_hp = monster_data["base_hp"] * grade["hp_mult"]
        base_atk = monster_data["base_atk"] * grade["atk_mult"]
        base_def = monster_data.get("base_def", 0)
        base_aspd = monster_data.get("atk_speed", 1.0)

        # 4. 특성 스탯 보정 적용 (곱연산/가산)
        hp_mult = 1.0
        atk_mult = 1.0
        def_mult = 1.0
        aspd_mult = 1.0
        acc_add = 0.0
        eva_add = 0.0
        crit_chance_add = 0.0
        crit_dmg_add = 0.0

        for trait in traits:
            mods = trait.get("stat_mods", {})
            hp_mult *= mods.get("hp_mult", 1.0)
            atk_mult *= mods.get("atk_mult", 1.0)
            def_mult *= mods.get("def_mult", 1.0)
            aspd_mult *= mods.get("aspd_mult", 1.0)
            acc_add += mods.get("acc_add", 0.0)
            eva_add += mods.get("eva_add", 0.0)
            crit_chance_add += mods.get("crit_chance_add", 0.0)
            crit_dmg_add += mods.get("crit_dmg_add", 0.0)

        elite_stats = {
            "hp": base_hp * hp_mult,
            "atk": base_atk * atk_mult,
            "defense": base_def * def_mult,
            "atk_speed": base_aspd * aspd_mult,
            "acc": monster_data.get("acc", 0.05) + acc_add,
            "eva": monster_data.get("eva", 0.0) + eva_add,
            "crit_chance": crit_chance_add,
            "crit_dmg": 1.5 + crit_dmg_add,
            "level": monster_data.get("level", 1),
        }

        trait_ids = [t["trait_id"] for t in traits]
        trait_names = [t["name_kr"] for t in traits]
        logger.info(f"[EliteManager] 정예 생성 (stage={stage_id}, traits={trait_names})")

        return elite_stats, trait_ids
