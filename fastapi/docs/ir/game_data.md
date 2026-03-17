---
feature: 게임 메타데이터 로드 / 클라이언트 제공
manager: GameDataManager
api_codes: [1002]
status: implemented
---

## 목적
서버 기동 시 CSV 파일을 메모리에 로드하고, 클라이언트 초기화 시 전체 메타데이터를 일괄 제공.

---

## 동작 규칙
- 서버 기동 시 `load_all_csv()` 1회 실행 → `REQUIRE_CONFIGS` 딕셔너리에 모든 메타데이터 로드
- CSV 파일 없으면 빈 상태(경고 로그)로 서버 계속 기동
- `level_exp_table.csv`, `spawn_grade_config.csv` 없으면 BattleManager 폴백 상수 사용
- 1002 (get_all_configs): `REQUIRE_CONFIGS` 전체를 클라이언트에 반환

**로드하는 CSV 목록**
| CSV 파일 | REQUIRE_CONFIGS 키 | 설명 |
|---------|-------------------|------|
| monster_info.csv | monsters | 몬스터 기본 스탯 |
| moster_score_config.csv | score_config | 드롭 스코어 계산 파라미터 |
| monster_drop_config.csv | drop_config | 등급별 드롭 가중치 |
| monster_drop_equipment.csv | drop_equip_weights | 몬스터 타입별 부위 가중치 |
| equip_rarity_config.csv | rarity_config | 장비 레어도 스코어 범위/옵션 수 |
| equipment_base.csv | equip_bases | 장비 베이스 아이템 목록 |
| equipment_prefix.csv | prefixes | 접두사 목록 |
| equipment_unique.csv | uniques | 유니크 아이템 목록 |
| chapter_info.csv | chapters | 챕터 정보 |
| stage_info.csv | stages | 스테이지 정보 |
| level_exp_table.csv | level_config | 레벨별 필요 XP (optional) |
| spawn_grade_config.csv | spawn_grade_config | 스폰 등급 배율 (optional) |

---

## 입력 / 출력

**입력**
| api_code | 파라미터 | 설명 |
|----------|----------|------|
| 1002 | (없음) | - |

**출력**
| 필드 | 타입 | 설명 |
|------|------|------|
| data | dict | REQUIRE_CONFIGS 전체 |

---

## 상태 변화

**DB / Redis**
- 없음 (읽기 전용)

---

## 구현 제약
- 런타임 파일 I/O 금지 — 서버 기동 시 1회 로드 후 메모리에서만 참조
- 모든 메타데이터는 `GameDataManager.REQUIRE_CONFIGS`에서만 접근
- PUBLIC_API_CODES: 1002 (세션 인증 제외)
- REQUIRE_CONFIGS 전체를 클라이언트에 반환 → 민감 데이터 포함 여부 확인 필요 (현재는 게임 공개 데이터만 포함)

---

## 변경 이력
| 날짜 | 내용 |
|------|------|
| 2026-03-16 | 최초 작성 |
| 2026-03-17 | Phase 12: level_config, spawn_grade_config CSV 로더 추가 |
