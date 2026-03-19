import logging
from database import SessionLocal
from models import User, UserStat
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")


VALID_SIN_TYPES = {"wrath", "envy", "greed", "sloth", "gluttony", "lust", "pride"}


class UserInfoManager:
    """유저 정보 관리 (API 1004, 1005, 1006)"""

    INITIAL_STAT_VALUE = 5           # 스탯 초기값 (5종 모두 동일)
    STAT_RESET_COST_PER_LEVEL = 100  # 스탯 리셋 비용 = 레벨 × 이 값

    @classmethod
    async def get_user_info(cls, user_no: int, data: dict):
        """
        유저 캐릭터 정보 반환
        - User: gold, current_stage, max_inventory
        - UserStat: level, exp, stat_*
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            if not stat:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯 정보가 없습니다.")

            return {
                "success": True,
                "message": "유저 정보 조회 성공",
                "data": {
                    "user_no": user.user_no,
                    "user_name": user.user_name,
                    "gold": user.gold,
                    "current_stage": user.current_stage,
                    "max_inventory": user.max_inventory,
                    "level": stat.level,
                    "exp": stat.exp,
                    "stats": {
                        "str": stat.stat_str,
                        "dex": stat.stat_dex,
                        "vit": stat.stat_vit,
                        "luck": stat.stat_luck,
                        "cost": stat.stat_cost,
                    },
                    "stat_points": stat.stat_points,
                    "basic_sin": user.basic_sin,
                },
            }

        except Exception as e:
            logger.error(f"[UserInfoManager] get_user_info 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "유저 정보 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

    @classmethod
    async def reset_stats(cls, user_no: int, data: dict):
        """
        API 1005: 스탯 리셋
        - 골드 소비 (레벨 × STAT_RESET_COST_PER_LEVEL)
        - 5종 스탯 → 초기값(5)으로 리셋
        - 투자한 포인트 전부 회수
        """
        # ── [1] 입력 추출 ── (추가 파라미터 없음)

        # ── [3] DB 세션 + 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            stat = db.query(UserStat).filter(UserStat.user_no == user_no).with_for_update().first()
            if not stat:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯 정보가 없습니다.")

            # 비용 계산
            reset_cost = stat.level * cls.STAT_RESET_COST_PER_LEVEL
            if user.gold < reset_cost:
                return error_response(ErrorCode.INSUFFICIENT_GOLD, f"골드가 부족합니다. (필요: {reset_cost}, 보유: {user.gold})")

            # 이미 초기 상태인지 체크
            invested = (
                (stat.stat_str - cls.INITIAL_STAT_VALUE)
                + (stat.stat_dex - cls.INITIAL_STAT_VALUE)
                + (stat.stat_vit - cls.INITIAL_STAT_VALUE)
                + (stat.stat_luck - cls.INITIAL_STAT_VALUE)
                + (stat.stat_cost - cls.INITIAL_STAT_VALUE)
            )
            if invested <= 0:
                return error_response(ErrorCode.INVALID_REQUEST, "리셋할 스탯이 없습니다.")

            # ── [4] 비즈니스 로직 ──
            user.gold -= reset_cost
            stat.stat_str = cls.INITIAL_STAT_VALUE
            stat.stat_dex = cls.INITIAL_STAT_VALUE
            stat.stat_vit = cls.INITIAL_STAT_VALUE
            stat.stat_luck = cls.INITIAL_STAT_VALUE
            stat.stat_cost = cls.INITIAL_STAT_VALUE
            stat.stat_points += invested

            logger.info(f"[UserInfoManager] 스탯 리셋 완료 (user_no={user_no}, cost={reset_cost}, 회수 포인트={invested})")

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()

            try:
                await RedisManager.delete(f"user:{user_no}:battle_stats")
            except RedisUnavailable:
                logger.warning(f"[UserInfoManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

        except Exception as e:
            db.rollback()
            logger.error(f"[UserInfoManager] reset_stats 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "스탯 리셋 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": "스탯이 초기화되었습니다.",
            "data": {
                "gold": user.gold,
                "stat_points": stat.stat_points,
                "stats": {
                    "str": stat.stat_str,
                    "dex": stat.stat_dex,
                    "vit": stat.stat_vit,
                    "luck": stat.stat_luck,
                    "cost": stat.stat_cost,
                },
                "reset_cost": reset_cost,
            },
        }

    # ── API 1006: 베이직 죄종 선택 ──

    @classmethod
    async def select_basic_sin(cls, user_no: int, data: dict):
        """
        API 1006: 베이직 죄종 선택/변경
        - 해당 죄종 세트포인트 +1
        - 변경 시 기존 선택 덮어쓰기 (무료)
        """
        # ── [1] 입력 추출 ──
        sin_type = data.get("sin_type")
        if not sin_type or sin_type not in VALID_SIN_TYPES:
            return error_response(ErrorCode.INVALID_REQUEST, f"유효하지 않은 죄종입니다. (허용: {', '.join(VALID_SIN_TYPES)})")

        # ── [3] DB 세션 + 검증 ──
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).with_for_update().first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            old_sin = user.basic_sin

            # ── [4] 비즈니스 로직 ──
            user.basic_sin = sin_type

            # ── [5] 커밋 + 캐시 무효화 ──
            db.commit()
            logger.info(f"[UserInfoManager] select_basic_sin (user_no={user_no}, {old_sin}→{sin_type})")

            try:
                await RedisManager.delete(f"user:{user_no}:battle_stats")
            except RedisUnavailable:
                logger.warning(f"[UserInfoManager] battle_stats 캐시 무효화 실패 (user_no={user_no})")

        except Exception as e:
            db.rollback()
            logger.error(f"[UserInfoManager] select_basic_sin 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "베이직 죄종 선택 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"베이직 죄종이 {sin_type}(으)로 설정되었습니다.",
            "data": {
                "basic_sin": sin_type,
            },
        }
