---
name: manager-convention
description: "Manager 클래스 코딩 컨벤션. 메서드 내부 구조, DB 트랜잭션 패턴, 검증 순서, 에러 처리, 로깅 규칙 등 Manager 코드 작성 시 반드시 따라야 할 코드 레벨 규칙."
---

# Manager 클래스 코딩 컨벤션

Manager 클래스 내부의 메서드를 작성할 때 반드시 따르는 코드 레벨 규칙.
`fastapi-server` skill의 아키텍처 규칙 위에서 동작한다.

---

## 1. 메서드 내부 구조 (실행 순서)

API Manager 메서드는 아래 6단계 순서를 따른다.
해당 없는 단계는 생략하되, 순서를 바꾸지 않는다.

```python
@classmethod
async def some_action(cls, user_no: int, data: dict):
    """
    [1] 입력 추출 & 타입 변환
    [2] 메타데이터 검증 (CSV 기반, DB 불필요)
    [3] DB 세션 열기 + 소유권/상태 검증
    [4] 비즈니스 로직 실행
    [5] DB 커밋
    [6] 응답 반환
    """
```

### 단계별 상세

```python
@classmethod
async def some_action(cls, user_no: int, data: dict):
    # ── [1] 입력 추출 ──
    item_uid = data.get("item_uid")
    if not item_uid:
        return error_response(ErrorCode.INVALID_REQUEST, "item_uid 필요")

    # ── [2] 메타데이터 검증 ──
    config = GameDataManager.REQUIRE_CONFIGS.get("some_config")
    if not config:
        return error_response(ErrorCode.INTERNAL_ERROR, "설정 미로드")

    # ── [3] DB 세션 + 소유권/상태 검증 ──
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_no == user_no).first()
        if not user:
            return error_response(ErrorCode.USER_NOT_FOUND, "유저 없음")

        item = db.query(Item).filter(
            Item.item_uid == item_uid,
            Item.user_no == user_no        # 소유권 검증 필수
        ).first()
        if not item:
            return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템 없음")

        if item.equip_slot is not None:
            return error_response(ErrorCode.INVALID_REQUEST, "장착 중인 아이템")

        # ── [4] 비즈니스 로직 ──
        user.gold -= cost
        item.item_level += 1

        # ── [5] 커밋 ──
        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"[SomeManager] some_action 실패: {e}", exc_info=True)
        return error_response(ErrorCode.DB_ERROR, "처리 중 오류")
    finally:
        db.close()

    # ── [6] 응답 반환 ──
    return {
        "success": True,
        "message": "처리 완료",
        "data": {"item_uid": item_uid, "new_level": item.item_level}
    }
```

> **Utility Manager** (ItemDropManager, EliteManager, StatusEffectManager)는
> DB 접근이 없으므로 6단계를 따르지 않음. 동기 메서드로 자유롭게 작성.

---

## 2. DB 트랜잭션 규칙

### 세션 생명주기
```python
db = SessionLocal()
try:
    # 모든 DB 작업
    db.commit()          # 성공 시 한 번만
except Exception:
    db.rollback()        # 실패 시 롤백
finally:
    db.close()           # 항상 닫기
```

### 원칙
- **하나의 메서드 = 하나의 트랜잭션**: 메서드 내에서 commit은 1회만
- **하나의 메서드 = 하나의 DB 세션**: 헬퍼가 별도 세션을 생성하지 않음
- **조기 반환 시 commit 하지 않음**: 검증 실패 → error_response 반환 시 commit 없이 finally로 직행
- **flush 사용**: auto-increment 값이 필요할 때만 `db.flush()` 사용 (commit 전 ID 확보)
- **읽기 전용 메서드**: commit 불필요, try/finally만 사용

### 금지사항
- 하나의 메서드에서 여러 번 commit 금지 (부분 커밋 방지)
- API Manager 간 DB 세션 공유 금지 (각 메서드가 자체 세션 관리)
- commit 후 같은 세션으로 추가 쿼리 금지
- 헬퍼 메서드 내에서 별도 SessionLocal() 생성 금지

---

## 3. 검증 순서 (Validation Chain)

검증은 비용이 낮은 것부터 높은 순서로 진행한다.

```
[1] 입력값 존재/타입 검증     ← DB 없이 가능, 가장 먼저
[2] 메타데이터 유효성          ← 메모리 조회만
[3] 소유권 검증 (user_no)     ← DB 필요
[4] 상태 검증                  ← DB 필요 (장착 여부, 레벨 등)
[5] 자원 검증 (골드, 슬롯)    ← DB 필요 (부족 시 차단)
```

### 소유권 검증 필수 항목
- **아이템**: `Item.user_no == user_no`
- **카드**: `Card.user_no == user_no`
- **스테이지**: `stage_id <= user.current_stage`
- 클라이언트가 보낸 ID로 다른 유저의 데이터에 접근하지 못하도록 항상 user_no 조건 포함

---

## 4. 에러 처리 패턴

### 비즈니스 에러 vs 시스템 에러

```python
# 비즈니스 에러: 유저 행동이 잘못된 경우 → error_response + 적절한 ErrorCode
if user.gold < cost:
    return error_response(ErrorCode.INSUFFICIENT_GOLD, "골드 부족")

# 시스템 에러: 예상치 못한 오류 → except 블록에서 처리
except Exception as e:
    db.rollback()
    logger.error(f"[ManagerName] method_name 실패: {e}", exc_info=True)
    return error_response(ErrorCode.DB_ERROR, "처리 중 오류")
```

### 규칙
- 비즈니스 에러는 `except`에 넣지 않는다 (정상 흐름의 분기)
- 시스템 에러의 `except`는 반드시 `logger.error` + `exc_info=True` 포함
- 에러 메시지에 내부 구현 상세를 노출하지 않는다 (유저에게는 간결한 메시지)
- `except Exception`은 최후의 방어선 — 예측 가능한 에러는 구체적 타입으로 잡는다

---

## 5. 로깅 컨벤션

### 포맷
```python
import logging
logger = logging.getLogger("RPG_SERVER")

logger.info(f"[ManagerName] 동작 설명 (user_no={user_no}, key=value)")
logger.error(f"[ManagerName] method_name 실패: {e}", exc_info=True)
```

### 레벨 사용 기준
| 레벨 | 용도 | 예시 |
|------|------|------|
| `debug` | 계산 중간값, 개발 추적용 | 전투 시뮬레이션 턴별 데미지 |
| `info` | 주요 비즈니스 이벤트 | 유저 생성, 장비 장착, 레벨업 |
| `warning` | 비정상이지만 서비스 가능 | 캐시 miss, 세션 만료 |
| `error` | 서비스 실패, 데이터 정합성 위험 | DB 커밋 실패, 예외 발생 |

### 규칙
- `[ManagerName]` 접두사 필수 (로그 추적용)
- 민감 정보 (비밀번호, 세션ID 전체) 로깅 금지
- `error` 레벨은 반드시 `exc_info=True` 포함

---

## 6. 응답 구성 규칙

### 성공 응답
```python
return {
    "success": True,
    "message": "처리 완료",        # 간결한 한글 설명
    "data": {                       # 클라이언트가 필요한 최소 데이터
        "item_uid": 123,
        "new_level": 5
    }
}
```

### 에러 응답
```python
return error_response(ErrorCode.INSUFFICIENT_GOLD, "골드가 부족합니다.")
# → {"success": False, "error_code": "E3008", "message": "골드가 부족합니다."}
```

### 규칙
- 성공 응답에 `error_code` 포함하지 않음
- 에러 응답에 반드시 `error_response()` 사용 (직접 dict 생성 금지)
- `data`에는 클라이언트 UI 갱신에 필요한 값만 포함
- DB 모델 객체를 그대로 반환하지 않음 (필요한 필드만 추출)

---

## 7. 헬퍼 메서드 규칙

### private 메서드 네이밍
```python
class BattleManager:
    @classmethod
    async def battle_result(cls, user_no, data):     # public: API 진입점
        ...

    @classmethod
    def _calculate_damage(cls, atk, defense):         # private + 동기: 순수 계산
        ...
```

### 규칙
- API 진입점 메서드: `snake_case` (api_map에 등록)
- 내부 헬퍼: `_underscore_prefix`
- 순수 계산 함수: `async` 불필요 시 동기 메서드로 작성
- **헬퍼가 DB 세션을 사용해야 하면 파라미터로 전달** (자체 세션 생성 금지)

### DB 세션 전달 패턴
```python
@classmethod
async def main_action(cls, user_no, data):
    db = SessionLocal()
    try:
        result = cls._validate_and_calc(db, user_no, item_uid)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"[SomeManager] main_action 실패: {e}", exc_info=True)
        return error_response(ErrorCode.DB_ERROR, "처리 중 오류")
    finally:
        db.close()
    return {"success": True, "message": "완료", "data": result}

@classmethod
def _validate_and_calc(cls, db, user_no, item_uid):
    """DB 세션을 받아 사용하되, commit/rollback하지 않음"""
    item = db.query(Item).filter(...).first()
    return item
```

---

## 8. 내부 호출 규칙

### 허용: Utility Manager의 순수 함수 호출
```python
# API Manager 내부에서 Utility Manager 호출 — OK
drops = ItemDropManager.process_kill(stage_id, monster_idx, spawn_type)
stats = CardManager.generate_card_stats(monster_idx)
```
세션 공유가 아닌 순수 계산 결과만 반환하므로 허용.

### 금지: API Manager 간 DB 세션 전달
```python
# ❌ 금지
db = SessionLocal()
InventoryManager.equip(db, ...)
BattleManager.reward(db, ...)
```

---

## 9. 상수 관리

### Manager 상수
```python
class EnhanceManager:
    MAX_ITEM_LEVEL = 20
    ENHANCE_BASE_COST = 100

# 또는 모듈 레벨 (둘 다 허용)
DEATH_EXP_PENALTY_RATE = 0.10
WAVES_PER_STAGE = 4
```

### 규칙
- 대문자 UPPER_SNAKE_CASE
- 매직 넘버 금지 — 모든 수치에 이름을 부여
- 여러 Manager에서 공유하는 상수는 `config.py`로 이동
- 기획 수치(밸런스)는 CSV 메타데이터로 관리 (코드 상수 X)
- 클래스 레벨 또는 모듈 레벨 둘 다 허용

---

## 10. 금지 패턴 (Anti-patterns)

```python
# ❌ 클라이언트 값을 그대로 신뢰
user.gold += data.get("gold_amount")  # 클라이언트가 금액을 결정

# ✅ 서버가 계산
reward_gold = cls._calculate_gold_reward(monster, player_level)
user.gold += reward_gold

# ❌ 헬퍼 내에서 별도 DB 세션 생성
def _load_stats(cls, user_no):
    db = SessionLocal()  # 금지! 호출자에게서 db를 받아야 함

# ✅ 헬퍼는 DB 세션을 파라미터로 받음
def _load_stats(cls, db, user_no):
    return db.query(UserStat).filter(...).first()

# ❌ commit 후 같은 세션으로 추가 작업
db.commit()
db.query(User).filter(...)  # 위험: 커밋된 세션 재사용

# ❌ except 블록에서 비즈니스 에러 처리
try:
    item = db.query(Item).filter(...).first()
    if not item:
        raise ValueError("아이템 없음")  # 비즈니스 에러를 예외로 던짐
except ValueError:
    return error_response(...)

# ✅ 비즈니스 에러는 조건문으로 처리
item = db.query(Item).filter(...).first()
if not item:
    return error_response(ErrorCode.ITEM_NOT_FOUND, "아이템 없음")

# ❌ JSON 컬럼 변경 후 flag_modified 누락
item.dynamic_options['key'] = value
db.commit()  # SQLAlchemy가 변경을 감지 못할 수 있음

# ✅ flag_modified 호출
from sqlalchemy.orm.attributes import flag_modified
item.dynamic_options['key'] = value
flag_modified(item, "dynamic_options")
db.commit()
```
