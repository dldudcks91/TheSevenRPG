# TheSevenRPG — 서버 로깅 정책

> 작성일: 2026-03-18
> 상태: 검토 완료, 미적용 (코드 수정은 추후 진행)

---

## 1. 로그 레벨 기준

| 레벨 | 기준 | 예시 |
|------|------|------|
| **ERROR** | 코드가 예상하지 못한 실패. except 블록 진입 | DB 쿼리 실패, Redis 장애, 예외 발생 |
| **WARNING** | 코드는 정상이지만 운영자가 알아야 할 상황 | 캐시 무효화 실패(폴백 동작), Rate Limit 초과, 반복 로그인 실패 |
| **INFO** | 비즈니스 이벤트. "무엇이 변했는가"의 기록 | 골드 변동, 아이템 드롭, 레벨업, 장비 장착, 스테이지 클리어 |
| **DEBUG** | 개발/디버깅용 상세. 운영 시 꺼도 무방 | 캐시 히트/미스, 전투 시뮬레이션 턴 상세, 드롭 확률 계산 과정 |

**핵심 원칙**: 비즈니스 에러(골드 부족, 슬롯 불일치 등)는 ERROR가 아닌 INFO. 유저의 정상적인 실패 시도이므로 에러가 아님.

---

## 2. 필수 기록 이벤트

### 2-1. 자원 변동 (INFO)

유저의 재화/자산이 변하는 모든 순간을 기록한다.

| 이벤트 | Manager | 기록할 값 |
|--------|---------|----------|
| 골드 획득 (전투) | BattleManager | user_no, +amount, total |
| 골드 소비 (리셋/확장/강화) | UserInfoManager, InventoryManager, EnhanceManager | user_no, -amount, reason, total |
| 골드 획득 (판매) | InventoryManager | user_no, +amount, item_uid, rarity, total |
| 경험치 획득 | BattleManager | user_no, +amount, total |
| 레벨업 | BattleManager | user_no, old_lv → new_lv, +stat_points |
| 아이템 생성 (드롭) | ItemDropManager | user_no, monster_idx, rarity, equip_type |
| 아이템 삭제 (판매) | InventoryManager | user_no, item_uid, rarity |
| 스탯 리셋 | UserInfoManager | user_no, cost, returned_points |
| 인벤 확장 | InventoryManager | user_no, cost, new_max |

### 2-2. 상태 전이 (INFO)

| 이벤트 | Manager | 기록할 값 |
|--------|---------|----------|
| 장비 장착 | InventoryManager | user_no, item_uid, slot, cost_used/cost_max |
| 장비 해제 | InventoryManager | user_no, item_uid, slot |
| 스킬 장착/해제 | CardManager | user_no, monster_idx, slot |
| 스테이지 입장 | StageManager | user_no, stage_id |
| 스테이지 클리어 | StageManager | user_no, stage_id, next_stage |
| 도감 등록 | CardManager | user_no, monster_idx, card_count |

### 2-3. 인증/접속 (INFO / WARNING)

| 이벤트 | Manager | 기록할 값 | 레벨 |
|--------|---------|----------|------|
| 회원가입 | UserInitManager | user_no, user_name | INFO |
| 로그인 성공 | UserInitManager | user_no | INFO |
| 로그인 실패 | UserInitManager | user_name | WARNING |
| 세션 만료 | main.py | api_code | WARNING |

### 2-4. API 게이트웨이 (INFO)

| 이벤트 | 위치 | 기록할 값 |
|--------|------|----------|
| API 요청 | main.py | user_no, api_code |
| API 응답 | main.py | user_no, api_code, success 여부, 처리시간(ms) |

### 2-5. 시스템 (WARNING / ERROR)

| 이벤트 | 레벨 | 기록할 값 |
|--------|------|----------|
| 캐시 무효화 실패 | WARNING | user_no, cache_key |
| Redis 장애 폴백 | WARNING | 영향 API |
| DB 예외 | ERROR | api_code, user_no, exc_info |
| 미등록 API 호출 | WARNING | api_code |

---

## 3. 포맷

### 3-1. 기본 포맷 (logger.py)

```
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
```

출력 예시:
```
[2026-03-18 14:30:05] [INFO] [RPG_SERVER] [BattleManager] user=123 level_up lv=9→10 stat_points=+5
```

### 3-2. 메시지 작성 규칙

모든 Manager의 `%(message)s` 부분을 아래 규칙으로 통일한다.

**구조:**
```
[Manager명] user={user_no} {동작} {key=value 쌍들}
```

**규칙:**
- `[Manager명]` 항상 먼저
- `user=N` 항상 두 번째 (누구의 이벤트인지)
- 동작은 영문 단어 (`sell`, `equip`, `clear`, `level_up`)
- 추가 정보는 `key=value` 형식
- 자원 변동은 `+/-` 부호 + `(total=N)` 잔액 표기
- 한 메서드에서 여러 자원 변동 시 한 줄에 모두 포함

### 3-3. 유형별 포맷 예시

**자원 변동:**
```
[BattleManager] user=123 reward exp=+120(total=980) gold=+15(total=8215) monster=skeleton_warrior
[InventoryManager] user=123 sell item_uid=456 rarity=rare gold=+1500(total=8200)
[UserInfoManager] user=123 reset_stats gold=-1000(total=7215) returned_points=25
[InventoryManager] user=123 expand gold=-500(total=6715) max_inventory=110
```

**상태 전이:**
```
[InventoryManager] user=123 equip item_uid=456 slot=weapon cost=12/15
[InventoryManager] user=123 unequip item_uid=456 slot=weapon
[CardManager] user=123 equip_skill monster_idx=201 slot=2
[StageManager] user=123 enter stage=201
[StageManager] user=123 clear stage=201 next=202
[CardManager] user=123 register_card monster_idx=201 card_count=3
```

**인증:**
```
[UserInitManager] user=123 signup user_name=홍길동
[UserInitManager] user=123 login
[UserInitManager] login_failed user_name=홍길동
```

**API 게이트웨이:**
```
[API] user=123 api_code=3001 request
[API] user=123 api_code=3001 response success=true elapsed=45ms
```

**에러:**
```
[BattleManager] user=123 battle_result 실패: {에러 메시지}
  Traceback (exc_info=True로 자동 포함)
```

---

## 4. 파일 정책

### 현재 (변경 전)

| 파일 | 레벨 | 보관 |
|------|------|------|
| `rpg_server.log` | WARNING+ | 7일 |
| 콘솔 | INFO+ | - |

### 변경 후

| 파일 | 레벨 | 용도 | 로테이션 | 보관 |
|------|------|------|----------|------|
| `rpg_server.log` | **INFO+** | 전체 로그 (비즈니스 + 에러) | 일일 자정 | **14일** |
| `rpg_error.log` | **ERROR+** | 에러만 분리 (빠른 확인용) | 일일 자정 | **30일** |
| 콘솔 | INFO+ | 실시간 모니터링 | - | - |

**변경 포인트:**
- `rpg_server.log`: WARNING+ → **INFO+** (비즈니스 이벤트 보존)
- `rpg_error.log`: 신규 추가 (에러만 빠르게 확인)
- 보관 기간: 전체 14일, 에러 30일

**용량 추정:**
- INFO 포함 시 약 5~10MB/일 예상
- 14일 보관 = 최대 140MB → 서버 용량 문제 없음

---

## 현재 로깅 현황 (문제점)

### Manager별 성공 로그 현황

| Manager | 성공 로그 | 실패 로그 | 평가 |
|---------|----------|----------|------|
| main.py (게이트웨이) | 요청 시작만 | O | 응답 결과 안 남음 |
| UserInitManager | 가입/로그인 성공 | O | 검증 실패 안 남음 |
| InventoryManager | **없음** | O | 장착/판매/확장 성공 전혀 안 남음 |
| BattleManager | 레벨업만 | O | 전투 결과/경험치/골드 획득 안 남음 |
| ItemDropManager | **없음** | O | 드롭 결과 완전 미기록 |
| StageManager | **없음** | O | 입장/클리어 성공 안 남음 |
| CardManager | **없음** | O | 도감 등록/스킬 장착 안 남음 |

### 로그로 답할 수 없는 질문들

- "유저 123의 골드가 왜 줄었지?" → 판매/리셋/확장 로그 없음
- "드롭이 안 나왔다는 민원" → 드롭 결과 로그 없음
- "어제 전투 몇 번 해서 몇 레벨 올랐나?" → 전투 결과 로그 없음
- "이 API 호출이 성공했나 실패했나?" → 응답 로그 없음

---

## 저장 방식 결정

- **현재 규모**: 로컬 파일 저장 (Python logging + TimedRotatingFileHandler)
- **OS 파일 버퍼 활용**: write() 시스템 콜 → 커널 페이지 캐시 → OS가 비동기로 디스크 쓰기
- **QueueHandler**: 현재 불필요, 초당 수천 건 이상 시 도입 검토
- **외부 로그 서비스**: 서비스 규모 확대 시 ELK Stack 또는 클라우드 로그 서비스 연동 검토
