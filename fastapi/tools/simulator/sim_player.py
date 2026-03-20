"""시뮬레이션용 플레이어 빌더 — DB/Redis 없이 전투 스탯 dict 생성

BattleManager._load_battle_stats (lines 280-331)의 계산 로직을 동일하게 재현.
"""
import random
from tools.simulator.sim_config import init_metadata, get_configs
from services.rpg.ItemDropManager import ItemDropManager

# ── 스탯 배분 프리셋 (str / dex / vit / luck 비율) ──
STAT_PRESETS = {
    "balanced": (25, 25, 25, 25),
    "str":      (60, 15, 15, 10),
    "dex":      (15, 60, 10, 15),
    "tank":     (10, 10, 60, 20),
}

# 장비 슬롯 목록 (weapon 제외 = armor 계열)
ARMOR_SLOTS = ["armor", "helmet", "gloves", "boots"]
ALL_EQUIP_SLOTS = ["weapon"] + ARMOR_SLOTS


def build_player(
    level: int,
    stat_str: int,
    stat_dex: int,
    stat_vit: int,
    stat_luck: int,
    weapon: dict = None,
    armor_opts: dict = None,
    set_points: dict = None,
    basic_sin: str = None,
) -> dict:
    """BattleManager._load_battle_stats 와 동일한 전투 스탯 dict 반환.

    Args:
        level: 캐릭터 레벨
        stat_str/dex/vit/luck: 유저 스탯
        weapon: 무기 옵션 dict (base_atk, base_aspd, atk_pct 등)
        armor_opts: 무기 외 장비 옵션 합산 dict (atk_pct, def 등)
        set_points: 세트포인트 dict {"wrath": 2, ...}
        basic_sin: 유저 기본 죄종 (세트포인트 +1)
    """
    weapon = weapon or {}
    armor_opts = armor_opts or {}
    set_points = dict(set_points) if set_points else {}

    # basic_sin → 세트포인트 +1
    if basic_sin:
        sin = basic_sin.lower()
        set_points[sin] = set_points.get(sin, 0) + 1

    # ── 장비 옵션 집계 (BattleManager L280-299 동일) ──
    # weapon의 옵션도 atk_pct 등에 합산된다 (base_atk/base_aspd 제외)
    i_atk_pct = i_aspd_pct = i_hp_pct = 0.0
    i_acc = i_eva = i_crit_ch = i_crit_dmg = 0.0
    i_def = i_mdef = 0.0

    # weapon + armor 옵션을 모두 합산
    for opts in (weapon, armor_opts):
        i_atk_pct  += opts.get("atk_pct", 0)
        i_aspd_pct += opts.get("aspd_pct", 0)
        i_hp_pct   += opts.get("hp_pct", 0)
        i_acc      += opts.get("acc", 0)
        i_eva      += opts.get("eva", 0)
        i_crit_ch  += opts.get("crit_chance", 0)
        i_crit_dmg += opts.get("crit_dmg", 0)
        i_def      += opts.get("def", 0)
        i_mdef     += opts.get("mdef", 0)

    base_wpn_atk  = weapon.get("base_atk", 10.0)
    base_wpn_aspd = weapon.get("base_aspd", 1.0)

    # ── 전투 스탯 계산 (BattleManager L304-315 동일) ──
    battle = {
        "level":       float(level),
        "max_hp":      (100 + stat_vit * 10) * (1 + i_hp_pct / 100),
        "attack":      base_wpn_atk * (1 + stat_str * 0.005) * (1 + i_atk_pct / 100),
        "atk_speed":   base_wpn_aspd * (1 + stat_dex * 0.003) * (1 + i_aspd_pct / 100),
        "acc":         stat_dex * 0.005 + i_acc,
        "eva":         stat_luck * 0.001 + i_eva,
        "crit_chance": stat_luck * 0.001 + i_crit_ch,
        "crit_dmg":    1.5 + stat_luck * 0.003 + i_crit_dmg,
        "defense":     i_def,
        "magic_def":   i_mdef,
        "set_points":  set_points,
    }

    # ── 폭식(gluttony) 패널티 (BattleManager L318-331 동일) ──
    gluttony_pts = set_points.get("gluttony", 0)
    if gluttony_pts >= 4:
        penalty = 0.35
    elif gluttony_pts >= 3:
        penalty = 0.20
    elif gluttony_pts >= 2:
        penalty = 0.10
    else:
        penalty = 0
    if penalty > 0:
        battle["attack"]  *= (1 - penalty)
        battle["defense"] *= (1 - penalty)
        battle["max_hp"]  *= (1 - penalty)

    # 전투 시작용 current_hp 설정
    battle["current_hp"] = battle["max_hp"]

    return battle


def _estimate_mlvl(level: int) -> int:
    """플레이어 레벨 → 예상 몬스터 레벨(mlvl) 추정.

    level_exp_table 기반으로 해당 레벨에서 파밍할 스테이지의 dlvl을 추정.
    간단하게 level 자체를 mlvl로 사용 (dlvl ≈ player level).
    """
    return max(1, min(level, 50))


def _weapon_base_stats(base_item: dict) -> tuple:
    """equipment_base.csv 행에서 base_atk, base_aspd 추출.

    base_atk = (min_damage + max_damage) / 2
    base_aspd = speed
    """
    min_dmg = float(base_item.get("min_damage", 10))
    max_dmg = float(base_item.get("max_damage", 10))
    speed = float(base_item.get("speed", 1.0))
    return (min_dmg + max_dmg) / 2, speed


def generate_equipment_for_level(level: int) -> tuple:
    """레벨에 맞는 장비 풀세트 생성.

    Returns:
        (weapon_opts, armor_opts, set_points)
        - weapon_opts: 무기 dynamic_options + base_atk/base_aspd
        - armor_opts: 방어구 4부위 dynamic_options 합산
        - set_points: 세트포인트 집계
    """
    configs = get_configs()
    mlvl = _estimate_mlvl(level)

    # 더미 몬스터 (부위 결정용)
    dummy_monster = {"monster_base": "Beast", "size_type": 1}
    # 챕터 추정 (level 기반): 1~10=ch1, 11~20=ch2, 21~30=ch3, 31~40=ch4
    chapter = max(1, min((level - 1) // 10 + 1, 7))
    stage_id = chapter * 100 + 1  # e.g. 101, 201, ...

    weapon_opts = {}
    armor_opts = {}
    set_points = {}

    # ── 무기 생성 ──
    weapon_bases = [b for b in configs.get("equip_bases", []) if b.get("main_group") == "weapon"]
    if weapon_bases:
        # _generate_equipment로 무기 생성 시도
        attempts = 0
        weapon_item = None
        while attempts < 20:
            item = ItemDropManager._generate_equipment(mlvl, dummy_monster, stage_id)
            if item and item.get("equip_slot") == "weapon":
                weapon_item = item
                break
            attempts += 1

        if weapon_item:
            weapon_opts = dict(weapon_item.get("dynamic_options", {}))
            # equipment_base.csv에서 base_atk/base_aspd 추출
            base_id = weapon_item.get("base_item_id", 0)
            base_row = next((b for b in weapon_bases if int(b.get("item_idx", 0)) == base_id), None)
            if base_row:
                base_atk, base_aspd = _weapon_base_stats(base_row)
                weapon_opts["base_atk"] = base_atk
                weapon_opts["base_aspd"] = base_aspd
            else:
                weapon_opts.setdefault("base_atk", 10.0)
                weapon_opts.setdefault("base_aspd", 1.0)

            # 세트포인트 집계
            for sin_id in (weapon_item.get("prefix_id"), weapon_item.get("suffix_id")):
                if sin_id:
                    sin = sin_id.lower()
                    set_points[sin] = set_points.get(sin, 0) + 1
        else:
            # 폴백: 기본 무기
            base_row = random.choice(weapon_bases)
            base_atk, base_aspd = _weapon_base_stats(base_row)
            weapon_opts = {"base_atk": base_atk, "base_aspd": base_aspd}

    # ── 방어구 4부위 생성 ──
    for slot in ARMOR_SLOTS:
        attempts = 0
        while attempts < 20:
            item = ItemDropManager._generate_equipment(mlvl, dummy_monster, stage_id)
            if item and item.get("equip_slot") == slot:
                opts = item.get("dynamic_options", {})
                for k, v in opts.items():
                    armor_opts[k] = armor_opts.get(k, 0) + v
                # 세트포인트
                item_sins = set()
                if item.get("prefix_id"):
                    item_sins.add(item["prefix_id"].lower())
                if item.get("suffix_id"):
                    item_sins.add(item["suffix_id"].lower())
                for sin in item_sins:
                    set_points[sin] = set_points.get(sin, 0) + 1
                break
            attempts += 1

    return weapon_opts, armor_opts, set_points


def build_player_from_level(level: int, stat_allocation: str = "balanced") -> dict:
    """레벨 기반 편의 빌더 — 스탯 자동 배분 + 장비 자동 생성.

    Args:
        level: 캐릭터 레벨 (1~50)
        stat_allocation: 스탯 배분 프리셋 ("balanced", "str", "dex", "tank")

    Returns:
        build_player()와 동일한 전투 스탯 dict
    """
    preset = STAT_PRESETS.get(stat_allocation, STAT_PRESETS["balanced"])

    # 기본 스탯 10 + (level-1)*5 포인트를 비율로 배분
    base_stat = 10
    total_bonus = (level - 1) * 5
    ratios = [r / sum(preset) for r in preset]

    stat_str  = base_stat + int(total_bonus * ratios[0])
    stat_dex  = base_stat + int(total_bonus * ratios[1])
    stat_vit  = base_stat + int(total_bonus * ratios[2])
    stat_luck = base_stat + int(total_bonus * ratios[3])

    # 장비 생성
    weapon_opts, armor_opts, set_points = generate_equipment_for_level(level)

    return build_player(
        level=level,
        stat_str=stat_str,
        stat_dex=stat_dex,
        stat_vit=stat_vit,
        stat_luck=stat_luck,
        weapon=weapon_opts,
        armor_opts=armor_opts,
        set_points=set_points,
    )
