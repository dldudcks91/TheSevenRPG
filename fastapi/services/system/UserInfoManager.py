import time
import logging
from database import SessionLocal
from models import User, UserStat
from services.redis_manager.RedisManager import RedisManager, RedisUnavailable
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")


class UserInfoManager:
    """유저 정보 조회 (API 1004)"""

    @classmethod
    async def get_user_info(cls, user_no: int, data: dict):
        """
        유저 캐릭터 정보 반환
        - User: gold, current_stage, max_inventory
        - UserStat: level, exp, stat_*
        - Redis: 방치 파밍 상태
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.user_no == user_no).first()
            if not user:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

            stat = db.query(UserStat).filter(UserStat.user_no == user_no).first()
            if not stat:
                return error_response(ErrorCode.USER_NOT_FOUND, "유저 스탯 정보가 없습니다.")

            # 방치 파밍 상태 조회
            idle_info = None
            try:
                idle_data = await RedisManager.hgetall(f"user:{user_no}:idle_farm")
                if idle_data:
                    start_time = int(idle_data["start_time"])
                    elapsed = min(int(time.time()) - start_time, 86400)
                    idle_info = {
                        "active": True,
                        "stage_id": int(idle_data["stage_id"]),
                        "elapsed_seconds": elapsed,
                    }
            except RedisUnavailable:
                logger.warning(f"[UserInfoManager] 방치 파밍 상태 조회 실패 - Redis 장애 (user_no={user_no})")

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
                    "idle_farm": idle_info,
                },
            }

        except Exception as e:
            logger.error(f"[UserInfoManager] get_user_info 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "유저 정보 조회 중 오류가 발생했습니다.")
        finally:
            db.close()
