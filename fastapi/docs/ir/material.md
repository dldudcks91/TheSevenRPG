---
feature: 재료 아이템 관리
manager: MaterialManager
api_codes: [2011, 2015]
status: implemented
---

## 목적
포션/광석/낙인/퀘스트재료/카드영혼의 인벤토리 조회 및 포션 사용 기능 제공.

---

## 동작 규칙

### 재료 조회 (API 2015)
- Materials 테이블에서 user_no 기준 전체 조회
- material_type별 그룹핑하여 반환
- 수량 0인 행은 제외

### 포션 사용 (API 2011)
- **사용 조건**: BattleSession 존재 + 웨이브 클리어 상태 (전투 중 불가)
  - "웨이브 클리어 상태" = 현재 웨이브의 wave_kills에 모든 몬스터 처치 기록 존재
  - 웨이브4(보스) 클리어 후에는 clear_stage를 호출해야 하므로 포션 사용 불가
- **지참 제한**: 스테이지 런 당 포션 사용 횟수 제한 (BattleSession에 potion_used 카운터)
- **회복 공식**: potion_id별 고정 회복량 (폴백 상수)
- **수량 차감**: Materials에서 amount -= 1, 0이면 행 삭제
- **HP 상한**: max_hp 초과 불가

### 포션 기본값 (CSV 미확정 → 폴백 상수)
| potion_id | 이름 | 회복량 | 비고 |
|-----------|------|--------|------|
| 1 | 하급 포션 | 50 HP | Ch1~2 구간 |
| 2 | 중급 포션 | 150 HP | Ch3~4 구간 |
| 3 | 상급 포션 | 400 HP | Ch5~7 구간 |

### 지참 제한 (폴백 상수)
- 스테이지 런 당 최대 포션 사용 횟수: 3회

---

## 입력 / 출력

**입력 (api_code별)**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 2015 | (없음) | 재료 전체 조회 |
| 2011 | potion_id (int) | 사용할 포션 종류 |

**출력 — 2015 (get_materials)**
| 필드 | 타입 | 설명 |
|------|------|------|
| materials | list | [{material_type, material_id, amount}, ...] |

**출력 — 2011 (use_potion)**
| 필드 | 타입 | 설명 |
|------|------|------|
| current_hp | int | 회복 후 HP |
| max_hp | int | 최대 HP |
| healed | int | 실제 회복량 |
| potion_used | int | 이번 런 포션 사용 횟수 |
| potion_remaining | int | 남은 포션 수량 |

---

## 상태 변화

**DB**
- `Materials`: amount 차감 (use_potion)
- `BattleSessions`: current_hp 증가, potion_used 증가 (use_potion)

**Redis**
- 무효화: 없음 (battle_stats 변경 없음)

---

## 구현 제약
- potion_id는 서버에서 POTION_CONFIG 상수 기반 검증 (클라이언트 값 불신)
- HP 회복은 서버 BattleSession.current_hp 기준으로만 처리
- 전투 중(웨이브 진행 중) 포션 사용 차단 — wave_kills 검증으로 판단
- BattleSession 없이 포션 사용 차단
- amount <= 0 시 에러 반환
- DB 쿼리: get_materials 1건, use_potion 최대 3건 (Material + BattleSession + User)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-20 | 최초 작성 (Phase 18) |
| 2026-03-20 | 구현 완료 — get_materials (2015) + use_potion (2011) |
