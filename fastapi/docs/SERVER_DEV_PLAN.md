# TheSevenRPG — 서버 개발 계획서

> 최초 작성: 2026-03-12
> 기준 기획서: `fastapi/docs/game_design/GAME_DESIGN.md`

---

## 현황 요약

### 완성된 컴포넌트
| 파일 | 상태 | 비고 |
|------|------|------|
| `main.py` | 완성 | 게이트웨이, 세션 인증, Rate Limit |
| `config.py` | 완성 | pydantic-settings 환경변수 |
| `logger.py` | 완성 | 콘솔(INFO+) / 파일(WARNING+) |
| `database.py` | 완성 | SQLAlchemy 엔진, 세션 |
| `schemas.py` | 완성 | ApiRequest (api_code + data) |
| `ErrorCode.py` | 완성 | E+4자리 에러 코드 체계 |
| `SessionManager.py` | 완성 | Redis 세션 생성/검증/삭제 |
| `RedisManager.py` | 완성 | 비동기 Redis 싱글톤 |
| `GameDataManager.py` | 완성 | CSV → 메모리 로드 |
| `ItemDropManager.py` | 완성 | 드롭 판정, 아이템 생성 로직 |
| `APIManager.py` | 완성 | api_map 등록 |

### 재작성 완료 ✅
| 파일 | 상태 | 비고 |
|------|------|------|
| `models.py` | ✅ 완료 | User/UserStat/Item/Collection 4테이블, 기획서 기준 |
| `UserInitManager.py` | ✅ 완료 | @classmethod 패턴, User+UserStat+초기장비 트랜잭션 |
| `BattleManager.py` | ✅ 완료 | 전투 시뮬레이션 엔진, Redis 캐싱, 보상 지급 |
| `InventoryManager.py` | ✅ 완료 | 장착/해제/조회/판매/인벤확장, 코스트 검증, Redis 무효화 |
| `StageManager.py` | ✅ 신규 | 스테이지 입장/클리어, 해금 검증 |
| `IdleFarmManager.py` | ✅ 신규 | 방치 파밍 ON/OFF, 보상 수령 |
| `CollectionManager.py` | ✅ 신규 | 도감 조회/스킬 장착/해제, 카드 등록 |
| `EnhanceManager.py` | ⏸️ 보류 | 기획 보류 (api_map 미등록, 코드 보존) |

---

## API 코드 전체 목록

| api_code | Manager | 메서드 | 설명 | 상태 |
|----------|---------|--------|------|------|
| 1002 | GameDataManager | `get_all_configs` | 클라이언트 초기 데이터 로드 | 완성 |
| 1003 | UserInitManager | `create_new_user` | 유저 생성 + 세션 발급 | ✅ 완성 |
| 1004 | UserInfoManager | `get_user_info` | 유저 정보 조회 (스탯/골드/방치) | ✅ 완성 |
| 2001 | InventoryManager | `equip_item` | 장비 장착 | ✅ 완성 |
| 2002 | InventoryManager | `unequip_item` | 장비 해제 | ✅ 완성 |
| 2003 | InventoryManager | `get_inventory` | 인벤토리 조회 | ✅ 완성 |
| 3001 | BattleManager | `battle_result` | 전투 시뮬레이션 결과 | ✅ 완성 |
| 3002 | ItemDropManager | `process_kill` | 몬스터 킬 & 드롭 처리 | 완성 |
| 3003 | StageManager | `enter_stage` | 스테이지 입장 (해금 검증) | ✅ 완성 |
| 3004 | StageManager | `clear_stage` | 스테이지 클리어 (다음 해금) | ✅ 완성 |
| 3005 | IdleFarmManager | `toggle_idle` | 방치 파밍 ON/OFF | ✅ 완성 |
| 3006 | IdleFarmManager | `collect_idle` | 방치 파밍 보상 수령 | ✅ 완성 |
| 2004 | InventoryManager | `sell_item` | 아이템 판매 | ✅ 완성 |
| 2005 | InventoryManager | `expand_inventory` | 인벤토리 확장 | ✅ 완성 |
| 2006 | EnhanceManager | `enhance_item` | 아이템 강화 | ⏸️ 보류 (기획 보류) |
| 2007 | CollectionManager | `get_collection` | 도감 목록 조회 | ✅ 완성 |
| 2008 | CollectionManager | `equip_skill` | 스킬 슬롯 장착 | ✅ 완성 |
| 2009 | CollectionManager | `unequip_skill` | 스킬 슬롯 해제 | ✅ 완성 |

---

## 개발 Phase

### Phase 1 — DB 모델 재정비 ✅
**목적**: 이후 모든 Phase의 기반. 기획서 DB 설계(§12) 기준으로 재작성.
**상태**: 완료

**변경 파일**
- `models.py` (수정)

**User 테이블 변경**
| 변경 | 컬럼 | 타입 | 비고 |
|------|------|------|------|
| 추가 | `gold` | BigInteger, default=0 | UserStat에서 이동 |
| 추가 | `current_stage` | Integer, default=1 | 진행 중 최고 스테이지 |
| 추가 | `max_inventory` | Integer, default=100 | 인벤토리 최대 칸 수 |
| 추가 | `collections` relationship | 1:N → Collections | |
| 유지 | `last_login`, `status` | | 기획서에 없지만 운영 필요 |

**UserStat 테이블 변경**
| 변경 | 컬럼 | 타입 | 비고 |
|------|------|------|------|
| 추가 | `stat_luck` | Integer, default=10 | 운 스탯 |
| 추가 | `stat_cost` | Integer, default=10 | 코스트 스탯 |
| 삭제 | `gold` | | → User로 이동 |
| 유지 | `stat_vit` | | 기획서 stat_vital이지만 3글자 약어 통일 |
| 변경 | `exp` | Integer → BigInteger | 기획서 스펙 |

**Inventory → Item 테이블 변경**
| 변경 | 컬럼 | 타입 | 비고 |
|------|------|------|------|
| 변경 | 테이블명 | `inventories` → `items` | 기획서 명칭 |
| 변경 | `item_uid` | Integer → String(36) | UUID |
| 변경 | `item_base_id` → `base_item_id` | String(50) → Integer | 메타데이터 참조 |
| 추가 | `item_level` | Integer | 장비 레벨 |
| 추가 | `rarity` | String(20) | magic/rare/craft/unique (일반 등급 제거) |
| 추가 | `item_score` | Integer | 몬스터 킬 점수 기반 품질 |
| 추가 | `item_cost` | Integer | 코스트 값 |
| 추가 | `prefix_id` | String(50), nullable | 접두사 ID |
| 추가 | `suffix_id` | String(50), nullable | 접미사 ID |
| 추가 | `set_id` | String(50), nullable | 세트 ID |
| 추가 | `dynamic_options` | JSON | 랜덤 부여 스탯 |
| 추가 | `is_equipped` | Boolean | 장착 여부 (인덱스 필수) |
| 추가 | `equip_slot` | String(20), nullable | 장착 부위 |
| 삭제 | `item_type` | | 장비 전용 테이블로 변경 |
| 삭제 | `amount` | | 장비 전용 테이블로 변경 |

**Collections 테이블 (도감 — 카드→도감 통합 개편)**
| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| `user_no` | BigInteger | PK/FK → Users | 소유자 (복합 PK) |
| `monster_idx` | Integer | PK | 몬스터 종류 (복합 PK) |
| `card_count` | Integer | | 누적 획득 카드 수 |
| `collection_level` | Integer | | 도감 레벨 (1~5) |
| `skill_slot` | Integer | nullable | 장착된 스킬 슬롯 (1~4) |

**의존성 확인 필요**
- `ItemDropManager.py`가 Inventory 모델 참조 시 Item으로 변경 필요

**완료 기준**: `database.init_db()` 실행 시 스키마 생성 성공

---

### Phase 2 — 유저 시스템
**목적**: 서버 첫 기동 테스트 진입점. 유저 생성과 세션 발급.

**변경 파일**
- `services/system/UserInitManager.py` (재작성)

**작업 내용 (API 1003)**
- `@classmethod async def create_new_user(cls, user_no, data)` 패턴으로 재작성
- 트랜잭션 1개로 처리: `User` + `UserStat` + 초기 장비 인벤 생성
- 완료 후 세션 발급 (`SessionManager.create_session`)
- 닉네임 중복 시 `E2002` 반환

**완료 기준**
- `curl -X POST /api -d '{"api_code": 1003, "data": {"user_name": "test"}}'` → 세션 반환

---

### Phase 3 — 인벤토리/장비 시스템
**목적**: 장비 장착 → 전투 스탯 캐시 업데이트 흐름 완성.

**변경 파일**
- `services/rpg/InventoryManager.py` (재작성)

**작업 내용**
- `equip_item` (API 2001): 슬롯 충돌 처리 + 코스트 검증 + Redis `battle_stats` 무효화
- `unequip_item` (API 2002): 장착 해제 + Redis `battle_stats` 무효화
- `get_inventory` (API 2003): 인벤토리 전체 조회

**어뷰징 방지 포인트**
- 아이템 소유권 검증 (클라이언트 item_uid 신뢰 금지)
- 코스트 초과 장착 차단 (서버 재계산)
- 같은 슬롯 동시 장착 Race Condition → DB 레벨 트랜잭션

**완료 기준**
- 아이템 장착 → `user:{no}:battle_stats` Redis 키 갱신 확인

---

### Phase 4 — 전투 시뮬레이션 엔진
**목적**: 핵심 게임플레이. 서버가 전투 전 과정을 시뮬레이션하고 결과만 반환.

**변경 파일**
- `services/rpg/BattleManager.py` (재작성)

**전투 흐름**
```
1. 유저 스탯 로드 (Redis battle_stats → 없으면 DB 재계산 후 캐싱)
2. 몬스터 스탯 로드 (GameDataManager.REQUIRE_CONFIGS)
3. 턴 기반 시뮬레이션 루프
   └ 공격 순서: 공격속도(atk_speed) 기준
   └ 명중 판정: clamp(Acc/(Acc+Eva) + LvDiff×0.01 + 0.1, 0.05, 0.95)
   └ 데미지 계산: 공격력 × (1 - 방어력/(방어력+100)) × 치명타
   └ 상태이상 처리 (화상/중독/스턴/빙결/침식/매혹/심판)
   └ 세트 보너스 적용 (각성 포함)
4. 승패 결정 → 경험치/골드 지급 (DB)
5. 전투 로그 반환 (클라이언트가 재생할 프레임 데이터)
```

**세부 스탯 공식** (기획서 기준)
```
최대HP      = (100 + 체력×10) × (1 + Σ아이템HP%)
공격력      = 무기기본공격력 × (1 + 힘×0.005) × (1 + Σ아이템공격력%)
공격속도    = 무기기본공격속도 × (1 + 민첩×0.003) × (1 + Σ아이템공속%)
Acc         = 민첩×0.005 + Σ아이템명중수치
Eva         = 운×0.001 + Σ아이템회피수치
치명타확률  = 운×0.001 + Σ아이템치확
치명타데미지 = 1.5 + 운×0.003 + Σ아이템치뎀
방어감소율  = 방어력 / (방어력 + 100)
```

**미결정 사항 (구현 전 확정 필요)**
- 데미지 공식 세부 (최소/최대 데미지 범위)
- 경험치 곡선 (레벨업 필요 경험치)
- 골드 드롭 공식

**완료 기준**
- 스테이지 1-1 몬스터 상대로 전투 시뮬레이션 결과 반환 확인

---

### Phase 5 — 스테이지 진행 관리
**목적**: 콘텐츠 해금 흐름. 스토리 모드 진행과 재입장 파밍 분리.

**신규 파일**
- `services/rpg/StageManager.py`

**작업 내용**
- `enter_stage` (API 3003): 해금 여부 검증, 스테이지 몬스터 풀 반환
- `clear_stage` (API 3004): 다음 스테이지 해금, 챕터 보스 해금 체크
- 포탈 귀환 지원: Redis `stage_progress`에 중간 진행 저장

**상태 전이 강제**
- `clear_stage`는 `enter_stage` 후에만 호출 가능
- 스테이지 순서 우회 차단 (current_stage 서버 검증)

---

### Phase 6 — 방치 파밍 (IdleFarm)
**목적**: 핵심 게임 루프 완성. 접속 없이도 아이템이 쌓이는 구조.

**신규 파일**
- `services/rpg/IdleFarmManager.py`

**작업 내용**
- `toggle_idle` (API 3005): 방치 ON → Redis 타이머 시작, OFF → 타이머 삭제
- `collect_idle` (API 3006): 경과 시간 계산 → 드롭 시뮬레이션 → 인벤 지급
- 인벤 풀 시 자동 중지 로직

**어뷰징 방지 포인트**
- 시작 시각은 서버가 기록 (클라이언트 타이머 신뢰 금지)
- 최대 누적 시간 cap (예: 24시간)
- 인벤 슬롯 초과 드롭 차단

---

## 개발 순서

```
Phase 1 (models.py)
    ↓
Phase 2 (UserInitManager) ← 여기서 첫 서버 기동 테스트
    ↓
Phase 3 (InventoryManager)
    ↓
Phase 4 (BattleManager) ← 핵심 / 가장 복잡
    ↓
Phase 5 (StageManager)
    ↓
Phase 6 (IdleFarmManager)
    ↓
Phase 7 (CollectionManager) ← 도감 시스템
    ↓
Phase 8 (InventoryManager 확장) ← 판매/인벤 확장
    ↓
Phase 9 (EnhanceManager) ← 아이템 강화
```

---

### Phase 7 — 도감 시스템 ✅ (카드→도감 통합 개편)
**목적**: 몬스터 카드 수집 → 도감 자동 등록 → 스킬 해금 → 스킬 슬롯 장착.

**신규 파일**
- `services/rpg/CollectionManager.py` (CardManager.py 대체)

**기획 변경 (15-b차)**
- 카드는 인벤토리 아이템이 아님 → 도감에 자동 등록
- 첫 카드 = 스킬 해금, 중복 카드 = 도감 경험치 → 레벨업 → 패시브 보너스
- 카드를 장비에 장착하는 방식 폐기 → 스킬 슬롯 4개 (Lv1/5/15/30 점진 해금)

**작업 내용**
- `get_collection` (API 2007): 도감 목록 조회 + 해금 슬롯 수 반환
- `equip_skill` (API 2008): 도감 스킬을 스킬 슬롯에 장착
- `unequip_skill` (API 2009): 스킬 슬롯에서 해제
- `register_card` (내부 전용): 카드 드롭 시 도감 등록 (신규/중복 처리)

**어뷰징 방지 포인트**
- 도감 소유권 검증 (user_no 조건 필수)
- 스킬 슬롯 해금 레벨 서버 검증
- 이미 사용 중인 슬롯 자동 교체 (기존 스킬 해제 후 장착)

**미구현 (기획 미확정)**
- 도감 레벨업 로직 (레벨별 필요 카드 수, 패시브 보너스)
- 카드 스킬의 전투 중 발동 로직

---

### Phase 8 — 아이템 판매 / 인벤토리 확장 ✅
**목적**: 골드 순환 경제 + 인벤토리 관리.

**변경 파일**
- `services/rpg/InventoryManager.py` (메서드 추가)

**작업 내용**
- `sell_item` (API 2004): 아이템 판매 (rarity × level 기반 가격)
  - 장착 중 판매 차단
- `expand_inventory` (API 2005): 골드 소비로 인벤 확장
  - 확장할수록 비용 증가, 최대 500칸 상한

**임시 수치**
- 판매가: magic=30, rare=100, craft=300, unique=500 (× item_level)
- 확장 비용: 500 × (현재칸/100 + 1), 10칸씩 확장

---

### Phase 9 — 아이템 강화 ⏸️ 보류
**목적**: 장비 성장 시스템. 골드 소비로 장비 스탯 증가.
**상태**: 기획 보류 — 엔드 콘텐츠 부족 시 추후 재활성화. 코드 보존, api_map 미등록.

**신규 파일**
- `services/rpg/EnhanceManager.py`

**작업 내용**
- `enhance_item` (API 2006): 골드 소비 → item_level 증가 → dynamic_options 수치 스케일링
  - 장착 중 강화 시 battle_stats 무효화

**임시 수치**
- 강화 비용: 100 × 현재 레벨
- 최대 강화 레벨: 20
- 레벨당 스탯 증가: 10% (복리)

---

### Phase 10 — Manager 컨벤션 리팩토링 ✅
**목적**: 전체 Manager를 `manager-convention` 스킬 기준에 맞게 통일. 트랜잭션 안전성, 에러 처리 일관성, 캐시 무효화 정확성 향상.

**변경 파일 (8개)**
- `services/rpg/EnhanceManager.py` — `with_for_update()`, 캐시 무효화 warning 로깅
- `services/rpg/CardManager.py` — `with_for_update()`, 캐시 무효화 warning 로깅
- `services/system/UserInfoManager.py` — Redis 장애 시 warning 로깅
- `services/rpg/InventoryManager.py` — 5개 메서드 모두 `with_for_update()`, warning 로깅
- `services/rpg/StageManager.py` — clear_stage `with_for_update()`, Redis warning 로깅
- `services/rpg/IdleFarmManager.py` — collect_idle `with_for_update()`, Redis warning 로깅
- `services/rpg/ItemDropManager.py` — `error_response()` 통일, 입력값 검증 강화
- `services/rpg/BattleManager.py` — `_grant_rewards` 트랜잭션 통합 (db 파라미터 전달), `with_for_update()`

**리팩토링 적용 사항**
| 항목 | 적용 내용 |
|------|-----------|
| 행 잠금 | 골드/스탯/슬롯 변경 시 `with_for_update()` 추가 (레이스 컨디션 방지) |
| 에러 처리 | 모든 Manager에서 `error_response()` 통일 (직접 dict 반환 제거) |
| 캐시 무효화 | `RedisUnavailable` catch 시 `logger.warning` 추가 (모니터링 사각지대 제거) |
| 로거 접두사 | `[ManagerName]` 형식으로 통일 (예: `[BattleManager]`) |
| 메서드 구조 | 6단계 순서 준수 (입력추출→메타검증→DB검증→로직→커밋→응답) |
| 트랜잭션 | BattleManager `_grant_rewards`가 자체 세션 → db 파라미터 전달로 변경 (1메서드=1커밋) |
| 응답 반환 | try 블록 밖에서 반환 (DB 세션 닫힌 후) |

---

### Phase 10.5 — 기획 동기화 (15-b차/16차) ✅
**목적**: 기획서 업데이트(카드→도감 통합, 장비 옵션 구조 확정, 강화 보류)에 맞춰 서버 코드 동기화.

**변경 파일 (7개)**
- `models.py` — Card→Collection 테이블 재설계, Item에 `prefix_id`/`item_score`/`is_equipped` 추가, rarity 기본값 `"magic"`
- `services/system/ErrorCode.py` — `CARD_NOT_FOUND`/`CARD_ALREADY_EQUIPPED` → `COLLECTION_NOT_FOUND`/`SKILL_SLOT_INVALID`
- `services/rpg/CollectionManager.py` — **신규** (CardManager.py 대체). 도감 CRUD + 스킬 슬롯 장착/해제
- `services/rpg/InventoryManager.py` — `SELL_PRICE_TABLE`에서 normal 제거 + craft 추가, 판매 시 카드 삭제 로직 제거
- `services/system/APIManager.py` — CardManager→CollectionManager, EnhanceManager(2006) 비활성화
- `services/rpg/__init__.py` — import 변경

**기획 변경 반영 요약**
| 기획 변경 | 서버 반영 |
|----------|----------|
| 카드→도감 통합 (15-b차) | Card 테이블→Collection 테이블, CardManager→CollectionManager |
| 스킬 슬롯 4개 점진 해금 | CollectionManager.equip_skill에 레벨 검증 |
| 일반 등급 제거 (16차) | Item.rarity default="magic", SELL_PRICE_TABLE normal 제거 |
| 장비 접두사 시스템 (16차) | Item.prefix_id 컬럼 추가 |
| 강화 시스템 보류 | EnhanceManager api_map 미등록 (코드 보존) |

---

## 데이터베이스 설계

> 기획서 GAME_DESIGN.md §12에서 이동

### Users (유저 계정)

| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| user_no | BIGINT | PK | 계정 고유 번호 (자동 증가) |
| user_name | VARCHAR(50) | Unique | 유저 닉네임 |
| gold | BIGINT | | 보유 재화 |
| current_stage | INT | | 진행 중인 최고 스테이지 |
| max_inventory | INT | | 인벤토리 최대 칸 수 (기본 100) |
| created_at | DATETIME | | 계정 생성일 |

### UserStats (캐릭터 스탯)

| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| user_no | BIGINT | PK/FK | 소유자 (Users 참조, 1:1) |
| level | INT | | 캐릭터 레벨 (최대 50) |
| exp | BIGINT | | 누적 경험치 |
| stat_points | INT | | 잔여 스탯 포인트 |
| stat_str | INT | | 힘 (공격력 +0.5%/pt) |
| stat_dex | INT | | 민첩 (공속 +0.3%, 명중 +0.5%/pt) |
| stat_vital | INT | | 체력 (HP +10/pt) |
| stat_luck | INT | | 운 (치명타확률 +0.1%, 치명타데미지 +0.3%, 회피 +0.1%/pt) |
| stat_cost | INT | | 코스트 (최대코스트 +2/pt) |

### Items (아이템 인스턴스)

| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| item_uid | VARCHAR(36) | PK | UUID |
| user_no | BIGINT | FK | 소유자 |
| base_item_id | INT | | equipment_base 메타데이터 참조 |
| item_level | INT | | 장비 레벨 (숨김, 옵션 풀 결정) |
| rarity | VARCHAR(20) | | magic / rare / craft / unique (일반 등급 제거) |
| item_score | INT | | 몬스터 킬 점수 기반 품질 |
| item_cost | INT | | 계산된 코스트 값 |
| prefix_id | VARCHAR(50) | | 접두사 ID (Nullable) |
| suffix_id | VARCHAR(50) | | 접미사 ID (Nullable) |
| set_id | VARCHAR(50) | | 7죄종 세트 ID (Nullable) |
| dynamic_options | JSON | | 랜덤 부여 스탯 (예: `{"atk": 15, "hp": 50}`) |
| is_equipped | BOOLEAN | | 장착 여부 (인덱스 필수) |
| equip_slot | VARCHAR(20) | | 장착 부위 (장착 시만 존재) |

### Collections (도감)

| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| user_no | BIGINT | PK/FK | 소유자 (복합 PK) |
| monster_idx | INT | PK | 몬스터 종류 (복합 PK) |
| card_count | INT | | 누적 획득 카드 수 |
| collection_level | INT | | 도감 레벨 (1~5) |
| skill_slot | INT | | 장착된 스킬 슬롯 1~4 (Nullable) |

---

## 클라이언트 개발 현황

> 상세 내용은 [CLIENT_DEV_PLAN.md](CLIENT_DEV_PLAN.md) 참조.
> Phase C1~C8 전체 완성.

---

## Phase 11 (예정) — 시뮬레이션 도구

**목적**: 기획 밸런싱을 위한 대량 시뮬레이션 CLI 도구. DB/Redis 없이 CSV 메타데이터만으로 독립 실행.
**전제조건**: 아래 기획 항목이 확정되어야 구현 가능.

**3가지 시뮬레이션 모드**

| 모드 | 용도 | 핵심 출력 |
|------|------|----------|
| PVE | 특정 빌드로 특정 몬스터 N회 전투 | 승률, 평균 턴수, DPS, 명중률, 위험구간 |
| PVP | 두 빌드 간 N회 대전 | 승률 비교, 스탯 우위 분석 |
| 드롭 | 특정 몬스터 N킬 드롭 분포 | 등급별 장비 수, 기대 파밍 횟수 |

**구현 전 확정 필요 항목**

| 항목 | 영향 모드 | 현재 상태 |
|------|----------|----------|
| 몬스터 레벨 정의 | PVE/PVP | 미정 (레벨차 명중 보정에 필수) |
| 몬스터 명중/회피 값 | PVE | 미정 (몬스터→플레이어 명중 판정 불가) |
| 몬스터 크리티컬 여부 | PVE | 미정 |
| 장비 레벨 스케일링 공식 | PVE/PVP | 미정 (레벨별 base_atk/base_def 성장) |
| 장비 옵션 수치 범위 | PVE/PVP | 미정 (접두/접미사 실제 수치) |
| 접미사(suffix) CSV | PVE/PVP/드롭 | 미작성 |
| PVP 전용 규칙 | PVP | 미정 (PVE와 동일? 별도 보정?) |
| PVP 선공 결정 방식 | PVP | 미정 |
| 방어구 base_def 적용 방식 | PVE/PVP | 미정 |
| 골드 드롭량 공식 | 드롭 | 미정 |
| 기타(카드/재료) 드롭 상세 | 드롭 | 미정 |
| cost 스탯 시뮬 처리 | PVE/PVP | 미정 (무시? 일정비율 투자 가정?) |

**아키텍처 (예정)**
```
fastapi/tools/simulator/
├── simulator.py           # CLI 진입점 (argparse)
├── engine/
│   ├── battle_engine.py   # 전투 공식 (BattleManager 로직 재사용)
│   ├── stat_calculator.py # 스탯 계산 (장비 포함)
│   ├── drop_engine.py     # 드롭 판정 (ItemDropManager 로직 재사용)
│   └── build_generator.py # 스탯빌드/장비셋 자동 생성
├── modes/
│   ├── pve_sim.py         # PVE 시뮬레이션
│   ├── pvp_sim.py         # PVP 시뮬레이션
│   └── drop_sim.py        # 드롭 시뮬레이션
└── report/
    └── formatter.py       # 결과 포맷팅 (텍스트/CSV)
```

**빌드 프리셋 (예정)**

| 프리셋 | STR | DEX | VIT | LUCK | 설명 |
|--------|-----|-----|-----|------|------|
| str_main | 60% | 15% | 20% | 5% | 근접 딜러 |
| dex_main | 15% | 60% | 10% | 15% | 민첩 딜러 |
| tank | 20% | 10% | 60% | 10% | 탱커 |
| luck_main | 10% | 20% | 15% | 55% | 크리/드롭 특화 |
| balanced | 25% | 25% | 25% | 25% | 균형 |

---

## 미결정 기획 항목 (개발 전 확정 필요)

| 항목 | 영향 Phase | 비고 |
|------|-----------|------|
| 경험치 곡선 (레벨업 필요 경험치) | Phase 4 | 미기획 |
| 데미지 공식 세부 (최소/최대 범위) | Phase 4 | 기획서에 미확정 |
| 골드 드롭 공식 | Phase 4, 6, 11 | 미기획 |
| 몬스터 스탯 (일반/정예/보스 배율) | Phase 4 | 미기획 |
| 방치 파밍 시간당 드롭 수량 | Phase 6 | 미기획 |
