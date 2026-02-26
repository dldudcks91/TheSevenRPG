from services.system import GameDataManager, UserInitManager
from services.rpg import InventoryManager, BattleManager, ItemDropManager # 새로 만든 폴더로 가정

class APIManager:
    api_map = {
        # === 시스템 및 로그인 API (1xxx) ===
        1002: (GameDataManager, GameDataManager.get_all_configs),
        1003: (UserInitManager, UserInitManager.create_new_user),
        
        
        # === RPG 인벤토리 API (2xxx) ===
        2001: (InventoryManager, InventoryManager.equip_item),
        # 2002: (InventoryManager, InventoryManager.unequip_item),
        
        # === RPG 전투 API (3xxx) ===
        3001: (BattleManager, BattleManager.battle_result),
        3002: (ItemDropManager, ItemDropManager.process_kill),
    }