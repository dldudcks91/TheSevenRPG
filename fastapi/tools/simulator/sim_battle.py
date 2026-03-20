"""
PVE / PVP 전투 시뮬레이터

사용법:
    from tools.simulator.sim_battle import run_pve, run_pvp
"""

import sys, os

_FASTAPI_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _FASTAPI_DIR not in sys.path:
    sys.path.insert(0, _FASTAPI_DIR)

import random
from services.system.GameDataManager import GameDataManager
from services.rpg.BattleManager import BattleManager
from services.rpg.EliteManager import EliteManager
from services.rpg.StatusEffectManager import CombatUnit, get_size_correction


def run_pve(
    player: dict,
    monster_idx: int,
    spawn_type: str = "일반",
    stage_id: int = None,
    iterations: int = 1000,
    seed: int = None,
) -> dict:
    """
    PVE 전투 시뮬레이션.

    Args:
        player: 플레이어 스탯 dict (max_hp, attack, atk_speed, defense, acc, eva,
                crit_chance, crit_dmg, level, size, fhr, magic_def, set_points 등)
        monster_idx: 몬스터 인덱스 (monsters CSV 키)
        spawn_type: "일반" | "정예" | "보스" | "챕터보스"
        stage_id: 스테이지 ID (정예 생성 시 필수)
        iterations: 시뮬레이션 반복 횟수
        seed: 랜덤 시드 (재현성용)

    Returns:
        {"wins", "losses", "timeouts", "win_rate", "avg_turns", "avg_remaining_hp_pct", "total"}
    """
    monsters = GameDataManager.REQUIRE_CONFIGS.get("monsters", {})
    monster = monsters.get(int(monster_idx))
    if not monster:
        raise ValueError(f"monster_idx={monster_idx} not found in monsters config")

    grade = BattleManager._get_spawn_grade(spawn_type)
    if not grade:
        raise ValueError(f"spawn_type={spawn_type} has no grade config")

    wins = 0
    losses = 0
    timeouts = 0
    total_turns = 0
    total_remaining_hp_pct = 0.0

    for i in range(iterations):
        if seed is not None:
            random.seed(seed + i)

        # 매 반복마다 HP 리셋
        player["current_hp"] = player["max_hp"]

        # 정예 생성
        elite_stats = None
        traits = None
        if spawn_type == "정예" and stage_id is not None:
            elite_stats, traits = EliteManager.generate_elite(stage_id, monster, grade)
        else:
            elite_stats = None
            traits = None

        # 전투 실행
        battle_log, result, remaining_hp = BattleManager._simulate_with_hp(
            player, monster, grade, elite_stats, traits
        )

        # 턴 수 계산 (battle_report 엔트리 제외)
        turn_count = len([e for e in battle_log if e.get("action") != "battle_report"])

        if result == "win":
            wins += 1
        elif result == "lose":
            losses += 1
        else:
            timeouts += 1

        total_turns += turn_count
        if player["max_hp"] > 0:
            total_remaining_hp_pct += remaining_hp / player["max_hp"]

    return {
        "wins": wins,
        "losses": losses,
        "timeouts": timeouts,
        "win_rate": round(wins / iterations, 4) if iterations > 0 else 0.0,
        "avg_turns": round(total_turns / iterations, 2) if iterations > 0 else 0.0,
        "avg_remaining_hp_pct": round(total_remaining_hp_pct / iterations, 4) if iterations > 0 else 0.0,
        "total": iterations,
    }


def run_pvp(
    player_a: dict,
    player_b: dict,
    iterations: int = 1000,
    seed: int = None,
) -> dict:
    """
    PVP 전투 시뮬레이션 (대칭 전투).

    양 플레이어 모두 동일한 규칙으로 교전.
    상태이상/정예 특성 없이 순수 스탯 기반.

    Args:
        player_a: 플레이어 A 스탯 dict
        player_b: 플레이어 B 스탯 dict
        iterations: 시뮬레이션 반복 횟수
        seed: 랜덤 시드

    Returns:
        {"a_wins", "b_wins", "draws", "a_win_rate", "avg_turns", "total"}
    """
    MAX_TURNS = 200

    a_wins = 0
    b_wins = 0
    draws = 0
    total_turns = 0

    for i in range(iterations):
        if seed is not None:
            random.seed(seed + i)

        # 유닛 생성
        a_size = int(player_a.get("size", 2))
        b_size = int(player_b.get("size", 2))

        a_unit = CombatUnit(
            hp=player_a["max_hp"], max_hp=player_a["max_hp"],
            atk=player_a["attack"], atk_speed=player_a["atk_speed"],
            defense=player_a["defense"], magic_def=player_a.get("magic_def", 0),
            acc=player_a["acc"], eva=player_a["eva"],
            crit_chance=player_a["crit_chance"], crit_dmg=player_a["crit_dmg"],
            level=int(player_a["level"]), size=a_size, fhr=player_a.get("fhr", 0.0),
        )

        b_unit = CombatUnit(
            hp=player_b["max_hp"], max_hp=player_b["max_hp"],
            atk=player_b["attack"], atk_speed=player_b["atk_speed"],
            defense=player_b["defense"], magic_def=player_b.get("magic_def", 0),
            acc=player_b["acc"], eva=player_b["eva"],
            crit_chance=player_b["crit_chance"], crit_dmg=player_b["crit_dmg"],
            level=int(player_b["level"]), size=b_size, fhr=player_b.get("fhr", 0.0),
        )

        # 사이즈 보정
        a_size_mult = get_size_correction(a_unit.size, b_unit.size)
        b_size_mult = get_size_correction(b_unit.size, a_unit.size)

        # 타이머 기반 전투 루프
        a_timer = 0.0
        b_timer = 0.0
        dt = 0.1
        turn = 0

        while a_unit.hp > 0 and b_unit.hp > 0 and turn < MAX_TURNS:
            a_timer += a_unit.atk_speed * dt
            b_timer += b_unit.atk_speed * dt

            # A 공격
            if a_timer >= 1.0 and b_unit.hp > 0:
                a_timer -= 1.0
                turn += 1

                entry = BattleManager._attack_v2(
                    "player_a", a_unit.atk, a_unit.level, a_unit.acc,
                    b_unit.defense, b_unit.eva, b_unit.level,
                    a_unit.crit_chance, a_unit.crit_dmg, a_size_mult,
                )
                b_unit.hp -= entry["damage"]

            # B 공격
            if b_timer >= 1.0 and a_unit.hp > 0 and b_unit.hp > 0:
                b_timer -= 1.0
                turn += 1

                entry = BattleManager._attack_v2(
                    "player_b", b_unit.atk, b_unit.level, b_unit.acc,
                    a_unit.defense, a_unit.eva, a_unit.level,
                    b_unit.crit_chance, b_unit.crit_dmg, b_size_mult,
                )
                a_unit.hp -= entry["damage"]

        # 결과 판정
        if b_unit.hp <= 0 and a_unit.hp > 0:
            a_wins += 1
        elif a_unit.hp <= 0 and b_unit.hp > 0:
            b_wins += 1
        else:
            draws += 1

        total_turns += turn

    return {
        "a_wins": a_wins,
        "b_wins": b_wins,
        "draws": draws,
        "a_win_rate": round(a_wins / iterations, 4) if iterations > 0 else 0.0,
        "avg_turns": round(total_turns / iterations, 2) if iterations > 0 else 0.0,
        "total": iterations,
    }
