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
- BattleSession 존재 검증 (Phase 14)
- 플레이어 HP: session.current_hp에서 시작 (연속 HP)
- 유저 전투 스탯 로드: Redis `battle_stats` → 없으면 DB 재계산 후 캐싱(TTL 1시간)
- 몬스터 스탯: `GameDataManager.REQUIRE_CONFIGS["monsters"]` + 스폰 등급 배율 적용
- 공격속도 타이머 방식 (dt=0.1, max_turns=200)
- 명중 판정: `clamp(Acc/(Acc+Eva+0.001) + LvDiff×0.01 + 0.1, 0.05, 0.95)`
- 데미지: `ATK × (1 - DEF/(DEF+100)) × random(0.9~1.1) × crit_mult`

**승리 시:**
- wave_kills에 킬 기록 추가
- 웨이브 클리어 판정 → 보상 지급 (경험치/골드 합산) → 다음 웨이브 진행
- 레벨업 시 Redis `battle_stats` 무효화

**패배/타임아웃 시:**
- 사망 패널티: 현재 레벨 내 경험치 10% 차감 (0% 하한, 레벨다운 없음)
- 현재 웨이브 킬 리셋 (웨이브 처음 재시작)
- HP를 max_hp로 복구

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
| battle_log | list | 턴별 공격 기록 |
| rewards | dict | 웨이브 클리어 시 경험치/골드/레벨 |
| wave_cleared | bool | 웨이브 클리어 여부 |
| stage_cleared | bool | 스테이지 보스 클리어 여부 |
| session | dict | 현재 세션 상태 (wave, hp, kills) |

---

## 상태 변화

**DB**
- BattleSession.wave_kills, current_hp, current_wave 업데이트
- 웨이브 클리어 시: UserStat.exp/level, User.gold 변경
- 사망 시: UserStat.exp 차감

**Redis**
- `user:{user_no}:battle_stats` 캐싱/무효화

---

## 구현 제약
- BattleSession with_for_update 필수 (동시 전투 방지)
- JSON 컬럼 변경 시 flag_modified 필수
- 몬스터 레벨 = 플레이어 레벨 (임시 — Phase 17 mlvl 체계 확정 시 변경)

## 미구현 항목 (Phase 16 예정)
- 경직 시스템 (기본경직 + 둔기 추가 + FHR)
- 사이즈 보정 (대형↔소형 ±10%)
- 마법 저항 별도 계산
- 상태이상 7종 (화상/중독/스턴/빙결/침식/매혹/심판)
- 카드 스킬 발동 (7종 트리거)
- 세트 보너스 전투 적용

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 4) |
| 2026-03-17 | Phase 12에서 경험치 커브 + 등급 배율 CSV 연동 추가 |
| 2026-03-19 | Phase 14 — BattleSession 연동, 연속 HP, 웨이브 보상, 사망 패널티 10% |
