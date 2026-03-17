---
feature: 도감 / 스킬 슬롯 관리
manager: CardManager
api_codes: [2007, 2008, 2009]
status: partial
# 미구현: 도감 레벨업 로직, 그룹 보너스, 카드 스킬 전투 발동
---

## 목적
몬스터 카드 수집 → 도감 등록 → 스킬 슬롯 장착. 전투에서 스킬 발동을 위한 선행 시스템.

---

## 동작 규칙
- 2007 (get_collection): 도감 전체 조회 + 현재 레벨 기준 해금 슬롯 수 반환
  - 슬롯 해금 레벨: Lv1(1개), Lv5(2개), Lv15(3개), Lv30(4개)
- 2008 (equip_skill): 레벨 해금 확인 → 도감 등록 확인 → 동일 몬스터 다중 슬롯 차단 → 슬롯 점유자 자동 해제 → 장착
- 2009 (unequip_skill): 도감 등록 확인 → 장착 여부 확인 → skill_slot = None
- register_card (내부 전용): 카드 드롭 시 도감 신규 등록(collection_level=1) 또는 card_count +1
  - 외부 트랜잭션 주입 패턴 지원 (db 파라미터 전달 시 commit 하지 않음)

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 2007 | (없음) | - |
| 2008 | monster_idx, slot_number(1~4) | 장착할 몬스터와 슬롯 번호 |
| 2009 | monster_idx | 해제할 몬스터 |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| (2007) collections[], unlocked_slots | list/int | 도감 목록 + 해금 슬롯 수 |
| (2008) monster_idx, slot_number | int | 장착 결과 |
| (2009) monster_idx | int | 해제된 몬스터 |

---

## 상태 변화

**DB**
- 2008: Collection.skill_slot 변경 (슬롯 점유자 skill_slot=None)
- 2009: Collection.skill_slot = None
- register_card: Collection 신규 생성 또는 card_count +1

**Redis**
- 없음 (스킬 장착은 전투 스탯에 미반영 — Phase 16 카드 스킬 발동 구현 시 변경 필요)

---

## 구현 제약
- 슬롯 번호: 1~4만 허용
- 도감 미등록 몬스터 장착 차단 (COLLECTION_NOT_FOUND)
- 동일 몬스터의 다중 슬롯 장착 금지 (이미 슬롯 있으면 먼저 해제하라고 에러)
- with_for_update(): 2008(entry + occupant), 2009(entry)

## 미구현 항목 (기획 확정됨)
- 도감 레벨업: 3단계(Lv1/2/3), 일반=1/3/10장, 보스=1/2/4장, Lv2=발동확률↑, Lv3=능력치↑
- 도감 그룹 보너스: 스테이지 노말3+보스1=1그룹, 합산 레벨(3/5/7/10)로 4단계 패시브
- 카드 스킬 전투 발동: Phase 16 전투 엔진 v2에서 구현

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 7, CardManager=CollectionManager 역할) |
| 2026-03-17 | 도감 레벨업/그룹 기획 확정 — 미구현 항목으로 기록 |
