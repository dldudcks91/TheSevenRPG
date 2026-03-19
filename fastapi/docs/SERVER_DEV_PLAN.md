# TheSevenRPG — 서버 개발 계획서

> 최초 작성: 2026-03-12
> 최종 업데이트: 2026-03-19 (Phase 14~16 구현 완료)
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
| `ItemDropManager.py` | 완성 | 드롭 판정, 아이템 생성 로직 (⚠️ DB 미저장 — Phase 17에서 서버사이드 저장으로 전환) |
| `APIManager.py` | 완성 | api_map 등록 |

### 재작성 완료 ✅
| 파일 | 상태 | 비고 |
|------|------|------|
| `models.py` | ✅ 완료 | User/UserStat/Item/Collection/BattleSession/Material/Card 7테이블 |
| `UserInitManager.py` | ✅ 완료 | 회원가입(bcrypt 해싱) + 로그인(비밀번호 검증) |
| `BattleManager.py` | ✅ 완료 | 전투 시뮬레이션 엔진, Redis 캐싱, 웨이브 보상, 사망 패널티 (Phase 14) |
| `InventoryManager.py` | ✅ 완료 | 장착/해제/조회/판매/인벤확장, 코스트 검증, Redis 무효화 |
| `StageManager.py` | ✅ 완료 | 4웨이브 체크포인트, 귀환(HP보존), 재접속, 13마리 구조 (Phase 14) |
| `CollectionManager.py` | ✅ 완료 | 도감 조회/스킬 장착/해제 (⚠️ 카드 인벤토리화 반영 필요 — Phase 18.5) |
| `UserInfoManager.py` | ✅ 수정 | 스탯 리셋 API 추가 (Phase 12) (⚠️ idle_farm 참조 코드 제거 필요 — Phase 12.5) |
| `EnhanceManager.py` | ⏸️ 보류 | 기획 보류 (api_map 미등록, 코드 보존) |
| `IdleFarmManager.py` | ❌ 삭제 완료 | 기획에서 완전 제거 (2026-03-17), Phase 12.5에서 정리 완료 |

---

## API 코드 전체 목록

### 활성 API
| api_code | Manager | 메서드 | 설명 | 상태 |
|----------|---------|--------|------|------|
| 1002 | GameDataManager | `get_all_configs` | 클라이언트 초기 데이터 로드 | ✅ 완성 |
| 1003 | UserInitManager | `create_new_user` | 회원가입 (비밀번호 해싱 + 세션 발급) | ✅ 완성 |
| 1004 | UserInfoManager | `get_user_info` | 유저 정보 조회 (스탯/골드) | ✅ 완성 |
| 1005 | UserInfoManager | `reset_stats` | 스탯 리셋 (골드 소비) | ✅ 완성 |
| 1007 | UserInitManager | `login` | 로그인 (비밀번호 검증 + 세션 발급) | ✅ 완성 |
| 2001 | InventoryManager | `equip_item` | 장비 장착 | ✅ 완성 |
| 2002 | InventoryManager | `unequip_item` | 장비 해제 | ✅ 완성 |
| 2003 | InventoryManager | `get_inventory` | 인벤토리 조회 | ✅ 완성 |
| 2004 | InventoryManager | `sell_item` | 아이템 판매 | ✅ 완성 |
| 2005 | InventoryManager | `expand_inventory` | 인벤토리 확장 | ✅ 완성 |
| 2007 | CollectionManager | `get_collection` | 도감 목록 조회 | ✅ 완성 |
| 2008 | CollectionManager | `equip_skill` | 스킬 슬롯 장착 | ✅ 완성 |
| 2009 | CollectionManager | `unequip_skill` | 스킬 슬롯 해제 | ✅ 완성 |
| 3001 | BattleManager | `battle_result` | 전투 시뮬레이션 결과 | ✅ 완성 |
| 3002 | ItemDropManager | `process_kill` | 몬스터 킬 & 드롭 처리 | ✅ 완성 |
| 3003 | StageManager | `enter_stage` | 스테이지 입장 (BattleSession 생성) | ✅ 완성 |
| 3004 | StageManager | `clear_stage` | 스테이지 클리어 (보스 처치 후) | ✅ 완성 |
| 3007 | StageManager | `return_to_town` | 마을 귀환 (HP 보존) | ✅ 완성 |
| 3008 | StageManager | `get_battle_session` | 전투 세션 조회 (재접속) | ✅ 완성 |

### 삭제 예정 API (Phase 12.5)
| api_code | Manager | 메서드 | 사유 |
|----------|---------|--------|------|
| ~~3005~~ | ~~IdleFarmManager~~ | ~~`toggle_idle`~~ | 방치 파밍 기획 제거 |
| ~~3006~~ | ~~IdleFarmManager~~ | ~~`collect_idle`~~ | 방치 파밍 기획 제거 |

### 보류 API
| api_code | Manager | 메서드 | 사유 |
|----------|---------|--------|------|
| 2006 | EnhanceManager | `enhance_item` | 기획 보류 (코드 보존, api_map 미등록) |

### Phase 12.5~ 에서 추가 예정 API

| api_code | Manager | 메서드 | 설명 | Phase |
|----------|---------|--------|------|-------|
| 1006 | UserInfoManager | `select_basic_sin` | 베이직 죄종 선택 | 22 |
| 2010 | InventoryManager | `disassemble_item` | 장비 분해 | 21 |
| 2011 | MaterialManager | `use_potion` | 포션 사용 | 18 |
| 2012 | CardManager | `get_cards` | 카드 인벤토리 조회 | 18.5 |
| 2013 | CardManager | `disassemble_card` | 카드 분해 → 카드 영혼 | 18.5 |
| 2014 | CardManager | `level_up_card` | 카드 레벨업 (동일카드N+영혼N) | 18.5 |
| 2015 | MaterialManager | `get_materials` | 재료 인벤토리 조회 | 18 |
| 4001 | CraftingManager | `craft_item` | 크래프팅 | 19 |
| 4002 | ShopManager | `buy_item` | 상인 구매 | 20 |
| 4003 | QuestManager | `submit_quest` | 퀘스트 재료 납품 | 20 |

---

## 개발 순서

```
=== Phase 1~10.5 완료 (기본 시스템) ===
Phase 1   (models.py)
Phase 2   (UserInitManager)
Phase 3   (InventoryManager)
Phase 4   (BattleManager)
Phase 5   (StageManager)
Phase 6   (IdleFarmManager) ❌ 기획 제거
Phase 7   (CollectionManager)
Phase 8   (InventoryManager 확장)
Phase 9   (EnhanceManager) ⏸️ 보류
Phase 10  (Manager 컨벤션 리팩토링)
Phase 10.5 (기획 동기화)

=== Phase 12~ (기획 확정 반영 — 시스템 고도화) ===
Phase 12   (경험치/레벨업) ✅ 완료
    ↓
Phase 12.5 (코드 정리) ← IdleFarmManager 삭제, 기획 불일치 수정
    ↓
Phase 13   (DB 모델 확장) ← BattleSessions, Materials, Cards, Users 컬럼
    ↓
Phase 14   (웨이브/체크포인트) ✅ 완료 ← StageManager + BattleManager 개편, 사망패널티 10%
    ↓
Phase 15   (정예 몬스터 특성) ✅ 완료
    ↓
Phase 16   (전투 엔진 v2) ✅ 부분완료 ← 경직/사이즈/마저항/상태이상/리포트 (카드스킬/세트=스텁)
    ↓
Phase 17   (드롭 시스템 v2) ← ilvl/mlvl/dlvl 체계 + 7종 드롭
    ↓
Phase 18   (재료 아이템 관리) ← 포션/광석/낙인/퀘스트재료/카드영혼
    ↓
Phase 18.5 (카드 인벤토리 시스템) ← 카드=아이템, 수치랜덤, 분해, 레벨업
    ↓
Phase 19   (크래프팅) ← 대장간
    ↓
Phase 20   (NPC 시설) ← 상인/퀘스트/흔적 조합소
    ↓
Phase 21   (장비 분해)
    ↓
Phase 22   (세트 보너스) ← 세트포인트 + 베이직 죄종 선택

=== Phase 23~ (엔드콘텐츠 — 추후) ===
Phase 23   (PVP / 아레나) ← Lv20 이상, 6등급, 시즌제
Phase 24   (연맹) ← 최대 15명, 경험치/골드/드롭률 버프

=== Phase 11 (시뮬레이션 도구) — Phase 16 이후 착수 ===
```

---

## 개발 Phase (완료)

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

**Collections 테이블 (도감)**
| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| `user_no` | BigInteger | PK/FK → Users | 소유자 (복합 PK) |
| `monster_idx` | Integer | PK | 몬스터 종류 (복합 PK) |
| `card_count` | Integer | | 누적 획득 카드 수 |
| `collection_level` | Integer | | 도감 레벨 (1~5) |
| `skill_slot` | Integer | nullable | 장착된 스킬 슬롯 (1~4) |

---

### Phase 2 — 유저 시스템 ✅
**목적**: 서버 첫 기동 테스트 진입점. 회원가입/로그인과 세션 발급.

**변경 파일**
- `services/system/UserInitManager.py` (재작성)
- `models.py` — `password_hash` 컬럼 추가

**작업 내용**
- API 1003 `create_new_user`: 회원가입 (user_name + password → bcrypt 해싱 저장 + 세션 발급)
- API 1007 `login`: 로그인 (user_name + password → 비밀번호 검증 → 세션 발급)
- 트랜잭션 1개로 처리: `User` + `UserStat` + 초기 장비 인벤 생성
- 닉네임 중복 시 `E2002`, 비밀번호 형식 오류 시 `E2003`
- 로그인 실패 시 유저 존재 여부 미노출 (보안: 동일 에러 메시지)
- `main.py` PUBLIC_API_CODES에 1003, 1007 등록

---

### Phase 3 — 인벤토리/장비 시스템 ✅
**목적**: 장비 장착 → 전투 스탯 캐시 업데이트 흐름 완성.

**변경 파일**
- `services/rpg/InventoryManager.py` (재작성)

**작업 내용**
- `equip_item` (API 2001): 슬롯 충돌 처리 + 코스트 검증 + Redis `battle_stats` 무효화
- `unequip_item` (API 2002): 장착 해제 + Redis `battle_stats` 무효화
- `get_inventory` (API 2003): 인벤토리 전체 조회

---

### Phase 4 — 전투 시뮬레이션 엔진 ✅
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
4. 승패 결정 → 경험치/골드 지급 (DB)
5. 전투 로그 반환 (클라이언트가 재생할 프레임 데이터)
```

> Phase 16에서 경직/사이즈/마저항/상태이상/세트보너스/스킬발동으로 대폭 개편 예정

---

### Phase 5 — 스테이지 진행 관리 ✅
**목적**: 콘텐츠 해금 흐름. 스토리 모드 진행과 재입장 파밍 분리.

**신규 파일**
- `services/rpg/StageManager.py`

**작업 내용**
- `enter_stage` (API 3003): 해금 여부 검증, stage_info.csv의 monster_pool/boss_id 기반 몬스터 풀 반환
- `clear_stage` (API 3004): 다음 스테이지 해금, 챕터 보스 해금 체크

> ✅ **2026-03-18**: 몬스터풀 기획 반영 완료 — 종별 집중 배치(AAA→BBB→CCC), [일반3+정예1]×3+보스=13마리, stage_id 101~704 해금 로직 개편
> Phase 14에서 웨이브/체크포인트/귀환/사망 시스템으로 대폭 개편 예정

---

### Phase 6 — 방치 파밍 (IdleFarm) ❌ 기획 제거
**목적**: ~~핵심 게임 루프 완성. 접속 없이도 아이템이 쌓이는 구조.~~
**상태**: ❌ **기획에서 완전 제거** (2026-03-17). 스토리 모드 단일 진행 + 클리어 후 재입장 파밍으로 확정.

**삭제 대상 (Phase 12.5에서 처리)**
- `services/rpg/IdleFarmManager.py` — 파일 삭제
- `APIManager.py` — api_map에서 3005, 3006 제거
- `UserInfoManager.py` — idle_farm Redis 조회 코드 제거
- Redis 키 `user:{no}:idle_farm` 관련 코드 전체 정리

---

### Phase 7 — 도감 시스템 ✅
**목적**: 몬스터 카드 최초 획득 → 도감 자동 등록 → 스킬 해금 → 스킬 슬롯 장착.

**신규 파일**
- `services/rpg/CollectionManager.py` (CardManager.py 대체)

**작업 내용**
- `get_collection` (API 2007): 도감 목록 조회 + 해금 슬롯 수 반환
- `equip_skill` (API 2008): 도감 스킬을 스킬 슬롯에 장착
- `unequip_skill` (API 2009): 스킬 슬롯에서 해제
- `register_card` (내부 전용): 카드 드롭 시 도감 등록 (신규/중복 처리)

**기획 변경 사항 (Phase 18.5에서 반영)**
- ~~도감 레벨업 로직~~ → **폐기**. 도감은 수집 기록 역할만 (첫 획득=자동 등록+스킬 해금)
- ~~도감 그룹 시스템~~ → **재설계 필요**. 기존 도감 레벨 합산 방식 폐기, 새 기준 미확정
- 카드 스킬 전투 발동 — **확정**: Ch1 17종 스킬 수치 1차 확정 (card_skill.csv) → Phase 16에서 구현
- **카드 = 인벤토리 아이템**으로 변경됨 → Phase 18.5에서 별도 카드 시스템 구현

---

### Phase 8 — 아이템 판매 / 인벤토리 확장 ✅
**목적**: 골드 순환 경제 + 인벤토리 관리.

**변경 파일**
- `services/rpg/InventoryManager.py` (메서드 추가)

**작업 내용**
- `sell_item` (API 2004): 아이템 판매 (rarity × level 기반 가격)
- `expand_inventory` (API 2005): 골드 소비로 인벤 확장

---

### Phase 9 — 아이템 강화 ⏸️ 보류
**목적**: 장비 성장 시스템. 골드 소비로 장비 스탯 증가.
**상태**: 기획 보류 — 엔드 콘텐츠 부족 시 추후 재활성화. 코드 보존, api_map 미등록.

---

### Phase 10 — Manager 컨벤션 리팩토링 ✅
**목적**: 전체 Manager를 `manager-convention` 스킬 기준에 맞게 통일.

**리팩토링 적용 사항**
| 항목 | 적용 내용 |
|------|-----------|
| 행 잠금 | 골드/스탯/슬롯 변경 시 `with_for_update()` 추가 |
| 에러 처리 | 모든 Manager에서 `error_response()` 통일 |
| 캐시 무효화 | `RedisUnavailable` catch 시 `logger.warning` 추가 |
| 로거 접두사 | `[ManagerName]` 형식으로 통일 |
| 메서드 구조 | 6단계 순서 준수 (입력추출→메타검증→DB검증→로직→커밋→응답) |
| 트랜잭션 | 1메서드=1커밋 원칙 |
| 응답 반환 | try 블록 밖에서 반환 (DB 세션 닫힌 후) |

---

### Phase 10.5 — 기획 동기화 (15-b차/16차) ✅
**목적**: 기획서 업데이트(카드→도감 통합, 장비 옵션 구조 확정, 강화 보류)에 맞춰 서버 코드 동기화.

**기획 변경 반영 요약**
| 기획 변경 | 서버 반영 |
|----------|----------|
| 카드→도감 통합 (15-b차) | Card 테이블→Collection 테이블, CardManager→CollectionManager |
| 스킬 슬롯 4개 점진 해금 | CollectionManager.equip_skill에 레벨 검증 |
| 일반 등급 제거 (16차) | Item.rarity default="magic", SELL_PRICE_TABLE normal 제거 |
| 장비 접두사 시스템 (16차) | Item.prefix_id 컬럼 추가 |
| 강화 시스템 보류 | EnhanceManager api_map 미등록 (코드 보존) |

---

## 개발 Phase (예정 — 기획 확정 반영)

### Phase 12 — 경험치/레벨업 시스템 ✅
**목적**: 확정된 경험치 커브와 레벨업 보상을 BattleManager에 적용.
**상태**: ✅ 완료 (2026-03-17)

**변경 파일 (5개)**
- `services/rpg/BattleManager.py` — EXP_TABLE→CSV 우선+폴백 공식, SPAWN_MULTIPLIERS→CSV 우선+폴백, _grant_rewards 등급별 XP/골드 배율 적용
- `services/system/UserInfoManager.py` — `reset_stats` (API 1005) 추가
- `services/system/ErrorCode.py` — `INVALID_REQUEST (E1004)` 추가
- `services/system/APIManager.py` — API 1005 등록
- `services/system/GameDataManager.py` — `level_config`, `spawn_grade_config` CSV 로더 추가

**CSV 연동 구조**
- `level_config` / `spawn_grade_config` CSV가 있으면 자동 로드, 없으면 폴백 상수 사용
- CSV 파일명: `level_exp_table.csv`, `spawn_grade_config.csv`

**작업 내용**
- [x] 경험치 필요량 테이블 — CSV 우선, 폴백: 기준10 × 1.3^(lv-1) / 그라인드 ×2.0
- [x] `_grant_rewards`에 몬스터 등급별 XP 계산 적용 (exp_reward × grade.exp_mult)
- [x] 레벨업 판정 + 스탯 포인트 지급 (CSV stat_points 또는 기본 5)
- [ ] 사망 패널티: 현재 레벨 내 경험치 **10%** 차감 — Phase 14(웨이브 시스템)에서 구현
- [x] 스탯 리셋 API (1005): 골드 소비 (레벨 × 100), 5종 스탯 초기화, 포인트 전부 회수

---

### Phase 12.5 — 코드 정리 (기획 불일치 해소) ✅
**목적**: 기획 제거/변경으로 인한 데드코드 정리 및 불일치 수정.
**상태**: ✅ 완료 (2026-03-18)

**작업 내용**
- [x] `IdleFarmManager.py` 파일 삭제
- [x] `APIManager.py`에서 API 3005, 3006 제거 + IdleFarmManager import 제거
- [x] `services/rpg/__init__.py`에서 IdleFarmManager import 제거
- [x] `UserInfoManager.get_user_info`에서 idle_farm Redis 조회 코드 제거 + `import time` 제거
- [x] IR 문서 `idle_farm.md` 상태를 `removed`로 변경
- [x] `.claude/rules/server.md`, `.claude/skills/` 내 idle_farm 관련 참조 정리

---

### Phase 13 — DB 모델 확장 ✅
**목적**: Phase 14~22에 필요한 신규 테이블과 컬럼 추가.
**상태**: ✅ 완료 (2026-03-18)

**변경 파일**
- `models.py` (수정)

**Users 테이블 추가 컬럼**
| 컬럼 | 타입 | 설명 | 사용 Phase |
|------|------|------|-----------|
| `basic_sin` | String(20), nullable | 베이직 죄종 선택 (세트포인트 +1) | Phase 22 |
| `unlocked_facilities` | Integer, default=0 | 해금된 시설 비트마스크 | Phase 20 |

**BattleSessions 테이블 (신규)**
| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| `user_no` | BIGINT | PK/FK | 소유자 |
| `stage_id` | INT | | 현재 스테이지 |
| `current_wave` | INT | | 현재 웨이브 (1~4) |
| `current_hp` | INT | | 현재 HP |
| `max_hp` | INT | | 최대 HP |
| `pending_drops` | JSON | | 웨이브 내 드롭 임시 저장 |
| `wave_kills` | JSON | | 웨이브별 처치 기록 |
| `started_at` | DATETIME | | 세션 시작 시각 |

**Materials 테이블 (신규 — 재료 아이템)**
| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| `id` | BIGINT | PK | 자동 증가 |
| `user_no` | BIGINT | FK | 소유자 |
| `material_type` | String(20) | | potion / ore / stigma / quest_material / card_soul |
| `material_id` | INT | | 메타데이터 참조 (포션 종류, 광석 등급, 죄종 등) |
| `amount` | INT | | 수량 (스택 가능) |

**Cards 테이블 (신규 — 카드 인벤토리)**
| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| `card_uid` | VARCHAR(36) | PK | UUID |
| `user_no` | BIGINT | FK | 소유자 |
| `monster_idx` | INT | | 몬스터 종류 (card_skill.csv 참조) |
| `card_level` | INT | | 카드 레벨 (기본 1) |
| `card_stats` | JSON | | 랜덤 부여 수치 (드롭 시 결정) |
| `is_equipped` | BOOLEAN | | 스킬 슬롯 장착 여부 |
| `skill_slot` | INT | nullable | 장착된 스킬 슬롯 (1~4) |
| `created_at` | DATETIME | | 획득 시각 |

---

### Phase 14 — 웨이브/체크포인트 시스템 ✅
**목적**: 스테이지 런 구조를 4웨이브 시스템으로 전면 개편.
**상태**: ✅ 완료 (2026-03-19)
**의존성**: Phase 13 (BattleSessions 테이블)

**변경 파일**
- `services/rpg/StageManager.py` (대폭 개편)
- `services/rpg/BattleManager.py` (수정)

**기획 (확정)**
```
스테이지 구성: [일반3+정예1]×3웨이브 + 보스(웨이브4) = 13마리
스폰 순서: 종별 집중 (AAA→BBB→CCC)

체크포인트: 웨이브 클리어마다 저장
귀환: HP 보존, 재입장 시 해당 웨이브 처음부터 (웨이브 내부 진행 리셋)
사망: 현재 레벨 내 경험치 10% 차감 (0% 하한, 레벨다운 없음), 현재 웨이브 처음 재시작, 드롭 유지
포션: 웨이브 클리어 후 사용 가능 (전투 중 불가), 지참 개수 제한 (수치 미확정)
```

**작업 내용**
- [x] `enter_stage` 개편: BattleSession 생성, 웨이브 몬스터 풀 반환 (13마리 구조)
- [x] `battle_result` 개편: BattleSession 연동, 연속 HP, 웨이브 킬 기록, 웨이브 클리어 보상
- [x] 체크포인트: 웨이브 클리어 시 BattleSession 업데이트 + 다음 웨이브 진행
- [x] `return_to_town` (API 3007): HP 보존 귀환, 세션 유지, 현재 웨이브 킬 리셋
- [x] `get_battle_session` (API 3008): 재접속 시 진행 복구
- [x] 사망 처리: 경험치 10% 차감, 웨이브 처음 재시작, HP max 복구
- [x] `clear_stage` 개편: 웨이브4(보스) 클리어 검증 후 스테이지 완료 + BattleSession 삭제
- [x] `main.py` CSV base_path 수정 (os.path.dirname 기반 절대경로)

**어뷰징 방지**
- 웨이브 순서 강제 (1→2→3→4)
- BattleSession 없이 battle_result 호출 차단
- HP 조작 방지 (서버 HP 관리)

---

### Phase 15 — 정예 몬스터 특성 시스템 ✅
**목적**: 정예 몬스터 런타임 생성 로직 구현.
**상태**: ✅ 완료 (2026-03-19)
**의존성**: Phase 14 (웨이브 시스템)

**변경 파일**
- `services/rpg/EliteManager.py` (신규)
- `services/rpg/BattleManager.py` (수정)

**기획 (확정 — monster_design.md)**
```
정예 = 노말 유닛 + 죄종 고유 특성 1개 + 공통 특성 2개

죄종 고유 특성 (7종):
- 분노: 격분 (HP30%↓ → 공격력×2, 공속+50%)
- 나태: 태만 (공속-50%, 공격력×2)
- 색욕: 유혹 (타격 시 플레이어 공격력 10% 흡수, 스택)
- 시기: 박탈 (치명타/회피 발동 시 무효화)
- 오만: 불가침 (모든 상태이상 면역)
- 폭식: 탐식 (매 타격 공격력 +2% 영구 누적)
- 탐욕: 도박 (피해 0.2~1.8배 랜덤, 처치 시 드롭+1)

공통 특성 풀 (16종): 강인한/단단한/거대한/날랜/흉포한/민첩한/정확한/치명적인
  + 재생하는/가시의/경화의/선제의/보복의/폭발하는/저주받은/흡혈의
```

**작업 내용**
- [x] `EliteManager.generate_elite(stage_id, monster_data, grade)` — 정예 유닛 생성 + 특성 스탯 보정
- [x] 죄종 고유 특성 7종 전투 적용 (불가침은 Phase 16 상태이상 구현 후 활성화)
- [x] 공통 특성 16종 전투 적용 (저주받은은 Phase 16 구현 후 활성화)
- [x] BattleManager._simulate_with_hp에 elite_stats/traits 파라미터 추가, 전투 루프 내 특성 효과 반영

---

### Phase 16 — 전투 엔진 v2 ★핵심 ✅ (부분)
**목적**: 확정된 전투 공식 전체를 BattleManager에 반영. 현재 기본 공방만 있는 엔진을 완전체로 개편.
**상태**: ✅ 부분 완료 (2026-03-19) — 카드 스킬/세트 보너스는 Phase 18.5/22에서 연동
**의존성**: Phase 12 (경험치), Phase 15 (정예 특성)

**변경 파일**
- `services/rpg/BattleManager.py` (대폭 개편)

**확정 공식 (기획서 battle_guide.md / battle_design.md)**
```
스탯 공식 (통합 계수):
- 최대HP = (100 + 체력×10) × (1 + Σ아이템HP%)
- ATK = 무기베이스(min~max) × (1 + 힘×0.005 + Σ아이템공격력%)
- 공격속도 = 무기기본공격속도 × (1 + 민첩×0.003) × (1 + Σ아이템공속%)
- Acc = (민첩×5 + Σ아이템명중수치) × 0.001
- Eva = (운×5 + Σ아이템회피수치) × 0.001
- 명중확률 = clamp(Acc/(Acc+Eva) + LvDiff×0.01 + 0.1, 0.05, 0.95)
- 치명타확률 = (운×5 + Σ아이템치확수치) × 0.001
- 치명타데미지 = 1.5 + Σ아이템치뎀
- 방어감소율 = DEF / (DEF + 100)
- 마법저항감소율 = MR / (MR + 100)

데미지 공식:
- 최종 데미지 = ATK × (1 - 방어감소율) × 사이즈보정 × 치명타배율
- 사이즈보정: 대형↔대형 +10%, 대형↔소형 -10%, 중형 보정 없음

경직 (확정):
- 경직 조건: 단타 피해 > 최대HP ÷ 10
- 경직 중: 평타 쿨 멈춤 (공격 불가)
- 둔기: 경직 시간 추가
- FHR: 경직시간 × (1 - FHR%)
```

**작업 내용**
- [x] CombatUnit 기반 전투 엔진 리팩토링 (StatusEffectManager.py 신규)
- [x] 경직 시스템: 피격 경직 조건(단타>최대HP÷10) + FHR 감소
- [x] 사이즈 보정: get_size_correction (대↔대 +10%, 대↔소 -10%)
- [x] 마법 저항: MR / (MR + 100) 감소율 (CombatUnit에 magic_def 포함)
- [x] 상태이상 7종 시스템 구현 (CombatUnit.apply_status / tick_status)
  - 화상(4s): 회복량 50% 감소
  - 중독(4s): 매초 고정 데미지
  - 스턴(1s): 공격 불가
  - 빙결(3s): 공속 50% 감소
  - 침식(영구): 피격당 DEF 2% 영구 감소 (스택)
  - 매혹(4s): 명중률 50% 감소
  - 심판(2s): 카드 스킬 봉인
  - 중첩: 갱신(타이머 리셋), 침식만 스택형
- [ ] 카드 스킬 발동: Phase 18.5 카드 인벤토리 구현 후 연동
- [ ] 세트 보너스 전투 적용: Phase 22 세트 보너스 구현 후 연동
- [x] 전투 리포트: battle_report (p_total_dmg/m_total_dmg/hits/misses/crits/staggers)

---

### Phase 17 — 드롭 시스템 v2
**목적**: 장비 전용이던 드롭을 7종 아이템으로 확장. ilvl/mlvl/dlvl 체계 적용. 서버사이드 DB 저장.
**상태**: [ ] 미착수
**의존성**: Phase 13 (Materials/Cards 테이블), Phase 14 (웨이브 시스템)

**변경 파일**
- `services/rpg/ItemDropManager.py` (대폭 개편)

**기획 (확정)**
```
ilvl/mlvl/dlvl 체계 (D2 구조):
- dlvl = 스테이지별 던전 레벨 (수치 배분 미확정 — 3안 중 선택 필요)
- mlvl 보정: 일반=dlvl / 정예=dlvl+2 / 스테이지보스=dlvl+3 / 챕터보스=고정(cap 50)
- ilvl = 드롭 몬스터의 mlvl
- mlvl↑ → 상위 등급 드롭 확률↑ + 접사 수치 상한↑

스폰 등급별 드롭:
| 등급 | 골드 | 포션 | 광석 | 퀘재 | 카드 | 장비 | 낙인 |
|------|------|------|------|------|------|------|------|
| 일반 | O | O | O | O | 극악 | X | X |
| 정예 | O | O | O | O | 극악 | O(매직/레어) | X |
| 보스 | O | O | O | O | 극악 | O(레어/유니크) | X |
| 챕보 | O | O | O | X | 극악 | O(전용유니크) | O(희귀) |

타겟 파밍 3축:
- 지역→죄종 편향 (접사 확률)
- 몬스터 베이스→부위 편향 (장비 부위 가중치)
- 챕터 보스→낙인 (크래프팅 죄종)
```

**작업 내용**
- [ ] ilvl/mlvl 계산 로직 구현
- [ ] 드롭 판정 로직: 등급별 7종 아이템 개별 확률 (mlvl 기반)
- [ ] 장비 드롭: 지역 죄종 편향 + 몬스터 베이스 부위 편향
- [ ] 카드 드롭: Cards 테이블에 저장 + CollectionManager.register_card 연동 (도감 자동 등록)
- [ ] 재료 드롭: Materials 테이블에 스택 추가
- [ ] 낙인 드롭: 챕터 보스 전용
- [ ] **서버사이드 DB 저장**: process_kill이 직접 DB에 저장 (현재 클라이언트 신뢰 구조 → 제거)
- [ ] 드롭 CSV 메타데이터 확장

**기획 확정 대기 항목**
- dlvl 스테이지별 배분 수치 (A-동행형 / B-선형형 / C-계단형 중 선택)
- mlvl별 등급 드롭 확률 테이블
- 접사 qlvl(수치 요구 레벨) 체계
- 골드 드롭량 공식
- 낙인 드롭률 수치
- 카드 드롭률 수치 (일반 vs 보스 차등)

---

### Phase 18 — 재료 아이템 관리
**목적**: 포션/광석/낙인/퀘스트재료/카드영혼의 인벤토리 관리 및 사용.
**상태**: [ ] 미착수
**의존성**: Phase 13 (Materials 테이블), Phase 17 (드롭)

**변경 파일**
- `services/rpg/MaterialManager.py` (신규)

**작업 내용**
- [ ] `get_materials` (API 2015): 재료 인벤토리 조회
- [ ] `use_potion` (API 2011): 웨이브 클리어 후 HP 회복 (전투 중 불가)
  - 지참 개수 제한 (수치 미확정 → 밸런싱 시)
- [ ] 광석 등급 계층: 합성 로직 (수치 미확정)
- [ ] 카드 영혼: 카드 분해 시 획득하는 범용 재료 (카드 종류 무관)

---

### Phase 18.5 — 카드 인벤토리 시스템 (신규)
**목적**: 카드 = 인벤토리 아이템 체계 구현. 카드 수치 랜덤, 분해, 레벨업.
**상태**: [ ] 미착수
**의존성**: Phase 13 (Cards 테이블), Phase 18 (카드 영혼 재료)

**변경 파일**
- `services/rpg/CardManager.py` (신규 — 기존 CollectionManager의 카드 로직 분리)
- `services/rpg/CollectionManager.py` (수정 — 도감은 수집 기록만)

**기획 (확정)**
```
카드 시스템:
- 카드 = 인벤토리 아이템 (카드 전용 탭)
- 드롭 시 랜덤 수치 부여 (같은 카드도 수치 다름)
- 더 좋은 수치의 카드로 교체 가능
- 첫 획득 시 도감 자동 등록 + 스킬 해금

카드 레벨업:
- 같은 카드 N장 + 카드 영혼 N개 소모 (수치는 밸런싱 단계 확정)

카드 분해:
- 카드 분해 → 카드 영혼 획득 (범용 재료, 카드 종류 무관)

카드 옵션 방향:
- 아이템에서 얻을 수 없는 고유 옵션 (경험치, 골드, 속성저항 등)

스킬 슬롯:
- 4개 점진적 해금: Lv1→1슬롯, Lv5→2, Lv15→3, Lv30→4
- 같은 카드 1개만 장착 가능
- 종족별 스킬 유형: Demon=공격스킬, Normal=자기버프, Undead=디버프/방해
```

**작업 내용**
- [ ] `get_cards` (API 2012): 카드 인벤토리 조회
- [ ] `disassemble_card` (API 2013): 카드 분해 → 카드 영혼 획득
- [ ] `level_up_card` (API 2014): 동일 카드 N장 + 카드 영혼 N개 → 레벨업
- [ ] CollectionManager 리팩토링: equip_skill이 Cards 테이블의 카드를 참조하도록 변경
- [ ] 도감 등록 로직 수정: 카드 최초 획득 시 Collections에 기록 (수집 기록만)

---

### Phase 19 — 크래프팅 시스템
**목적**: 대장간 — 매직 장비 + 낙인 + 광석 + 골드 → 크래프트 장비.
**상태**: [ ] 미착수
**의존성**: Phase 18 (재료), Ch1 클리어 해금

**변경 파일**
- `services/rpg/CraftingManager.py` (신규)

**기획 (확정 — equipment_guide.md)**
```
크래프팅 규칙:
- 베이스: 매직 아이템 (접두 OR 접미 하나)
- 낙인: 빈 쪽의 죄종 카테고리 결정
- 결과: 크래프트 등급 (접두+접미 = 5옵션)
- 기존 옵션 유지, 추가된 쪽만 랜덤
- 코스트 = 레어보다 높음 (통제권 프리미엄)
```

**작업 내용**
- [ ] `craft_item` (API 4001): 재료 검증 → 크래프팅 실행 → 아이템 등급 변환
- [ ] 시설 해금 검증 (Ch1 클리어 여부)
- [ ] 낙인 소모 + 광석 소모 + 골드 소모

**기획 확정 대기 항목**
- 크래프팅 광석/골드 소모 공식
- 크래프트 전용 옵션 목록

---

### Phase 20 — NPC 시설 시스템
**목적**: 죄악의 성 NPC 시설. 챕터 클리어마다 시설 해금.
**상태**: [ ] 미착수
**의존성**: Phase 18 (재료)

**변경 파일**
- `services/rpg/ShopManager.py` (신규)
- `services/rpg/QuestManager.py` (신규)

**기획 (확정 — GAME_DESIGN.md)**
| 해금 조건 | 시설 | 기능 |
|----------|------|------|
| Ch1 클리어 | 대장간 | Phase 19에서 구현 |
| Ch2 클리어 | 퀘스트 게시판 | 퀘스트 재료 납품 → 보상 |
| Ch3 클리어 | 상인 | 광석/포션 구매 (골드 소모) |
| Ch4 클리어 | 흔적 조합소 | 흔적 현황 확인, 슬롯 조정 |

**작업 내용**
- [ ] 시설 해금 체크 로직 (챕터 클리어 기반, `unlocked_facilities` 비트마스크)
- [ ] `buy_item` (API 4002): 상인 상품 구매
- [ ] `submit_quest` (API 4003): 퀘스트 재료 납품 → 보상
- [ ] 흔적 조합소 (상세 기획 미확정)

---

### Phase 21 — 장비 분해
**목적**: 불필요 장비 → 광석 + 골드 회수. 광석 순환 루프 완성.
**상태**: [ ] 미착수
**의존성**: Phase 18 (재료 관리)

**변경 파일**
- `services/rpg/InventoryManager.py` (메서드 추가)

**작업 내용**
- [ ] `disassemble_item` (API 2010): 장비 분해 → 광석 + 골드
  - 장착 중 분해 차단
  - 등급별 광석 회수량 차등
  - 레벨 기반 골드 회수

---

### Phase 22 — 세트 보너스 시스템
**목적**: 세트포인트 계산 + 베이직 죄종 선택 + 세트 보너스 전투 적용.
**상태**: [ ] 미착수
**의존성**: Phase 16 (전투 엔진 v2)

**변경 파일**
- `services/rpg/BattleManager.py` (수정 — 세트 보너스 계산)
- `services/system/UserInfoManager.py` (수정 — 베이직 죄종)

**기획 (확정 — equipment_design.md)**
```
세트포인트 구조:
- 접두/접미 각 1포인트 기여 (5슬롯 최대 10포인트)
- 베이직 죄종 선택: 플레이어가 1죄종 선택 → 해당 죄종 +1
- 세트레벨 상한: 7 (초기 구현 5), 장비5+베이직1=6 도달 가능
- 브레이크포인트: 2/4/6 (폭식·오만 제외)
- 2세트 = 챕터 상태이상 부여
- 한 장비에서 같은 죄종 중복 불가

확정된 세트 보너스:
- 분노 2/4/6: 화상 / 잃은체력 비례 공격력 / 최후의 저항(1회 생존+체력40%)
- 시기 2/4/6: 중독 / 적 버프 1개 제거 / 약자멸시(HP30%↓ 방무)
- 색욕 2/4/6: 매혹 / 갈취(적 공방 흡수) / 지배(n% 마법피해 변환)
- 탐욕 2/4/6: 스턴 / 접사 상위 굴림 / 약탈왕(보스 2드롭)
- 폭식: 독립형 (2+부터 스탯 감소 패널티: 2세트-10%, 3세트-20%, 4세트이상-35%)
- 오만 6: 완전무결(상태이상 면역 + 상태이상 적 20% 추가피해)
- 나태 2: 빙결 20% (4/6 미확정)
```

**작업 내용**
- [ ] `select_basic_sin` (API 1006): 베이직 죄종 선택/변경
- [ ] 세트포인트 계산: 장착 장비 접두/접미 + 베이직 죄종
- [ ] 세트 보너스 전투 적용 (Phase 16 전투 엔진에 연동)
- [ ] Redis battle_stats에 세트 정보 포함

**기획 확정 대기 항목**
- 나태 세트 4/6세트 효과
- 오만 세트 2/4세트 (별도 구조 검토 중)

---

### Phase 23 — PVP / 아레나 (엔드콘텐츠)
**목적**: 1:1 실시간 대전. 랭킹 시스템.
**상태**: [ ] 미착수 (엔드콘텐츠)
**의존성**: Phase 16 (전투 엔진 v2)

**기획 (확정)**
```
PVP 규칙:
- 1:1 자동전투, 양측 동시 공격
- 60초 시간 제한 (초과 시 HP% 비교)
- 레벨 보정 없음
- Lv20 이상 참가 가능

아레나:
- 6등급: 청동/은/금/백금/다이아/챔피언
- 시즌제 (시즌 보상)
```

---

### Phase 24 — 연맹 (엔드콘텐츠)
**목적**: 길드 시스템. 공동 버프.
**상태**: [ ] 미착수 (엔드콘텐츠)
**의존성**: Phase 23 이후

**기획 (확정)**
```
연맹:
- 최대 15명
- 연맹 레벨 1~10
- 경험치/골드/드롭률 버프 (전투 스탯 직접 상승 없음)
```

---

## Phase 11 (예정) — 시뮬레이션 도구
**목적**: 기획 밸런싱을 위한 대량 시뮬레이션 CLI 도구. DB/Redis 없이 CSV 메타데이터만으로 독립 실행.
**전제조건**: Phase 16 전투 엔진 v2 완료 후 착수. 아래 기획 항목이 추가 확정되어야 구현 가능.

**3가지 시뮬레이션 모드**

| 모드 | 용도 | 핵심 출력 |
|------|------|----------|
| PVE | 특정 빌드로 특정 몬스터 N회 전투 | 승률, 평균 턴수, DPS, 명중률, 위험구간 |
| PVP | 두 빌드 간 N회 대전 | 승률 비교, 스탯 우위 분석 |
| 드롭 | 특정 몬스터 N킬 드롭 분포 | 등급별 장비 수, 기대 파밍 횟수 |

**구현 전 확정 필요 항목**

| 항목 | 영향 모드 | 현재 상태 |
|------|----------|----------|
| 몬스터 레벨 정의 | PVE/PVP | 미정 |
| 몬스터 명중/회피 값 | PVE | 미정 |
| 몬스터 크리티컬 여부 | PVE | 미정 |
| 접미사(suffix) CSV | PVE/PVP/드롭 | 미작성 |
| PVP 전용 규칙 | PVP | 미정 |
| 방어구 base_def 수치 | PVE/PVP | 미정 |
| 골드 드롭량 공식 | 드롭 | 미정 |
| 기타(카드/재료) 드롭 상세 | 드롭 | 미정 |

---

## 데이터베이스 설계

> 기획서 GAME_DESIGN.md 기반

### Users (유저 계정)

| 컬럼 | 타입 | 키 | 설명 | 상태 |
|------|------|-----|------|------|
| user_no | BIGINT | PK | 계정 고유 번호 (자동 증가) | ✅ 구현 |
| user_name | VARCHAR(50) | Unique | 유저 닉네임 | ✅ 구현 |
| password_hash | VARCHAR(255) | | bcrypt 해싱된 비밀번호 | ✅ 구현 |
| gold | BIGINT | | 보유 재화 | ✅ 구현 |
| current_stage | INT | | 진행 중인 최고 스테이지 | ✅ 구현 |
| max_inventory | INT | | 인벤토리 최대 칸 수 (기본 100) | ✅ 구현 |
| basic_sin | VARCHAR(20) | | 베이직 죄종 선택 (Nullable) | Phase 13 |
| unlocked_facilities | INT | | 해금 시설 비트마스크 | Phase 13 |
| created_at | DATETIME | | 계정 생성일 | ✅ 구현 |

### UserStats (캐릭터 스탯)

| 컬럼 | 타입 | 키 | 설명 | 상태 |
|------|------|-----|------|------|
| user_no | BIGINT | PK/FK | 소유자 (Users 참조, 1:1) | ✅ 구현 |
| level | INT | | 캐릭터 레벨 (최대 50) | ✅ 구현 |
| exp | BIGINT | | 누적 경험치 | ✅ 구현 |
| stat_points | INT | | 잔여 스탯 포인트 | ✅ 구현 |
| stat_str | INT | | 힘 (공격력 +0.5%/pt) | ✅ 구현 |
| stat_dex | INT | | 민첩 (공속 +0.3%, 명중 +5/pt) | ✅ 구현 |
| stat_vit | INT | | 체력 (HP +10/pt) | ✅ 구현 |
| stat_luck | INT | | 운 (치확 +5, 회피 +5/pt) | ✅ 구현 |
| stat_cost | INT | | 코스트 (최대코스트 +2/pt) | ✅ 구현 |

### Items (장비 인스턴스)

| 컬럼 | 타입 | 키 | 설명 | 상태 |
|------|------|-----|------|------|
| item_uid | VARCHAR(36) | PK | UUID | ✅ 구현 |
| user_no | BIGINT | FK | 소유자 | ✅ 구현 |
| base_item_id | INT | | equipment_base 메타데이터 참조 | ✅ 구현 |
| item_level | INT | | 장비 레벨 = ilvl (드롭 몬스터 mlvl) | ✅ 구현 |
| rarity | VARCHAR(20) | | magic / rare / craft / unique | ✅ 구현 |
| item_score | INT | | 몬스터 킬 점수 기반 품질 | ✅ 구현 |
| item_cost | INT | | 계산된 코스트 값 | ✅ 구현 |
| prefix_id | VARCHAR(50) | | 접두사 ID (Nullable) | ✅ 구현 |
| suffix_id | VARCHAR(50) | | 접미사 ID (Nullable) | ✅ 구현 |
| set_id | VARCHAR(50) | | 7죄종 세트 ID (Nullable) | ✅ 구현 |
| dynamic_options | JSON | | 랜덤 부여 스탯 | ✅ 구현 |
| is_equipped | BOOLEAN | | 장착 여부 (인덱스 필수) | ✅ 구현 |
| equip_slot | VARCHAR(20) | | 장착 부위 (장착 시만 존재) | ✅ 구현 |

### Collections (도감 — 수집 기록)

| 컬럼 | 타입 | 키 | 설명 | 상태 |
|------|------|-----|------|------|
| user_no | BIGINT | PK/FK | 소유자 (복합 PK) | ✅ 구현 |
| monster_idx | INT | PK | 몬스터 종류 (복합 PK) | ✅ 구현 |
| card_count | INT | | 누적 획득 카드 수 | ✅ 구현 |
| collection_level | INT | | ~~도감 레벨~~ → 미사용 (도감 레벨업 폐기) | ✅ 구현 (리팩토링 예정) |
| skill_slot | INT | | ~~스킬슬롯~~ → Cards 테이블로 이관 예정 | ✅ 구현 (리팩토링 예정) |

### Cards (카드 인벤토리) — Phase 13 신규

| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| card_uid | VARCHAR(36) | PK | UUID |
| user_no | BIGINT | FK | 소유자 |
| monster_idx | INT | | 몬스터 종류 (card_skill.csv 참조) |
| card_level | INT | | 카드 레벨 (기본 1) |
| card_stats | JSON | | 랜덤 부여 수치 (드롭 시 결정) |
| is_equipped | BOOLEAN | | 스킬 슬롯 장착 여부 |
| skill_slot | INT | nullable | 장착된 스킬 슬롯 (1~4) |
| created_at | DATETIME | | 획득 시각 |

### BattleSessions (전투 세션) — Phase 13 신규

| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| user_no | BIGINT | PK/FK | 소유자 |
| stage_id | INT | | 현재 스테이지 |
| current_wave | INT | | 현재 웨이브 (1~4) |
| current_hp | INT | | 현재 HP |
| max_hp | INT | | 최대 HP |
| pending_drops | JSON | | 웨이브 내 드롭 임시 저장 |
| wave_kills | JSON | | 웨이브별 처치 기록 |
| started_at | DATETIME | | 세션 시작 시각 |

### Materials (재료 아이템) — Phase 13 신규

| 컬럼 | 타입 | 키 | 설명 |
|------|------|-----|------|
| id | BIGINT | PK | 자동 증가 |
| user_no | BIGINT | FK | 소유자 |
| material_type | VARCHAR(20) | | potion / ore / stigma / quest_material / card_soul |
| material_id | INT | | 메타데이터 참조 |
| amount | INT | | 수량 (스택 가능) |

---

## 클라이언트 개발 현황

> 상세 내용은 [CLIENT_DEV_PLAN.md](CLIENT_DEV_PLAN.md) 참조.
> 구조 개편 완료: 좌우 분할 5탭 구조 (Phase C8~C14 완성, C16 통합테스트 미착수).

---

## 미결정 기획 항목 (개발 전 확정 필요)

### 확정 완료 ✅ (Phase에 반영됨)
| 항목 | 반영 Phase | 비고 |
|------|-----------|------|
| ~~경험치 곡선~~ | Phase 12 | 기준10, ×1.3/×2.0 확정 |
| ~~데미지 공식~~ | Phase 16 | ATK×(1-방감)×사이즈×치명타 확정 |
| ~~몬스터 XP 배율~~ | Phase 12 | 1x/3x/10x/20x 확정 |
| ~~상태이상 7종~~ | Phase 16 | 화상/중독/스턴/빙결/침식/매혹/심판 + 지속시간/효과 확정 |
| ~~세트 보너스~~ | Phase 22 | 분노/시기/색욕/탐욕/폭식/오만 확정 |
| ~~경직 시스템~~ | Phase 16 | 조건(단타>HP÷10) + 둔기 추가 + FHR 확정 |
| ~~정예 특성~~ | Phase 15 | 죄종 7종 + 공통 16종 확정 |
| ~~방치 파밍~~ | Phase 12.5 | 기획에서 완전 제거 (2026-03-17) |
| ~~카드=인벤토리 아이템~~ | Phase 18.5 | 수치랜덤, 분해→영혼, 레벨업 확정 |
| ~~ilvl/mlvl/dlvl 체계~~ | Phase 17 | D2 구조, mlvl 보정 확정 |
| ~~사망 패널티~~ | Phase 14 | 현재 레벨 내 경험치 10% 차감 확정 |
| ~~스킬 트리거 7종~~ | Phase 16 | on_attack/on_hit 등 7종 확정 |
| ~~PVP 기본 규칙~~ | Phase 23 | 1:1 자동, 60초, Lv20+, 6등급 확정 |
| ~~연맹~~ | Phase 24 | 최대 15명, 버프형 확정 |

### 미확정 (기획 필요)
| 항목 | 영향 Phase | 비고 |
|------|-----------|------|
| dlvl 스테이지별 배분 수치 | Phase 17 | 3안 중 선택 필요 (A-동행 / B-선형 / C-계단) |
| mlvl별 등급 드롭 확률 테이블 | Phase 17 | 미기획 |
| 접사 qlvl 체계 | Phase 17 | 미기획 |
| 골드 드롭 공식 | Phase 17 | 미기획 |
| 카드 드롭률 수치 | Phase 17 | 일반 vs 보스 차등, 미기획 |
| 낙인 드롭률 수치 | Phase 17 | 미기획 |
| 포션 종류/효과/가격/지참 제한 | Phase 18 | 밸런싱 시 확정 |
| 광석 등급 계층/합성 비율 | Phase 18 | 미기획 |
| 카드 레벨업 소모량 (동일카드 N장, 영혼 N개) | Phase 18.5 | 미기획 |
| 크래프팅 광석/골드 소모 공식 | Phase 19 | 미기획 |
| 크래프트 전용 옵션 목록 | Phase 19 | 미기획 |
| 퀘스트 재료 종류/NPC 보상 | Phase 20 | 미기획 |
| 장비 분해 광석 회수량 | Phase 21 | 미기획 |
| 나태 세트 4/6세트 | Phase 22 | 미확정 |
| 오만 세트 2/4세트 | Phase 22 | 별도 구조 검토 중 |
| 코스트 등급배율 세부 수치 | Phase 16 | 시뮬레이션 후 튜닝 |
| 유니크 고정 효과 설계 | Phase 17 | 미기획 |
| 방어구 base_def 수치 | Phase 16 | 미기획 |
| 정예 특성 수치 밸런싱 | Phase 15 | 시뮬레이션 후 튜닝 |
| 나태 죄종 접사 (무기/신발) | Phase 16 | 미확정 |
| 신발 공통 옵션풀 | Phase 16 | 미확정 |
| 도감 그룹 보너스 재설계 | Phase 18.5 | 기존 방식 폐기, 새 기준 미확정 |
| 마일스톤 레벨 보상 | Phase 12 보완 | Lv10/20/40/50 보너스 미확정 |
| Ch5~Ch7 몬스터 인스턴스 | Phase 15+ | 미설계 |
| Ch2~Ch7 카드 스킬 매칭 | Phase 16 | Ch1만 확정 (17종) |

---

## 기존 코드 vs 기획 불일치 (수정 추적)

| 위치 | 불일치 내용 | 해결 Phase |
|------|-----------|-----------|
| ~~`StageManager._generate_monster_pool`~~ | ~~[normal4+elite1]×3=16마리 → 기획 [3+1]×3+보스=13마리~~ | ✅ 2026-03-18 수정 완료 |
| ~~`IdleFarmManager.py`~~ | ~~기획 제거됨, 코드 존재~~ | ✅ Phase 12.5 완료 |
| ~~`APIManager.py` 3005/3006~~ | ~~삭제 대상 API 등록 중~~ | ✅ Phase 12.5 완료 |
| ~~`UserInfoManager.get_user_info`~~ | ~~idle_farm Redis 참조 코드~~ | ✅ Phase 12.5 완료 |
| `ItemDropManager.process_kill` | DB 미저장 (클라이언트 신뢰) | Phase 17 |
| `CollectionManager` | 도감 레벨업 전제 설계 + 스킬슬롯 | Phase 18.5 |
| `Collections.collection_level` | 도감 레벨업 폐기됨, 컬럼 미사용 | Phase 18.5 |
| `User.current_stage` default=101 | stage_id 1~21 범위와 불일치 가능성 | Phase 14에서 검증 |

---

*마지막 업데이트: 2026-03-18*
