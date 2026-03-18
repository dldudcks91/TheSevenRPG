---
feature: 스테이지 진행 관리
manager: StageManager
api_codes: [3003, 3004]
status: partial
# Phase 14에서 웨이브/체크포인트/귀환/사망 시스템으로 대폭 개편 예정
---

## 목적
스테이지 해금 검증 + 입장/클리어 처리. 콘텐츠 해금 흐름 관리.

---

## 동작 규칙

**스테이지 구조 (stage_info.csv)**
- stage_id: `{챕터}{스테이지번호}` 2자리 형식 (예: 101 = Ch1 Stage1)
- 일반 스테이지: 7챕터 × 3스테이지 = 21개 (stage_num 1~3)
- 챕터 보스 스테이지: 7개 (stage_num 4, 3스테이지 모두 클리어 후 개방)
- stage_info.csv 컬럼: stage_id, chapter_id, stage_num, monster_type, stage_name, monster_pool, boss_id
  - `monster_pool`: 해당 스테이지 일반 몬스터 목록 (콤마 구분 monster_idx)
  - `boss_id`: 스테이지 보스 or 챕터 보스 monster_idx

**웨이브 구조 (확정)**
- 일반 스테이지(stage_num 1~3): [일반3+정예1] × 3웨이브 + 보스1(웨이브4) = 13마리
- 챕터 보스 스테이지(stage_num 4): [일반3+정예1] × 3웨이브 + 챕터보스1(웨이브4) = 13마리
- 스폰 순서: 종별 집중 (AAA→BBB→CCC)
- 정예 = 일반 몬스터 + 런타임 정예 특성 부여 (Phase 15 구현)

**3003 (enter_stage)**
- 일반 스테이지: `stage_id ≤ user.current_stage` 검증
- 챕터 보스(stage_num=4): 해당 챕터 stage_num 1~3 모두 클리어 필요
- Redis에 진행 상태 저장 (TTL 24시간)
- 몬스터 풀 반환: stage_info.csv의 monster_pool + boss_id 기반

**3004 (clear_stage)**
- Redis stage_progress에서 enter_stage 선행 여부 확인
- 현재 진행 중인 스테이지(`stage_id == current_stage`)일 때만 current_stage +1
- Redis 진행 상태 삭제

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 3003 | stage_id | 입장할 스테이지 ID |
| 3004 | stage_id | 클리어한 스테이지 ID |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| (3003) stage_id, monsters[] | int/list | 웨이브별 몬스터 풀 |
| (3004) stage_id, unlocked_next, current_stage | int/bool | 클리어 결과 |

---

## 상태 변화

**DB** (3004만)
- User.current_stage +1 (신규 스테이지 클리어 시만)

**Redis**
- `user:{user_no}:stage_progress` 저장 (3003, TTL 24h)
- `user:{user_no}:stage_progress` 삭제 (3004)

---

## 구현 제약
- clear_stage는 반드시 enter_stage 이후에만 호출 가능 (Redis stage_progress로 강제)
- Redis 장애 시 clear_stage의 순서 검증 실패 → 경고 로그만 남기고 진행 (관대한 처리)
- with_for_update(): 3004에서 User 행 잠금

## Phase 14 변경 예정
- BattleSessions 테이블 도입
- enter_stage: BattleSession 생성, 웨이브1 몬스터만 반환
- 체크포인트: 웨이브 클리어마다 저장
- 귀환(API 3007): HP 보존, 세션 유지
- 재접속(API 3008): 진행 복구
- 사망: 경험치 5% 차감, 웨이브 처음부터 재시작

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 5) |
| 2026-03-17 | stage_id 구조 수정 (1~21 → 101~104 형식), 웨이브 구성 수정 ([일반3+정예1]×3+보스), stage_info.csv monster_pool/boss_id 컬럼 반영 |
| 2026-03-18 | _generate_monster_pool 기획 반영: 종별 집중 배치(AAA→BBB→CCC), 13마리 구조, 웨이브4 보스 분리. stage_id 해금/진행 로직 개편 (101~704 형식 대응) |
