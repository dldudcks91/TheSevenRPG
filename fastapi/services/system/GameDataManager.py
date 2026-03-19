import csv
import os
import logging

logger = logging.getLogger("RPG_SERVER")

class GameDataManager:
    _instance = None
    _loaded = False  # 중복 로드 방지용 플래그
    
    # 네가 요구한 단일 통합 딕셔너리 구조
    REQUIRE_CONFIGS = {
        'monsters': {},
        'drop_config': {},
        'drop_equip_weights': {},
        'score_config': {},
        'rarity_config': {},
        'equip_bases': [],
        'prefixes': [],
        'suffixes': [],
        'uniques': [],
        'chapters': {},
        'stages': {},
        'level_config': {},          # 레벨별 필요 XP + 보상 (CSV 미존재 시 BattleManager 폴백)
        'spawn_grade_config': {},    # 스폰 등급별 배율 (CSV 미존재 시 BattleManager 폴백)
        'equip_drop_rate': [],       # mlvl 구간별 장비 등급 확률
        'unique_drop_rate': {},      # 챕터보스별 유니크 드롭률
        'gold_drop_config': {},      # 골드 드롭 공식 파라미터
        'stigma_drop_config': {},    # 챕터보스별 낙인 드롭률
        'set_bonus': {},             # 세트 보너스 (sin → breakpoint → effect)
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameDataManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load_all_csv(cls, base_path="./"):
        """서버 기동 시 딱 한 번만 실행되는 메타데이터 로더"""
        if cls._loaded:
            return

        logger.info("=== Loading Game CSV Data into REQUIRE_CONFIGS ===")
        
        try:
            # 1. Monster Info
            for row in cls._read_csv(os.path.join(base_path, "monster_info.csv")):
                cls.REQUIRE_CONFIGS['monsters'][int(row["monster_idx"])] = {
                    "name": row["monster_name"],
                    "monster_base": row["monster_base"],
                    "size_type": int(row["size_type"]) if row["size_type"].isdigit() else 1,
                    "base_hp": float(row["hp"]),
                    "base_atk": float(row["attack"]),
                    "base_def": float(row["defense"]),
                    "base_mdef": float(row["magic_defense"]),
                    "atk_speed": float(row["attack_speed"]),
                    "exp_reward": int(row["exp_reward"])
                }

            # 2. Score Config
            for row in cls._read_csv(os.path.join(base_path, "moster_score_config.csv")):
                cls.REQUIRE_CONFIGS['score_config'][row["param_name"]] = float(row["value"])

            # 3. Drop Config
            for row in cls._read_csv(os.path.join(base_path, "monster_drop_config.csv")):
                cls.REQUIRE_CONFIGS['drop_config'][int(row["monster_grade"])] = [
                    ("Nodrop", float(row["Nodrop"])),
                    ("gold", float(row["gold"])),
                    ("equipment", float(row["equipment"])),
                    ("card", float(row.get("card", 0))),
                    ("etc", float(row.get("etc(Card/Mat)", row.get("etc", 0))))
                ]

            # 4. Drop Equipment Weights (JSON 직렬화를 위해 튜플 대신 String Key 사용)
            for row in cls._read_csv(os.path.join(base_path, "monster_drop_equipment.csv")):
                sub_type = row["monster_sub_type"]
                m_class = int(row["monster_grade"])
                
                # "Wolf_1" 형태의 키로 저장
                key_str = f"{sub_type}_{m_class}"
                cls.REQUIRE_CONFIGS['drop_equip_weights'][key_str] = {
                    "weapon": int(row.get("무기", 0)),
                    "armor": int(row.get("갑옷", 0)),
                    "helmet": int(row.get("투구", 0)),
                    "gloves": int(row.get("장갑", 0)),
                    "boots": int(row.get("신발", 0))
                }

            # 5. Rarity Config
            for row in cls._read_csv(os.path.join(base_path, "equip_rarity_config.csv")):
                cls.REQUIRE_CONFIGS['rarity_config'][row["rarity"]] = {
                    "rarity_korean": row.get("rarity_korean", ""),
                    "min_score": float(row["min_score"]),
                    "max_score": float(row["max_score"]),
                    "base_cost": int(float(row.get("base_cost", 0))),
                    "prefix_count": int(row["prefix_count"]),
                    "suffix_count": int(row["suffix_count"]),
                    "option_min": int(row["option_min"]),
                    "option_max": int(row["option_max"]),
                    "color_hex": row.get("color_hex", ""),
                }

            # 6. Equipment Base
            cls.REQUIRE_CONFIGS['equip_bases'] = cls._read_csv(os.path.join(base_path, "equipment_base.csv"))

            # 7. Equipment Prefix
            cls.REQUIRE_CONFIGS['prefixes'] = cls._read_csv(os.path.join(base_path, "equipment_prefix.csv"))

            # 8. Equipment Suffix
            cls.REQUIRE_CONFIGS['suffixes'] = cls._read_csv(os.path.join(base_path, "equipment_suffix.csv"))

            # 8b. Equipment Unique
            cls.REQUIRE_CONFIGS['uniques'] = cls._read_csv(os.path.join(base_path, "equipment_unique.csv"))

            # 9. Chapter Info
            for row in cls._read_csv(os.path.join(base_path, "chapter_info.csv")):
                cls.REQUIRE_CONFIGS['chapters'][int(row["chapter_id"])] = {
                    "sin_kr": row["sin_kr"],
                    "sin_en": row["sin_en"],
                    "region_kr": row["region_kr"],
                    "region_en": row["region_en"],
                    "boss_name": row["boss_name_kr"],
                    "boss_desc": row["boss_desc"],
                }

            # 10. Stage Info (웨이브별 행 → stage_idx 기준 집계)
            for row in cls._read_csv(os.path.join(base_path, "stage_info.csv")):
                stage_idx = int(row["stage_idx"])
                wave = int(row["wave"])
                if stage_idx not in cls.REQUIRE_CONFIGS['stages']:
                    dlvl = int(row.get("dlvl", 1)) if row.get("dlvl", "").strip() else 1
                    ch_boss_mlvl_raw = row.get("chapter_boss_mlvl", "").strip()
                    ch_boss_mlvl = int(ch_boss_mlvl_raw) if ch_boss_mlvl_raw else None
                    cls.REQUIRE_CONFIGS['stages'][stage_idx] = {
                        "chapter": int(row["chapter"]),
                        "stage_num": int(row["stage_num"]),
                        "stage_name": row["stage_name"],
                        "dlvl": dlvl,
                        "chapter_boss_mlvl": ch_boss_mlvl,
                        "waves": {},
                    }
                cls.REQUIRE_CONFIGS['stages'][stage_idx]["waves"][wave] = int(row["monster_idx"])

            # 11. Level Config (optional)
            for row in cls._read_csv(os.path.join(base_path, "level_exp_table.csv")):
                lv = int(row["level"])
                cls.REQUIRE_CONFIGS['level_config'][lv] = {
                    "required_exp": int(row["required_exp"]),
                    "stat_points": int(row.get("stat_points", 5)),
                }

            # 12. Spawn Grade Config (optional)
            for row in cls._read_csv(os.path.join(base_path, "spawn_grade_config.csv")):
                cls.REQUIRE_CONFIGS['spawn_grade_config'][row["grade"]] = {
                    "hp_mult": float(row["hp_mult"]),
                    "atk_mult": float(row["atk_mult"]),
                    "exp_mult": float(row["exp_mult"]),
                    "gold_mult": float(row["gold_mult"]),
                    "drop_roll": int(row.get("drop_roll", 1)) if row.get("drop_roll", "").strip() else 1,
                }

            # 13. Equip Drop Rate (mlvl 구간별 장비 등급 확률)
            cls.REQUIRE_CONFIGS['equip_drop_rate'] = []
            for row in cls._read_csv(os.path.join(base_path, "equip_drop_rate.csv")):
                cls.REQUIRE_CONFIGS['equip_drop_rate'].append({
                    "mlvl_min": int(row["mlvl_min"]),
                    "mlvl_max": int(row["mlvl_max"]),
                    "magic_rate": float(row["magic_rate"]),
                    "rare_rate": float(row["rare_rate"]),
                })

            # 14. Unique Drop Rate (챕터보스별 유니크 드롭률)
            for row in cls._read_csv(os.path.join(base_path, "unique_drop_rate.csv")):
                cls.REQUIRE_CONFIGS['unique_drop_rate'][int(row["stage_idx"])] = {
                    "mlvl": int(row["mlvl"]),
                    "unique_rate": float(row["unique_rate"]) / 100.0,
                }

            # 15. Gold Drop Config
            for row in cls._read_csv(os.path.join(base_path, "gold_drop_config.csv")):
                cls.REQUIRE_CONFIGS['gold_drop_config'] = {
                    "mlvl_mult": float(row["mlvl_base_multiplier"]),
                    "base_constant": float(row["mlvl_base_constant"]),
                    "random_min": float(row["random_min"]),
                    "random_max": float(row["random_max"]),
                }

            # 16. Set Bonus
            for row in cls._read_csv(os.path.join(base_path, "equipment_set_bonus.csv")):
                set_id = row["set_id"]
                bp = int(row["breakpoint"])
                if set_id not in cls.REQUIRE_CONFIGS['set_bonus']:
                    cls.REQUIRE_CONFIGS['set_bonus'][set_id] = {}
                cls.REQUIRE_CONFIGS['set_bonus'][set_id][bp] = {
                    "effect_type": row["effect_type"],
                    "effect_id": row.get("effect_id", ""),
                    "effect_name": row.get("effect_name", ""),
                    "effect_desc": row.get("effect_desc", ""),
                    "value_1": float(row["value_1"]) if row.get("value_1", "").strip() else 0,
                    "value_2": float(row["value_2"]) if row.get("value_2", "").strip() else 0,
                    "status": row.get("status", "confirmed"),
                }

            # 17. Stigma Drop Config (챕터보스별 낙인 드롭률)
            for row in cls._read_csv(os.path.join(base_path, "stigma_drop_config.csv")):
                cls.REQUIRE_CONFIGS['stigma_drop_config'][int(row["stage_idx"])] = {
                    "sin_type": row["sin_type"],
                    "stigma_rate": float(row["stigma_rate"]) / 100.0,
                }

            cls._loaded = True
            logger.info("=== Game CSV Data Load Complete ===")
            
        except Exception as e:
            logger.error(f"[FATAL ERROR] CSV 로드 중 서버 파괴됨: {str(e)}")
            raise e

    @staticmethod
    def _read_csv(filepath: str) -> list:
        if not os.path.exists(filepath):
            logger.warning(f"[WARNING] {filepath} is missing! 해당 데이터를 빈 상태로 둡니다.")
            return []
            
        with open(filepath, mode='r', encoding='utf-8-sig') as f:
            return list(csv.DictReader(f))

    @classmethod
    async def get_all_configs(cls, user_no: int, data: dict):
        """API Code 1002: 클라이언트 접속 시 모든 기초 데이터를 한 번에 쏴줌"""
        if not cls._loaded:
            return {"success": False, "message": "Configs not loaded yet."}
            
        return {
            "success": True, 
            "message": "Config loaded",
            # 네가 원하던 대로 REQUIRE_CONFIGS를 통째로 반환함
            "data": cls.REQUIRE_CONFIGS 
        }