---
feature: 전투 시뮬레이션
manager: BattleManager
api_codes: [3001]
status: partial
# Phase 16에서 경직/사이즈/마저항/상태이상/세트/스킬 발동 대폭 개편 예정
---

## 목적
서버가 전투 전 과정을 시뮬레이션하고 결과를 반환. 클라이언트는 battle_log를 재생만 함.

---

## 동작 규칙
- 유저 전투 스탯 로드: Redis `battle_stats` → 없으면 DB 재계산 후 캐싱(TTL 1시간)
- 몬스터 스탯: `GameDataManager.REQUIRE_CONFIGS["monsters"]` + 스폰 등급 배율 적용
- 공격속도 타이머 방식 (dt=0.1, max_turns=200)
- 명중 판정: `clamp(Acc/(Acc+Eva+0.001) + LvDiff×0.01 + 0.1, 0.05, 0.95)`
- 데미지: `ATK × (1 - DEF/(DEF+100)) × random(0.9~1.1) × crit_mult`
- 결과: win / lose / timeout
- 승리 시만 DB에 경험치/골드 지급 + 레벨업 처리
- 레벨업 시 Redis `battle_stats` 무효화

**스폰 등급 배율 (CSV 우선, 없으면 폴백 상수)**
| 등급 | hp_mult | atk_mult | exp_mult | gold_mult |
|------|---------|----------|----------|-----------|
| 일반 | 1.0 | 1.0 | 1.0 | 1.0 |
| 정예 | 3.0 | 1.5 | 3.0 | 2.0 |
| 보스 | 10.0 | 2.5 | 10.0 | 5.0 |
| 챕터보스 | 20.0 | 5.0 | 20.0 | 10.0 |

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 3001 | monster_idx | 몬스터 ID |
| 3001 | spawn_type | 일반/정예/보스/챕터보스 (default=일반) |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| result | str | win / lose / timeout |
| battle_log | list | 턴별 공격 기록 (actor, action, damage, crit, turn, target_hp) |
| rewards.exp_gained | int | 획득 경험치 (승리 시) |
| rewards.gold_gained | int | 획득 골드 (승리 시) |
| rewards.level, exp, next_required_exp | int | 현재 레벨/경험치 상태 |
| rewards.leveled_up, levels_gained | bool/int | 레벨업 여부 |
| rewards.gold | int | 현재 보유 골드 |

---

## 상태 변화

**DB** (승리 시만)
- UserStat.exp += exp_gained
- UserStat.level 증가 (레벨업 시), stat_points += 레벨당 5
- User.gold += gold_gained

**Redis**
- `user:{user_no}:battle_stats` 캐싱 (캐시 미스 시 DB 재계산 후 저장, TTL 1시간)
- `user:{user_no}:battle_stats` 삭제 (레벨업 시만)

---

## 구현 제약
- 전투 결과는 서버에서만 확정 (클라이언트 값 신뢰 금지)
- 몬스터 레벨 = 플레이어 레벨 (임시 — Phase 14 몬스터 스탯 확정 시 변경)
- 골드 드롭 공식 임시: `random(5~20) × max(1, level//5) × grade.gold_mult` — Phase 17에서 확정
- 경험치 테이블: CSV(level_exp_table.csv) 우선, 없으면 폴백 공식 `10 × 1.3^(lv-1)` 사용

## 미구현 항목 (Phase 16 예정)
- 경직 시스템 (기본경직 + 둔기 추가 + FHR)
- 사이즈 보정 (대형↔소형 ±10%)
- 마법 저항 별도 계산
- 상태이상 7종 (화상/중독/스턴/빙결/침식/매혹/심판)
- 카드 스킬 발동 (공격 시/적중 시/피격 시)
- 세트 보너스 전투 적용

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 4) |
| 2026-03-17 | Phase 12에서 경험치 커브 + 등급 배율 CSV 연동 추가 |
