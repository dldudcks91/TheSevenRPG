import random
import uuid
import logging
from services.system.GameDataManager import GameDataManager

logger = logging.getLogger("RPG_SERVER")

# mlvl cap
MLVL_CAP = 50

# 등급별 mlvl 보정
MLVL_OFFSET = {
    "일반": 0,
    "정예": 2,
    "보스": 3,
    "챕터보스": 0,  # chapter_boss_mlvl 고정값 사용
}

# 등급 한글→숫자 매핑 (monster_drop_config.csv의 monster_grade)
GRADE_TO_NUM = {
    "일반": 1,
    "정예": 2,
    "보스": 3,
    "챕터보스": 4,
}


class ItemDropManager:
    """드롭 시스템 v2 — mlvl 기반, 서버사이드 DB 저장"""

    # ── 내부 호출: BattleManager에서 호출 ──

    @classmethod
    def process_kill(cls, stage_id: int, monster_idx: int, spawn_type: str) -> list:
        """
        몬스터 처치 시 드롭 판정 (DB 저장 없이 드롭 목록만 반환)
        BattleManager가 pending_drops에 축적 후 웨이브 클리어 시 일괄 저장.

        Returns: list of drop dicts
            - {"type": "gold", "amount": int}
            - {"type": "equipment", "data": dict}
            - {"type": "card", "monster_idx": int}
            - {"type": "material", "material_type": str, "material_id": int, "amount": int}
            - {"type": "stigma", "sin_type": str}
        """
        configs = GameDataManager.REQUIRE_CONFIGS

        # mlvl 계산
        mlvl = cls._calc_mlvl(stage_id, spawn_type)

        # 드롭롤 수 결정
        grade_num = GRADE_TO_NUM.get(spawn_type, 1)
        grade_config = configs.get("spawn_grade_config", {})
        grade_en_map = {"일반": "normal", "정예": "elite", "보스": "stage_boss", "챕터보스": "chapter_boss"}
        grade_en = grade_en_map.get(spawn_type, "normal")
        grade_data = grade_config.get(grade_en, {})
        drop_rolls = int(grade_data.get("drop_roll", 1)) if grade_data else grade_num

        # 드롭 테이블
        drop_table = configs.get("drop_config", {}).get(grade_num, [("Nodrop", 100)])

        # 몬스터 정보
        monster = configs.get("monsters", {}).get(int(monster_idx), {})

        drops = []

        # 일반 드롭롤
        for _ in range(drop_rolls):
            category = cls._roll_weighted(drop_table)

            if category == "Nodrop":
                continue
            elif category == "gold":
                gold = cls._calc_gold_drop(mlvl, grade_data)
                if gold > 0:
                    drops.append({"type": "gold", "amount": gold})
            elif category == "equipment":
                equip = cls._generate_equipment(mlvl, monster, stage_id)
                if equip:
                    drops.append({"type": "equipment", "data": equip})
            elif category == "card":
                drops.append({"type": "card", "monster_idx": int(monster_idx)})
            elif category == "etc":
                # Phase 18에서 세분화. 현재는 광석으로 통일
                ore_tier = max(1, mlvl // 10)
                drops.append({
                    "type": "material",
                    "material_type": "ore",
                    "material_id": ore_tier,
                    "amount": random.randint(1, 3),
                })

        # 챕터보스 전용: 유니크 장비 추가 판정
        if spawn_type == "챕터보스":
            unique_drop = cls._roll_unique_drop(stage_id, mlvl, monster)
            if unique_drop:
                drops.append({"type": "equipment", "data": unique_drop})

            # 낙인 추가 판정
            stigma = cls._roll_stigma_drop(stage_id)
            if stigma:
                drops.append(stigma)

        return drops

    # ── mlvl 계산 ──

    @classmethod
    def _calc_mlvl(cls, stage_id: int, spawn_type: str) -> int:
        """stage_id + spawn_type → mlvl"""
        stages = GameDataManager.REQUIRE_CONFIGS.get("stages", {})
        stage_info = stages.get(stage_id, {})
        dlvl = stage_info.get("dlvl", 1)

        if spawn_type == "챕터보스":
            ch_boss_mlvl = stage_info.get("chapter_boss_mlvl")
            if ch_boss_mlvl:
                return min(ch_boss_mlvl, MLVL_CAP)
            return min(dlvl, MLVL_CAP)

        offset = MLVL_OFFSET.get(spawn_type, 0)
        return min(dlvl + offset, MLVL_CAP)

    # ── 골드 드롭 ──

    @classmethod
    def _calc_gold_drop(cls, mlvl: int, grade_data: dict) -> int:
        """골드 드롭량 = (mlvl × mult + constant) × gold_mult × random"""
        gold_config = GameDataManager.REQUIRE_CONFIGS.get("gold_drop_config", {})
        mlvl_mult = gold_config.get("mlvl_mult", 2)
        base_const = gold_config.get("base_constant", 5)
        rand_min = gold_config.get("random_min", 0.8)
        rand_max = gold_config.get("random_max", 1.2)

        base_gold = mlvl * mlvl_mult + base_const
        gold_mult = grade_data.get("gold_mult", 1.0) if grade_data else 1.0
        return max(1, int(base_gold * gold_mult * random.uniform(rand_min, rand_max)))

    # ── 장비 생성 ──

    @classmethod
    def _generate_equipment(cls, mlvl: int, monster: dict, stage_id: int) -> dict:
        """mlvl 기반 장비 생성"""
        configs = GameDataManager.REQUIRE_CONFIGS

        # 1. 등급 판정 (equip_drop_rate.csv)
        rarity = cls._determine_rarity(mlvl)

        # 2. 부위 결정 (몬스터 베이스별 가중치)
        equip_slot = cls._determine_equip_slot(monster)

        # 3. 베이스 아이템 선택
        valid_bases = [b for b in configs.get("equip_bases", []) if b.get("main_group") == equip_slot]
        if not valid_bases:
            return {}
        base_item = random.choice(valid_bases)

        # 4. 접두사 부여 (지역 죄종 편향)
        prefix_data = None
        prefix_id = None
        if rarity in ("magic", "rare"):
            prefix_data = cls._roll_affix(configs.get("prefixes", []), equip_slot, stage_id)
            if prefix_data:
                prefix_id = prefix_data.get("prefix", prefix_data.get("suffix", ""))

        # 5. 접미사 부여 (rare 이상만)
        suffix_data = None
        suffix_id = None
        if rarity == "rare":
            suffix_data = cls._roll_affix(configs.get("suffixes", []), equip_slot, stage_id)
            if suffix_data:
                suffix_id = suffix_data.get("suffix", suffix_data.get("prefix", ""))

        # 6. dynamic_options 구성
        dynamic_options = {}
        if prefix_data:
            cls._apply_affix_stats(dynamic_options, prefix_data)
        if suffix_data:
            cls._apply_affix_stats(dynamic_options, suffix_data)

        # 7. 아이템 이름 조합
        item_name = base_item.get("item_base", "Unknown")
        prefix_label = prefix_data.get('prefix_korean', prefix_data.get('suffix_korean', '')) if prefix_data else ''
        suffix_label = suffix_data.get('suffix_korean', suffix_data.get('prefix_korean', '')) if suffix_data else ''
        if prefix_label:
            item_name = f"[{prefix_label}] {item_name}"
        if suffix_label:
            item_name = f"{item_name} [{suffix_label}]"

        # 8. 코스트 계산
        rarity_config = configs.get("rarity_config", {}).get(rarity, {})
        base_cost = rarity_config.get("base_cost", 1)
        item_cost = int(base_cost * (1 + mlvl * 0.1))

        # 9. set_id (죄종)
        chapter = stage_id // 100
        chapters = configs.get("chapters", {})
        sin_en = chapters.get(chapter, {}).get("sin_en", "")
        set_id = sin_en.lower() if prefix_id and sin_en else None

        return {
            "item_uid": str(uuid.uuid4()),
            "base_item_id": int(base_item.get("item_idx", 0)),
            "item_level": mlvl,
            "rarity": rarity,
            "item_score": mlvl * 10,
            "item_cost": item_cost,
            "prefix_id": prefix_id,
            "suffix_id": suffix_id,
            "set_id": set_id,
            "dynamic_options": dynamic_options,
            "equip_slot": equip_slot,
            "name": item_name,
        }

    @classmethod
    def _determine_rarity(cls, mlvl: int) -> str:
        """mlvl 기반 레어도 판정"""
        equip_rates = GameDataManager.REQUIRE_CONFIGS.get("equip_drop_rate", [])
        for rate in equip_rates:
            if rate["mlvl_min"] <= mlvl <= rate["mlvl_max"]:
                roll = random.uniform(0, 100)
                if roll < rate["rare_rate"]:
                    return "rare"
                return "magic"
        return "magic"

    @classmethod
    def _determine_equip_slot(cls, monster: dict) -> str:
        """몬스터 베이스 기반 부위 가중치"""
        m_base = monster.get("monster_base", "")
        m_size = monster.get("size_type", 1)
        weight_key = f"{m_base}_{m_size}"

        weights = GameDataManager.REQUIRE_CONFIGS.get("drop_equip_weights", {}).get(weight_key, {})
        if weights and sum(weights.values()) > 0:
            items = list(weights.items())
            return cls._roll_weighted(items)
        return random.choice(["weapon", "armor", "helmet", "gloves", "boots"])

    @classmethod
    def _roll_affix(cls, affix_list: list, equip_slot: str, stage_id: int) -> dict:
        """접두사/접미사 롤 (지역 죄종 편향)"""
        valid = [a for a in affix_list if a.get("equipment_type") == equip_slot]
        if not valid:
            return None

        # 지역 죄종 편향: 해당 챕터 죄종의 가중치를 2배로
        chapter = stage_id // 100
        chapters = GameDataManager.REQUIRE_CONFIGS.get("chapters", {})
        region_sin = chapters.get(chapter, {}).get("sin_en", "").lower()

        weighted = []
        for a in valid:
            base_weight = float(a.get("weight", 50))
            affix_sin = a.get("prefix", a.get("suffix", "")).lower()
            if affix_sin == region_sin:
                base_weight *= 2.0
            weighted.append((a, base_weight))

        if not weighted:
            return None
        return cls._roll_weighted(weighted)

    @classmethod
    def _apply_affix_stats(cls, options: dict, affix: dict):
        """접사 수치를 dynamic_options에 추가"""
        stat1 = affix.get("stat_1", "")
        if stat1 and stat1 != "-":
            min1 = cls._parse_float(affix.get("min_stat_1", "0"))
            max1 = cls._parse_float(affix.get("max_stat_1", "0"))
            if max1 > min1:
                val = round(random.uniform(min1, max1), 2)
            else:
                val = min1
            options[stat1] = options.get(stat1, 0) + val

        stat2 = affix.get("stat_2", "")
        if stat2 and stat2 != "-":
            min2 = cls._parse_float(affix.get("min_stat_2", "0"))
            max2 = cls._parse_float(affix.get("max_stat_2", "0"))
            if max2 > min2:
                val = round(random.uniform(min2, max2), 2)
            elif min2 > max2:
                # 음수 범위 (예: atk_speed -20 ~ -10)
                val = round(random.uniform(max2, min2), 2)
                val = -abs(val)
            else:
                val = min2
            options[stat2] = options.get(stat2, 0) + val

    # ── 유니크 드롭 (챕터보스 전용) ──

    @classmethod
    def _roll_unique_drop(cls, stage_id: int, mlvl: int, monster: dict) -> dict:
        """챕터보스 유니크 드롭 판정"""
        unique_config = GameDataManager.REQUIRE_CONFIGS.get("unique_drop_rate", {})
        config = unique_config.get(stage_id)
        if not config:
            return None

        if random.random() >= config["unique_rate"]:
            return None

        # 유니크 아이템 목록에서 선택
        uniques = GameDataManager.REQUIRE_CONFIGS.get("uniques", [])
        if not uniques:
            return None

        # 해당 챕터에 맞는 유니크 필터링 (없으면 전체에서 랜덤)
        chapter = stage_id // 100
        chapter_uniques = [u for u in uniques if int(u.get("chapter", 0)) == chapter]
        selected = random.choice(chapter_uniques) if chapter_uniques else random.choice(uniques)

        equip_slot = selected.get("main_group", "weapon")

        return {
            "item_uid": str(uuid.uuid4()),
            "base_item_id": int(selected.get("item_id", 0)),
            "item_level": mlvl,
            "rarity": "unique",
            "item_score": mlvl * 20,
            "item_cost": int(2.5 * (1 + mlvl * 0.1)),
            "prefix_id": selected.get("item_id", None),
            "suffix_id": None,
            "set_id": None,
            "dynamic_options": {},  # 유니크는 고정 효과 (추후 설계)
            "equip_slot": equip_slot,
            "name": selected.get("item_name", "유니크 아이템"),
        }

    # ── 낙인 드롭 (챕터보스 전용) ──

    @classmethod
    def _roll_stigma_drop(cls, stage_id: int) -> dict:
        """챕터보스 낙인 드롭 판정"""
        stigma_config = GameDataManager.REQUIRE_CONFIGS.get("stigma_drop_config", {})
        config = stigma_config.get(stage_id)
        if not config:
            return None

        if random.random() >= config["stigma_rate"]:
            return None

        return {
            "type": "stigma",
            "sin_type": config["sin_type"],
        }

    # ── 유틸리티 ──

    @staticmethod
    def _roll_weighted(choices) -> any:
        """가중치 기반 랜덤 선택. choices: list of (item, weight) tuples"""
        items, weights = zip(*choices)
        return random.choices(items, weights=weights, k=1)[0]

    @staticmethod
    def _parse_float(val) -> float:
        """안전한 float 파싱"""
        try:
            s = str(val).strip()
            if not s or s == "-":
                return 0.0
            return float(s)
        except (ValueError, TypeError):
            return 0.0
