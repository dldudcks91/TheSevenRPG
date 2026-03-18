---
feature: DB 모델 확장 (Phase 13)
manager: N/A (모델 전용)
api_codes: []
status: implemented
---

## 목적
Phase 14~22에 필요한 신규 테이블(BattleSessions, Materials, Cards)과 Users 테이블 컬럼 추가.

---

## 동작 규칙

### Users 테이블 컬럼 추가
| 컬럼 | 타입 | 설명 |
|------|------|------|
| `basic_sin` | String(20), nullable | 베이직 죄종 선택 (Phase 22) |
| `unlocked_facilities` | Integer, default=0 | 해금 시설 비트마스크 (Phase 20) |

### BattleSessions 테이블 (신규)
- 유저당 1개 (PK = user_no)
- 웨이브/체크포인트 시스템의 진행 상태 저장
- 스테이지 입장 시 생성, 클리어/포기 시 삭제

### Materials 테이블 (신규)
- 재료 아이템 (포션/광석/낙인/퀘스트재료/카드영혼)
- user_no + material_type + material_id 조합으로 스택 관리
- amount 증감으로 수량 관리

### Cards 테이블 (신규)
- 카드 = 인벤토리 아이템 (기획 확정)
- 드롭 시 랜덤 수치 부여 (card_stats JSON)
- 스킬 슬롯 장착 관리 (기존 Collections.skill_slot에서 이관)

---

## 상태 변화

**DB**
- Users: `basic_sin`, `unlocked_facilities` 컬럼 추가
- BattleSessions: 신규 테이블 생성
- Materials: 신규 테이블 생성
- Cards: 신규 테이블 생성
- Users.cards relationship 추가

**Redis**
- 변경 없음

---

## 구현 제약
- `Base.metadata.create_all()`이 신규 테이블을 자동 생성
- 기존 테이블에 컬럼 추가는 Alembic 마이그레이션 또는 수동 ALTER TABLE 필요
- nullable 컬럼 추가이므로 기존 데이터 호환성 문제 없음
- Collections 테이블의 `collection_level`, `skill_slot`은 Phase 18.5까지 유지 (하위 호환)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-18 | 최초 작성 (Phase 13) |
| 2026-03-18 | 구현 완료: BattleSessions, Materials, Cards 테이블 + Users 컬럼 추가 |
