from services.system import GameDataManager, UserInitManager, UserInfoManager
from services.rpg import (
    InventoryManager, BattleManager,
    StageManager, CardManager, MaterialManager,
    CraftingManager, ShopManager, QuestManager,
)

class APIManager:
    api_map = {
        # === 시스템 및 로그인 API (1xxx) ===
        1002: (GameDataManager, GameDataManager.get_all_configs),
        1003: (UserInitManager, UserInitManager.create_new_user),
        1004: (UserInfoManager, UserInfoManager.get_user_info),
        1005: (UserInfoManager, UserInfoManager.reset_stats),
        1006: (UserInfoManager, UserInfoManager.select_basic_sin),
        1007: (UserInitManager, UserInitManager.login),

        # === RPG 인벤토리 API (2xxx) ===
        2001: (InventoryManager, InventoryManager.equip_item),
        2002: (InventoryManager, InventoryManager.unequip_item),
        2003: (InventoryManager, InventoryManager.get_inventory),
        2004: (InventoryManager, InventoryManager.sell_item),
        2005: (InventoryManager, InventoryManager.expand_inventory),
        # 2006: EnhanceManager — 기획 보류 (엔드 콘텐츠 부족 시 추후 재활성화)
        2007: (CardManager, CardManager.get_collection),
        2008: (CardManager, CardManager.equip_skill),
        2009: (CardManager, CardManager.unequip_skill),
        2010: (InventoryManager, InventoryManager.disassemble_item),
        2011: (MaterialManager, MaterialManager.use_potion),
        2012: (CardManager, CardManager.get_cards),
        2013: (CardManager, CardManager.disassemble_card),
        2014: (CardManager, CardManager.level_up_card),
        2015: (MaterialManager, MaterialManager.get_materials),

        # === RPG 전투 API (3xxx) ===
        3001: (BattleManager, BattleManager.battle_result),
        # 3002: 제거 — ItemDropManager는 BattleManager 내부 호출로 전환 (Phase 17)
        3003: (StageManager, StageManager.enter_stage),
        3004: (StageManager, StageManager.clear_stage),
        3007: (StageManager, StageManager.return_to_town),
        3008: (StageManager, StageManager.get_battle_session),

        # === NPC 시설 API (4xxx) ===
        4001: (CraftingManager, CraftingManager.craft_item),
        4002: (ShopManager, ShopManager.buy_item),
        4003: (QuestManager, QuestManager.submit_quest),
        4004: (QuestManager, QuestManager.get_quests),
        4005: (ShopManager, ShopManager.get_shop),
    }
