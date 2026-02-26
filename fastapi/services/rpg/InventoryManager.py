from services.db_manager import DBManager
from services.redis_manager import RedisManager

class InventoryManager:
    def __init__(self, db_manager: DBManager, redis_manager: RedisManager):
        self.db_manager = db_manager
        self.redis_manager = redis_manager
        self.user_no = None
        self.data = None

    async def equip_item(self):
        """장비 장착 및 Redis 스탯 캐시 갱신"""
        target_uid = self.data.get("item_uid")
        
        # 1. DB에서 해당 아이템을 장착 상태로 변경 (기존 부위 해제 포함) 로직...
        # ... (생략: DB UPDATE 처리) ...

        # 2. 유저의 최종 스탯 재계산
        db = self.db_manager.get_session()
        stat = db.query(UserStat).filter(UserStat.user_id == self.user_no).first()
        equipped_items = db.query(Inventory).filter(Inventory.user_id == self.user_no, Inventory.is_equipped == True).all()
        
        # 공식 적용 (예: STR * 2 + 무기 공격력)
        total_attack = (stat.stat_str * 2) + sum(item.attack_power for item in equipped_items if hasattr(item, 'attack_power'))
        
        # 3. Redis에 최종 스탯 덮어쓰기 (전투 시 무조건 여기서 꺼내 씀!)
        redis = self.redis_manager.get_client()
        await redis.hset(f"user_combat_stat:{self.user_no}", mapping={
            "attack": total_attack,
            "hp": 100 + (stat.stat_vit * 10)
        })
        
        return {"success": True, "total_attack": total_attack}