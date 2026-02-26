from services.db_manager import DBManager
import logging

class UserInitManager:
    def __init__(self, db_manager: DBManager, redis_manager=None):
        self.db_manager = db_manager
    
    async def create_new_user(self, account_name: str):
        """신규 RPG 유저 생성 (DB 트랜잭션)"""
        db = self.db_manager.get_session()
        try:
            # 1. User 메타 데이터 생성
            new_user = User(account_name=account_name)
            db.add(new_user)
            db.flush() # user.id 발급을 위해 flush
            
            # 2. UserStat (1레벨 기본 스탯) 생성
            new_stat = UserStat(
                user_id=new_user.id,
                level=1, exp=0, gold=0,
                stat_str=10, stat_dex=10, stat_vit=10
            )
            db.add(new_stat)
            
            # 3. 기본 인벤토리 지급 (낡은 단검)
            basic_weapon = Inventory(
                user_id=new_user.id,
                item_type="WEAPON",
                item_base_id="dagger_001",
                is_equipped=True # 시작부터 장착시킴
            )
            db.add(basic_weapon)
            
            db.commit()
            return {"success": True, "user_id": new_user.id, "message": "RPG Character Created!"}
            
        except Exception as e:
            db.rollback()
            return {"success": False, "message": str(e)}
        finally:
            db.close()