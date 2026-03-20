import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm.attributes import flag_modified
from database import SessionLocal
from models import User, UserStat, BattleSession, Item, Card, Material, Collection
from services.system.GameDataManager import GameDataManager
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

STAGES_PER_CHAPTER = 4  # stage_num 1~3 일반 + 4 챕터보스
TOTAL_CHAPTERS = 7
FIRST_STAGE = 101  # 최초 스테이지
LAST_STAGE = 704   # 최종 스테이지
WAVES_PER_STAGE = 4  # 웨이브 1~3 일반 + 웨이브4 보스
DEATH_EXP_PENALTY_RATE = 0.10  # 사망 시 현재 레벨 내 경험치 10% 차감

# 챕터 클리어 시 시설 해금 매핑 (chapter_id → facility bit)
CHAPTER_FACILITY_UNLOCK = {
    1: 0,  # 대장간 (비트 0)
    2: 1,  # 퀘스트 게시판 (비트 1)
    3: 2,  # 상인 (비트 2)
    4: 3,  # 흔적 조합소 (비트 3)
}


class StageManager:
    """스테이지 진행 관리 (API 3003, 3004, 3007, 3008)"""

    # ── API 3003: 스테이지 입장 ──

    @classmethod
    async def enter_stage(cls, user_no: int, data: dict):
        """
        API 3003: 스테이지 입장
        - BattleSession 생성, 웨이브1 몬스터 반환
        - 이미 진행 중인 세션이 있으면 차단
        """
        # ── [1] 입력 추출 ──
        stage_id = data.get("stage_id")
        if stage_id is None:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        # ── [2] 메타데이터 검증 ──
        stages = GameDataManager.REQUIRE_CONFIGS.get("stages", {})
        if stage_id not in stages:
            return error_response(ErrorCode.STAGE_NOT_FOUND, f"존재하지 않는 스테이지: {stage_id}")

        monster_pool = cls._generate_monster_pool(stage_id)
        if not monster_pool:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "몬스터 풀을 생성할 수 없습니다.")

        # ── [3] DB 세션 + 상태 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            # 해금 검증
            if stage_id > user.current_stage:
                return error_response(ErrorCode.STAGE_NOT_UNLOCKED, "아직 해금되지 않은 스테이지입니다.")

            # 기존 세션이 있으면 삭제 (재입장 허용)
            existing = db.query(BattleSession).filter(
                BattleSession.user_no == user_no
            ).with_for_update().first()
            if existing:
                logger.info(f"[StageManager] 기존 세션 삭제 (user_no={user_no}, old_stage={existing.stage_id})")
                db.delete(existing)

            # 유저 전투 스탯에서 max_hp 계산
            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            if not stat:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯을 찾을 수 없습니다.")

            max_hp = cls._calc_max_hp(stat, user_no)

            # ── [4] 비즈니스 로직: BattleSession 생성 ──
            session = BattleSession(
                user_no=user_no,
                stage_id=stage_id,
                current_wave=1,
                current_hp=max_hp,
                max_hp=max_hp,
                pending_drops=[],
                wave_kills={},
                started_at=datetime.now(),
            )
            db.add(session)

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[StageManager] enter_stage (user_no={user_no}, stage_id={stage_id}, max_hp={max_hp})")

        except Exception as e:
            db.rollback()
            logger.error(f"[StageManager] enter_stage 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스테이지 입장 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"스테이지 {stage_id} 입장",
            "data": {
                "stage_id": stage_id,
                "current_wave": 1,
                "current_hp": max_hp,
                "max_hp": max_hp,
                "monsters": monster_pool,
            },
        }

    # ── API 3004: 스테이지 클리어 ──

    @classmethod
    async def clear_stage(cls, user_no: int, data: dict):
        """
        API 3004: 스테이지 클리어
        - 웨이브4(보스) 클리어 후 호출
        - 다음 스테이지 해금 + BattleSession 삭제
        """
        # ── [1] 입력 추출 ──
        stage_id = data.get("stage_id")
        if stage_id is None:
            return error_response(ErrorCode.STAGE_NOT_FOUND, "stage_id가 필요합니다.")

        # ── [3] DB 세션 + 상태 검증 ──
        db = SessionLocal()
        try:
            # BattleSession 검증
            session = db.query(BattleSession).filter(
                BattleSession.user_no == user_no
            ).with_for_update().first()
            if not session:
                return error_response(ErrorCode.BATTLE_SESSION_NOT_FOUND, "진행 중인 전투 세션이 없습니다.")
            if session.stage_id != stage_id:
                return error_response(ErrorCode.INVALID_BATTLE_REQ, "현재 진행 중인 스테이지와 일치하지 않습니다.")

            # 웨이브4 클리어 검증: current_wave가 4를 초과했거나, 보스 처치 완료 상태
            wave_kills = session.wave_kills or {}
            wave4_kills = wave_kills.get("4", [])
            if session.current_wave < WAVES_PER_STAGE or (session.current_wave == WAVES_PER_STAGE and len(wave4_kills) == 0):
                return error_response(ErrorCode.WAVE_NOT_CLEARED, "보스 웨이브를 클리어해야 합니다.")

            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            # ── [4] 비즈니스 로직: pending_drops → DB 저장 + 해금 + 세션 삭제 ──
            saved_drops = cls._save_pending_drops(db, user_no, user, session.pending_drops or [])

            unlocked = False
            facility_unlocked = None
            if stage_id == user.current_stage and stage_id < LAST_STAGE:
                next_stage = cls._next_stage_id(stage_id)
                if next_stage:
                    user.current_stage = next_stage
                    unlocked = True

            # 챕터 보스(stage_num=4) 클리어 시 시설 해금
            stage_num = stage_id % 100
            chapter = stage_id // 100
            if stage_num == STAGES_PER_CHAPTER and chapter in CHAPTER_FACILITY_UNLOCK:
                facility_bit = CHAPTER_FACILITY_UNLOCK[chapter]
                if not ((user.unlocked_facilities or 0) & (1 << facility_bit)):
                    user.unlocked_facilities = (user.unlocked_facilities or 0) | (1 << facility_bit)
                    facility_unlocked = facility_bit
                    logger.info(f"[StageManager] 시설 해금 (user_no={user_no}, chapter={chapter}, bit={facility_bit})")

            current_stage = user.current_stage
            db.delete(session)

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()
            logger.info(f"[StageManager] clear_stage (user_no={user_no}, stage_id={stage_id}, unlocked={unlocked})")

        except Exception as e:
            db.rollback()
            logger.error(f"[StageManager] clear_stage 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스테이지 클리어 처리 중 오류가 발생했습니다.")
        finally:
            db.close()

        # Redis 스테이지 진행 상태 삭제 (구버전 호환)
        try:
            await RedisManager.delete(f"user:{user_no}:stage_progress")
        except RedisUnavailable:
            pass

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"스테이지 {stage_id} 클리어!",
            "data": {
                "stage_id": stage_id,
                "unlocked_next": unlocked,
                "current_stage": current_stage,
                "saved_drops": saved_drops,
                "facility_unlocked": facility_unlocked,
            },
        }

    # ── API 3007: 귀환 ──

    @classmethod
    async def return_to_town(cls, user_no: int, data: dict):
        """
        API 3007: 마을 귀환
        - HP 보존, BattleSession 유지 (재입장 시 현재 웨이브 처음부터)
        - 웨이브 내부 진행은 리셋 (wave_kills에서 현재 웨이브 킬 제거)
        """
        # ── [3] DB 세션 + 상태 검증 ──
        db = SessionLocal()
        try:
            session = db.query(BattleSession).filter(
                BattleSession.user_no == user_no
            ).with_for_update().first()
            if not session:
                return error_response(ErrorCode.BATTLE_SESSION_NOT_FOUND, "진행 중인 전투 세션이 없습니다.")

            # ── [4] 비즈니스 로직: 현재 웨이브 킬 리셋 (웨이브 내부 진행 리셋) ──
            wave_kills = session.wave_kills or {}
            current_wave_key = str(session.current_wave)
            if current_wave_key in wave_kills:
                wave_kills.pop(current_wave_key)
                session.wave_kills = wave_kills
                flag_modified(session, "wave_kills")

            stage_id = session.stage_id
            current_wave = session.current_wave
            current_hp = session.current_hp

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[StageManager] return_to_town (user_no={user_no}, stage_id={stage_id}, wave={current_wave}, hp={current_hp})")

        except Exception as e:
            db.rollback()
            logger.error(f"[StageManager] return_to_town 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "귀환 처리 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "마을로 귀환했습니다.",
            "data": {
                "stage_id": stage_id,
                "current_wave": current_wave,
                "current_hp": current_hp,
            },
        }

    # ── API 3008: 전투 세션 조회 ──

    @classmethod
    async def get_battle_session(cls, user_no: int, data: dict):
        """
        API 3008: 전투 세션 조회
        - 재접속 시 진행 상태 복구용
        - 세션이 없으면 null 반환 (에러 아님)
        """
        # ── [3] DB 세션 ──
        db = SessionLocal()
        try:
            session = db.query(BattleSession).filter(
                BattleSession.user_no == user_no
            ).first()

            if not session:
                return {
                    "success": True,
                    "message": "진행 중인 전투가 없습니다.",
                    "data": {"session": None},
                }

            # 몬스터 풀 재생성
            monster_pool = cls._generate_monster_pool(session.stage_id)

            # ── [6] 응답 반환 ──
            return {
                "success": True,
                "message": "전투 세션 조회",
                "data": {
                    "session": {
                        "stage_id": session.stage_id,
                        "current_wave": session.current_wave,
                        "current_hp": session.current_hp,
                        "max_hp": session.max_hp,
                        "pending_drops": session.pending_drops or [],
                        "wave_kills": session.wave_kills or {},
                    },
                    "monsters": monster_pool,
                },
            }

        except Exception as e:
            logger.error(f"[StageManager] get_battle_session 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "전투 세션 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

    # ── 헬퍼: 다음 스테이지 ID 계산 ──

    @classmethod
    def _next_stage_id(cls, stage_id: int) -> Optional[int]:
        """101→102→103→104→201→202→...→704(마지막)"""
        chapter = stage_id // 100
        stage_num = stage_id % 100

        if stage_num < STAGES_PER_CHAPTER:
            return stage_id + 1
        elif chapter < TOTAL_CHAPTERS:
            return (chapter + 1) * 100 + 1
        return None

    # ── 헬퍼: 몬스터 풀 생성 ──

    @classmethod
    def _generate_monster_pool(cls, stage_id: int) -> list:
        """
        스테이지 몬스터 풀 생성
        웨이브 구조: [일반3+정예1] × 3웨이브 + 보스1(웨이브4) = 13마리
        스폰 순서: 종별 집중 (AAA→BBB→CCC)
        """
        stages = GameDataManager.REQUIRE_CONFIGS.get("stages", {})
        stage_info = stages.get(stage_id)

        if not stage_info:
            return []

        waves = stage_info.get("waves", {})
        if not waves:
            return []

        pool = []

        # 웨이브 1~3: 일반 몬스터 (일반3 + 정예1)
        for wave_num in range(1, 4):
            monster_idx = waves.get(wave_num)
            if not monster_idx:
                continue
            wave_data = []
            for _ in range(3):
                wave_data.append({"monster_idx": monster_idx, "spawn_type": "일반"})
            wave_data.append({"monster_idx": monster_idx, "spawn_type": "정예"})
            pool.append({"wave": wave_num, "monsters": wave_data})

        # 웨이브 4: 보스
        boss_idx = waves.get(4)
        if boss_idx:
            stage_num = stage_id % 100
            boss_type = "챕터보스" if stage_num == 4 else "보스"
            pool.append({"wave": 4, "monsters": [{"monster_idx": boss_idx, "spawn_type": boss_type}]})

        return pool

    # ── 헬퍼: pending_drops → DB 저장 ──

    @classmethod
    def _save_pending_drops(cls, db, user_no: int, user: User, pending_drops: list) -> dict:
        """
        pending_drops를 DB에 일괄 저장.
        - gold → Users.gold 합산
        - equipment → Items INSERT
        - card → Cards INSERT + Collections 도감 등록
        - material/stigma → Materials UPSERT
        """
        summary = {"gold": 0, "equipment": 0, "card": 0, "material": 0, "stigma": 0}

        items_to_add = []
        cards_to_add = []
        total_gold = 0

        # 인벤토리 현재 수 확인
        current_item_count = db.query(Item).filter(Item.user_no == user_no).count()
        max_inv = user.max_inventory

        for drop in pending_drops:
            drop_type = drop.get("type")

            if drop_type == "gold":
                total_gold += drop.get("amount", 0)
                summary["gold"] += drop.get("amount", 0)

            elif drop_type == "equipment":
                # 인벤 가득 차면 장비 무시
                if current_item_count + len(items_to_add) >= max_inv:
                    continue
                equip_data = drop.get("data", {})
                if not equip_data:
                    continue
                item = Item(
                    item_uid=equip_data.get("item_uid"),
                    user_no=user_no,
                    base_item_id=equip_data.get("base_item_id", 0),
                    item_level=equip_data.get("item_level", 1),
                    rarity=equip_data.get("rarity", "magic"),
                    item_score=equip_data.get("item_score", 0),
                    item_cost=equip_data.get("item_cost", 0),
                    prefix_id=equip_data.get("prefix_id"),
                    suffix_id=equip_data.get("suffix_id"),
                    set_id=equip_data.get("set_id"),
                    dynamic_options=equip_data.get("dynamic_options", {}),
                    is_equipped=False,
                    equip_slot=None,
                )
                items_to_add.append(item)
                summary["equipment"] += 1

            elif drop_type == "card":
                monster_idx = drop.get("monster_idx")
                if not monster_idx:
                    continue
                import uuid
                from services.rpg.CardManager import CardManager
                card = Card(
                    card_uid=str(uuid.uuid4()),
                    user_no=user_no,
                    monster_idx=int(monster_idx),
                    card_level=1,
                    card_stats=CardManager.generate_card_stats(int(monster_idx)),
                    is_equipped=False,
                    skill_slot=None,
                )
                cards_to_add.append(card)
                summary["card"] += 1

                # 도감 등록 (첫 획득 시 자동 등록)
                existing_col = db.query(Collection).filter(
                    Collection.user_no == user_no,
                    Collection.monster_idx == int(monster_idx),
                ).first()
                if not existing_col:
                    col = Collection(
                        user_no=user_no,
                        monster_idx=int(monster_idx),
                        card_count=1,
                        collection_level=1,
                    )
                    db.add(col)
                else:
                    existing_col.card_count += 1

            elif drop_type == "material":
                mat_type = drop.get("material_type", "ore")
                mat_id = drop.get("material_id", 1)
                amount = drop.get("amount", 1)
                cls._upsert_material(db, user_no, mat_type, mat_id, amount)
                summary["material"] += amount

            elif drop_type == "stigma":
                sin_type = drop.get("sin_type", "")
                if sin_type:
                    # 낙인은 material_type="stigma", material_id는 죄종 번호
                    sin_id_map = {"wrath": 1, "envy": 2, "greed": 3, "sloth": 4, "gluttony": 5, "lust": 6, "pride": 7}
                    mat_id = sin_id_map.get(sin_type, 0)
                    cls._upsert_material(db, user_no, "stigma", mat_id, 1)
                    summary["stigma"] += 1

        # bulk 저장
        if total_gold > 0:
            user.gold += total_gold
        if items_to_add:
            db.add_all(items_to_add)
        if cards_to_add:
            db.add_all(cards_to_add)

        logger.info(f"[StageManager] _save_pending_drops (user_no={user_no}, gold={summary['gold']}, equip={summary['equipment']}, card={summary['card']}, mat={summary['material']}, stigma={summary['stigma']})")
        return summary

    @classmethod
    def _upsert_material(cls, db, user_no: int, material_type: str, material_id: int, amount: int):
        """재료 UPSERT — 기존이면 amount 증가, 없으면 INSERT"""
        existing = db.query(Material).filter(
            Material.user_no == user_no,
            Material.material_type == material_type,
            Material.material_id == material_id,
        ).first()
        if existing:
            existing.amount += amount
        else:
            db.add(Material(
                user_no=user_no,
                material_type=material_type,
                material_id=material_id,
                amount=amount,
            ))

    # ── 헬퍼: 최대 HP 계산 ──

    @classmethod
    def _calc_max_hp(cls, stat: 'UserStat', user_no: int) -> int:
        """유저 스탯 기반 최대 HP 계산 (기획서 공식: (100 + 체력×10) × (1 + Σ아이템HP%))"""
        from models import Item

        # 장착 아이템 HP% 합산
        db = stat._sa_instance_state.session
        equipped = db.query(Item).filter(
            Item.user_no == user_no,
            Item.equip_slot.isnot(None),
        ).all()

        i_hp_pct = 0.0
        for item in equipped:
            opts = item.dynamic_options or {}
            i_hp_pct += opts.get("hp_pct", 0)

        max_hp = int((100 + stat.stat_vit * 10) * (1 + i_hp_pct / 100))
        return max_hp
