# TheSevenRPG 코드 감사 보고서

> 작성일: 2026-03-17
> 감사 범위: 서버 전체 Manager, CSV 메타데이터, 기획-코드 정합성, Phase 13-14 계획

---

## 1. 코드 리뷰 & 버그 헌팅

### 전체 요약

| 파일 | 심각 | 주의 | 주요 이슈 |
|------|------|------|-----------|
| BattleManager.py | 2 | 3 | spawn_type 클라이언트 조작 → 보상 20배; 스테이지 입장 검증 없음 |
| ItemDropManager.py | 3 | 2 | 아이템 DB 미저장; field_level 조작 가능 |
| StageManager.py | 1 | 3 | Redis 장애 시 clear_stage 우회 → 무한 해금 |
| UserInfoManager.py | 1 | 1 | reset_stats 커밋 후 DetachedInstanceError |
| InventoryManager.py | 0 | 3 | equip 조기 리턴 시 명시적 커밋/롤백 없음 |
| IdleFarmManager.py | 0 | 3 | 기획 제거됐으나 코드 잔존; 골드 중복 획득 가능 |
| CardManager.py | 0 | 3 | slot_number 타입 미변환; 헬퍼 자체 세션 생성 |
| UserInitManager.py | 0 | 3 | bcrypt 이벤트 루프 블로킹 |
| GameDataManager.py | 0 | 3 | 드롭 확률 등 내부 데이터 클라이언트 전체 노출 |
| models.py | 0 | 2 | 스탯 default=10 vs 리셋=5; is_equipped/equip_slot 중복 |
| main.py | 0 | 2 | deprecated startup 패턴 |
| SessionManager.py | 0 | 1 | 다중 세션 무한 생성 |
| APIManager.py | 0 | 0 | 이슈 없음 |
| ErrorCode.py | 0 | 0 | 이슈 없음 |
| database.py | 0 | 0 | 이슈 없음 |
| **합계** | **7** | **29** | |

### 우선 수정 TOP 5

1. **[BattleManager] spawn_type 서버 결정** — 클라이언트가 "챕터보스" 등급을 지정하면 경험치/골드 20배 획득 가능. 서버가 스테이지/웨이브 상태에서 등급을 결정해야 한다.
2. **[ItemDropManager] 아이템 DB 저장 + 클라이언트 값 불신** — 드롭 아이템이 DB에 저장되지 않고 클라이언트에 반환만 됨. field_level 등을 클라이언트가 지정하므로 아이템 생성이 완전히 클라이언트 의존적.
3. **[StageManager] Redis 장애 시 clear_stage 차단** — Redis 장애 시 입장 검증을 건너뛰므로 무한 스테이지 해금 가능.
4. **[UserInfoManager] reset_stats DetachedInstanceError** — 커밋 후 닫힌 세션에서 ORM 속성 접근 시 런타임 에러.
5. **[models.py + UserInfoManager] 스탯 초기값 불일치** — models.py default=10 vs INITIAL_STAT_VALUE=5 → 리셋하면 스탯 절반 감소.

### 상세 — BattleManager.py

**심각:**
- `battle_result`에 스테이지 입장 검증 없음. 클라이언트가 임의의 `monster_idx`와 `spawn_type`을 보내면 아무 몬스터든 전투 가능.
- `spawn_type`을 클라이언트가 자유롭게 지정. 일반 몬스터에 "챕터보스" 등급을 넣으면 경험치/골드 20배 획득.

**주의:**
- `_load_battle_stats`, `_grant_rewards`에서 동기 DB 쿼리를 async 메서드 내에서 직접 호출 → 이벤트 루프 블로킹. `asyncio.to_thread()` 권장.
- `_load_battle_stats`와 `_grant_rewards`가 별도 세션을 열어 동시 전투 시 레벨/경험치 꼬일 가능성.
- `base_wpn_atk = 10.0`, `base_wpn_aspd = 1.0` 등 매직 넘버 상수화 권장.

### 상세 — ItemDropManager.py

**심각:**
- `process_kill`이 DB에 아이템을 저장하지 않음. 드롭 결과를 계산해서 클라이언트에 반환만.
- `spawned_level`, `spawned_grade`, `field_level`을 모두 클라이언트에서 수신. 서버 검증 없이 스코어 계산에 사용.
- `rarity_config` fallback 시 "normal" 키가 존재하지 않을 수 있음.

**주의:**
- `_roll_weighted`에 빈 리스트 입력 시 ValueError 발생 가능.
- DB 트랜잭션 없음 (현재는 순수 계산이라 영향 없으나, DB 저장 추가 시 필수).

### 상세 — StageManager.py

**심각:**
- `clear_stage`에서 Redis `stage_progress` 검증 실패 시 경고만 출력하고 계속 진행. `enter_stage` 없이 `clear_stage` 직접 호출로 무한 해금 가능.

**주의:**
- `stage_id` 타입 검증 없음.
- `_generate_monster_pool`에서 `chapter_monster_pool.csv`를 활용하지 않고 전체 풀에서 랜덤 선택.

### 상세 — UserInfoManager.py

**심각:**
- `reset_stats` 응답 반환 시 `db.close()` 이후 ORM 속성 접근 → `DetachedInstanceError` 발생 가능. `db.commit()` 전에 결과값을 로컬 변수에 저장해야 함.

**주의:**
- `INITIAL_STAT_VALUE = 5` vs `models.py` default=10 불일치.

### 상세 — InventoryManager.py

**주의:**
- `equip_item`에서 이미 장착 중이면 `success: True` 반환하는데 명시적 commit/rollback 없이 세션 종료.
- `SELL_PRICE_TABLE`에 "normal" 없음. fallback 30이 의도적인지 불명확.

### 상세 — IdleFarmManager.py

**주의:**
- 기획에서 완전 제거 결정됐으나 코드 잔존 + API 등록 상태.
- Redis `idle_farm` 키에 TTL 미설정 → 메모리 영구 잔류.
- `collect_idle`에서 골드 지급(DB commit) 후 타이머 리셋(Redis) 실패 시 골드 중복 획득.

### 상세 — CardManager.py

**주의:**
- `equip_skill`에서 `slot_number`가 문자열 "1"이면 `(1,2,3,4)` 비교를 통과하지 못함. `int()` 변환 필요.
- `register_card`가 `db=None`일 때 자체 세션 생성 — convention 위반.
- `register_card` 에러 시 `None` 반환. 호출부에서 누락 시 조용히 실패.

### 상세 — UserInitManager.py

**주의:**
- `bcrypt` 해싱이 async 내에서 동기 실행 → 이벤트 루프 블로킹. `asyncio.to_thread()` 권장.
- `create_new_user` 시그니처에 사용하지 않는 `user_no` 인자 (게이트웨이 패턴상 불가피).
- 초기 무기 `rarity="normal"` — 기획에서 일반 등급 제거됨.

### 상세 — GameDataManager.py

**주의:**
- `get_all_configs`가 `REQUIRE_CONFIGS` 전체를 클라이언트에 반환. 드롭 확률, 스코어 설정 등 내부 데이터 노출.
- 필수 CSV 없어도 빈 리스트 반환 + 경고만. 필수 데이터(monsters 등)는 예외 발생 권장.

### 상세 — main.py

**주의:**
- `on_event("startup"/"shutdown")` deprecated. `lifespan` 컨텍스트 매니저 권장.
- Rate limiter가 `get_remote_address` 기반. 프록시 뒤에서 전체 트래픽에 limit 걸릴 수 있음.

### 상세 — models.py

**주의:**
- `UserStat` 스탯 default=10 vs `UserInfoManager.INITIAL_STAT_VALUE=5`. 리셋 시 스탯 감소.
- `is_equipped`와 `equip_slot` 중복. `equip_item`/`unequip_item`에서 `is_equipped`를 변경하지 않아 불일치 위험.

### 상세 — SessionManager.py

**주의:**
- 동일 유저 다중 로그인 시 이전 세션 미삭제. 세션 무한 생성 가능.

---

## 2. CSV 메타데이터 정합성 검증

### 검증 결과 요약

| CSV 파일 | 행 수 | 결과 | 발견 이슈 |
|----------|-------|------|----------|
| monster_info | 94 | 정상 | |
| monster_drop_equipment | 48 | 정상 | |
| monster_drop_config | 4 | 정상 | |
| equipment_base | 39 | 정상 | |
| equipment_prefix | 35 | 정상 | |
| equipment_suffix | 35 | 정상 | |
| equipment_common_option | 70 | 정상 | |
| equip_rarity_config | 4 | 정상 | |
| chapter_info | 7 | 정상 | |
| stage_info | 28 | 정상 | |
| chapter_monster_pool | 42 | 정상 | |
| level_exp_table | 50 | 정상 | |
| spawn_grade_config | 4 | 정상 | |
| collection_group_bonus | 20 | 정상 | |
| elite_trait | 23 | 정상 | |
| status_effect | 7 | 정상 | |
| equipment_set_bonus | 17 | 경고 | 3개 세트 불완전 (오만/폭식/나태) |
| collection_group | 22 | 경고 | Ch2~7 보스 스테이지 6건 누락 |
| card_skill | 16 | 경고 | Ch1만 존재 |
| equipment_unique | 0 | 경고 | 빈 파일 (헤더만) |
| moster_score_config | 4 | 경고 | 파일명 오타 |

### 참조 무결성: 깨짐 없음

모든 CSV 간 FK 참조 100% 일치. 확률 합산, 수치 범위, PK 중복 등 모두 정상.

### 데이터 이상 (확인 필요)

**1. 파일명 오타: `moster_score_config.csv`**
- `monster_score_config.csv`가 올바른 이름
- GameDataManager 코드에서도 `moster`로 참조하므로 동작은 하지만, 양쪽 수정 필요

**2. GameDataManager 미로드 CSV 8개**
- `equipment_suffix`, `equipment_common_option`, `equipment_set_bonus`, `card_skill`, `collection_group`, `collection_group_bonus`, `elite_trait`, `status_effect`
- 해당 기능 구현(Phase 15~22) 시 GameDataManager에 추가 필요

**3. Ch2~7 데이터 미입력**
- card_skill: Ch1 16건만 존재
- collection_group: Ch1만 보스 스테이지 그룹 존재, Ch2~7 누락
- 기획 확정 후 채워야 함

**4. 불완전 세트 보너스**
- 오만(pride): 6세트만 존재
- 폭식(gluttony): 2세트만 존재
- 나태(sloth): 4/6세트 pending
- 기획 미확정 상태와 일치

**5. equipment_unique.csv 빈 파일**
- 헤더만 존재, 데이터 0건. 유니크 장비 데이터 미입력 상태.

---

## 3. 기획 문서 ↔ 코드 불일치 분석

### 수치 불일치 (코드 수정 필요)

| 항목 | 기획서 값 | 코드 값 | 위치 | 비고 |
|------|----------|---------|------|------|
| 스탯 초기값 | 각 **5** | models.py default=**10** | models.py:42-46 | 리셋 시 스탯 절반 감소 버그 |
| ATK 공식 | 합연산 `(1+힘×0.005+아이템%)` | 곱연산 `(1+힘%)×(1+아이템%)` | BattleManager.py:201 | 곱연산이면 아이템% 효과 과대 |
| Acc 공식 | `(민첩×5+아이템명중)×0.001` | `dex*0.005+i_acc` | BattleManager.py:203 | 아이템에 ×0.001 미적용 → 1000배 과대 |
| Eva 공식 | `(운×5+아이템회피)×0.001` | `luck*0.001+i_eva` | BattleManager.py:204 | 운×5 아닌 운×1, 아이템 ×0.001 미적용 |
| 치명타확률 | `(운×5+아이템치확)×0.001` | `luck*0.001+i_crit_ch` | BattleManager.py:205 | Eva와 동일 문제 |
| 초기 무기 rarity | 일반 등급 제거, "magic" 최저 | `rarity="normal"` | UserInitManager.py:102 | 기획 변경 미반영 |

### 기능 불일치 (확인 필요)

| 항목 | 기획서 | 코드 상태 | 비고 |
|------|--------|----------|------|
| 방치 파밍 | 기획에서 **완전 제거** | IdleFarmManager 존재 + API 등록 | 코드 정리 필요 |
| 웨이브 구조 | [일반3+정예1]×3+보스1=**13마리** | 코드는 **16마리** (구 기획) | StageManager 개편 필요 |
| 도감 레벨 상한 | 3단계 (Lv1/2/3) | models.py/DEV_PLAN "1~5" | 기획 변경 미반영 |
| 치명타데미지 | `1.5+아이템치뎀` (운 무관) | `1.5+luck*0.003+아이템` | 코드에 운 영향 추가됨 |
| 몬스터 레벨 | 미확정 | `m_level=p_level` 고정 | LvDiff 항상 0 |
| CollectionManager 파일명 | DEV_PLAN: CollectionManager.py | 실제: CardManager.py | 파일명 불일치 |

### 일치 확인됨

- 최대 레벨(50), HP 공식, 방어감소율, 명중률 클램프(5~95%)
- 코스트 공식, 스킬슬롯 해금, 장비 5슬롯
- 경험치 커브 구조, 그라인드 시작 레벨(40)
- 챕터 수/스테이지 수, 챕터 보스 해금 조건

---

## 4. Phase 13-14 구현 계획 초안

### Phase 13 — DB 모델 확장

**목적**: Phase 14~22에 필요한 신규 테이블/컬럼 선행 추가
**작업 유형**: 신규 개발
**변경 파일**: `models.py` (수정)

#### 추가 항목

| 항목 | 내용 |
|------|------|
| User 컬럼 | `basic_sin` (Phase 22용), `unlocked_facilities` 비트마스크 (Phase 20용) |
| BattleSession 테이블 | user_no(PK), stage_id, current_wave, current_hp, max_hp, pending_drops(JSON), wave_kills(JSON), monster_queue(JSON), started_at, updated_at |
| Material 테이블 | id(PK), user_no(FK), material_type, material_id, amount + UniqueConstraint |

#### BattleSession 설계 근거

- **PK = user_no**: 유저당 활성 세션 최대 1개
- **monster_queue 추가** (DEV_PLAN에 없음): 귀환 후 재접속 시 웨이브 내 진행 복원에 필수
- **updated_at 추가**: 세션 만료 처리(24시간 방치) 용도

#### DB 마이그레이션 이슈

- Alembic 미사용 중 → `create_all()`은 기존 테이블에 컬럼 추가 불가
- 권장: 개발 단계 DB 재생성 + 향후 Alembic 도입 검토

---

### Phase 14 — 웨이브/체크포인트 시스템

**목적**: 스테이지 런을 4웨이브 체크포인트 구조로 전면 개편
**작업 유형**: 신규 개발 + 기존 코드 대폭 개편
**의존성**: Phase 13 (BattleSession 테이블)

#### API 변경 요약

| API | 변경 | 하위 호환 |
|-----|------|----------|
| 3001 (battle_result) | 입력에서 monster_idx **제거** (서버가 큐에서 pop), 출력에 session 블록 추가 | 깨짐 |
| 3003 (enter_stage) | BattleSession 생성, 웨이브1 몬스터만 반환 | 깨짐 |
| 3004 (clear_stage) | battle_result 내부에서 자동 처리 권장 | 동작 변경 |
| 3007 (신규) | return_to_town — HP 보존 귀환, 세션 유지 | N/A |
| 3008 (신규) | get_battle_session — 재접속 시 진행 복구 | N/A |

#### 어뷰징 방지 설계

| 위협 | 방어 | 구현 위치 |
|------|------|----------|
| monster_idx 조작 | 클라이언트가 보내지 않음. 서버가 큐에서 pop | BattleManager |
| spawn_type 조작 | 서버가 웨이브 구성에서 결정 | StageManager |
| HP 조작 | 서버에서만 관리 (BattleSession.current_hp) | BattleManager |
| BattleSession 없이 호출 | 존재 여부 필수 검증 | BattleManager |
| 웨이브 순서 건너뛰기 | monster_queue 비어야 다음 웨이브 | StageManager |
| 동시 전투 Race Condition | with_for_update() 행 잠금 | BattleManager |

#### 사망 처리

1. 경험치 5% 차감 (최소 0)
2. 현재 웨이브 몬스터 큐 리셋 (웨이브 처음부터)
3. HP 전량 회복
4. pending_drops 유지
5. wave_kills 현재 웨이브만 초기화

#### Redis 캐시 전략

- `stage_progress` Redis 키 **폐기** → BattleSession DB로 대체
- `battle_stats` 캐시는 유지 (스탯 계산 읽기 전용)
- BattleSession 자체는 DB only (매 전투 UPDATE 필수이므로 Redis 캐싱 불필요)

#### 결정 필요 사항 (구현 전 확인)

| 항목 | 내용 |
|------|------|
| stage_id 체계 통일 | current_stage(1~21) vs stage_info.csv(101~704) 매핑 |
| 귀환 시 웨이브 내 진행 | 웨이브 처음부터? 남은 몬스터부터? |
| clear_stage API 유지 | 별도 API vs battle_result 내부 처리 |
| DB 마이그레이션 | Alembic 도입 여부 |
| pending_drops 지급 타이밍 | 웨이브 클리어 시? 귀환 시? 스테이지 완료 시? |
| 동일 스테이지 재입장 시 기존 세션 | 파기? 이어서? |
| 챕터 보스 스테이지 웨이브 구조 | 일반 스테이지와 다른 구성 |

---

*이 보고서는 코드 감사 자동 분석 결과입니다. 기획 의도와 다른 부분이 있을 수 있으니 확인 후 반영하세요.*
