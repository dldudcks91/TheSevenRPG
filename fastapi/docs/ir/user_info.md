---
feature: 유저 정보 조회 / 스탯 리셋
manager: UserInfoManager
api_codes: [1004, 1005]
status: implemented
---

## 목적
캐릭터 정보 전체 조회(스탯/골드/방치 상태 통합)와 스탯 포인트 리셋.

---

## 동작 규칙
- 1004 (get_user_info): User + UserStat + Redis idle_farm 상태를 통합해 반환
  - Redis 장애 시 idle_info=None으로 폴백 (서비스 중단 없음)
- 1005 (reset_stats): 골드 소비(레벨 × 100) → 5종 스탯 초기값(5)으로 리셋 → 투자 포인트 전부 회수
  - 이미 초기 상태(투자 포인트 0) → E1004
  - 골드 부족 → INSUFFICIENT_GOLD

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 1004 | (없음) | - |
| 1005 | (없음) | - |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| (1004) user_no, user_name | int/str | 기본 정보 |
| (1004) gold, current_stage, max_inventory | int | User 필드 |
| (1004) level, exp, stat_points | int | UserStat 필드 |
| (1004) stats.str/dex/vit/luck/cost | int | 5종 스탯 |
| (1004) idle_farm | dict\|null | 방치 파밍 상태 (active, stage_id, elapsed_seconds) |
| (1005) gold, stat_points, stats, reset_cost | int/dict | 리셋 후 상태 |

---

## 상태 변화

**DB** (1005만)
- User.gold 감소 (레벨 × 100)
- UserStat.stat_str/dex/vit/luck/cost = 5 (초기값)
- UserStat.stat_points += 투자했던 포인트 합

**Redis** (1005만)
- `user:{user_no}:battle_stats` 삭제 (커밋 이후)

---

## 구현 제약
- with_for_update()로 gold/stat 동시 수정 보호
- 리셋 비용 상수: `STAT_RESET_COST_PER_LEVEL = 100`
- 스탯 초기값 상수: `INITIAL_STAT_VALUE = 5`

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 12) |
| 2026-03-17 | 1005 스탯 리셋 API 추가 확정 |
