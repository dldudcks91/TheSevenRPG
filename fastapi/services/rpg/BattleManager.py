import random
import logging
from typing import Optional
from sqlalchemy.orm.attributes import flag_modified
from database import SessionLocal
from models import User, UserStat, Item, BattleSession
from services.system.GameDataManager import GameDataManager
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response
from services.rpg.ItemDropManager import ItemDropManager

logger = logging.getLogger("RPG_SERVER")

DEATH_EXP_PENALTY_RATE = 0.10  # 사망 시 현재 레벨 내 경험치 10% 차감
WAVES_PER_STAGE = 4
NORMAL_WAVE_MONSTER_COUNT = 4  # 웨이브 1~3: 일반3 + 정예1
BOSS_WAVE_MONSTER_COUNT = 1    # 웨이브 4: 보스 1


class BattleManager:
    """전투 시뮬레이션 엔진 (API 3001)"""

    MAX_LEVEL = 50
    STAT_POINTS_PER_LEVEL = 5
    BASE_EXP = 10
    EXP_STORY_MULT = 1.3
    EXP_GRIND_MULT = 2.0
    GRIND_START_LEVEL = 40

    # ── CSV 폴백용 스폰 등급 배율 ──
    _FALLBACK_SPAWN_GRADES = {
        "normal":       {"hp_mult": 1.0,  "atk_mult": 1.0, "exp_mult": 1.0,  "gold_mult": 1.0},
        "elite":        {"hp_mult": 3.0,  "atk_mult": 1.5, "exp_mult": 3.0,  "gold_mult": 2.0},
        "stage_boss":   {"hp_mult": 10.0, "atk_mult": 2.5, "exp_mult": 10.0, "gold_mult": 5.0},
        "chapter_boss": {"hp_mult": 20.0, "atk_mult": 5.0, "exp_mult": 20.0, "gold_mult": 10.0},
    }

    _GRADE_KR_TO_EN = {
        "일반": "normal",
        "정예": "elite",
        "보스": "stage_boss",
        "챕터보스": "chapter_boss",
    }

    _exp_table_cache = None

    # ── 레벨 테이블 ──

    @classmethod
    def _get_exp_table(cls) -> dict:
        """레벨별 필요 XP 테이블. CSV 우선, 없으면 공식으로 생성."""
        if cls._exp_table_cache is not None:
            return cls._exp_table_cache

        csv_table = GameDataManager.REQUIRE_CONFIGS.get("level_config")
        if csv_table:
            cls._exp_table_cache = csv_table
            logger.info(f"[BattleManager] level_config CSV 로드 완료 ({len(csv_table)}레벨)")
            return cls._exp_table_cache

        table = {}
        last_story_exp = cls.BASE_EXP * (cls.EXP_STORY_MULT ** (cls.GRIND_START_LEVEL - 2))
        for lv in range(1, cls.MAX_LEVEL):
            if lv < cls.GRIND_START_LEVEL:
                required = cls.BASE_EXP * (cls.EXP_STORY_MULT ** (lv - 1))
            else:
                required = last_story_exp * (cls.EXP_GRIND_MULT ** (lv - cls.GRIND_START_LEVEL + 1))
            table[lv] = {"required_exp": int(required), "stat_points": cls.STAT_POINTS_PER_LEVEL}

        cls._exp_table_cache = table
        logger.info(f"[BattleManager] level_config 폴백 테이블 생성 (Lv1={table[1]['required_exp']}, Lv39={table[39]['required_exp']}, Lv40={table[40]['required_exp']})")
        return cls._exp_table_cache

    @classmethod
    def _get_spawn_grade(cls, spawn_type: str) -> Optional[dict]:
        """스폰 등급 배율. CSV 우선, 없으면 폴백."""
        grade_en = cls._GRADE_KR_TO_EN.get(spawn_type, spawn_type)
        csv_grades = GameDataManager.REQUIRE_CONFIGS.get("spawn_grade_config")
        if csv_grades and grade_en in csv_grades:
            return csv_grades[grade_en]
        return cls._FALLBACK_SPAWN_GRADES.get(grade_en)

    # ── API 3001: 전투 시뮬레이션 ──

    @classmethod
    async def battle_result(cls, user_no: int, data: dict):
        """
        API 3001: 전투 시뮬레이션
        - BattleSession 존재 검증
        - 플레이어 HP: session.current_hp에서 시작 (연속 HP)
        - 승리: wave_kills 업데이트, pending_drops 저장, 웨이브 클리어 시 보상 지급
        - 패배: 사망 패널티 (EXP 10% 차감), 현재 웨이브 리셋
        """
        # ── [1] 입력 추출 ──
        monster_idx = data.get("monster_idx")
        spawn_type = data.get("spawn_type", "일반")

        if monster_idx is None:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "monster_idx가 필요합니다.")

        grade = cls._get_spawn_grade(spawn_type)
        if not grade:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, f"유효하지 않은 spawn_type: {spawn_type}")

        # ── [2] 메타데이터 검증 ──
        monsters = GameDataManager.REQUIRE_CONFIGS.get("monsters", {})
        monster = monsters.get(int(monster_idx))
        if not monster:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, f"몬스터를 찾을 수 없습니다: {monster_idx}")

        # ── [3] DB 세션 + BattleSession 검증 ──
        db = SessionLocal()
        try:
            session = db.query(BattleSession).filter(
                BattleSession.user_no == user_no
            ).with_for_update().first()
            if not session:
                return error_response(ErrorCode.BATTLE_SESSION_NOT_FOUND, "진행 중인 전투 세션이 없습니다.")

            # 웨이브 순서 검증: 현재 웨이브의 킬 수로 몬스터 순서 확인
            current_wave = session.current_wave
            wave_kills = session.wave_kills or {}
            current_wave_kills = wave_kills.get(str(current_wave), [])

            expected_count = BOSS_WAVE_MONSTER_COUNT if current_wave == WAVES_PER_STAGE else NORMAL_WAVE_MONSTER_COUNT
            if len(current_wave_kills) >= expected_count:
                return error_response(ErrorCode.WAVE_NOT_CLEARED, "현재 웨이브는 이미 클리어되었습니다. 다음 웨이브로 진행하세요.")

            # 유저 전투 스탯 로드
            player = await cls._load_battle_stats(user_no)
            if not player:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯을 찾을 수 없습니다.")

            # 플레이어 HP를 세션에서 가져옴 (연속 HP)
            player["current_hp"] = float(session.current_hp)

            # ── [4] 전투 시뮬레이션 ──
            # 정예 몬스터: EliteManager로 특성 생성 + 스탯 보정
            elite_traits = []
            if spawn_type == "정예":
                from services.rpg.EliteManager import EliteManager
                elite_stats, elite_traits = EliteManager.generate_elite(
                    session.stage_id, monster, grade
                )
                battle_log, result, remaining_hp = cls._simulate_with_hp(
                    player, monster, grade, elite_stats=elite_stats, traits=elite_traits
                )
            else:
                battle_log, result, remaining_hp = cls._simulate_with_hp(
                    player, monster, grade
                )

            rewards = {}
            wave_cleared = False
            stage_cleared = False

            drops = []

            if result == "win":
                # 킬 기록 업데이트
                current_wave_kills.append({
                    "monster_idx": int(monster_idx),
                    "spawn_type": spawn_type,
                })
                wave_kills[str(current_wave)] = current_wave_kills
                session.wave_kills = wave_kills
                flag_modified(session, "wave_kills")
                session.current_hp = max(1, remaining_hp)

                # 드롭 판정
                drops = ItemDropManager.process_kill(session.stage_id, int(monster_idx), spawn_type)
                if drops:
                    pending = session.pending_drops or []
                    pending.extend(drops)
                    session.pending_drops = pending
                    flag_modified(session, "pending_drops")

                # 웨이브 클리어 판정
                if len(current_wave_kills) >= expected_count:
                    wave_cleared = True

                    # 보상 지급 (웨이브 클리어 시점)
                    rewards = cls._grant_wave_rewards(db, user_no, wave_kills, str(current_wave))

                    if current_wave >= WAVES_PER_STAGE:
                        # 스테이지 보스 클리어 → clear_stage 호출 가능 상태
                        stage_cleared = True
                    else:
                        # 다음 웨이브로 진행
                        session.current_wave = current_wave + 1

            elif result == "lose":
                # 사망 처리: EXP 10% 차감 + 현재 웨이브 리셋
                cls._apply_death_penalty(db, user_no)

                # 현재 웨이브 킬 리셋 (웨이브 처음부터 재시작)
                if str(current_wave) in wave_kills:
                    wave_kills.pop(str(current_wave))
                    session.wave_kills = wave_kills
                    flag_modified(session, "wave_kills")

                # HP를 max_hp로 복구
                session.current_hp = session.max_hp

            else:  # timeout
                # 타임아웃도 패배 처리
                cls._apply_death_penalty(db, user_no)
                if str(current_wave) in wave_kills:
                    wave_kills.pop(str(current_wave))
                    session.wave_kills = wave_kills
                    flag_modified(session, "wave_kills")
                session.current_hp = session.max_hp

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()

            if rewards.get("leveled_up"):
                try:
                    await RedisManager.delete(f"user:{user_no}:battle_stats")
                except RedisUnavailable:
                    logger.warning(f"[BattleManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

            # 응답용 데이터 추출
            session_state = {
                "stage_id": session.stage_id,
                "current_wave": session.current_wave,
                "current_hp": session.current_hp,
                "max_hp": session.max_hp,
                "wave_kills": session.wave_kills,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[BattleManager] battle_result 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "전투 처리 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "전투 완료",
            "data": {
                "result": result,
                "battle_log": battle_log,
                "rewards": rewards,
                "drops": drops,
                "wave_cleared": wave_cleared,
                "stage_cleared": stage_cleared,
                "session": session_state,
                "elite_traits": elite_traits,
            },
        }

    # ── 전투 스탯 로드 ──

    @classmethod
    async def _load_battle_stats(cls, user_no: int) -> Optional[dict]:
        """Redis 캐시 → DB 재계산 → Redis 저장"""
        cache_key = f"user:{user_no}:battle_stats"

        try:
            cached = await RedisManager.hgetall(cache_key)
            if cached:
                return {k: float(v) for k, v in cached.items()}
        except RedisUnavailable:
            logger.warning(f"[BattleManager] battle_stats 캐시 조회 실패 - Redis 장애 (user_no={user_no})")

        db = SessionLocal()
        try:
            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            if not stat:
                return None

            equipped = db.query(Item).filter(
                Item.user_no == user_no,
                Item.equip_slot.isnot(None),
            ).all()

            i_atk_pct = i_aspd_pct = i_hp_pct = 0.0
            i_acc = i_eva = i_crit_ch = i_crit_dmg = 0.0
            i_def = i_mdef = 0.0
            base_wpn_atk = 10.0
            base_wpn_aspd = 1.0

            for item in equipped:
                opts = item.dynamic_options or {}
                i_atk_pct   += opts.get("atk_pct", 0)
                i_aspd_pct  += opts.get("aspd_pct", 0)
                i_hp_pct    += opts.get("hp_pct", 0)
                i_acc       += opts.get("acc", 0)
                i_eva       += opts.get("eva", 0)
                i_crit_ch   += opts.get("crit_chance", 0)
                i_crit_dmg  += opts.get("crit_dmg", 0)
                i_def       += opts.get("def", 0)
                i_mdef      += opts.get("mdef", 0)
                if item.equip_slot == "weapon":
                    base_wpn_atk  = opts.get("base_atk", 10.0)
                    base_wpn_aspd = opts.get("base_aspd", 1.0)

            # 세트포인트 계산 (같은 DB 세션에서 basic_sin 조회)
            set_points = cls._calc_set_points(equipped, user_no, db)

            battle = {
                "level":      float(stat.level),
                "max_hp":     (100 + stat.stat_vit * 10) * (1 + i_hp_pct / 100),
                "attack":     base_wpn_atk * (1 + stat.stat_str * 0.005) * (1 + i_atk_pct / 100),
                "atk_speed":  base_wpn_aspd * (1 + stat.stat_dex * 0.003) * (1 + i_aspd_pct / 100),
                "acc":        stat.stat_dex * 0.005 + i_acc,
                "eva":        stat.stat_luck * 0.001 + i_eva,
                "crit_chance": stat.stat_luck * 0.001 + i_crit_ch,
                "crit_dmg":   1.5 + stat.stat_luck * 0.003 + i_crit_dmg,
                "defense":    i_def,
                "magic_def":  i_mdef,
                "set_points": set_points,
            }

            # 폭식 패널티: 2세트포인트 이상 시 스탯 감소
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
                battle["attack"] *= (1 - penalty)
                battle["defense"] *= (1 - penalty)
                battle["max_hp"] *= (1 - penalty)

            try:
                await RedisManager.hmset(cache_key, {k: str(v) for k, v in battle.items()})
                await RedisManager.expire(cache_key, 3600)
            except RedisUnavailable:
                logger.warning(f"[BattleManager] battle_stats 캐시 저장 실패 - Redis 장애 (user_no={user_no})")

            return battle
        finally:
            db.close()

    # ── 전투 시뮬레이션 v2 (경직/사이즈/마저항/상태이상/정예특성) ──

    @classmethod
    def _simulate_with_hp(
        cls, player: dict, monster: dict, grade: dict,
        elite_stats: dict = None, traits: list = None,
    ) -> tuple[list, str, int]:
        """
        전투 엔진 v2 — 경직/사이즈보정/상태이상/정예특성 포함
        반환: (battle_log, result, remaining_hp)
        """
        from services.rpg.StatusEffectManager import (
            CombatUnit, get_size_correction,
            POISON_DMG_PER_SEC, BURN_HEAL_REDUCTION,
        )
        traits = traits or []

        # ── 유닛 생성 ──
        p_size = int(player.get("size", 2))
        p_unit = CombatUnit(
            hp=player["current_hp"], max_hp=player["max_hp"],
            atk=player["attack"], atk_speed=player["atk_speed"],
            defense=player["defense"], magic_def=player.get("magic_def", 0),
            acc=player["acc"], eva=player["eva"],
            crit_chance=player["crit_chance"], crit_dmg=player["crit_dmg"],
            level=int(player["level"]), size=p_size, fhr=player.get("fhr", 0.0),
        )

        if elite_stats:
            m_unit = CombatUnit(
                hp=elite_stats["hp"], max_hp=elite_stats["hp"],
                atk=elite_stats["atk"], atk_speed=elite_stats["atk_speed"],
                defense=elite_stats["defense"], magic_def=0,
                acc=elite_stats.get("acc", 0.05), eva=elite_stats.get("eva", 0.0),
                crit_chance=elite_stats.get("crit_chance", 0.0),
                crit_dmg=elite_stats.get("crit_dmg", 1.5),
                level=int(player["level"]),
                size=monster.get("size_type", 2),
            )
        else:
            m_unit = CombatUnit(
                hp=monster["base_hp"] * grade["hp_mult"],
                max_hp=monster["base_hp"] * grade["hp_mult"],
                atk=monster["base_atk"] * grade["atk_mult"],
                atk_speed=monster.get("atk_speed", 1.0),
                defense=monster.get("base_def", 0), magic_def=monster.get("base_mdef", 0),
                acc=0.05, eva=0.0, crit_chance=0.0, crit_dmg=1.5,
                level=int(player["level"]),
                size=monster.get("size_type", 2),
            )

        # 사이즈 보정
        p_size_mult = get_size_correction(p_unit.size, m_unit.size)
        m_size_mult = get_size_correction(m_unit.size, p_unit.size)

        # ── 세트 보너스 플래그 ──
        set_points = player.get("set_points", {})
        set_effects = cls._get_active_set_effects(set_points)
        set_effect_ids = {e["effect_id"] for e in set_effects}

        # 분노 2세트: 화상 부여 (타격 시)
        has_set_burn = "burn" in set_effect_ids
        # 분노 4세트: 잃은 체력 비례 공격력
        has_set_lost_hp_atk = "lost_hp_atk" in set_effect_ids
        # 분노 6세트: 최후의 저항
        has_set_last_stand = "last_stand" in set_effect_ids
        last_stand_used = False
        # 시기 2세트: 중독 부여
        has_set_poison = "poison" in set_effect_ids
        # 시기 6세트: 약자멸시 (적 HP 30% 이하 방무)
        has_set_weak_exec = "weak_execution" in set_effect_ids
        # 탐욕 2세트: 스턴 부여
        has_set_stun = "stun" in set_effect_ids
        # 나태 2세트: 빙결 부여
        has_set_freeze = "freeze" in set_effect_ids
        # 색욕 2세트: 매혹 부여
        has_set_charm = "charm" in set_effect_ids
        # 오만 6세트: 상태이상 면역 + 상태이상 적 추가 피해
        has_set_perfection = "perfection" in set_effect_ids

        # ── 정예 특성 플래그 ──
        has_wrath_rage = "wrath_rage" in traits
        wrath_rage_active = False
        has_lust_seduce = "lust_seduce" in traits
        has_envy_deprive = "envy_deprive" in traits
        has_gluttony_devour = "gluttony_devour" in traits
        has_greed_gamble = "greed_gamble" in traits
        has_regenerating = "regenerating" in traits
        has_thorned = "thorned" in traits
        has_hardening = "hardening" in traits
        hardening_base_def = m_unit.base_defense
        has_first_strike = "first_strike" in traits
        has_retaliatory = "retaliatory" in traits
        has_exploding = "exploding" in traits
        has_vampiric = "vampiric" in traits

        log = []
        turn = 0
        p_timer = 0.0
        m_timer = 0.0
        dt = 0.1
        max_turns = 300
        regen_acc = 0.0
        poison_acc = 0.0

        # 전투 리포트 통계
        report = {"p_total_dmg": 0, "m_total_dmg": 0, "p_hits": 0, "p_misses": 0,
                  "m_hits": 0, "m_misses": 0, "p_crits": 0, "p_staggers": 0, "m_staggers": 0}

        # ── 선제의 ──
        if has_first_strike:
            turn += 1
            dmg = max(1, int(m_unit.atk * random.uniform(0.9, 1.1)))
            def_red = p_unit.defense / (p_unit.defense + 100) if p_unit.defense > 0 else 0
            dmg = max(1, int(dmg * (1 - def_red) * m_size_mult))
            p_unit.hp -= dmg
            p_unit.apply_stagger(dmg)
            report["m_total_dmg"] += dmg
            report["m_hits"] += 1
            log.append({"actor": "monster", "action": "first_strike", "damage": dmg, "crit": False, "turn": turn, "target_hp": max(0, int(p_unit.hp))})

        while p_unit.hp > 0 and m_unit.hp > 0 and turn < max_turns:
            # 경직 중이면 해당 유닛의 타이머 멈춤
            p_staggered = p_unit.tick_stagger(dt)
            m_staggered = m_unit.tick_stagger(dt)

            if not p_staggered:
                p_timer += p_unit.atk_speed * dt
            if not m_staggered:
                m_timer += m_unit.atk_speed * dt

            regen_acc += dt
            poison_acc += dt

            # ── 상태이상 틱 ──
            p_unit.tick_status(dt)
            m_unit.tick_status(dt)

            # ── 중독: 매초 고정 데미지 ──
            if poison_acc >= 1.0:
                poison_acc -= 1.0
                if p_unit.has_status("poison"):
                    p_unit.hp -= POISON_DMG_PER_SEC
                if m_unit.has_status("poison"):
                    m_unit.hp -= POISON_DMG_PER_SEC

            # ── 재생하는: 매초 최대HP 1% 회복 ──
            if has_regenerating and regen_acc >= 1.0:
                regen_acc -= 1.0
                regen = int(m_unit.max_hp * 0.01)
                # 화상: 회복량 감소
                if m_unit.has_status("burn"):
                    regen = int(regen * (1 - BURN_HEAL_REDUCTION))
                m_unit.hp = min(m_unit.max_hp, m_unit.hp + regen)

            # ── 분노(격분) ──
            if has_wrath_rage and not wrath_rage_active and m_unit.hp <= m_unit.max_hp * 0.3:
                wrath_rage_active = True
                m_unit.atk *= 2.0
                m_unit.atk_speed *= 1.5
                log.append({"actor": "monster", "action": "trait_wrath_rage", "damage": 0, "crit": False, "turn": turn, "target_hp": int(m_unit.hp)})

            # ── 플레이어 공격 ──
            if p_timer >= 1.0 and not p_unit.has_status("stun"):
                p_timer -= 1.0
                turn += 1

                eff_crit = 0.0 if has_envy_deprive else p_unit.crit_chance
                eff_crit_dmg = 1.5 if has_envy_deprive else p_unit.crit_dmg
                gamble_mult = random.uniform(0.2, 1.8) if has_greed_gamble else 1.0

                # 분노 4세트: 잃은 체력 비례 공격력 보너스
                lost_hp_mult = 1.0
                if has_set_lost_hp_atk and p_unit.max_hp > 0:
                    lost_ratio = 1.0 - (p_unit.hp / p_unit.max_hp)
                    lost_hp_mult = 1.0 + lost_ratio  # 최대 +100% (HP 0일 때)

                # 시기 6세트: 약자멸시 (적 HP 30% 이하 방무)
                eff_m_def = m_unit.defense
                if has_set_weak_exec and m_unit.hp <= m_unit.max_hp * 0.3:
                    eff_m_def = 0

                entry = cls._attack_v2(
                    "player", p_unit.atk * gamble_mult * lost_hp_mult, p_unit.level, p_unit.acc,
                    eff_m_def, m_unit.eva, m_unit.level,
                    eff_crit, eff_crit_dmg, p_size_mult,
                )

                actual_dmg = entry["damage"]

                # 오만 6세트: 상태이상 적에게 20% 추가 피해
                if has_set_perfection and actual_dmg > 0 and m_unit.has_any_status():
                    actual_dmg = int(actual_dmg * 1.2)
                    entry["damage"] = actual_dmg

                m_unit.hp -= actual_dmg
                entry.update(turn=turn, target_hp=max(0, int(m_unit.hp)))
                log.append(entry)

                if actual_dmg > 0:
                    report["p_total_dmg"] += actual_dmg
                    report["p_hits"] += 1
                    if entry["crit"]:
                        report["p_crits"] += 1
                    # 경직 판정
                    m_unit.apply_stagger(actual_dmg)
                    if m_unit.stagger_timer > 0:
                        report["m_staggers"] += 1

                    # ── 세트 보너스: 타격 시 상태이상 부여 ──
                    if has_set_burn and not m_unit.has_status("burn"):
                        m_unit.apply_status("burn")
                    if has_set_poison and not m_unit.has_status("poison"):
                        m_unit.apply_status("poison")
                    if has_set_stun and random.random() < 0.10 and not m_unit.has_status("stun"):
                        m_unit.apply_status("stun")
                    if has_set_freeze and random.random() < 0.20 and not m_unit.has_status("freeze"):
                        m_unit.apply_status("freeze")
                    if has_set_charm and not m_unit.has_status("charm"):
                        m_unit.apply_status("charm")
                else:
                    report["p_misses"] += 1

                # 가시의
                if has_thorned and actual_dmg > 0:
                    thorn_dmg = max(1, int(actual_dmg * 0.15))
                    p_unit.hp -= thorn_dmg
                    report["m_total_dmg"] += thorn_dmg
                    log.append({"actor": "monster", "action": "trait_thorned", "damage": thorn_dmg, "crit": False, "turn": turn, "target_hp": max(0, int(p_unit.hp))})

                # 경화의
                if has_hardening and actual_dmg > 0:
                    m_unit.defense = hardening_base_def * (1 + m_unit.corrode_stacks * 0.01)
                    hardening_base_def *= 1.01

                # 보복의
                if has_retaliatory and actual_dmg > 0 and m_unit.hp > 0 and random.random() < 0.3:
                    turn += 1
                    r_entry = cls._attack_v2(
                        "monster", m_unit.atk, m_unit.level, m_unit.acc,
                        p_unit.defense, p_unit.eva, p_unit.level,
                        m_unit.crit_chance, m_unit.crit_dmg, m_size_mult,
                    )
                    p_unit.hp -= r_entry["damage"]
                    r_entry["action"] = "trait_retaliatory"
                    r_entry.update(turn=turn, target_hp=max(0, int(p_unit.hp)))
                    log.append(r_entry)
                    if r_entry["damage"] > 0:
                        report["m_total_dmg"] += r_entry["damage"]

            elif p_timer >= 1.0 and p_unit.has_status("stun"):
                p_timer -= 1.0  # 스턴 중 공격 불가, 타이머만 소모

            # ── 몬스터 공격 ──
            if m_timer >= 1.0 and m_unit.hp > 0 and p_unit.hp > 0 and not m_unit.has_status("stun"):
                m_timer -= 1.0
                turn += 1

                eff_p_eva = 0.0 if has_envy_deprive else p_unit.eva

                entry = cls._attack_v2(
                    "monster", m_unit.atk, m_unit.level, m_unit.acc,
                    p_unit.defense, eff_p_eva, p_unit.level,
                    m_unit.crit_chance, m_unit.crit_dmg, m_size_mult,
                )

                actual_dmg = entry["damage"]
                p_unit.hp -= actual_dmg
                entry.update(turn=turn, target_hp=max(0, int(p_unit.hp)))
                log.append(entry)

                if actual_dmg > 0:
                    report["m_total_dmg"] += actual_dmg
                    report["m_hits"] += 1
                    p_unit.apply_stagger(actual_dmg)
                    if p_unit.stagger_timer > 0:
                        report["p_staggers"] += 1
                    # 침식: 피격마다 플레이어 방어력 영구 감소
                    if p_unit.has_status("corrode"):
                        pass  # corrode는 apply_status 시점에 이미 처리됨
                else:
                    report["m_misses"] += 1

                # 색욕(유혹)
                if has_lust_seduce and actual_dmg > 0:
                    steal = p_unit.atk * 0.10
                    p_unit.atk = max(1, p_unit.atk - steal)
                    m_unit.atk += steal

                # 폭식(탐식)
                if has_gluttony_devour and actual_dmg > 0:
                    m_unit.atk *= 1.02

                # 흡혈의
                if has_vampiric and actual_dmg > 0:
                    vamp_heal = int(actual_dmg * 0.20)
                    if m_unit.has_status("burn"):
                        vamp_heal = int(vamp_heal * (1 - BURN_HEAL_REDUCTION))
                    m_unit.hp = min(m_unit.max_hp, m_unit.hp + vamp_heal)

            elif m_timer >= 1.0 and m_unit.has_status("stun"):
                m_timer -= 1.0

        # ── 분노 6세트: 최후의 저항 (사망 시 1회 생존 + 체력 40% 회복) ──
        if has_set_last_stand and not last_stand_used and p_unit.hp <= 0:
            last_stand_used = True
            p_unit.hp = int(p_unit.max_hp * 0.4)
            log.append({"actor": "player", "action": "set_last_stand", "damage": 0, "crit": False, "turn": turn, "target_hp": int(p_unit.hp)})

        # ── 폭발하는 ──
        if has_exploding and m_unit.hp <= 0:
            explode_dmg = max(1, int(m_unit.max_hp * 0.50))
            p_unit.hp -= explode_dmg
            report["m_total_dmg"] += explode_dmg
            log.append({"actor": "monster", "action": "trait_exploding", "damage": explode_dmg, "crit": False, "turn": turn, "target_hp": max(0, int(p_unit.hp))})

        if m_unit.hp <= 0 and p_unit.hp > 0:
            result = "win"
        elif p_unit.hp <= 0:
            result = "lose"
        else:
            result = "timeout"

        # 전투 리포트를 로그 마지막에 추가
        log.append({"action": "battle_report", "report": report})

        return log, result, max(0, int(p_unit.hp))

    @staticmethod
    def _attack_v2(
        actor: str, atk: float, atk_lv: int, acc: float,
        target_def: float, target_eva: float, def_lv: int,
        crit_ch: float, crit_dmg: float, size_mult: float = 1.0,
    ) -> dict:
        """단일 공격 판정 v2 — 사이즈 보정 포함"""
        lv_diff = atk_lv - def_lv
        hit_chance = max(0.05, min(0.95,
            acc / (acc + target_eva + 0.001) + lv_diff * 0.01 + 0.1
        ))

        if random.random() >= hit_chance:
            return {"actor": actor, "action": "miss", "damage": 0, "crit": False}

        def_reduction = target_def / (target_def + 100) if target_def > 0 else 0
        dmg = atk * (1 - def_reduction) * size_mult * random.uniform(0.9, 1.1)

        is_crit = random.random() < crit_ch
        if is_crit:
            dmg *= crit_dmg

        dmg = max(1, int(dmg))
        return {"actor": actor, "action": "attack", "damage": dmg, "crit": is_crit}


    # ── 웨이브 보상 지급 ──

    @classmethod
    def _grant_wave_rewards(cls, db, user_no: int, wave_kills: dict, wave_key: str) -> dict:
        """
        웨이브 클리어 시 보상 지급 (경험치 + 골드)
        해당 웨이브에서 처치한 몬스터 전체에 대해 합산 지급
        """
        user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
        stat = db.query(UserStat).filter(UserStat.user_no == user_no).with_for_update().first()
        if not user or not stat:
            return {}

        monsters_config = GameDataManager.REQUIRE_CONFIGS.get("monsters", {})
        kills = wave_kills.get(wave_key, [])

        total_exp = 0
        total_gold = 0

        for kill in kills:
            m_idx = kill.get("monster_idx")
            s_type = kill.get("spawn_type", "일반")
            grade = cls._get_spawn_grade(s_type)
            m_data = monsters_config.get(int(m_idx), {})

            if not grade or not m_data:
                continue

            base_exp = m_data.get("exp_reward", 10)
            total_exp += int(base_exp * grade.get("exp_mult", 1.0))

            base_gold = random.randint(5, 20) * max(1, stat.level // 5)
            total_gold += int(base_gold * grade.get("gold_mult", 1.0))

        stat.exp += total_exp
        leveled_up = False
        old_level = stat.level
        exp_table = cls._get_exp_table()

        while stat.level < cls.MAX_LEVEL:
            lv_info = exp_table.get(stat.level)
            if not lv_info:
                break
            required = lv_info["required_exp"]
            if stat.exp >= required:
                stat.exp -= required
                stat.level += 1
                stat.stat_points += lv_info.get("stat_points", cls.STAT_POINTS_PER_LEVEL)
                leveled_up = True
                logger.info(f"[BattleManager] 레벨업! user_no={user_no} Lv{stat.level - 1}→{stat.level}")
            else:
                break

        user.gold += total_gold

        next_lv_info = exp_table.get(stat.level, {})
        next_required = next_lv_info.get("required_exp", 0) if stat.level < cls.MAX_LEVEL else 0

        logger.info(f"[BattleManager] 웨이브 보상 (user_no={user_no}, wave={wave_key}, exp={total_exp}, gold={total_gold})")

        return {
            "exp_gained": total_exp,
            "gold_gained": total_gold,
            "level": stat.level,
            "exp": stat.exp,
            "next_required_exp": next_required,
            "leveled_up": leveled_up,
            "levels_gained": stat.level - old_level,
            "gold": user.gold,
        }

    # ── 사망 패널티 ──

    @classmethod
    def _apply_death_penalty(cls, db, user_no: int):
        """사망 시 현재 레벨 내 경험치 10% 차감 (0% 하한, 레벨다운 없음)"""
        stat = db.query(UserStat).filter(UserStat.user_no == user_no).with_for_update().first()
        if not stat:
            return

        penalty = int(stat.exp * DEATH_EXP_PENALTY_RATE)
        stat.exp = max(0, stat.exp - penalty)
        logger.info(f"[BattleManager] 사망 패널티 (user_no={user_no}, exp_lost={penalty}, remaining_exp={stat.exp})")

    # ── 세트포인트 계산 ──

    @classmethod
    def _calc_set_points(cls, equipped_items, user_no: int, db=None) -> dict:
        """
        장착 장비의 prefix_id/suffix_id에서 세트포인트 합산.
        한 장비에서 같은 죄종은 1로 카운트.
        + basic_sin → +1
        """
        set_points = {}

        for item in equipped_items:
            item_sins = set()
            if item.prefix_id:
                item_sins.add(item.prefix_id.lower())
            if item.suffix_id:
                item_sins.add(item.suffix_id.lower())
            for sin in item_sins:
                set_points[sin] = set_points.get(sin, 0) + 1

        # basic_sin 추가
        if db:
            user = db.query(User).filter(User.user_no == user_no).first()
            if user and user.basic_sin:
                sin = user.basic_sin.lower()
                set_points[sin] = set_points.get(sin, 0) + 1

        return set_points

    # ── 세트 보너스 활성 효과 조회 ──

    @classmethod
    def _get_active_set_effects(cls, set_points: dict) -> list:
        """세트포인트에서 활성화된 세트 효과 목록 반환"""
        set_bonus_config = GameDataManager.REQUIRE_CONFIGS.get("set_bonus", {})
        active = []

        for sin, points in set_points.items():
            sin_bonuses = set_bonus_config.get(sin, {})
            for bp in sorted(sin_bonuses.keys()):
                if points >= bp:
                    effect = sin_bonuses[bp]
                    if effect.get("status") == "confirmed":
                        active.append({
                            "sin": sin,
                            "breakpoint": bp,
                            **effect,
                        })
        return active
