---
feature: 기능명
manager: XxxManager
api_codes: []
status: planned
# status: planned | partial | implemented
---

## 목적
한 줄 요약.

---

## 동작 규칙
- 규칙 1
- 규칙 2

---

## 입력 / 출력

**입력 (api_code별)**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| xxxx | field_name | 설명 |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| field_name | type | 설명 |

---

## 상태 변화

**DB**
- 변경되는 테이블/컬럼

**Redis**
- 무효화되는 캐시 키
- 새로 캐싱되는 항목

---

## 구현 제약
- 서버에서 재검증해야 하는 값
- 허용하지 않는 패턴
- 성능 제약 (쿼리 수 등)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| YYYY-MM-DD | 최초 작성 |
