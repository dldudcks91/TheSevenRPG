---
feature: 몬스터 킬 & 드롭 처리
manager: ItemDropManager
api_codes: [3002]
status: partial
# Phase 17에서 7종 드롭 + 등급별 드롭 분리로 대폭 개편 예정
---

## 목적
몬스터 처치 시 드롭 아이템 판정 및 생성. 현재는 장비 드롭만 처리.

---

## 동작 규칙
- 클라이언트가 킬 결과(monster_idx, 등급 등)를 전송 → 서버가 드롭 판정
- 스코어 계산: `(min_base + level×growth) × (field_level × multiplier) × random(±5%)`
- 스폰 등급별 드롭 롤 수: 일반=1, 정예=3, 보스=5
- 드롭 판정: CSV `monster_drop_config.csv`의 등급별 가중치 테이블에서 카테고리 선택
  - 카테고리: Nodrop / gold / equipment / etc(Card/Mat)
- 장비 생성 시: 스코어 → 레어도 판정 → 몬스터 타입 → 부위 가중치 → 베이스 아이템 선택 → 접두사 부여
  - 부위 가중치 없으면 랜덤 5종(weapon/armor/helmet/gloves/boots) 중 선택

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 3002 | monster_idx | 몬스터 ID |
| 3002 | spawned_level | 스폰 레벨 (≥1) |
| 3002 | spawned_grade | 스폰 등급 (≥1) |
| 3002 | field_level | 필드 레벨 (≥1) |
| 3002 | spawn_type | 일반/정예/보스 (default=일반) |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| monster_score | float | 계산된 몬스터 점수 |
| drops[] | list | 드롭 목록 (type + data/amount) |

---

## 상태 변화

**DB**
- 없음 (드롭 결과 반환만, 인벤토리 저장은 클라이언트가 별도 처리)

**Redis**
- 없음

---

## 구현 제약
- 입력값 서버 재검증: spawned_level/grade/field_level ≥ 1, spawn_type 유효값 체크
- 드롭 결과 반환만 하고 DB 저장 안 함 — 클라이언트가 별도로 저장해야 함
  - **어뷰징 리스크**: 클라이언트가 결과를 조작해 저장 시도 가능 → Phase 17에서 구조 개선 필요
- monster_idx는 GameDataManager에서 존재 여부 검증
- 스코어 계산 파라미터: CSV `moster_score_config.csv` 참조

## Phase 17 변경 예정
- 7종 드롭 확장: 골드/장비/카드/포션/광석/퀘스트재료/낙인
- 등급별 드롭 분리 (일반/정예/보스/챕터보스 각기 다른 드롭 테이블)
- 카드 드롭 시 CardManager.register_card 연동
- 재료 드롭 시 Materials 테이블에 직접 저장 (클라이언트 의존 제거)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 4 이전 구현됨) |
