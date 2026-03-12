from services.system import GameDataManager, UserInitManager, UserInfoManager
from services.rpg import (
    InventoryManager, BattleManager, ItemDropManager,
    StageManager, IdleFarmManager, CardManager, EnhanceManager,
)

class APIManager:
    api_map = {
        # === 시스템 및 로그인 API (1xxx) ===
        1002: (GameDataManager, GameDataManager.get_all_configs),
        1003: (UserInitManager, UserInitManager.create_new_user),
        1004: (UserInfoManager, UserInfoManager.get_user_info),

        # === RPG 인벤토리 API (2xxx) ===
        2001: (InventoryManager, InventoryManager.equip_item),
        2002: (InventoryManager, InventoryManager.unequip_item),
        2003: (InventoryManager, InventoryManager.get_inventory),
        2004: (InventoryManager, InventoryManager.sell_item),
        2005: (InventoryManager, InventoryManager.expand_inventory),
        2006: (EnhanceManager, EnhanceManager.enhance_item),
        2007: (CardManager, CardManager.get_cards),
        2008: (CardManager, CardManager.equip_card),
        2009: (CardManager, CardManager.unequip_card),

        # === RPG 전투 API (3xxx) ===
        3001: (BattleManager, BattleManager.battle_result),
        3002: (ItemDropManager, ItemDropManager.process_kill),
        3003: (StageManager, StageManager.enter_stage),
        3004: (StageManager, StageManager.clear_stage),
        3005: (IdleFarmManager, IdleFarmManager.toggle_idle),
        3006: (IdleFarmManager, IdleFarmManager.collect_idle),
    }
