import uuid
import logging
from database import SessionLocal
from models import User, UserStat, Item
from services.system.ErrorCode import ErrorCode, error_response
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable

logger = logging.getLogger("RPG_SERVER")

# ── 튜토리얼 상수 ──
TUTORIAL_STEP_BATTLE = 1

TUTORIAL_MONSTER_NAME = "사탄의 하수"
TUTORIAL_MONSTER_HP = 30
TUTORIAL_MONSTER_ATK = 3

TUTORIAL_EXP_REWARD = 15
TUTORIAL_GOLD_REWARD = 10

# 확정 드롭: Dusk Shroud (heavy_armor, small)
TUTORIAL_DROP_BASE_ITEM_ID = 200101
TUTORIAL_DROP_RARITY = "magic"

# 고정 전투 로그 (바알 초기 스탯 기준: 시작 무기 ATK 7~10)
TUTORIAL_BATTLE_LOG = {
    "turns": [
        {"turn": 1, "attacker": "player", "damage": 8, "target_hp": 22},
        {"turn": 1, "attacker": "monster", "damage": 3, "target_hp": 197},
        {"turn": 2, "attacker": "player", "damage": 9, "target_hp": 13},
        {"turn": 2, "attacker": "monster", "damage": 2, "target_hp": 195},
        {"turn": 3, "attacker": "player", "damage": 10, "target_hp": 3},
        {"turn": 3, "attacker": "monster", "damage": 3, "target_hp": 192},
        {"turn": 4, "attacker": "player", "damage": 8, "target_hp": 0},
    ],
    "result": "victory",
    "player_max_hp": 200,
    "monster_max_hp": TUTORIAL_MONSTER_HP,
    "monster_name": TUTORIAL_MONSTER_NAME,
}


class TutorialBattleManager:
    """튜토리얼 전투 (API 1010) — 프롤로그 직후 첫 전투 체험"""

    @classmethod
    async def tutorial_battle(cls, user_no: int, data: dict):
        """
        API 1010: 튜토리얼 전투
        - 스크립트 전투 결과 + 확정 드롭(방어구) 지급
        - 유저당 1회만 실행 가능
        """
        # ── [1] 입력 추출 ──
        # 파라미터 없음 (user_no만 필요)

        # ── [3] DB 세션 + 상태 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            # 튜토리얼 중복 실행 차단
            if user.tutorial_step >= TUTORIAL_STEP_BATTLE:
                return error_response(ErrorCode.TUTORIAL_ALREADY_DONE, "이미 튜토리얼을 완료했습니다.")

            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            if not stat:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯을 찾을 수 없습니다.")

            # ── [4] 비즈니스 로직 ──
            # 골드 + 경험치 지급
            user.gold += TUTORIAL_GOLD_REWARD
            stat.exp += TUTORIAL_EXP_REWARD

            # 튜토리얼 완료 플래그
            user.tutorial_step = TUTORIAL_STEP_BATTLE

            # 확정 드롭: 방어구 생성
            drop_item_uid = str(uuid.uuid4())
            drop_item = Item(
                item_uid=drop_item_uid,
                user_no=user_no,
                base_item_id=TUTORIAL_DROP_BASE_ITEM_ID,
                item_level=1,
                rarity=TUTORIAL_DROP_RARITY,
                item_score=0,
                item_cost=0,
                prefix_id=None,
                suffix_id=None,
                dynamic_options={"base_defense": 20.0, "base_magic_defense": 5.0},
                is_equipped=False,
                equip_slot=None,
            )
            db.add(drop_item)

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[TutorialBattleManager] 튜토리얼 전투 완료 (user_no={user_no}, drop={drop_item_uid})")

        except Exception as e:
            db.rollback()
            logger.error(f"[TutorialBattleManager] tutorial_battle 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "튜토리얼 처리 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "첫 전투에서 승리했습니다!",
            "data": {
                "battle_log": TUTORIAL_BATTLE_LOG,
                "exp_gained": TUTORIAL_EXP_REWARD,
                "gold_gained": TUTORIAL_GOLD_REWARD,
                "drop_item": {
                    "item_uid": drop_item_uid,
                    "base_item_id": TUTORIAL_DROP_BASE_ITEM_ID,
                    "item_name": "Dusk Shroud",
                    "main_group": "armor",
                    "sub_group": "heavy_armor",
                    "rarity": TUTORIAL_DROP_RARITY,
                    "item_level": 1,
                    "dynamic_options": {"base_defense": 20.0, "base_magic_defense": 5.0},
                },
            },
        }
