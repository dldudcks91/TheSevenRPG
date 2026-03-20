"""
시뮬레이션 결과 리포트 포매터

PVE / PVP / 드롭 / 성장 시뮬레이션 결과를 콘솔 출력용 문자열로 변환한다.

사용법:
    from tools.simulator.sim_report import report_pve, report_pvp, report_drop, report_growth
"""

import sys, os

_FASTAPI_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _FASTAPI_DIR not in sys.path:
    sys.path.insert(0, _FASTAPI_DIR)

from services.system.GameDataManager import GameDataManager


def _get_monster_name(monster_idx: int) -> str:
    """몬스터 인덱스로 한글 이름 조회. 없으면 'Unknown'."""
    monsters = GameDataManager.REQUIRE_CONFIGS.get("monsters", {})
    monster = monsters.get(int(monster_idx))
    if monster:
        return monster.get("name", f"Unknown({monster_idx})")
    return f"Unknown({monster_idx})"


def report_pve(
    results: dict,
    monster_idx: int,
    spawn_type: str,
    iterations: int,
) -> str:
    """PVE 시뮬레이션 결과 포매팅.

    Args:
        results: run_pve() 반환값
        monster_idx: 몬스터 인덱스
        spawn_type: 스폰 타입
        iterations: 반복 횟수
    """
    monster_name = _get_monster_name(monster_idx)
    win_rate = results["win_rate"] * 100
    avg_turns = results["avg_turns"]
    avg_hp_pct = results["avg_remaining_hp_pct"] * 100
    timeout_pct = (results["timeouts"] / iterations * 100) if iterations > 0 else 0.0

    lines = [
        "",
        "=== PVE Simulation Results ===",
        f"Monster: {monster_name} ({monster_idx}) | Spawn: {spawn_type}",
        f"Iterations: {iterations:,}",
        "",
        f"Win Rate:     {win_rate:.1f}%",
        f"Avg Turns:    {avg_turns:.1f}",
        f"Avg HP Left:  {avg_hp_pct:.1f}%",
        f"Timeouts:     {timeout_pct:.1f}%",
        "",
        f"Wins: {results['wins']:,}  |  Losses: {results['losses']:,}  |  Timeouts: {results['timeouts']:,}",
        "",
    ]
    return "\n".join(lines)


def report_pvp(
    results: dict,
    a_level: int,
    a_preset: str,
    b_level: int,
    b_preset: str,
    iterations: int,
) -> str:
    """PVP 시뮬레이션 결과 포매팅.

    Args:
        results: run_pvp() 반환값
        a_level / a_preset: 플레이어 A 정보
        b_level / b_preset: 플레이어 B 정보
        iterations: 반복 횟수
    """
    a_win_pct = results["a_win_rate"] * 100
    b_win_pct = (results["b_wins"] / iterations * 100) if iterations > 0 else 0.0
    draw_pct = (results["draws"] / iterations * 100) if iterations > 0 else 0.0

    lines = [
        "",
        "=== PVP Simulation Results ===",
        f"Player A (Lv{a_level} {a_preset.upper()}) vs Player B (Lv{b_level} {b_preset.upper()})",
        f"Iterations: {iterations:,}",
        "",
        f"Player A Win Rate: {a_win_pct:.1f}%",
        f"Player B Win Rate: {b_win_pct:.1f}%",
        f"Draws:             {draw_pct:.1f}%",
        f"Avg Turns:         {results['avg_turns']:.1f}",
        "",
    ]
    return "\n".join(lines)


def report_drop(
    results: dict,
    stage_id: int,
    monster_idx: int,
    spawn_type: str,
    kills: int,
) -> str:
    """드롭 시뮬레이션 결과 포매팅.

    Args:
        results: run_drop_sim() 반환값
        stage_id: 스테이지 ID
        monster_idx: 몬스터 인덱스
        spawn_type: 스폰 타입
        kills: 처치 횟수
    """
    monster_name = _get_monster_name(monster_idx)
    drop_rate = results["drop_rate"] * 100

    gold = results["gold"]
    equip = results["equipment"]
    card = results["card"]
    potion = results["potion"]
    ore = results["ore"]
    material = results["monster_material"]
    stigma = results["stigma"]

    lines = [
        "",
        "=== Drop Simulation Results ===",
        f"Stage: {stage_id} | Monster: {monster_name} ({monster_idx}) ({spawn_type}) | Kills: {kills:,}",
        "",
        f"Drop Rate: {drop_rate:.1f}%  (total drops: {results['total_drops']:,})",
        "",
    ]

    # Gold
    if gold["count"] > 0:
        lines.append(f"Gold:      {gold['count']:,} drops  (avg {gold['avg']:.1f} / drop, "
                      f"min {gold['min']}, max {gold['max']}, total {gold['total']:,})")
    else:
        lines.append("Gold:      0 drops")

    # Equipment
    if equip["count"] > 0:
        rarity_parts = []
        for rarity, count in sorted(equip["by_rarity"].items()):
            rarity_parts.append(f"{rarity}: {count:,}")
        rarity_str = ", ".join(rarity_parts)
        lines.append(f"Equipment: {equip['count']:,}  ({rarity_str})")
        if equip["by_slot"]:
            slot_parts = [f"{s}: {c}" for s, c in sorted(equip["by_slot"].items())]
            lines.append(f"           slots: {', '.join(slot_parts)}")
    else:
        lines.append("Equipment: 0")

    # Card
    lines.append(f"Cards:     {card['count']:,}")

    # Potion
    lines.append(f"Potion:    {potion['count']:,}")

    # Ore
    if ore["count"] > 0:
        ore_parts = [f"{ore_id}: {cnt}" for ore_id, cnt in sorted(ore["by_id"].items(), key=lambda x: str(x[0]))]
        lines.append(f"Ore:       {ore['count']:,}  ({', '.join(ore_parts)})")
    else:
        lines.append("Ore:       0")

    # Monster Material
    if material["count"] > 0:
        mat_parts = [f"{mid}: {cnt}" for mid, cnt in sorted(material["by_id"].items(), key=lambda x: str(x[0]))]
        lines.append(f"Material:  {material['count']:,}  ({', '.join(mat_parts)})")
    else:
        lines.append("Material:  0")

    # Stigma
    if stigma["count"] > 0:
        lines.append(f"Stigma:    {stigma['count']:,}")
    else:
        lines.append("Stigma:    0")

    lines.append("")
    return "\n".join(lines)


def report_stage_sweep(results: dict, stage_id: int) -> str:
    """스테이지 sweep (일반/정예/보스 비교) 결과 포매팅.

    Args:
        results: run_stage_sweep() 반환값 — {"일반": {...}, "정예": {...}, "보스": {...}}
        stage_id: 스테이지 ID
    """
    lines = [
        "",
        f"=== Stage Sweep Results (Stage {stage_id}) ===",
        "",
    ]

    # 헤더
    header = f"{'Spawn Type':<12} {'Kills':>8} {'Drops':>8} {'Rate':>7} " \
             f"{'Gold':>6} {'Equip':>6} {'Card':>5} {'Ore':>5} {'Mat':>5} {'Stigma':>6}"
    lines.append(header)
    lines.append("-" * len(header))

    for spawn_type in ["일반", "정예", "보스"]:
        r = results.get(spawn_type)
        if not r:
            continue

        rate = r["drop_rate"] * 100
        row = (
            f"{spawn_type:<12} "
            f"{r['total_kills']:>8,} "
            f"{r['total_drops']:>8,} "
            f"{rate:>6.1f}% "
            f"{r['gold']['count']:>6,} "
            f"{r['equipment']['count']:>6,} "
            f"{r['card']['count']:>5,} "
            f"{r['ore']['count']:>5,} "
            f"{r['monster_material']['count']:>5,} "
            f"{r['stigma']['count']:>6,}"
        )
        lines.append(row)

    lines.append("")

    # 상세 장비 등급 비교
    lines.append("--- Equipment Rarity Breakdown ---")
    for spawn_type in ["일반", "정예", "보스"]:
        r = results.get(spawn_type)
        if not r or r["equipment"]["count"] == 0:
            continue
        rarity_parts = [f"{k}: {v}" for k, v in sorted(r["equipment"]["by_rarity"].items())]
        lines.append(f"  {spawn_type}: {', '.join(rarity_parts)}")

    lines.append("")
    return "\n".join(lines)


def report_growth(results: dict, allocation: str) -> str:
    """성장 시뮬레이션 결과 포매팅.

    Args:
        results: run_growth_sim() 반환값
        allocation: 스탯 배분 프리셋명
    """
    chapters = results.get("chapters", {})
    summary = results.get("summary", {})

    # 챕터 범위 추출
    if chapters:
        ch_min = min(chapters.keys())
        ch_max = max(chapters.keys())
    else:
        ch_min = ch_max = 0

    lines = [
        "",
        "=== Growth Simulation Results ===",
        f"Allocation: {allocation} | Chapters: {ch_min}-{ch_max}",
        "",
    ]

    # 테이블 헤더
    header = f"{'Chapter':<9} {'Entry Lv':>9} {'Exit Lv':>8} {'Kills':>7} {'Deaths':>7} {'Gold':>10} {'EXP':>10} {'Stages':>7}"
    lines.append(header)
    lines.append("-" * len(header))

    for ch_num in sorted(chapters.keys()):
        ch = chapters[ch_num]
        row = (
            f"Ch{ch_num:<7} "
            f"{ch['entry_level']:>9} "
            f"{ch['exit_level']:>8} "
            f"{ch['total_kills']:>7,} "
            f"{ch['deaths']:>7,} "
            f"{ch['gold_earned']:>10,} "
            f"{ch['exp_earned']:>10,} "
            f"{ch['stages_cleared']:>7}"
        )
        lines.append(row)

    lines.append("-" * len(header))

    # 요약
    lines.append(
        f"{'Total':<9} "
        f"{'':>9} "
        f"{summary.get('final_level', 0):>8} "
        f"{summary.get('total_kills', 0):>7,} "
        f"{summary.get('total_deaths', 0):>7,} "
        f"{summary.get('total_gold', 0):>10,}"
    )

    lines.append("")
    lines.append(f"Final Level: {summary.get('final_level', 0)}  |  "
                 f"Remaining EXP: {summary.get('final_exp', 0):,}")
    lines.append("")

    return "\n".join(lines)
