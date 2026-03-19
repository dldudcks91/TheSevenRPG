---
feature: 스테이지 진행 관리 (웨이브/체크포인트)
manager: StageManager
api_codes: [3003, 3004, 3007, 3008]
status: implemented
---

## 목적
스테이지 해금 검증 + 4웨이브 체크포인트 시스템 + 귀환/재접속.

---

## 동작 규칙

**스테이지 구조 (stage_info.csv)**
- stage_id: `{챕터}{스테이지번호}` 형식 (예: 101 = Ch1 Stage1)
- 일반 스테이지: 7챕터 × 3스테이지 = 21개 (stage_num 1~3)
- 챕터 보스 스테이지: 7개 (stage_num 4, 3스테이지 모두 클리어 후 개방)

**웨이브 구조 (Phase 14 확정)**
- [일반3+정예1] × 3웨이브 + 보스1(웨이브4) = 13마리
- 스폰 순서: 종별 집중 (AAA→BBB→CCC)
- 정예 = 일반 몬스터 + 런타임 정예 특성 부여 (Phase 15 구현)

**3003 (enter_stage)**
- 해금 검증: `stage_id ≤ user.current_stage`
- 기존 BattleSession 있으면 차단 (E4005)
- BattleSession 생성: wave=1, hp=max_hp
- 4웨이브 몬스터 풀 반환

**3004 (clear_stage)**
- BattleSession 검증 + 웨이브4 보스 클리어 확인
- 다음 스테이지 해금 + BattleSession 삭제

**3007 (return_to_town)**
- HP 보존, BattleSession 유지
- 현재 웨이브 킬 리셋 (재입장 시 웨이브 처음부터)

**3008 (get_battle_session)**
- 재접속 시 진행 상태 복구
- 세션 없으면 null 반환 (에러 아님)

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 3003 | stage_id | 입장할 스테이지 ID |
| 3004 | stage_id | 클리어한 스테이지 ID |
| 3007 | (없음) | |
| 3008 | (없음) | |

**출력**
| api_code | 필드 | 설명 |
|----------|------|------|
| 3003 | stage_id, current_wave, current_hp, max_hp, monsters[] | 세션 + 몬스터 풀 |
| 3004 | stage_id, unlocked_next, current_stage | 클리어 결과 |
| 3007 | stage_id, current_wave, current_hp | 귀환 상태 |
| 3008 | session{...}, monsters[] | 세션 상태 + 몬스터 풀 |

---

## 상태 변화

**DB**
- BattleSession 생성 (3003), 삭제 (3004)
- User.current_stage +1 (3004, 신규 클리어 시)

---

## 구현 제약
- BattleSession은 유저당 1개만 (with_for_update 동시 생성 방지)
- 웨이브 순서 강제: wave_kills 개수로 판정
- JSON 컬럼 변경 시 flag_modified 필수 (SQLAlchemy)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 5) |
| 2026-03-17 | stage_id 구조 수정, 웨이브 구성 수정 |
| 2026-03-18 | 13마리 구조, 웨이브4 보스 분리 |
| 2026-03-19 | Phase 14 구현 완료 — BattleSession 기반 웨이브/체크포인트/귀환/재접속 |
