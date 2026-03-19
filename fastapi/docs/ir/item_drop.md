---
feature: 드롭 시스템 v2 (Phase 17)
manager: ItemDropManager
api_codes: [3002]
status: implemented
---

## 목적
몬스터 처치 시 드롭 판정 + 서버사이드 DB 저장. ilvl/mlvl/dlvl 체계 적용, 5종 드롭 카테고리.

---

## 동작 규칙

### mlvl 계산
- dlvl = stage_info.csv의 dlvl 컬럼
- 일반: mlvl = dlvl
- 정예: mlvl = dlvl + 2
- 스테이지보스: mlvl = dlvl + 3
- 챕터보스: mlvl = stage_info.csv의 chapter_boss_mlvl (고정)
- mlvl cap = 50

### 드롭 판정 흐름
1. BattleManager가 몬스터 처치 시 ItemDropManager.process_kill 호출 (내부 호출, API 아님)
2. 등급별 드롭롤 수: spawn_grade_config.csv의 drop_rolls (일반=1, 정예=3, 스테보=5, 챕보=7)
3. 각 롤마다 monster_drop_config.csv 가중치로 카테고리 선택
   - 카테고리: Nodrop / gold / equipment / card / etc
4. 카테고리별 처리:
   - **Nodrop**: 아무것도 안 나옴
   - **gold**: gold_drop_config.csv 공식 → (mlvl×2+5) × grade.gold_mult × random(0.8~1.2)
   - **equipment**: equip_drop_rate.csv로 등급 판정 (magic/rare) → 장비 생성
   - **card**: 처치 몬스터의 카드 드롭 (monster_idx 1:1 매칭)
   - **etc**: 포션/광석/퀘재 (Phase 18에서 세분화, 현재는 광석으로 통일)
5. 챕터보스 전용 추가 판정:
   - 유니크 장비: unique_drop_rate.csv (3~10%)
   - 낙인: stigma_drop_config.csv (5%)

### 장비 생성
- ilvl = mlvl
- 등급: equip_drop_rate.csv에서 mlvl 구간별 magic/rare 확률
- 부위: monster_drop_equipment.csv 가중치 (몬스터 베이스별)
- 접두사: equipment_prefix.csv (지역 죄종 편향)
- 접미사: equipment_suffix.csv (rare 이상만)
- 유니크: 챕터보스 전용, equipment_unique.csv 참조

### 서버사이드 DB 저장
- 장비 → Items 테이블 INSERT
- 카드 → Cards 테이블 INSERT + CollectionManager.register_card (도감 등록)
- 재료 → Materials 테이블 UPSERT (스택)
- 골드 → Users.gold 증가
- 모든 저장은 BattleSession의 pending_drops에 축적 → 웨이브 클리어 시 일괄 커밋

---

## 입력 / 출력

**입력 (내부 호출 — BattleManager → ItemDropManager)**
| 파라미터 | 설명 |
|----------|------|
| user_no | 유저 번호 |
| monster_idx | 몬스터 ID |
| spawn_type | 일반/정예/스테이지보스/챕터보스 |
| stage_id | 스테이지 ID (dlvl 조회용) |
| db_session | DB 세션 (트랜잭션 공유) |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| drops[] | list | 드롭 목록 (type: gold/equipment/card/material + data) |

---

## 상태 변화

**DB**
- Items: 장비 드롭 시 INSERT
- Cards: 카드 드롭 시 INSERT
- Materials: 재료 드롭 시 UPSERT (amount 증가)
- Users.gold: 골드 드롭 시 증가

**Redis**
- battle_stats 무효화 불필요 (드롭은 전투 스탯에 영향 없음)

---

## 구현 제약
- process_kill은 BattleManager 내부에서만 호출 (API 직접 호출 제거 → 어뷰징 방지)
- DB 세션은 호출자(BattleManager)에서 전달받음 (자체 세션 생성 금지)
- mlvl cap = 50
- 인벤토리 가득 찬 경우: 장비/카드 드롭 무시 (골드/재료는 항상 획득)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 4 이전 구현됨) |
| 2026-03-19 | Phase 17 기획 확정 — ilvl/mlvl/dlvl, 5종 드롭, 서버사이드 저장 |
| 2026-03-19 | Phase 17 구현 완료 — ItemDropManager 전면 재작성, API 3002 제거, BattleManager/StageManager 연동 |
