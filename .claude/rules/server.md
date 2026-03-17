---
paths:
  - "fastapi/**/*.py"
---

# 서버 코딩 규칙

자세한 가이드는 `fastapi-server` skill 참조.

## 응답 형식 (반드시 준수)
- 성공: `{"success": True, "message": str, "data": ...}`
- 에러: `error_response(ErrorCode.XXX, "설명")` — 직접 dict 작성 금지

## Manager 클래스
- 모든 메서드: `@classmethod` + `async`
- 시그니처: `async def method(cls, user_no: int, data: dict)`
- 새 기능 추가 = Manager 메서드 작성 + `APIManager.api_map` 등록, 그 외 변경 없음

## API 코드 체계
- `1xxx`: 시스템 (1002 config, 1003 회원가입, 1007 로그인)
- `2xxx`: 인벤토리
- `3xxx`: 전투

## 에러 코드 체계 (E+4자리)
- `E1xxx`: 시스템/인증 — `E1001` 알 수 없는 API, `E1002` 인증 실패, `E1004` 잘못된 요청
- `E2xxx`: 유저 — `E2001` 유저 없음, `E2002` 이미 존재, `E2003` 비밀번호 오류
- `E3xxx`: 인벤토리 — `E3001` 아이템 없음, `E3002` 장착 불가
- `E4xxx`: 전투 — `E4001` 스테이지 없음, `E4002` 잘못된 전투 요청
- `E9xxx`: 서버 내부 — `E9001` DB 오류, `E9002` Redis 오류, `E9999` 알 수 없는 오류

## Redis 캐시 키 네이밍
```
user:{user_no}:battle_stats    # 전투 스탯 (장비 변경 시 무효화)
user:{user_no}:idle_farm       # 방치형 타이머
user:{user_no}:stage_progress  # 스테이지 진행
session:{session_id}           # 세션 (TTL 7일)
```

## 인증
- `user_no`는 클라이언트가 전송 안 함 — 서버가 세션에서 조회
- `Authorization: Bearer {session_id}` 헤더로 전달
- PUBLIC_API_CODES (1002, 1003, 1007)는 세션 검증 제외

## 메타데이터
- CSV 메타데이터는 `GameDataManager.REQUIRE_CONFIGS`에서만 참조
- 런타임 파일 I/O 금지 — 서버 기동 시 메모리 로드된 데이터만 사용
