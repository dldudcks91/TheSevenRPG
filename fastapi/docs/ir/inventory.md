---
feature: 인벤토리 / 장비 관리
manager: InventoryManager
api_codes: [2001, 2002, 2003, 2004, 2005]
status: implemented
---

## 목적
장비 장착/해제, 인벤토리 조회/판매, 인벤토리 확장.

---

## 동작 규칙
- 2001 (equip_item): 소유권 확인 → 코스트 검증 → 동일 슬롯 기존 장비 자동 해제 → 장착
  - 최대 코스트 = 레벨 × 1 + stat_cost × 2
  - 이미 같은 슬롯에 장착 중 → 성공 응답(idempotent)
  - 코스트 초과 → COST_EXCEEDED
- 2002 (unequip_item): 소유권 확인 → 장착 여부 확인 → equip_slot = None
- 2003 (get_inventory): 소유 아이템 전체 반환 (필터 없음)
- 2004 (sell_item): 장착 중 차단 → 가격 계산 → Item 삭제 + gold 증가
  - 판매가: rarity 배율(magic=30, rare=100, craft=300, unique=500) × item_level
- 2005 (expand_inventory): 골드 소비 → max_inventory +10 (최대 500)
  - 비용: 500 × (max_inventory // 100 + 1) — 100칸마다 단계 상승

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 2001 | item_uid, equip_slot | 장착할 아이템과 슬롯 |
| 2002 | item_uid | 해제할 아이템 |
| 2003 | (없음) | - |
| 2004 | item_uid | 판매할 아이템 |
| 2005 | (없음) | - |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| (2001) item_uid, equip_slot | str | 장착 결과 |
| (2002) item_uid | str | 해제된 아이템 |
| (2003) items[] | list | 아이템 전체 목록 |
| (2004) item_uid, sell_price, total_gold | str/int | 판매 결과 |
| (2005) max_inventory, cost, total_gold | int | 확장 결과 |

---

## 상태 변화

**DB**
- 2001: Item.equip_slot 변경 (기존 슬롯 점유자 equip_slot=None)
- 2002: Item.equip_slot = None
- 2004: Item 삭제, User.gold 증가
- 2005: User.gold 감소, User.max_inventory 증가

**Redis**
- `user:{user_no}:battle_stats` 삭제 (2001, 2002 — 커밋 이후)

---

## 구현 제약
- 소유권 검증: `Item.user_no == user_no` 조건 필수
- 장착 중 판매 차단 (`equip_slot is not None`)
- 유효 equip_slot: weapon / armor / helmet / gloves / boots
- with_for_update(): 2001(아이템+stat), 2002(아이템), 2004(아이템+유저), 2005(유저)
- Phase 21 장비 분해(2010) — InventoryManager에 메서드 추가 예정

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 3 + Phase 8) |
