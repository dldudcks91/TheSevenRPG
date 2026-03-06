# TheSevenRPG - Project Guide

## 프로젝트 개요
7대 죄악(Seven Deadly Sins) 테마의 웹 RPG 게임.
몬스터 파밍 → 장비 드롭 → 스탯 강화의 핵심 루프를 가진 하드코어 파밍 RPG.

## 기술 스택
- **Server**: FastAPI (Python 3.9+)
- **DB**: MySQL (pymysql + SQLAlchemy ORM)
- **Cache**: Redis (비동기, 전투 스탯 캐싱 등)
- **메타데이터**: CSV 파일 → 서버 기동 시 메모리 로드 (GameDataManager)
- **Frontend**: 미정 (현재 public/index.html)

## 프로젝트 구조
```
TheSevenRPG/
├── CLAUDE.md
├── fastapi/
│   ├── main.py               # FastAPI 앱, 단일 /api 게이트웨이
│   ├── database.py           # SQLAlchemy 엔진, 세션
│   ├── models.py             # User, UserStat, Inventory 모델
│   ├── schemas.py            # Pydantic 요청 스키마 (ApiRequest)
│   ├── meta_data/            # CSV 기획 데이터 (장비, 몬스터, 드롭 등)
│   ├── public/               # 정적 프론트엔드 파일
│   └── services/
│       ├── system/           # GameDataManager, APIManager, UserInitManager
│       ├── rpg/              # BattleManager, InventoryManager, ItemDropManager
│       ├── db_manager/       # DBManager (DB 세션 관리)
│       └── redis_manager/    # RedisManager (캐시/태스크)
```

## 아키텍처 규칙

### 단일 API 게이트웨이 패턴
- 모든 클라이언트 요청은 `POST /api` 하나로 들어온다.
- `ApiRequest(user_no, api_code, data)` 형태로 전달.
- `APIManager.api_map`에서 api_code → (ManagerClass, method) 매핑.
- 새 기능 추가 시: Manager 메서드 작성 → api_map에 등록.

### API 코드 체계
- 1xxx: 시스템/로그인 (GameDataManager, UserInitManager)
- 2xxx: 인벤토리 (InventoryManager)
- 3xxx: 전투 (BattleManager, ItemDropManager)

### Manager 클래스 규칙
- 모든 API 핸들러 메서드는 `async def method(cls, user_no: int, data: dict)` 시그니처.
- 반환 형식: `{"success": bool, "message": str, "data": ...}`
- 메타데이터 참조는 항상 `GameDataManager.REQUIRE_CONFIGS`에서.

### 데이터 흐름
- **메타데이터(CSV)** → 서버 기동 시 메모리 로드 (read-only, 런타임 변경 없음)
- **유저 데이터** → MySQL (SQLAlchemy ORM)
- **전투 스탯 캐시** → Redis (장비 변경 시 갱신)

## 코딩 컨벤션
- 한국어 주석 사용
- 클래스명: PascalCase (예: ItemDropManager)
- 파일명: 클래스명과 동일 (예: ItemDropManager.py)
- 로깅: `logging.getLogger("RPG_SERVER")` 사용

## 기획 문서
- 기획 관련 논의 및 문서는 `fastapi/docs/game_design/`에서 관리.
- 마크다운 기획서: `fastapi/docs/game_design/GAME_DESIGN.md`
- 구글 시트 동기화: `sync_design_from_gs.py` (다운로드), `sync_design_to_gs.py` (업로드)

## 데이터 동기화 규칙
- "메타데이터를 불러와" = `fastapi/meta_data/sync_data_from_gs.py` 실행
- "기획 데이터를 불러와" = `fastapi/docs/game_design/sync_design_from_gs.py` 실행

## 기획 논의 규칙
- 기획 논의 시 분석/제안만 제공한다. "CSV에 반영할까요?" 같은 마무리 질문을 절대 하지 않는다.
- 문서(CSV/마크다운) 수정은 사용자가 최종 결정을 내린 후 명시적으로 요청할 때만 진행한다.
