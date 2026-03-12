import random
import logging
from database import SessionLocal
from models import User, UserStat, Item
from services.system.GameDataManager import GameDataManager
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")


class BattleManager:
    """전투 시뮬레이션 엔진 (API 3001)"""

    MAX_LEVEL = 50
    # 임시 경험치 테이블 — 미확정 기획, level^2 * 100
    EXP_TABLE = {lv: lv * lv * 100 for lv in range(1, 51)}

    SPAWN_MULTIPLIERS = {
        "일반": {"hp": 1.0, "atk": 1.0},
        "정예": {"hp": 3.0, "atk": 1.5},
        "보스": {"hp": 10.0, "atk": 2.5},
    }

    # ── API 엔트리 ─────────────────────────────────────────

    @classmethod
    async def battle_result(cls, user_no: int, data: dict):
        """API 3001: 전투 시뮬레이션 — 서버가 전 과정을 시뮬레이션하고 결과만 반환"""
        monster_idx = data.get("monster_idx")
        spawn_type = data.get("spawn_type", "일반")

        if monster_idx is None:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, "monster_idx가 필요합니다.")

        # 1. 몬스터 정보 로드
        monsters = GameDataManager.REQUIRE_CONFIGS.get("monsters", {})
        monster = monsters.get(int(monster_idx))
        if not monster:
            return error_response(ErrorCode.INVALID_BATTLE_REQ, f"몬스터를 찾을 수 없습니다: {monster_idx}")

        # 2. 유저 전투 스탯 로드 (Redis 캐시 → DB fallback)
        player = await cls._load_battle_stats(user_no)
        if not player:
            return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯을 찾을 수 없습니다.")

        # 3. 전투 시뮬레이션
        battle_log, result = cls._simulate(player, monster, spawn_type)

        # 4. 승리 시 보상 지급
        rewards = {}
        if result == "win":
            rewards = await cls._grant_rewards(user_no, monster, int(player["level"]))

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
    async def _load_battle_stats(cls, user_no: int) -> dict | None:
        """Redis 캐시 → DB 재계산 → Redis 저장"""
        cache_key = f"user:{user_no}:battle_stats"

        # 캐시 히트
        try:
            cached = await RedisManager.hgetall(cache_key)
            if cached:
                return {k: float(v) for k, v in cached.items()}
        except RedisUnavailable:
            pass

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
                pass

            return battle
        finally:
            db.close()

    # ── 전투 시뮬레이션 ────────────────────────────────────

    @classmethod
    def _simulate(cls, player: dict, monster: dict, spawn_type: str) -> tuple[list, str]:
        """턴 기반 시뮬레이션 — 공격속도 타이머 방식"""
        mult = cls.SPAWN_MULTIPLIERS.get(spawn_type, cls.SPAWN_MULTIPLIERS["일반"])

        p_hp     = player["max_hp"]
        p_atk    = player["attack"]
        p_aspd   = player["atk_speed"]
        p_def    = player["defense"]
        p_level  = int(player["level"])

        m_hp     = monster["base_hp"] * mult["hp"]
        m_atk    = monster["base_atk"] * mult["atk"]
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
    async def _grant_rewards(cls, user_no: int, monster: dict, player_level: int) -> dict:
        """승리 시 경험치/골드 지급 + 레벨업 처리"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()

            # 경험치 (임시 — 미확정 기획)
            exp_gained = monster.get("exp_reward", 10)

            # 골드 (임시 — 미확정 기획)
            gold_gained = random.randint(5, 20) * max(1, player_level // 5)

            stat.exp += exp_gained
            leveled_up = False
            while stat.level < cls.MAX_LEVEL:
                required = cls.EXP_TABLE.get(stat.level, float("inf"))
                if stat.exp >= required:
                    stat.exp -= required
                    stat.level += 1
                    stat.stat_points += 5
                    leveled_up = True
                else:
                    break

            user.gold += gold_gained
            db.commit()

            if leveled_up:
                try:
                    await RedisManager.delete(f"user:{user_no}:battle_stats")
                except RedisUnavailable:
                    pass

            return {
                "exp_gained": exp_gained,
                "gold_gained": gold_gained,
                "level": stat.level,
                "exp": stat.exp,
                "leveled_up": leveled_up,
                "gold": user.gold,
            }

        except Exception as e:
            db.rollback()
            logger.error(f"[Battle] 보상 지급 실패: {e}", exc_info=True)
            return {}
        finally:
            db.close()
