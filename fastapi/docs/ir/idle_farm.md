---
feature: 방치 파밍
manager: IdleFarmManager
api_codes: [3005, 3006]
status: removed
---

## 목적
~~오프라인 중 자동 골드/아이템 누적.~~

**기획에서 완전 제거** (2026-03-17). 스토리 모드 단일 진행 + 클리어 후 재입장 파밍으로 확정.

---

## 제거 사유
- 2026-03-16 기획 회의: "방치 파밍 없음 (수동 반복만)" 방향 결정
- 2026-03-17 최종 확정: 방치 파밍 시스템 기획에서 완전 제거
- 핵심 게임 루프: 스테이지 선택 → 입장 → 웨이브 진행 → 마을 귀환 → 드롭 확인 → 재입장

---

## 제거 대상 (Phase 12.5)
- `services/rpg/IdleFarmManager.py` — 파일 삭제
- `services/rpg/__init__.py` — IdleFarmManager import 제거
- `services/system/APIManager.py` — api_map에서 3005, 3006 제거
- `services/system/UserInfoManager.py` — get_user_info에서 idle_farm 관련 코드 제거
- Redis 키 `user:{no}:idle_farm` 관련 코드 전체 정리

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 (Phase 6) |
| 2026-03-16 | 기획 회의: "방치 파밍 없음" 방향 논의 — 존속 여부 미확정 |
| 2026-03-17 | 기획 최종 확정: 방치 파밍 완전 제거 |
| 2026-03-18 | Phase 12.5: 코드 삭제 및 정리 완료, status → removed |
