import uuid
import logging
from sqlalchemy.exc import IntegrityError
from database import SessionLocal
from models import User, UserStat, Item
from services.system.SessionManager import SessionManager
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")


class UserInitManager:
    """유저 생성/로그인 (API 1003)"""

    @classmethod
    async def create_new_user(cls, user_no: int, data: dict):
        """
        신규 유저 생성 + 세션 발급
        - 닉네임 존재 시 → 기존 유저 로그인 (세션 재발급)
        - 닉네임 미존재 시 → User + UserStat + 초기 장비 생성 후 세션 발급
        """
        user_name = (data.get("user_name") or "").strip()
        if not user_name:
            return error_response(ErrorCode.USER_NOT_FOUND, "유저 이름이 필요합니다.")

        db = SessionLocal()
        try:
            # 기존 유저 확인 → 로그인
            existing = db.query(User).filter(User.user_name == user_name).first()
            if existing:
                session_id = await SessionManager.create_session(existing.user_no)
                return {
                    "success": True,
                    "message": "로그인 성공",
                    "data": {
                        "user_no": existing.user_no,
                        "user_name": existing.user_name,
                        "session_id": session_id,
                    }
                }

            # 신규 유저 생성 (트랜잭션 1개)
            new_user = User(user_name=user_name)
            db.add(new_user)
            db.flush()

            new_stat = UserStat(user_no=new_user.user_no)
            db.add(new_stat)

            starter_weapon = Item(
                item_uid=str(uuid.uuid4()),
                user_no=new_user.user_no,
                base_item_id=1,
                item_level=1,
                rarity="normal",
                item_cost=0,
                equip_slot="weapon",
            )
            db.add(starter_weapon)

            db.commit()

            session_id = await SessionManager.create_session(new_user.user_no)

            return {
                "success": True,
                "message": "캐릭터가 생성되었습니다.",
                "data": {
                    "user_no": new_user.user_no,
                    "user_name": new_user.user_name,
                    "session_id": session_id,
                }
            }

        except IntegrityError:
            db.rollback()
            return error_response(ErrorCode.USER_ALREADY_EXISTS, f"이미 존재하는 닉네임: {user_name}")
        except Exception as e:
            db.rollback()
            logger.error(f"[UserInit] 유저 생성 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "유저 생성 중 오류가 발생했습니다.")
        finally:
            db.close()
