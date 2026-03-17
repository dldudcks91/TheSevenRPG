---
feature: 방치 파밍
manager: IdleFarmManager
api_codes: [3005, 3006]
status: partial
# 기획 재검토 필요: 2026-03-16 기획 회의에서 "방치 파밍 없음(수동 반복만)" 결정됨
---

## 목적
오프라인 중 자동 골드/아이템 누적. 현재는 골드만 지급.

> ⚠️ 기획 주의: 2026-03-16 기획 회의에서 "방치 파밍 없음 (수동 반복만)" 방향이 결정됨.
> 이 기능의 존속 여부를 확인 후 진행할 것.

---

## 동작 규칙
**3005 (toggle_idle) — ON/OFF 토글**
- 이미 활성 상태 → OFF: Redis 키 삭제
- 비활성 상태 → ON: stage_id 해금 검증 + 인벤 여유 확인 → Redis 타이머 시작

**3006 (collect_idle)**
- Redis idle_farm에서 경과 시간 계산
- 최소 1분 경과 필요, 최대 누적 24시간 (86400초)
- 골드 지급: `(elapsed // 300) × KILLS_PER_5MIN × GOLD_PER_KILL`
- 수령 후 타이머 리셋 (파밍은 자동 유지됨)

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 3005 (ON) | stage_id | 파밍할 스테이지 |
| 3005 (OFF) | (없음) | - |
| 3006 | (없음) | - |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| (3005) idle_active, stage_id | bool/int | 현재 파밍 상태 |
| (3006) elapsed_minutes, kill_count, gold_reward, total_gold | int | 보상 결과 |

---

## 상태 변화

**DB** (3006만)
- User.gold += gold_reward

**Redis**
- `user:{user_no}:idle_farm` 생성 (3005 ON)
- `user:{user_no}:idle_farm` 삭제 (3005 OFF)
- `user:{user_no}:idle_farm.start_time` 갱신 (3006 수령 후 타이머 리셋)

---

## 구현 제약
- Redis 필수 의존: RedisUnavailable 시 E9002 반환 (방치 파밍은 Redis 없으면 동작 불가)
- 인벤 가득 참 시 ON 차단
- 보상 수치 임시 상수: `KILLS_PER_5MIN=1`, `GOLD_PER_KILL=10` — 기획 확정 후 CSV 대체
- 시간 조작 방지: 경과 시간은 서버 시간 기준, MAX_IDLE_SECONDS=86400 상한

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 6) |
| 2026-03-16 | 기획 회의: "방치 파밍 없음" 방향 논의 — 존속 여부 미확정 |
