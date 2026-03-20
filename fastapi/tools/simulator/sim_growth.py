"""
성장 시뮬레이터 — 챕터별 진행 시뮬레이션

플레이어가 Chapter 1~4를 순서대로 클리어할 때의 레벨/골드/사망 추이를 추정한다.
DB/Redis 없이 순수 계산만 수행.

사용법:
    from tools.simulator.sim_growth import run_growth_sim
"""

import sys, os

_FASTAPI_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _FASTAPI_DIR not in sys.path:
    sys.path.insert(0, _FASTAPI_DIR)

import random
from services.system.GameDataManager import GameDataManager
from services.rpg.BattleManager import BattleManager

# ── 상수 ──
WAVES_PER_STAGE = 4
NORMAL_WAVE_FIGHT_COUNT = 4   # 웨이브 1~3: 일반 3 + 정예 1
BOSS_WAVE_FIGHT_COUNT = 1     # 웨이브 4: 보스 1
MAX_RETRIES_PER_WAVE = 10
STAT_POINTS_PER_LEVEL = 5

# ── 스탯 배분 프리셋 ──
# (str, dex, vit, luck) 비율
ALLOCATION_PRESETS = {
    "balanced": (0.30, 0.25, 0.25, 0.20),
    "str":      (0.50, 0.20, 0.15, 0.15),
    "dex":      (0.15, 0.50, 0.15, 0.20),
    "tank":     (0.15, 0.15, 0.55, 0.15),
}


def _allocate_stats(total_points: int, preset: str) -> dict:
    """총 스탯 포인트를 프리셋 비율로 배분"""
    ratios = ALLOCATION_PRESETS.get(preset, ALLOCATION_PRESETS["balanced"])
    raw = [total_points * r for r in ratios]
    # 정수 배분 (반올림 후 잔여 보정)
    allocated = [int(v) for v in raw]
    remainder = total_points - sum(allocated)
    # 잔여 포인트를 비율 큰 순으로 분배
    sorted_indices = sorted(range(4), key=lambda i: raw[i] - allocated[i], reverse=True)
    for i in range(remainder):
        allocated[sorted_indices[i % 4]] += 1
    return {
        "stat_str": allocated[0],
        "stat_dex": allocated[1],
        "stat_vit": allocated[2],
        "stat_luck": allocated[3],
    }


def _build_player_simple(level: int, stats: dict) -> dict:
    """간이 플레이어 빌드 (장비 없는 베이스 스탯)

    장비 시뮬레이션을 위해 레벨에 비례하는 기본 무기 스탯을 부여한다.
    """
    stat_str = stats["stat_str"]
    stat_dex = stats["stat_dex"]
    stat_vit = stats["stat_vit"]
    stat_luck = stats["stat_luck"]

    # 레벨에 비례하는 기본 무기 (장비 드롭 시뮬레이션 대체)
    base_wpn_atk = 10.0 + level * 2.0
    base_wpn_aspd = 1.0 + level * 0.01

    # 장비 보너스 (레벨에 비례하여 간이 추정)
    i_atk_pct = level * 1.0       # 매 레벨 +1% 공격력
    i_aspd_pct = level * 0.3
    i_hp_pct = level * 0.5
    i_def = level * 0.8
    i_acc = level * 0.002
    i_eva = level * 0.001
    i_crit_ch = level * 0.001
    i_crit_dmg = level * 0.005

    max_hp = (100 + stat_vit * 10) * (1 + i_hp_pct / 100)
    attack = base_wpn_atk * (1 + stat_str * 0.005) * (1 + i_atk_pct / 100)
    atk_speed = base_wpn_aspd * (1 + stat_dex * 0.003) * (1 + i_aspd_pct / 100)
    acc = stat_dex * 0.005 + i_acc
    eva = stat_luck * 0.001 + i_eva
    crit_chance = stat_luck * 0.001 + i_crit_ch
    crit_dmg = 1.5 + stat_luck * 0.003 + i_crit_dmg

    return {
        "level": float(level),
        "max_hp": max_hp,
        "current_hp": max_hp,
        "attack": attack,
        "atk_speed": atk_speed,
        "defense": i_def,
        "magic_def": 0,
        "acc": acc,
        "eva": eva,
        "crit_chance": crit_chance,
        "crit_dmg": crit_dmg,
        "size": 2,
        "fhr": 0.0,
        "set_points": {},
    }


def _calc_rewards(monster: dict, spawn_type: str, player_level: int) -> tuple:
    """전투 보상 계산 (exp, gold). DB 없이 로컬 계산."""
    grade = BattleManager._get_spawn_grade(spawn_type)
    if not grade:
        return 0, 0

    base_exp = monster.get("exp_reward", 10)
    exp = int(base_exp * grade.get("exp_mult", 1.0))

    base_gold = random.randint(5, 20) * max(1, player_level // 5)
    gold = int(base_gold * grade.get("gold_mult", 1.0))

    return exp, gold


def _try_level_up(level: int, exp: int, stat_points: int) -> tuple:
    """레벨업 시도. (new_level, remaining_exp, gained_stat_points) 반환."""
    exp_table = BattleManager._get_exp_table()
    gained_sp = 0

    while level < BattleManager.MAX_LEVEL:
        lv_info = exp_table.get(level)
        if not lv_info:
            break
        required = lv_info["required_exp"]
        if exp >= required:
            exp -= required
            level += 1
            sp = lv_info.get("stat_points", STAT_POINTS_PER_LEVEL)
            gained_sp += sp
            stat_points += sp
        else:
            break

    return level, exp, stat_points, gained_sp


def run_growth_sim(
    stat_allocation: str = "balanced",
    seed: int = None,
    start_chapter: int = 1,
    end_chapter: int = 4,
) -> dict:
    """
    성장 시뮬레이션 — 챕터별 스테이지를 순서대로 진행하며 레벨/사망/골드를 추적.

    Args:
        stat_allocation: 스탯 배분 프리셋 ("balanced", "str", "dex", "tank")
        seed: 랜덤 시드 (재현성용)
        start_chapter: 시작 챕터 (1~7)
        end_chapter: 종료 챕터 (1~7)

    Returns:
        {
            "chapters": {
                1: {"entry_level", "exit_level", "total_kills", "deaths",
                    "gold_earned", "exp_earned", "stages_cleared"},
                ...
            },
            "summary": {"final_level", "total_kills", "total_deaths", "total_gold"}
        }
    """
    if seed is not None:
        random.seed(seed)

    stages_config = GameDataManager.REQUIRE_CONFIGS.get("stages", {})
    monsters_config = GameDataManager.REQUIRE_CONFIGS.get("monsters", {})

    # 초기 상태
    level = 1
    exp = 0
    gold = 0
    stat_points = 0  # 미배분 포인트 (레벨1 시작 시 기본 포인트 없음)
    total_allocated_points = 0

    chapter_results = {}
    total_kills = 0
    total_deaths = 0
    total_gold = 0

    # 스테이지를 챕터별로 그룹화
    stages_by_chapter = {}
    for stage_idx, stage_data in sorted(stages_config.items()):
        ch = stage_data["chapter"]
        if ch not in stages_by_chapter:
            stages_by_chapter[ch] = []
        stages_by_chapter[ch].append((stage_idx, stage_data))

    for chapter in range(start_chapter, end_chapter + 1):
        if chapter not in stages_by_chapter:
            continue

        ch_entry_level = level
        ch_kills = 0
        ch_deaths = 0
        ch_gold = 0
        ch_exp = 0
        ch_stages_cleared = 0

        for stage_idx, stage_data in stages_by_chapter[chapter]:
            waves = stage_data.get("waves", {})
            if not waves:
                continue

            # 스테이지 시작 시 스탯 재배분
            total_allocated_points = (level - 1) * STAT_POINTS_PER_LEVEL
            stats = _allocate_stats(total_allocated_points, stat_allocation)
            player = _build_player_simple(level, stats)

            stage_hp = player["max_hp"]  # 스테이지 시작 HP

            for wave_num in range(1, WAVES_PER_STAGE + 1):
                monster_idx = waves.get(wave_num)
                if not monster_idx:
                    continue

                monster = monsters_config.get(int(monster_idx))
                if not monster:
                    continue

                # 웨이브 구성 결정
                if wave_num < WAVES_PER_STAGE:
                    # 웨이브 1~3: 일반 3마리 + 정예 1마리
                    fight_list = [("일반", monster_idx)] * 3 + [("정예", monster_idx)]
                else:
                    # 웨이브 4: 보스/챕터보스
                    is_chapter_boss = (stage_data.get("stage_num") == 4)
                    boss_type = "챕터보스" if is_chapter_boss else "보스"
                    fight_list = [(boss_type, monster_idx)]

                retries = 0
                wave_cleared = False

                while not wave_cleared and retries < MAX_RETRIES_PER_WAVE:
                    wave_failed = False

                    for spawn_type, m_idx in fight_list:
                        monster_data = monsters_config.get(int(m_idx), monster)
                        grade = BattleManager._get_spawn_grade(spawn_type)
                        if not grade:
                            continue

                        # HP 이어받기
                        player["current_hp"] = stage_hp

                        # 전투 실행
                        _, result, remaining_hp = BattleManager._simulate_with_hp(
                            player, monster_data, grade
                        )

                        if result == "win":
                            ch_kills += 1
                            stage_hp = max(1, remaining_hp)

                            # 보상 계산
                            fight_exp, fight_gold = _calc_rewards(
                                monster_data, spawn_type, level
                            )
                            exp += fight_exp
                            gold += fight_gold
                            ch_gold += fight_gold
                            ch_exp += fight_exp

                        else:
                            # 패배 or 타임아웃
                            ch_deaths += 1
                            retries += 1
                            wave_failed = True

                            # 사망 패널티: exp 10% 차감
                            penalty = int(exp * 0.10)
                            exp = max(0, exp - penalty)

                            # HP 전회복 후 웨이브 재시도
                            stage_hp = player["max_hp"]
                            break

                    if not wave_failed:
                        wave_cleared = True

                    # 웨이브 클리어 시점에서 레벨업 체크
                    if wave_cleared:
                        old_level = level
                        level, exp, stat_points, gained_sp = _try_level_up(
                            level, exp, stat_points
                        )
                        if level > old_level:
                            # 레벨업 시 플레이어 리빌드
                            total_allocated_points = (level - 1) * STAT_POINTS_PER_LEVEL
                            stats = _allocate_stats(total_allocated_points, stat_allocation)
                            player = _build_player_simple(level, stats)
                            stage_hp = player["max_hp"]

            ch_stages_cleared += 1

        chapter_results[chapter] = {
            "entry_level": ch_entry_level,
            "exit_level": level,
            "total_kills": ch_kills,
            "deaths": ch_deaths,
            "gold_earned": ch_gold,
            "exp_earned": ch_exp,
            "stages_cleared": ch_stages_cleared,
        }

        total_kills += ch_kills
        total_deaths += ch_deaths
        total_gold += ch_gold

    return {
        "chapters": chapter_results,
        "summary": {
            "final_level": level,
            "total_kills": total_kills,
            "total_deaths": total_deaths,
            "total_gold": total_gold,
            "final_exp": exp,
        },
    }
