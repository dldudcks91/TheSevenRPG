"""TheSevenRPG 시뮬레이션 도구 — 밸런싱용 오프라인 CLI

사용법:
    # PVE 시뮬레이션
    python -m tools.simulator.sim_runner pve --monster 1101 --level 5 --iterations 500

    # 드롭 시뮬레이션
    python -m tools.simulator.sim_runner drop --stage 101 --monster 1101 --kills 5000
    python -m tools.simulator.sim_runner drop --stage 101 --monster 1101 --sweep

    # 성장 시뮬레이션
    python -m tools.simulator.sim_runner growth --allocation balanced --start-chapter 1 --end-chapter 4

    # PVP 시뮬레이션
    python -m tools.simulator.sim_runner pvp --a-level 20 --a-preset str --b-level 20 --b-preset tank
"""

import sys, os

_FASTAPI_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _FASTAPI_DIR not in sys.path:
    sys.path.insert(0, _FASTAPI_DIR)

import argparse
import random


def main():
    parser = argparse.ArgumentParser(
        description="TheSevenRPG Simulator — offline balancing tool"
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # ── PVE mode ──
    pve = subparsers.add_parser("pve", help="PVE 전투 시뮬레이션")
    pve.add_argument("--monster", type=int, required=True, help="몬스터 인덱스 (monster_idx)")
    pve.add_argument("--spawn-type", default="일반", help="스폰 타입 (일반/정예/보스/챕터보스)")
    pve.add_argument("--stage", type=int, default=101, help="스테이지 ID (정예 시 필수)")
    pve.add_argument("--level", type=int, required=True, help="플레이어 레벨")
    pve.add_argument("--preset", default="balanced",
                     choices=["balanced", "str", "dex", "tank"],
                     help="스탯 프리셋")
    pve.add_argument("--iterations", type=int, default=1000, help="반복 횟수")
    pve.add_argument("--seed", type=int, default=None, help="랜덤 시드")

    # ── Drop mode ──
    drop = subparsers.add_parser("drop", help="드롭 시뮬레이션")
    drop.add_argument("--stage", type=int, required=True, help="스테이지 ID")
    drop.add_argument("--monster", type=int, required=True, help="몬스터 인덱스")
    drop.add_argument("--spawn-type", default="일반", help="스폰 타입")
    drop.add_argument("--kills", type=int, default=10000, help="처치 횟수")
    drop.add_argument("--sweep", action="store_true", help="일반/정예/보스 전체 비교")
    drop.add_argument("--seed", type=int, default=None, help="랜덤 시드")

    # ── Growth mode ──
    growth = subparsers.add_parser("growth", help="성장 시뮬레이션")
    growth.add_argument("--allocation", default="balanced",
                        choices=["balanced", "str", "dex", "tank"],
                        help="스탯 배분 프리셋")
    growth.add_argument("--start-chapter", type=int, default=1, help="시작 챕터")
    growth.add_argument("--end-chapter", type=int, default=4, help="종료 챕터")
    growth.add_argument("--seed", type=int, default=None, help="랜덤 시드")

    # ── PVP mode ──
    pvp = subparsers.add_parser("pvp", help="PVP 시뮬레이션")
    pvp.add_argument("--a-level", type=int, required=True, help="플레이어 A 레벨")
    pvp.add_argument("--a-preset", default="balanced",
                     choices=["balanced", "str", "dex", "tank"],
                     help="플레이어 A 스탯 프리셋")
    pvp.add_argument("--b-level", type=int, required=True, help="플레이어 B 레벨")
    pvp.add_argument("--b-preset", default="balanced",
                     choices=["balanced", "str", "dex", "tank"],
                     help="플레이어 B 스탯 프리셋")
    pvp.add_argument("--iterations", type=int, default=1000, help="반복 횟수")
    pvp.add_argument("--seed", type=int, default=None, help="랜덤 시드")

    args = parser.parse_args()

    # ── 메타데이터 초기화 ──
    from tools.simulator.sim_config import init_metadata
    init_metadata()

    # ── Dispatch ──
    if args.mode == "pve":
        _run_pve(args)
    elif args.mode == "drop":
        _run_drop(args)
    elif args.mode == "growth":
        _run_growth(args)
    elif args.mode == "pvp":
        _run_pvp(args)


def _run_pve(args):
    """PVE 모드 실행"""
    from tools.simulator.sim_growth import _allocate_stats, _build_player_simple, STAT_POINTS_PER_LEVEL
    from tools.simulator.sim_battle import run_pve
    from tools.simulator.sim_report import report_pve

    # sim_player가 있으면 사용, 없으면 sim_growth의 간이 빌더 사용
    try:
        from tools.simulator.sim_player import build_player_from_level
        player = build_player_from_level(args.level, args.preset)
    except ImportError:
        total_points = (args.level - 1) * STAT_POINTS_PER_LEVEL
        stats = _allocate_stats(total_points, args.preset)
        player = _build_player_simple(args.level, stats)

    results = run_pve(
        player, args.monster, args.spawn_type, args.stage,
        args.iterations, args.seed,
    )
    print(report_pve(results, args.monster, args.spawn_type, args.iterations))


def _run_drop(args):
    """드롭 모드 실행"""
    from tools.simulator.sim_drop import run_drop_sim, run_stage_sweep
    from tools.simulator.sim_report import report_drop, report_stage_sweep

    if args.sweep:
        results = run_stage_sweep(args.stage, args.kills, args.seed)
        print(report_stage_sweep(results, args.stage))
    else:
        results = run_drop_sim(
            args.stage, args.monster, args.spawn_type, args.kills, args.seed,
        )
        print(report_drop(results, args.stage, args.monster, args.spawn_type, args.kills))


def _run_growth(args):
    """성장 모드 실행"""
    from tools.simulator.sim_growth import run_growth_sim
    from tools.simulator.sim_report import report_growth

    results = run_growth_sim(
        args.allocation, args.seed, args.start_chapter, args.end_chapter,
    )
    print(report_growth(results, args.allocation))


def _run_pvp(args):
    """PVP 모드 실행"""
    from tools.simulator.sim_growth import _allocate_stats, _build_player_simple, STAT_POINTS_PER_LEVEL
    from tools.simulator.sim_battle import run_pvp
    from tools.simulator.sim_report import report_pvp

    # sim_player 사용 시도, 없으면 간이 빌더
    try:
        from tools.simulator.sim_player import build_player_from_level
        player_a = build_player_from_level(args.a_level, args.a_preset)
        player_b = build_player_from_level(args.b_level, args.b_preset)
    except ImportError:
        pts_a = (args.a_level - 1) * STAT_POINTS_PER_LEVEL
        stats_a = _allocate_stats(pts_a, args.a_preset)
        player_a = _build_player_simple(args.a_level, stats_a)

        pts_b = (args.b_level - 1) * STAT_POINTS_PER_LEVEL
        stats_b = _allocate_stats(pts_b, args.b_preset)
        player_b = _build_player_simple(args.b_level, stats_b)

    results = run_pvp(player_a, player_b, args.iterations, args.seed)
    print(report_pvp(
        results, args.a_level, args.a_preset,
        args.b_level, args.b_preset, args.iterations,
    ))


if __name__ == "__main__":
    main()
