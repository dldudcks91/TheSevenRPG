---
name: fastapi-server
description: "FastAPI 서버 개발 가이드. SQLAlchemy + 단일 API 게이트웨이 패턴. Manager 클래스 작성, DB 세션 관리, 인증(세션), 에러 코드 체계 설계 시 사용."
---

# FastAPI Server 개발 가이드

## 아키텍처 원칙

### 단일 게이트웨이 패턴
- 모든 요청은 `POST /api` → `ApiRequest(api_code, data)`
- `Authorization: Bearer {session_id}` 헤더로 인증
- api_code로 Manager.method 라우팅 (APIManager.api_map)
- 새 기능 = Manager 메서드 작성 + api_map 등록, 그 외 변경 없음

### 데이터 계층
| 계층 | 저장소 | 용도 | 특성 |
|------|--------|------|------|
| 메타데이터 | CSV → 메모리 | 장비/몬스터/드롭 테이블 | read-only, 서버 기동 시 로드 |
| 유저 데이터 | MySQL (SQLAlchemy) | 계정, 인벤토리, 진행도 | 영구 저장, ORM 관리 |
| 세션 | Redis | 세션 토큰 → user_no 매핑 | TTL 7일, 인증 전용 |

> **Redis 현황**: 세션 관리 전용. 전투 스탯 캐싱은 DB 직접 조회로 대체.
> **Redis 재도입 조건**: PVP 매칭 큐, 랭킹 sorted set, 연맹 실시간 상태 구현 시.

### 파일 구조
```
fastapi/
├── main.py               # 게이트웨이, 세션 검증, Rate Limiting
├── config.py             # pydantic-settings 환경 변수 (settings.XXX)
├── logger.py             # 전역 로거 (from logger import logger)
├── database.py           # SQLAlchemy 엔진 + 커넥션 풀
├── schemas.py            # ApiRequest (api_code + data)
├── models.py             # ORM 모델 (User, UserStat, Item, Card, Material, BattleSession)
└── services/
    ├── system/
    │   ├── APIManager.py       # api_code → Manager 매핑
    │   ├── GameDataManager.py  # CSV 메타데이터 로드
    │   ├── SessionManager.py   # 세션 생성/검증/삭제 (Redis)
    │   ├── ErrorCode.py        # 에러 코드 Enum + error_response()
    │   ├── UserInitManager.py  # 유저 생성/로그인
    │   └── UserInfoManager.py  # 스탯 배분, 죄종 선택
    ├── rpg/
    │   ├── BattleManager.py    # 전투 시뮬레이션
    │   ├── StageManager.py     # 스테이지 입장/클리어
    │   ├── InventoryManager.py # 장비 장착/해제
    │   ├── ItemDropManager.py  # 드롭 판정 (순수 계산)
    │   ├── CardManager.py      # 카드 조회/분해/레벨업
    │   ├── MaterialManager.py  # 재료 조회/포션 사용/광석 합성
    │   ├── CraftManager.py     # 크래프팅 (매직→크래프트)
    │   ├── ShopManager.py      # 상점 구매
    │   ├── QuestManager.py     # 퀘스트 납품
    │   ├── DisassembleManager.py # 장비 분해
    │   ├── EliteManager.py     # 정예 몬스터 생성 (순수 계산)
    │   └── StatusEffectManager.py # 상태이상/전투 유닛 (순수 계산)
    ├── db_manager/
    │   └── DBManager.py
    └── redis_manager/
        └── RedisManager.py     # 비동기 Redis 싱글톤 (세션 전용)
```

---

## Manager 유형

### API Manager (DB 접근 O, API 진입점)
```python
@classmethod
async def some_method(cls, user_no: int, data: dict):
    # DB 세션, 트랜잭션, 에러 처리 포함
```
- BattleManager, StageManager, InventoryManager, CardManager, MaterialManager,
  CraftManager, ShopManager, QuestManager, DisassembleManager, UserInitManager, UserInfoManager

### Utility Manager (DB 접근 X, 순수 계산)
```python
@classmethod
def some_method(cls, ...):
    # async 불필요, DB/Redis 접근 없음
```
- ItemDropManager, EliteManager, StatusEffectManager
- API Manager에서 내부적으로 호출됨
- `async` 불필요, 동기 메서드로 작성

---

## 인증 패턴

### 요청 구조
```
POST /api
Authorization: Bearer {session_id}      ← 세션 헤더
Content-Type: application/json

{"api_code": 3001, "data": {"monster_idx": 1101}}
```
- `user_no`는 클라이언트가 보내지 않음 — 서버가 세션에서 조회
- `main.py`가 세션 → user_no 변환 후 Manager에 전달

### PUBLIC API (세션 불필요)
```python
# main.py
PUBLIC_API_CODES = {
    1002,   # 게임 config 로드
    1003,   # 유저 생성/로그인 (세션 발급)
    1007,   # 튜토리얼 전투
}
```

### 세션 발급 (로그인 Manager에서)
```python
from services.system.SessionManager import SessionManager

session_id = await SessionManager.create_session(user_no)
return {"success": True, "message": "로그인 완료", "data": {"session_id": session_id}}
```

---

## 에러 코드 체계

### 형식: `E + 4자리`
```
E1xxx — 시스템/인증   E1001 알 수 없는 API | E1002 인증 실패 | E1003 권한 없음
E2xxx — 유저          E2001 유저 없음       | E2002 이미 존재
E3xxx — 인벤토리      E3001 아이템 없음     | E3002 장착 불가 | E3008 골드 부족
                      E3009 카드 없음       | E3010 카드 장착중 | E3012 재료 부족
E4xxx — 전투          E4001 스테이지 없음   | E4002 잘못된 전투 요청
E9xxx — 서버 내부     E9001 DB 오류         | E9999 알 수 없는 오류
```

### 사용법
```python
from services.system.ErrorCode import ErrorCode, error_response

# 에러 반환
return error_response(ErrorCode.USER_NOT_FOUND, "유저를 찾을 수 없습니다.")

# 성공 반환
return {"success": True, "message": "완료", "data": {...}}
```

---

## API 코드 체계

| 범위 | 분류 | 주요 코드 |
|------|------|-----------|
| 1xxx | 시스템 | 1002 config, 1003 로그인, 1006 죄종선택, 1007 튜토리얼 |
| 2001~2009 | 장비 | 2001 장착, 2002 해제, 2003 인벤조회 |
| 2010~2019 | 카드/재료 | 2010 카드목록, 2011 포션사용, 2012 카드분해, 2013 카드레벨업, 2015 재료조회, 2016 광석합성 |
| 2020~2029 | 크래프팅 | 2020 크래프트실행, 2021 미리보기 |
| 2030~2039 | NPC | 2030 상점목록, 2031 구매, 2032 퀘스트목록, 2033 납품 |
| 2040~2049 | 분해 | 2040 분해실행, 2041 미리보기 |
| 3xxx | 전투 | 3001 전투결과, 3003 입장, 3004 클리어, 3007 귀환 |

### API 코드 등록
```python
# APIManager.py의 api_map에 추가
api_map = {
    2020: (CraftManager, CraftManager.craft_item),
    # ...
}
```

---

## DB 패턴

### SQLAlchemy 세션 (동기)
```python
from database import SessionLocal

db = SessionLocal()
try:
    user = db.query(User).filter(User.user_no == user_no).first()
    db.commit()
except Exception as e:
    db.rollback()
    logger.error(f"[ManagerName] method 실패: {e}", exc_info=True)
    return error_response(ErrorCode.DB_ERROR, "처리 중 오류")
finally:
    db.close()
```

### 복합 인덱스
자주 사용하는 쿼리 패턴에 맞춘 인덱스:
```python
# models.py
__table_args__ = (
    Index('ix_items_user_equip', 'user_no', 'equip_slot'),
    Index('ix_cards_user_monster', 'user_no', 'monster_idx'),
    Index('ix_materials_user_type', 'user_no', 'material_type', 'material_id'),
)
```

### JSON 컬럼 업데이트
```python
from sqlalchemy.orm.attributes import flag_modified

item.dynamic_options['new_key'] = value
flag_modified(item, "dynamic_options")  # SQLAlchemy가 변경 감지하도록 필수
```

### bulk insert
```python
db.add_all([item1, item2, item3])  # 다수 아이템 저장 시
db.flush()  # auto-increment ID 필요 시
```

### Race condition 방지
```python
item = db.query(Item).filter(...).with_for_update().first()  # SELECT FOR UPDATE
```

### 주의사항
- N+1 쿼리 방지: 필요 시 `joinedload` 활용
- 트랜잭션 단위 명확히 (전투 결과 저장 + 드롭 생성은 하나의 트랜잭션)
- API 1건당 DB 쿼리 3개 이하 목표

---

## 내부 호출 패턴

### 허용: Utility Manager의 순수 함수 호출
```python
# BattleManager 안에서 — OK
drops = ItemDropManager.process_kill(stage_id, monster_idx, spawn_type)
elite_stats = EliteManager.generate_elite(base_stats, traits)
```
이는 세션 공유가 아닌 순수 계산 결과 반환이므로 허용.

### 금지: API Manager 간 DB 세션 전달
```python
# ❌ 금지
db = SessionLocal()
InventoryManager.equip(db, ...)
BattleManager.reward(db, ...)
```

---

## 환경 변수 / 설정

```python
from config import settings

settings.DB_HOST
settings.SESSION_TTL_SECONDS   # 604800 (7일)
settings.RATE_LIMIT_DEFAULT    # "30/second"
settings.ENV                   # "development" / "production"
```

`.env` 파일로 관리 (git 제외). `.env.example` 참고.

---

## 로깅

```python
import logging
logger = logging.getLogger("RPG_SERVER")

logger.debug("전투 계산 중간값: ...")    # 개발 시만
logger.info("[ManagerName] 동작 (user_no=N)")
logger.warning("[ManagerName] 비정상 상황")
logger.error("[ManagerName] 실패: {e}", exc_info=True)
```
- 콘솔: INFO 이상
- 파일 (`logs/rpg_server.log`): WARNING 이상, 7일 보관

---

## 시뮬레이션 도구

DB/Redis 없이 CSV 메타데이터 + 순수 함수만으로 밸런싱 검증:
```
fastapi/tools/simulator/
├── sim_runner.py   ← CLI 진입점 (python -m tools.simulator.sim_runner pve ...)
├── sim_config.py   ← GameDataManager CSV 로딩
├── sim_player.py   ← 가상 플레이어 생성 (DB 없이 dict 구성)
├── sim_battle.py   ← PVE/PVP 전투 시뮬레이션
├── sim_drop.py     ← 드롭 시뮬레이션
├── sim_growth.py   ← 성장 곡선 시뮬레이션
└── sim_report.py   ← 결과 통계 출력
```

---

## 성능 체크리스트

- [ ] DB 쿼리 수 확인 (API 1건당 3개 이하 목표)
- [ ] 응답 시간 100ms 이하 목표
- [ ] CSV 메타데이터는 절대 런타임에 파일 I/O 금지 (메모리 참조만)
- [ ] 복합 인덱스가 주요 쿼리 패턴을 커버하는지 확인
- [ ] JSON 컬럼 변경 시 flag_modified 호출 여부 확인
