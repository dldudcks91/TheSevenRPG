---
feature: 튜토리얼 전투 (프롤로그 첫 전투)
manager: TutorialBattleManager
api_codes: [1010]
status: implemented
---

## 목적
프롤로그 5씬 종료 후 간이 전투 화면으로 첫 전투를 체험시키고, 확정 드롭(방어구)을 지급하여 핵심 루프(전투→드롭→장착→강해짐)를 학습시킨다.

---

## 동작 규칙

### 전체 흐름
```
프롤로그 씬 5 "불길" 종료
  ↓
튜토리얼 전투 씬 (TutorialBattleScene)
  - 서버 API 1010 호출 → 스크립트 전투 결과 수신
  - 간이 전투 화면에서 전투 재생 (HP바, 데미지 텍스트)
  - 승리 연출
  ↓
드롭 결과 표시 + 장착 유도
  - 확정 드롭: 방어구 (Dusk Shroud, 200101)
  - "장착하기" 버튼 → API 2001 호출
  ↓
Chapter 1 진입 → 메인 화면
```

### 서버 규칙
1. **1회 제한**: 유저당 1번만 실행 가능. 이미 실행했으면 에러 반환
2. **스크립트 전투**: 실제 BattleManager 호출 없이 고정된 전투 로그 생성
3. **확정 드롭**: 방어구 1개를 DB에 저장 (magic 등급, Dusk Shroud)
4. **튜토리얼 완료 플래그**: User.tutorial_step 필드로 관리
   - 0: 미완료 (기본값)
   - 1: 전투 완료 + 드롭 지급됨

### 튜토리얼 몬스터 (스크립트)
- 이름: "사탄의 하수" (임프 계열)
- HP: 30, ATK: 3, DEF: 0
- 바알 초기 스탯으로 3~4턴에 승리 확정

### 전투 로그 구조 (고정)
```json
{
  "turns": [
    {"turn": 1, "attacker": "player", "damage": 8, "target_hp": 22},
    {"turn": 1, "attacker": "monster", "damage": 3, "target_hp": 197},
    {"turn": 2, "attacker": "player", "damage": 9, "target_hp": 13},
    {"turn": 2, "attacker": "monster", "damage": 2, "target_hp": 195},
    {"turn": 3, "attacker": "player", "damage": 10, "target_hp": 3},
    {"turn": 3, "attacker": "monster", "damage": 3, "target_hp": 192},
    {"turn": 4, "attacker": "player", "damage": 8, "target_hp": 0}
  ],
  "result": "victory",
  "player_max_hp": 200,
  "monster_max_hp": 30,
  "monster_name": "사탄의 하수",
  "exp_gained": 15,
  "gold_gained": 10
}
```

### 클라이언트 규칙
1. **간이 전투 화면**: HP바 2개 (플레이어/몬스터) + 데미지 텍스트 애니메이션
2. **자동 재생**: 서버에서 받은 턴 로그를 순차 재생 (턴당 ~800ms)
3. **승리 후**: 드롭 아이템 표시 + "장착하기" 버튼
4. **장착 완료 후**: "— Chapter 1. 분노 / 불타는 전장 —" 표시 → 메인 진입
5. **가이드 텍스트**: 전투 중/후 오버레이로 안내 메시지 표시

---

## 입력 / 출력

**입력 (api_code별)**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 1010 | (없음) | user_no는 세션에서 추출 |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| battle_log | object | 스크립트 전투 로그 (turns, result, hp 등) |
| drop_item | object | 확정 드롭 아이템 정보 (item_uid, base_item_id, rarity, dynamic_options) |
| exp_gained | int | 획득 경험치 |
| gold_gained | int | 획득 골드 |

---

## 상태 변화

**DB**
- `users.tutorial_step`: 0 → 1
- `users.gold`: +10 (골드 드롭)
- `user_stats.exp`: +15 (경험치)
- `items`: 방어구 1개 INSERT (Dusk Shroud, magic)

**Redis**
- 무효화: `user:{user_no}:battle_stats` (새 장비 추가 시)

---

## 구현 제약
- BattleSession 사용하지 않음 (스크립트 전투)
- 전투 로그는 서버에서 고정 생성 (랜덤 없음)
- tutorial_step 중복 실행 방지: 이미 1이면 에러
- 드롭 아이템은 장착되지 않은 상태로 지급 (클라이언트에서 장착 유도)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-20 | 최초 작성 |
| 2026-03-20 | 구현 완료 — 서버(API 1010) + 클라이언트(TutorialBattleScene) |
