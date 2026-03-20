---
feature: 크래프팅 시스템
manager: CraftingManager
api_codes: [4001]
status: implemented
---

## 목적
매직 장비 + 낙인 + 광석 + 골드 → 크래프트 등급 장비 제작. 대장간 시설 (Ch1 클리어 해금).

---

## 동작 규칙

### 크래프팅 (API 4001)
- **입력**: item_uid (매직 장비) + stigma_sin (낙인 죄종)
- **전제 조건**:
  - Ch1 클리어 (대장간 해금)
  - 대상 장비가 magic 등급
  - 대상 장비가 장착 중이 아님
  - 접두사 OR 접미사 중 하나만 있어야 함 (둘 다 있으면 불가)
- **동작**:
  1. 기존 접사 보존
  2. 낙인의 죄종으로 빈 쪽(접두/접미) 접사 랜덤 롤
  3. 등급을 "craft"로 변경
  4. dynamic_options에 새 접사 수치 추가
  5. 코스트 재계산 (craft 등급 기준)
- **소모**: 낙인 1개 + 광석 N개 + 골드 N
- **광석 소모**: item_level 기반 (폴백: item_level × 2)
- **골드 소모**: item_level 기반 (폴백: item_level × 50)

### 시설 해금 검증
- Users.unlocked_facilities 비트마스크 검사
- 비트 0: 대장간 (Ch1), 비트 1: 퀘스트 게시판 (Ch2), 비트 2: 상인 (Ch3), 비트 3: 흔적 조합소 (Ch4)

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 4001 | item_uid (str), stigma_sin (str) | 제작할 장비 + 사용할 낙인 죄종 |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| item | dict | 크래프트된 장비 전체 정보 |
| ore_consumed | int | 소모된 광석 수 |
| gold_consumed | int | 소모된 골드 |

---

## 상태 변화

**DB**
- Items: rarity, prefix_id/suffix_id, dynamic_options, item_cost 변경
- Materials: stigma amount -1, ore amount -N
- Users: gold 차감

**Redis**
- 무효화: 없음 (장착 중 아이템 크래프팅 불가)

---

## 구현 제약
- 장착 중 아이템 크래프팅 불가
- 매직 등급만 크래프팅 가능 (rare/unique/craft 불가)
- 접두/접미 중 하나만 있어야 함
- 시설 해금 여부 서버 검증

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-20 | 최초 작성 + 구현 완료 (Phase 19) |
