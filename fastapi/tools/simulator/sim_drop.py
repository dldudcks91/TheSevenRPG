"""
드롭 시뮬레이터

사용법:
    from tools.simulator.sim_drop import run_drop_sim, run_stage_sweep
"""

import sys, os

_FASTAPI_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _FASTAPI_DIR not in sys.path:
    sys.path.insert(0, _FASTAPI_DIR)

import random
from collections import defaultdict
from services.rpg.ItemDropManager import ItemDropManager


def run_drop_sim(
    stage_id: int,
    monster_idx: int,
    spawn_type: str = "일반",
    kills: int = 10000,
    seed: int = None,
) -> dict:
    """
    드롭 시뮬레이션 — 몬스터를 kills회 처치하고 드롭 통계 집계.

    Args:
        stage_id: 스테이지 ID
        monster_idx: 몬스터 인덱스
        spawn_type: "일반" | "정예" | "보스" | "챕터보스"
        kills: 처치 횟수
        seed: 랜덤 시드

    Returns:
        집계 dict (total_kills, total_drops, gold, equipment, card, potion, ore,
                    monster_material, stigma, drop_rate)
    """
    if seed is not None:
        random.seed(seed)

    # 집계 변수
    total_drops = 0

    gold_count = 0
    gold_total = 0
    gold_min = float("inf")
    gold_max = 0

    equip_count = 0
    equip_by_rarity = defaultdict(int)
    equip_by_slot = defaultdict(int)

    card_count = 0
    potion_count = 0

    ore_count = 0
    ore_by_id = defaultdict(int)

    material_count = 0
    material_by_id = defaultdict(int)

    stigma_count = 0

    for _ in range(kills):
        drops = ItemDropManager.process_kill(stage_id, monster_idx, spawn_type)
        total_drops += len(drops)

        for drop in drops:
            drop_type = drop.get("type")

            if drop_type == "gold":
                amount = drop.get("amount", 0)
                gold_count += 1
                gold_total += amount
                if amount < gold_min:
                    gold_min = amount
                if amount > gold_max:
                    gold_max = amount

            elif drop_type == "equipment":
                equip_count += 1
                data = drop.get("data", {})
                rarity = data.get("rarity", "unknown")
                slot = data.get("equip_slot", data.get("main_group", "unknown"))
                equip_by_rarity[rarity] += 1
                equip_by_slot[slot] += 1

            elif drop_type == "card":
                card_count += 1

            elif drop_type == "potion":
                potion_count += 1

            elif drop_type == "material":
                mat_type = drop.get("material_type", "")
                mat_id = drop.get("material_id", 0)
                amount = drop.get("amount", 1)

                if mat_type == "ore":
                    ore_count += amount
                    ore_by_id[mat_id] += amount
                else:
                    material_count += amount
                    material_by_id[mat_id] += amount

            elif drop_type == "stigma":
                stigma_count += 1

    # gold_min 보정 (드롭 0건이면 inf -> 0)
    if gold_count == 0:
        gold_min = 0

    return {
        "total_kills": kills,
        "total_drops": total_drops,
        "gold": {
            "count": gold_count,
            "total": gold_total,
            "avg": round(gold_total / gold_count, 2) if gold_count > 0 else 0,
            "min": gold_min,
            "max": gold_max,
        },
        "equipment": {
            "count": equip_count,
            "by_rarity": dict(equip_by_rarity),
            "by_slot": dict(equip_by_slot),
        },
        "card": {"count": card_count},
        "potion": {"count": potion_count},
        "ore": {
            "count": ore_count,
            "by_id": dict(ore_by_id),
        },
        "monster_material": {
            "count": material_count,
            "by_id": dict(material_by_id),
        },
        "stigma": {"count": stigma_count},
        "drop_rate": round(total_drops / kills, 4) if kills > 0 else 0.0,
    }


def run_stage_sweep(
    stage_id: int,
    kills_per_type: int = 3000,
    seed: int = None,
) -> dict:
    """
    스테이지 전체 드롭 시뮬레이션 — 일반/정예/보스 각각 실행.

    Args:
        stage_id: 스테이지 ID
        kills_per_type: spawn_type별 처치 횟수
        seed: 랜덤 시드

    Returns:
        {"일반": {...}, "정예": {...}, "보스": {...}} 각 run_drop_sim 결과
    """
    from services.system.GameDataManager import GameDataManager

    # 스테이지에 등장하는 대표 몬스터 찾기
    stages = GameDataManager.REQUIRE_CONFIGS.get("stages", {})
    stage_info = stages.get(stage_id, {})
    monster_idx = stage_info.get("monster_idx", stage_info.get("monster_id", 1))

    spawn_types = ["일반", "정예", "보스"]
    results = {}

    for spawn_type in spawn_types:
        type_seed = None
        if seed is not None:
            # spawn_type별 시드 분리
            type_offset = {"일반": 0, "정예": 1_000_000, "보스": 2_000_000}
            type_seed = seed + type_offset.get(spawn_type, 0)

        results[spawn_type] = run_drop_sim(
            stage_id=stage_id,
            monster_idx=monster_idx,
            spawn_type=spawn_type,
            kills=kills_per_type,
            seed=type_seed,
        )

    return results
