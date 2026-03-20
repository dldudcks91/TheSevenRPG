---
feature: 장비 분해
manager: InventoryManager
api_codes: [2010]
status: implemented
---

## 목적
불필요 장비 → 광석 + 골드 회수. 광석 순환 루프 완성.

---

## 동작 규칙

### 장비 분해 (API 2010)
- item_uid 입력
- 장착 중 분해 차단
- 등급별 광석 회수: magic×1, rare×2, craft×3, unique×5 (× item_level)
- 골드 회수: item_level × 20
- 아이템 DELETE + Material(ore) UPSERT + User.gold 증가

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-20 | 최초 작성 + 구현 완료 (Phase 21) |
