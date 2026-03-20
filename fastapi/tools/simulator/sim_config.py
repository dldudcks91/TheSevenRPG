"""CSV 메타데이터 로더 — DB/Redis 없이 GameDataManager 초기화"""
import sys
import os

# fastapi/ 디렉토리를 sys.path에 추가
_FASTAPI_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _FASTAPI_DIR not in sys.path:
    sys.path.insert(0, _FASTAPI_DIR)

from services.system.GameDataManager import GameDataManager


def init_metadata():
    """CSV 메타데이터 로드 (서버 기동 없이)"""
    base_path = os.path.join(_FASTAPI_DIR, "meta_data") + "/"
    GameDataManager._loaded = False
    GameDataManager.load_all_csv(base_path)


def get_configs():
    return GameDataManager.REQUIRE_CONFIGS
