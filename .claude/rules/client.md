---
paths:
  - "fastapi/public/**"
---

# 클라이언트 코딩 규칙

자세한 가이드는 `web-client` skill 참조.

## 현재 상태
- 프론트엔드 미정 — `fastapi/public/index.html` 임시 플레이스홀더
- 서버 API 완성 후 클라이언트 개발 시작 예정

## 설계 원칙
- 서버는 전투 결과를 계산해서 반환 (시뮬레이션)
- 클라이언트는 결과를 받아 애니메이션으로 재생 (뷰어)
- 게임 로직을 클라이언트에 두지 않는다

## 정적 파일 서빙
- FastAPI `StaticFiles`로 `fastapi/public/` 디렉토리 마운트
- SPA 라우팅 필요 시 `html=True` 옵션 사용 중
