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

### 재작성 필요
| 파일 | 문제 |
|------|------|
| `models.py` | 기획서 DB 설계와 불일치 (상세 아래) |
| `UserInitManager.py` | 인스턴스 메서드 구조 → `@classmethod` 패턴 위반 |
| `BattleManager.py` | 인스턴스 메서드 구조, 스켈레톤 |
| `InventoryManager.py` | 인스턴스 메서드 구조, 스켈레톤 |

### models.py 불일치 상세
| 항목 | 현재 코드 | 기획서 스펙 |
|------|----------|------------|
| `stat_luck`, `stat_cost` | 누락 | 5스탯 체계 (힘/민첩/체력/운/코스트) |
| `gold` 위치 | `UserStat`에 있음 | `User` 테이블 소속 |
| `current_stage`, `max_inventory` | `User`에 없음 | `User` 테이블 필수 컬럼 |
| `Inventory` 컬럼 | 일부 누락 | `item_level`, `rarity`, `item_cost`, `suffix_id`, `set_id`, `dynamic_options`, `equip_slot` |
| `Cards` 테이블 | 없음 | 기획서에 정의됨 |

---

## API 코드 전체 목록

| api_code | Manager | 메서드 | 설명 | 상태 |
|----------|---------|--------|------|------|
| 1002 | GameDataManager | `get_all_configs` | 클라이언트 초기 데이터 로드 | 완성 |
| 1003 | UserInitManager | `create_new_user` | 유저 생성 + 세션 발급 | 재작성 필요 |
| 2001 | InventoryManager | `equip_item` | 장비 장착 | 재작성 필요 |
| 2002 | InventoryManager | `unequip_item` | 장비 해제 | 미구현 |
| 2003 | InventoryManager | `get_inventory` | 인벤토리 조회 | 미구현 |
| 3001 | BattleManager | `battle_result` | 전투 시뮬레이션 결과 | 재작성 필요 |
| 3002 | ItemDropManager | `process_kill` | 몬스터 킬 & 드롭 처리 | 완성 |
| 3003 | StageManager | `enter_stage` | 스테이지 입장 (해금 검증) | 미구현 |
| 3004 | StageManager | `clear_stage` | 스테이지 클리어 (다음 해금) | 미구현 |
| 3005 | IdleFarmManager | `toggle_idle` | 방치 파밍 ON/OFF | 미구현 |
| 3006 | IdleFarmManager | `collect_idle` | 방치 파밍 보상 수령 | 미구현 |

---

## 개발 Phase

### Phase 1 — DB 모델 재정비
**목적**: 이후 모든 Phase의 기반. 기획서 DB 설계(§12) 기준으로 재작성.
**상태**: 계획 수립 완료, 검증 단계 진행 전

**변경 파일**
- `models.py` (수정)

**User 테이블 변경**
| 변경 | 컬럼 | 타입 | 비고 |
|------|------|------|------|
| 추가 | `gold` | BigInteger, default=0 | UserStat에서 이동 |
| 추가 | `current_stage` | Integer, default=1 | 진행 중 최고 스테이지 |
| 추가 | `max_inventory` | Integer, default=100 | 인벤토리 최대 칸 수 |
| 추가 | `cards` relationship | 1:N → Cards | |
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
| 추가 | `rarity` | String(20) | normal/magic/rare/unique |
| 추가 | `item_cost` | Integer | 코스트 값 |
| 추가 | `suffix_id` | String(50), nullable | 접미사 ID |
| 추가 | `set_id` | String(50), nullable | 세트 ID |
| 추가 | `dynamic_options` | JSON | 랜덤 부여 스탯 |
| 추가 | `equip_slot` | String(20), nullable | 장착 부위 |
| 삭제 | `item_type` | | 장비 전용 테이블로 변경 |
| 삭제 | `amount` | | 장비 전용 테이블로 변경 |

**Cards 테이블 (신규)**
| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| `card_uid` | String(36) | PK | UUID |
| `user_no` | BigInteger | FK → Users | 소유자 |
| `monster_idx` | Integer | | 드랍한 몬스터 종류 |
| `equipped_item` | String(36) | FK → Items, nullable | 장착된 장비 참조 |

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
```

---

## 미결정 기획 항목 (개발 전 확정 필요)

| 항목 | 영향 Phase | 비고 |
|------|-----------|------|
| 경험치 곡선 (레벨업 필요 경험치) | Phase 4 | 미기획 |
| 데미지 공식 세부 (최소/최대 범위) | Phase 4 | 기획서에 미확정 |
| 골드 드롭 공식 | Phase 4, 6 | 미기획 |
| 몬스터 스탯 (일반/정예/보스 배율) | Phase 4 | 미기획 |
| 방치 파밍 시간당 드롭 수량 | Phase 6 | 미기획 |
