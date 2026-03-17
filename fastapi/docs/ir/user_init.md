---
feature: 회원가입 / 로그인
manager: UserInitManager
api_codes: [1003, 1007]
status: implemented
---

## 목적
신규 유저 계정 생성 및 로그인 처리. 세션 발급까지 포함.

---

## 동작 규칙
- 회원가입(1003): user_name(2~20자) + password(4~100자) 검증 → bcrypt 해싱 → User + UserStat + 스타터 무기 단일 트랜잭션 생성 → 세션 발급
- 로그인(1007): user_name + password → bcrypt 검증 → 세션 발급
- 닉네임 중복 → E2002 (IntegrityError 포함)
- 로그인 실패: 유저 없음/비밀번호 불일치 모두 동일 메시지 (보안: 존재 여부 미노출)
- 세션 발급은 DB 커밋 완료 후 Redis에서 수행

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 1003 | user_name | 닉네임 (2~20자) |
| 1003 | password | 비밀번호 (4~100자) |
| 1007 | user_name | 닉네임 |
| 1007 | password | 비밀번호 |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| user_no | int | 유저 고유 번호 |
| user_name | str | 닉네임 |
| session_id | str | Redis 세션 키 |

---

## 상태 변화

**DB**
- (1003만) User 생성, UserStat 생성, Item(base_item_id=1, weapon, is_equipped=True) 생성

**Redis**
- `session:{session_id}` 생성 (TTL 7일)

---

## 구현 제약
- 비밀번호는 서버에서 bcrypt 해싱 (클라이언트 사전 해싱 수신 금지)
- user_no는 클라이언트에 반환하나 인증에 사용하지 않음 (session_id 사용)
- PUBLIC_API_CODES: 1003, 1007 (세션 인증 제외)
- 스타터 무기 base_item_id=1 하드코딩 (추후 메타데이터 참조로 전환 필요)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 2) |
| 2026-03-17 | bcrypt 해싱 + 로그인 분리 확정 |
