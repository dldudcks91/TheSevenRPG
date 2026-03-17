import random
import logging
from typing import Optional
from database import SessionLocal
from models import User, UserStat, Item
from services.system.GameDataManager import GameDataManager
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")


class BattleManager:
    """전투 시뮬레이션 엔진 (API 3001)"""

    MAX_LEVEL = 50
    STAT_POINTS_PER_LEVEL = 5       # 레벨업 시 스탯 포인트 지급
    BASE_EXP = 10                    # 기준 XP (Lv1→2)
    EXP_STORY_MULT = 1.3            # 스토리 구간 (Lv1~40) 레벨당 배율
    EXP_GRIND_MULT = 2.0            # 그라인드 구간 (Lv40~50) 레벨당 배율
    GRIND_START_LEVEL = 40           # 그라인드 구간 시작 레벨

    # ── CSV 폴백용 스폰 등급 배율 ──
    _FALLBACK_SPAWN_GRADES = {
        "normal":       {"hp_mult": 1.0,  "atk_mult": 1.0, "exp_mult": 1.0,  "gold_mult": 1.0},
        "elite":        {"hp_mult": 3.0,  "atk_mult": 1.5, "exp_mult": 3.0,  "gold_mult": 2.0},
        "stage_boss":   {"hp_mult": 10.0, "atk_mult": 2.5, "exp_mult": 10.0, "gold_mult": 5.0},
        "chapter_boss": {"hp_mult": 20.0, "atk_mult": 5.0, "exp_mult": 20.0, "gold_mult": 10.0},
    }

    # ── 한글→영문 등급 매핑 (클라이언트 호환) ──
    _GRADE_KR_TO_EN = {
        "일반": "normal",
        "정예": "elite",
        "보스": "stage_boss",
        "챕터보스": "chapter_boss",
    }

    # ── 레벨 테이블 캐시 (서버 기동 시 1회 생성) ──
    _exp_table_cache = None

    @classmethod
    def _get_exp_table(cls) -> dict:
        """레벨별 필요 XP 테이블. CSV 우선, 없으면 공식으로 생성."""
        if cls._exp_table_cache is not None:
            return cls._exp_table_cache

        # CSV 우선
        csv_table = GameDataManager.REQUIRE_CONFIGS.get("level_config")
        if csv_table:
            cls._exp_table_cache = csv_table
            logger.info(f"[BattleManager] level_config CSV 로드 완료 ({len(csv_table)}레벨)")
            return cls._exp_table_cache

        # 폴백: 확정 공식으로 생성
        # 기획서: 기준10, 스토리 ×1.3^(lv-1), 그라인드 = 마지막 스토리 값 × 2^n
        table = {}
        last_story_exp = cls.BASE_EXP * (cls.EXP_STORY_MULT ** (cls.GRIND_START_LEVEL - 2))
        for lv in range(1, cls.MAX_LEVEL):
            if lv < cls.GRIND_START_LEVEL:
                required = cls.BASE_EXP * (cls.EXP_STORY_MULT ** (lv - 1))
            else:
                # Lv40~: 마지막 스토리 레벨(Lv39→40) 값을 기준으로 ×2.0씩 증가
                required = last_story_exp * (cls.EXP_GRIND_MULT ** (lv - cls.GRIND_START_LEVEL + 1))
            table[lv] = {"required_exp": int(required), "stat_points": cls.STAT_POINTS_PER_LEVEL}

        cls._exp_table_cache = table
        logger.info(f"[BattleManager] level_config 폴백 테이블 생성 (Lv1={table[1]['required_exp']}, Lv39={table[39]['required_exp']}, Lv40={table[40]['required_exp']})")
        return cls._exp_table_cache

    @classmethod
    def _get_spawn_grade(cls, spawn_type: str) -> Optional[dict]:
        """스폰 등급 배율. CSV 우선, 없으면 폴백."""
        # 한글→영문 변환
        grade_en = cls._GRADE_KR_TO_EN.get(spawn_type, spawn_type)

        # CSV 우선
        csv_grades = GameDataManager.REQUIRE_CONFIGS.get("spawn_grade_config")
        if csv_grades and grade_en in csv_grades:
            return csv_grades[grade_en]

        # 폴백
        return cls._FALLBACK_SPAWN_GRADES.get(grade_en)

    # ── API 엔트리 ─────────────────────────────────────────

    @classmethod
    async def battle_result(cls, user_no: int, data: dict):
        """API 3001: 전투 시뮬레이션 — 서버가 전 과정을 시뮬레이션하고 결과만 반환"""
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

        # 유저 전투 스탯 로드 (Redis 캐시 → DB fallback)
        player = await cls._load_battle_stats(user_no)
        if not player:
            return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯을 찾을 수 없습니다.")

        # ── [4] 전투 시뮬레이션 (순수 계산) ──
        battle_log, result = cls._simulate(player, monster, grade)

        # ── 승리 시 보상 지급 (단일 트랜잭션) ──
        rewards = {}
        if result == "win":
            db = SessionLocal()
            try:
                rewards = cls._grant_rewards(db, user_no, monster, grade, int(player["level"]))

                # ── [5] 커밋 + 캐시 무효화 ──
                db.commit()

                if rewards.get("leveled_up"):
                    try:
                        await RedisManager.delete(f"user:{user_no}:battle_stats")
                    except RedisUnavailable:
                        logger.warning(f"[BattleManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

            except Exception as e:
                db.rollback()
                logger.error(f"[BattleManager] battle_result 보상 지급 실패: {e}", exc_info=True)
                return error_response(ErrorCode.DB_ERROR, "전투 보상 지급 중 오류가 발생했습니다.")
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
            },
        }

    # ── 전투 스탯 로드 ─────────────────────────────────────

    @classmethod
    async def _load_battle_stats(cls, user_no: int) -> Optional[dict]:
        """Redis 캐시 → DB 재계산 → Redis 저장"""
        cache_key = f"user:{user_no}:battle_stats"

        # 캐시 히트
        try:
            cached = await RedisManager.hgetall(cache_key)
            if cached:
                return {k: float(v) for k, v in cached.items()}
        except RedisUnavailable:
            logger.warning(f"[BattleManager] battle_stats 캐시 조회 실패 - Redis 장애 (user_no={user_no})")

        # DB 계산
        db = SessionLocal()
        try:
            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            if not stat:
                return None

            equipped = db.query(Item).filter(
                Item.user_no == user_no,
                Item.equip_slot.isnot(None),
            ).all()

            # 장비 보너스 합산
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

            # 기획서 공식 적용
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
            }

            # Redis 캐싱 (1시간)
            try:
                await RedisManager.hmset(cache_key, {k: str(v) for k, v in battle.items()})
                await RedisManager.expire(cache_key, 3600)
            except RedisUnavailable:
                logger.warning(f"[BattleManager] battle_stats 캐시 저장 실패 - Redis 장애 (user_no={user_no})")

            return battle
        finally:
            db.close()

    # ── 전투 시뮬레이션 ────────────────────────────────────

    @classmethod
    def _simulate(cls, player: dict, monster: dict, grade: dict) -> tuple[list, str]:
        """턴 기반 시뮬레이션 — 공격속도 타이머 방식"""
        p_hp     = player["max_hp"]
        p_atk    = player["attack"]
        p_aspd   = player["atk_speed"]
        p_def    = player["defense"]
        p_level  = int(player["level"])

        m_hp     = monster["base_hp"] * grade["hp_mult"]
        m_atk    = monster["base_atk"] * grade["atk_mult"]
        m_aspd   = monster.get("atk_speed", 1.0)
        m_def    = monster.get("base_def", 0)
        m_level  = p_level  # 몬스터 레벨 = 플레이어 레벨 (미확정)

        log = []
        turn = 0
        p_timer = 0.0
        m_timer = 0.0
        dt = 0.1
        max_turns = 200

        while p_hp > 0 and m_hp > 0 and turn < max_turns:
            p_timer += p_aspd * dt
            m_timer += m_aspd * dt

            # 플레이어 공격
            if p_timer >= 1.0:
                p_timer -= 1.0
                turn += 1
                entry = cls._attack(
                    "player", p_atk, p_level, player["acc"],
                    m_def, 0.0, m_level,
                    player["crit_chance"], player["crit_dmg"],
                )
                m_hp -= entry["damage"]
                entry.update(turn=turn, target_hp=max(0, int(m_hp)))
                log.append(entry)

            # 몬스터 공격
            if m_timer >= 1.0 and m_hp > 0:
                m_timer -= 1.0
                turn += 1
                m_acc = 0.05
                entry = cls._attack(
                    "monster", m_atk, m_level, m_acc,
                    p_def, player["eva"], p_level,
                    0.0, 1.5,
                )
                p_hp -= entry["damage"]
                entry.update(turn=turn, target_hp=max(0, int(p_hp)))
                log.append(entry)

        if m_hp <= 0:
            result = "win"
        elif p_hp <= 0:
            result = "lose"
        else:
            result = "timeout"

        return log, result

    @staticmethod
    def _attack(
        actor: str, atk: float, atk_lv: int, acc: float,
        target_def: float, target_eva: float, def_lv: int,
        crit_ch: float, crit_dmg: float,
    ) -> dict:
        """단일 공격 판정 — 명중/데미지/크리티컬"""
        lv_diff = atk_lv - def_lv
        hit_chance = max(0.05, min(0.95,
            acc / (acc + target_eva + 0.001) + lv_diff * 0.01 + 0.1
        ))

        if random.random() >= hit_chance:
            return {"actor": actor, "action": "miss", "damage": 0, "crit": False}

        def_reduction = target_def / (target_def + 100) if target_def > 0 else 0
        dmg = atk * (1 - def_reduction) * random.uniform(0.9, 1.1)

        is_crit = random.random() < crit_ch
        if is_crit:
            dmg *= crit_dmg

        dmg = max(1, int(dmg))
        return {"actor": actor, "action": "attack", "damage": dmg, "crit": is_crit}

    # ── 보상 지급 ──────────────────────────────────────────

    @classmethod
    def _grant_rewards(cls, db, user_no: int, monster: dict, grade: dict, player_level: int) -> dict:
        """승리 시 경험치/골드 지급 + 레벨업 처리 (DB 세션을 전달받아 사용, commit하지 않음)"""
        user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
        stat = db.query(UserStat).filter(UserStat.user_no == user_no).with_for_update().first()

        if not user or not stat:
            return {}

        # 경험치: 몬스터 기본 XP × 등급 배율
        base_exp = monster.get("exp_reward", 10)
        exp_gained = int(base_exp * grade.get("exp_mult", 1.0))

        # 골드: 몬스터 기본 XP 기반 임시 공식 × 등급 배율 (골드 드롭 공식 미확정)
        base_gold = random.randint(5, 20) * max(1, player_level // 5)
        gold_gained = int(base_gold * grade.get("gold_mult", 1.0))

        stat.exp += exp_gained
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

        user.gold += gold_gained

        # 다음 레벨 필요 XP 정보 포함
        next_lv_info = exp_table.get(stat.level, {})
        next_required = next_lv_info.get("required_exp", 0) if stat.level < cls.MAX_LEVEL else 0

        return {
            "exp_gained": exp_gained,
            "gold_gained": gold_gained,
            "level": stat.level,
            "exp": stat.exp,
            "next_required_exp": next_required,
            "leveled_up": leveled_up,
            "levels_gained": stat.level - old_level,
            "gold": user.gold,
        }
