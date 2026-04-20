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

## 재생 방식 (클라, idle 횡스크롤)

> **서버 규칙은 불변.** 이 섹션은 `battle_log`를 클라이언트가 어떻게 시각화하는지만 규정한다. 전투 공식·결과·드롭·경험치·레벨 등 모든 데이터는 서버 결과를 그대로 사용한다.

### 페이즈 FSM (몬스터 1기 기준)
서버가 반환한 1 몬스터분 `battle_log[]`를 클라이언트가 4페이즈로 재해석한다.

| 페이즈 | 입력 | 시각 액션 | 종료 조건 |
|--------|------|-----------|-----------|
| `SPAWN` | monster_idx, spawn_type | 오른쪽 밖에서 몬스터 스프라이트 생성 | 스프라이트 생성 완료 |
| `APPROACH` | — | 몬스터 walk-W, 플레이어 walk-E + 배경 가로 스크롤 (CSS `translateX`) | 몬스터가 조우 지점(스테이지 너비 × 0.58)에 도달 (800ms) |
| `EXCHANGE` | `battle_log[]` | 각 엔트리마다 공격자 slash 애니 + 피격자 hurt + 데미지/MISS 수치 표시. HP 바 갱신 | battle_log 모두 재생 후 300ms |
| `DEATH` | `data.result` | 패배 측(win=몬스터, lose=플레이어) fadeOut + 아래로 살짝 낙하 | 400ms |

- 페이즈 간 간격: PRE_EXCHANGE 200ms, POST_EXCHANGE 300ms, POST_DEATH 250ms.
- 턴 간격: `TURN_DELAY_MS = 350`.
- **`battle_log`의 순서·수치·actor는 절대 변경하지 않는다.** 이동·조우 좌표는 순전히 시각 레이어에서 결정된다.

### 레이아웃
- 플레이어는 스테이지 좌측 22%에 고정, 배경만 왼쪽으로 스크롤하여 "오른쪽으로 나아가는" 감각 연출.
- 전투 로그는 하단 고정창 대신 스테이지 우하단 플로팅 로그(최근 3줄, 1.2s 후 fade out).
- 웨이브 진입 시 중앙에 `WAVE n / 총` 배너 2.2s flash (`is_boss` 플래그가 오면 `BOSS WAVE` 빨간색).

### 스프라이트 시스템
- 플레이어: `LpcSprite`(LPC 레이어 합성 — body / head / legs) → PNG `StaticSprite` → RectSprite 3단 폴백.
- 몬스터: `MONSTER_MANIFEST[monster_idx]` 매니페스트 존재 시 LpcSprite → PNG StaticSprite → RectSprite 3단 폴백.
- 스폰 등급별 크기 배수: 일반 1.00 / 정예 1.10 / 보스 1.30 / 챕터보스 1.55. 기존 `SPAWN_TINT`도 유지.

### 관련 클라이언트 파일
| 경로 | 역할 |
|------|------|
| `fastapi/public/js/main/views/battle-view.js` | 데이터/HUD/로그/결과 오버레이. `IdleBattleScene`에 1 몬스터 재생 위임 |
| `fastapi/public/js/main/views/idle-battle-scene.js` | Phaser Scene + 4페이즈 FSM (`playMob()`) |
| `fastapi/public/js/main/views/pace-ctrl.js` | 속도/일시정지 래퍼 (Iter 4에서 UI 연결 예정) |
| `fastapi/public/js/sprites/lpc-sprite.js` | LPC 레이어 합성 + Phaser 스프라이트 래퍼 |
| `fastapi/public/js/sprites/lpc-manifest.js` | 캐릭터 레이어/애니 스펙, 몬스터 매니페스트, 스폰 사이즈 |
| `fastapi/public/js/sprites/static-sprite.js` | PNG 기반 폴백 스프라이트 (동일 시그니처) |
| `fastapi/public/css/components/battle-view.css` | `.bv-stage` 횡스크롤 배경, 플로팅 로그, 웨이브 배너 |

### 미구현 (Iter 4 예정)
- 재생 속도 1x / 2x / 3x 배속
- 일시정지 / 재개 UI
- `PaceCtrl`의 내부 로직(현재는 passthrough skeleton)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 4) |
| 2026-03-17 | Phase 12에서 경험치 커브 + 등급 배율 CSV 연동 추가 |
| 2026-03-19 | Phase 14 — BattleSession 연동, 연속 HP, 웨이브 보상, 사망 패널티 10% |
| 2026-04-21 | 클라 전투 뷰 idle 횡스크롤 개편 (Iter 1~3). 서버 규칙 불변. "재생 방식 (클라)" 섹션 추가 |
