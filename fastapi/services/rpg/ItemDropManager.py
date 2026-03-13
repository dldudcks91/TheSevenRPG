import random
import logging
from services.system.GameDataManager import GameDataManager
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")


class ItemDropManager:
    """몬스터 킬 & 드랍 처리 (API 3002)"""

    # --- [기획 밸런싱 상수] ---
    STAT_GROWTH_RATE = 1.10
    SPAWN_MULTIPLIERS = {
        "일반": {"hp": 1.0, "atk": 1.0, "drop_roll": 1},
        "정예": {"hp": 3.0, "atk": 1.5, "drop_roll": 3},
        "보스": {"hp": 10.0, "atk": 2.5, "drop_roll": 5}
    }

    @classmethod
    async def process_kill(cls, user_no: int, data: dict):
        """API Code 3002: 몬스터 킬 및 드랍 처리"""
        # ── [1] 입력 추출 ──
        monster_idx = data.get("monster_idx")
        spawned_level = data.get("spawned_level")
        spawned_grade = data.get("spawned_grade")
        field_level = data.get("field_level")
        spawn_type = data.get("spawn_type", "일반")

        if monster_idx is None:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "monster_idx가 필요합니다.")
        if spawned_level is None or spawned_grade is None or field_level is None:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "spawned_level, spawned_grade, field_level이 필요합니다.")

        # 타입 변환 + 범위 검증
        try:
            monster_idx = int(monster_idx)
            spawned_level = int(spawned_level)
            spawned_grade = int(spawned_grade)
            field_level = int(field_level)
        except (ValueError, TypeError):
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "전투 파라미터 타입이 올바르지 않습니다.")

        if spawned_level < 1 or spawned_grade < 1 or field_level < 1:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "전투 파라미터는 1 이상이어야 합니다.")

        if spawn_type not in cls.SPAWN_MULTIPLIERS:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, f"유효하지 않은 spawn_type: {spawn_type}")

        # ── [2] 메타데이터 검증 ──
        configs = GameDataManager.REQUIRE_CONFIGS
        if not configs.get('monsters'):
            return error_response(ErrorCode.INTERNAL_ERROR, "게임 데이터가 로드되지 않았습니다.")

        if monster_idx not in configs['monsters']:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, f"존재하지 않는 몬스터: {monster_idx}")

        base_monster = configs['monsters'][monster_idx]

        # ── [4] 비즈니스 로직 ──
        try:
            score = cls._calc_monster_score(spawned_level, field_level, configs['score_config'])

            drop_table = configs['drop_config'].get(spawned_grade, [("Nodrop", 100)])
            roll_count = cls.SPAWN_MULTIPLIERS[spawn_type]["drop_roll"]

            drops = []
            for _ in range(roll_count):
                category = cls._roll_weighted(drop_table)
                if category == "equipment":
                    equip_data = cls._generate_equip(score, base_monster, configs)
                    if equip_data:
                        drops.append({"type": "equipment", "data": equip_data})
                elif category != "Nodrop":
                    amount = random.randint(10, 50) * spawned_grade
                    drops.append({"type": category, "amount": amount})

        except Exception as e:
            logger.error(f"[ItemDropManager] process_kill 실패: {e}", exc_info=True)
            return error_response(ErrorCode.INTERNAL_ERROR, "드랍 처리 중 오류가 발생했습니다.")

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "드랍 처리 완료",
            "data": {
                "monster_score": round(score, 2),
                "drops": drops
            }
        }

    # --- 내부 헬퍼 메서드들 ---
    @classmethod
    def _calc_monster_score(cls, level, field_level, score_config):
        min_base = score_config.get('min_base_score', 5.0)
        level_growth = score_config.get('level_growth_rate', 0.01)
        field_multi = score_config.get('field_level_multiplier', 2.0)
        variance = score_config.get('score_variance', 0.05)

        base = min_base + (level * level_growth)
        score = base * (field_level * field_multi)
        return score * random.uniform(1 - variance, 1 + variance)

    @staticmethod
    def _roll_weighted(choices: list[tuple]) -> str:
        items, weights = zip(*choices)
        return random.choices(items, weights=weights, k=1)[0]

    @classmethod
    def _generate_equip(cls, score: float, monster: dict, configs: dict) -> dict:
        """스코어와 몬스터 종족값에 기반한 장비 생성"""
        # 1. 레어도 판정
        valid_rarities = [
            (k, v["weight"]) for k, v in configs['rarity_config'].items()
            if v["min_score"] <= score <= v["max_score"]
        ]
        rarity_key = cls._roll_weighted(valid_rarities) if valid_rarities else "normal"
        r_data = configs['rarity_config'].get(rarity_key, {"prefix_count": 0, "suffix_count": 0})

        # 2. 타겟 파밍: 몬스터 타입에 따른 드랍 부위 결정 (투구, 무기 등)
        m_base = monster["monster_base"]
        m_size = monster["size_type"]
        weight_key = f"{m_base}_{m_size}"

        part_weights = configs['drop_equip_weights'].get(weight_key, {})

        # 부위 가중치가 없으면 랜덤 부위로 fallback
        if part_weights and sum(part_weights.values()) > 0:
            target_part_korean = cls._roll_weighted(list(part_weights.items()))
            part_map = {"무기": "weapon", "갑옷": "armor", "투구": "helmet", "장갑": "gloves", "신발": "boots"}
            target_main_group = part_map.get(target_part_korean, "weapon")
        else:
            target_main_group = random.choice(["weapon", "armor", "helmet", "gloves", "boots"])

        # 3. 결정된 부위(main_group)에 맞는 베이스 아이템 필터링
        valid_bases = [b for b in configs['equip_bases'] if b.get('main_group') == target_main_group]
        if not valid_bases:
            return {}

        base_item = random.choice(valid_bases)
        item_name = base_item.get("item_base", "Unknown Item")

        # 4. 접두사/접미사 부여 (옵션 개수는 rarity_config 참조)
        options = []
        if r_data["prefix_count"] > 0 and configs['prefixes']:
            valid_prefixes = [p for p in configs['prefixes'] if p.get("equipment_type") == target_main_group]

            if valid_prefixes:
                prefix = random.choice(valid_prefixes)

                # 방어코드: 빈 문자열이나 '-' 처리
                min_val = float(prefix["min_stat_1"]) if str(prefix.get("min_stat_1", "")).replace('.','',1).isdigit() else 1.0
                max_val = float(prefix["max_stat_1"]) if str(prefix.get("max_stat_1", "")).replace('.','',1).isdigit() else 5.0

                val = round(random.uniform(min_val, max_val), 2)

                stat_name = prefix.get("stat_1", "stat")
                options.append(f"{stat_name} +{val}")
                item_name = f"{prefix.get('prefix_korean', 'Unknown')}의 {item_name}"

        return {
            "name": item_name,
            "rarity": rarity_key,
            "base_type": target_main_group,
            "sub_type": base_item.get("sub_group", "unknown"),
            "req_score": round(score, 2),
            "options": options
        }
