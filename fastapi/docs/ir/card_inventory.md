---
feature: 카드 인벤토리 시스템
manager: CardManager
api_codes: [2007, 2008, 2009, 2012, 2013, 2014]
status: implemented
---

## 목적
카드 = 인벤토리 아이템 체계 구현. 카드 조회/분해/레벨업 + 스킬 장착을 Cards 테이블 기반으로 전환.

---

## 동작 규칙

### 기존 API 리팩토링

#### 도감 조회 (API 2007) — 변경 없음
- Collections 테이블 기반 도감 목록 조회 (수집 기록)
- 해금 슬롯 수는 유저 레벨 기반

#### 스킬 장착 (API 2008) — Cards 테이블로 전환
- **기존**: Collection.skill_slot에 장착
- **변경**: Card.is_equipped + Card.skill_slot에 장착
- 플레이어가 보유한 **특정 카드(card_uid)**를 슬롯에 장착
- 같은 monster_idx 카드는 1개만 장착 가능
- 슬롯 점유자 자동 해제

#### 스킬 해제 (API 2009) — Cards 테이블로 전환
- **기존**: Collection.skill_slot = None
- **변경**: Card.is_equipped = False, Card.skill_slot = None
- card_uid 기반으로 해제

### 신규 API

#### 카드 인벤토리 조회 (API 2012)
- Cards 테이블에서 user_no 기준 전체 조회
- card_skill.csv 메타데이터와 매핑하여 스킬 정보 포함 반환

#### 카드 분해 (API 2013)
- 장착 중인 카드 분해 차단
- 카드 삭제 → 카드 영혼(card_soul) 획득
- 카드 레벨에 따른 영혼 획득량: Lv1=1개, Lv2=3개, Lv3=7개 (투자분 일부 회수)

#### 카드 레벨업 (API 2014)
- 같은 monster_idx 카드 N장 + 카드 영혼 N개 소모
- 레벨업 소모량 (폴백 상수, CSV 미확정):
  - Lv1→2: 동일 카드 2장 + 카드 영혼 3개
  - Lv2→3: 동일 카드 4장 + 카드 영혼 8개
- 최대 레벨: 3
- 소모 카드는 장착 중이면 안 됨
- 레벨업 대상 카드는 장착 중이어도 가능

### 카드 랜덤 수치 (card_stats)
- 드롭 시 랜덤 수치 부여 (card_skill.csv의 trigger_rate 범위 기반)
- card_stats 구조: `{"trigger_rate": float}` — trigger_rate_lv1 기준으로 ±10% 랜덤
- 레벨업 시 trigger_rate 상승: Lv2 = lv1~lv2 중간값, Lv3 = lv2 값

### card_skill.csv 메타데이터 로드
- GameDataManager에 `card_skills` 키 추가
- monster_idx → 스킬 데이터 매핑

---

## 입력 / 출력

**입력 (api_code별)**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 2007 | (없음) | 도감 조회 (변경 없음) |
| 2008 | card_uid (str), slot_number (int) | 카드를 슬롯에 장착 |
| 2009 | card_uid (str) | 카드 장착 해제 |
| 2012 | (없음) | 카드 인벤토리 전체 조회 |
| 2013 | card_uid (str) | 카드 분해 |
| 2014 | card_uid (str) | 레벨업 대상 카드 (소모 카드는 자동 선택) |

**출력 — 2012 (get_cards)**
| 필드 | 타입 | 설명 |
|------|------|------|
| cards | list | [{card_uid, monster_idx, card_level, card_stats, is_equipped, skill_slot, skill_info}, ...] |

**출력 — 2013 (disassemble_card)**
| 필드 | 타입 | 설명 |
|------|------|------|
| card_uid | str | 분해된 카드 |
| card_soul_gained | int | 획득한 카드 영혼 |
| card_soul_total | int | 보유 카드 영혼 총량 |

**출력 — 2014 (level_up_card)**
| 필드 | 타입 | 설명 |
|------|------|------|
| card_uid | str | 레벨업된 카드 |
| new_level | int | 새 레벨 |
| new_card_stats | dict | 갱신된 수치 |
| cards_consumed | int | 소모된 카드 수 |
| souls_consumed | int | 소모된 영혼 수 |

---

## 상태 변화

**DB**
- `Cards`: INSERT(드롭), DELETE(분해/레벨업 소모), UPDATE(레벨업/장착/해제)
- `Materials`: card_soul amount 증감 (분해/레벨업)
- `Collections`: skill_slot 컬럼 미사용으로 전환 (Cards.skill_slot로 이관)

**Redis**
- 무효화: 없음 (카드 스킬은 전투 시 Cards 테이블에서 직접 조회)

---

## 구현 제약
- card_uid 소유권 검증 필수 (Card.user_no == user_no)
- 장착 중 카드 분해 차단
- 소모 카드 장착 중이면 차단 (레벨업 대상은 장착 가능)
- 카드 레벨 최대 3 (MAX_CARD_LEVEL 상수)
- DB 쿼리: get_cards 1건, disassemble 2건(Card+Material), level_up 최대 3건(Card+소모Cards+Material)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-20 | 최초 작성 (Phase 18.5) |
| 2026-03-20 | 구현 완료 — get_cards(2012), disassemble_card(2013), level_up_card(2014), equip/unequip Cards 전환 |
