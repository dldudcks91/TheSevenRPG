# meta_data — 서버 메타데이터 CSV

> 서버 기동 시 `GameDataManager.load_all_csv()`로 메모리에 로드되는 read-only 데이터.
> 런타임 변경 불가. 수정 후 서버 재시작 필요.

---

## 서버 로드 CSV (GameDataManager에서 읽음)

| 파일 | 설명 | 키 구조 | 행 수 |
|------|------|---------|-------|
| `monster_info.csv` | 전체 몬스터 인스턴스 (Ch1~7 일반/보스) | `monsters[monster_idx]` | ~70 |
| `moster_score_config.csv` | 드롭 점수 계산 파라미터 | `score_config[param_name]` | 4 |
| `monster_drop_config.csv` | 몬스터 등급별 드롭 확률 (Nodrop/골드/장비/기타) | `drop_config[monster_grade]` | 4 |
| `monster_drop_equipment.csv` | 몬스터 베이스별 장비 부위 드롭 가중치 | `drop_equip_weights["Wolf_1"]` | 48 |
| `equip_rarity_config.csv` | 장비 등급 설정 (매직/레어/크래프트/유니크) | `rarity_config["magic"]` | 4 |
| `equipment_base.csv` | 장비 베이스 (무기15 + 갑옷6 + 투구6 + 장갑6 + 신발6) | `equip_bases[]` (리스트) | 39 |
| `equipment_prefix.csv` | 장비 접두사 (7죄종 × 5슬롯) | `prefixes[]` (리스트) | 35 |
| `equipment_unique.csv` | 유니크 장비 정의 (챕터 보스 드롭) | `uniques[]` (리스트) | 0 (미작성) |
| `chapter_info.csv` | 7챕터 정보 (죄종/지역/보스) | `chapters[chapter_id]` | 7 |
| `stage_info.csv` | 스테이지 정보 (챕터당 4스테이지) | `stages[stage_id]` | 28 |
| `level_exp_table.csv` | 레벨 1~50 필요 경험치 커브 | `level_config[level]` | 50 |
| `spawn_grade_config.csv` | 스폰 등급별 배율 (일반/정예/보스/챕보) | `spawn_grade_config["normal"]` | 4 |

## 서버 미로드 CSV (기획 데이터 — 향후 Phase에서 로더 추가 예정)

| 파일 | 설명 | 사용 Phase |
|------|------|-----------|
| `equipment_suffix.csv` | 장비 접미사 (7죄종 × 5슬롯) | Phase 17 (드롭 v2) |
| `equipment_common_option.csv` | 장비 공통 옵션 풀 (슬롯별 14종) | Phase 17 |
| `equipment_set_bonus.csv` | 세트 보너스 (2/4/6 브레이크포인트) | Phase 22 |
| `elite_trait.csv` | 정예 몬스터 특성 (죄종 고유 7 + 공통 16) | Phase 15 |
| `status_effect.csv` | 상태이상 7종 정의 | Phase 16 |
| `chapter_monster_pool.csv` | 챕터별 몬스터 베이스 풀 | Phase 14 |
| `collection_group.csv` | 도감 그룹 정의 | Phase 7 보완 |
| `collection_group_bonus.csv` | 도감 그룹 보너스 | Phase 7 보완 |

## 기획 미확정 CSV

| 파일 | 상태 |
|------|------|
| `equipment_unique.csv` | 헤더만 존재. 챕터 보스 유니크 장비 기획 필요 |
| `spawn_grade_config.csv` | BattleManager 폴백 상수를 옮긴 것. 수치 미확정 |

## 기타 파일

| 파일 | 설명 |
|------|------|
| `sync_data_from_gs.py` | 구글 시트 → 로컬 CSV 다운로드 |
| `sync_data_to_gs.py` | 로컬 CSV → 구글 시트 업로드 |

---

## 컬럼 상세

### monster_info.csv
| 컬럼 | 타입 | 설명 |
|------|------|------|
| monster_idx | int | PK. 챕터×1000 + 스테이지×100 + 순번. 보스=x50, 챕보=x900 |
| monster_name | str | 한글 이름 |
| monster_type | str | Normal / Demon / Undead |
| monster_base | str | 베이스 종족 (Human, Wolf, Goblin 등 15종) |
| size_type | int | 1=소형 / 2=중형 / 3=대형 |
| hp, attack, defense, magic_defense | int | 기본 스탯 (스폰 등급 배율 적용 전) |
| attack_speed | float | 공격속도 (attacks/sec) |
| exp_reward | int | 기본 경험치 (등급 배율 적용 전) |
| sprite_path | str | 클라이언트 스프라이트 경로 |
| description | str | 설명 |

### equipment_base.csv
| 컬럼 | 타입 | 설명 |
|------|------|------|
| item_idx | int | PK. 무기=100xxx, 갑옷=200xxx, 투구=300xxx, 장갑=400xxx, 신발=500xxx |
| item_base | str | 영문 이름 (Gladius, Archon Plate 등) |
| main_group | str | weapon / armor / helmet / gloves / boots |
| sub_group | str | sword, heavy_armor, survival_helm 등 |
| size_type | str | small / medium / large |
| min_damage, max_damage | int | 무기 전용. 방어구는 0 |
| speed | float | 무기 공격속도. 방어구는 0 |
| base_defense | int | 방어구 기본 방어력. 무기는 0 |
| base_magic_defense | int | 방어구 기본 마법저항. 무기는 0 |
| implicit | str | 무기 Implicit (crit_rate_10, armor_ignore_20 등). 없으면 빈값 |
| cost_size_multiplier | float | 코스트 사이즈 배율. 갑옷: 소0.9/중1.0/대1.1, 나머지 1.0 |

### equipment_prefix.csv / equipment_suffix.csv
| 컬럼 | 타입 | 설명 |
|------|------|------|
| prefix (suffix) | str | 죄종 영문 (wrath, sloth 등) |
| prefix_korean (suffix_korean) | str | 죄종 한글 |
| equipment_type | str | weapon / armor / helmet / gloves / boots |
| weight | int | 드롭 가중치 |
| stat_1 | str | 주 옵션 ID (crit_rate, life_steal 등) |
| stat_1_type | str | percentile / fixed |
| min_stat_1, max_stat_1 | float | 주 옵션 수치 범위 |
| stat_2 ~ max_stat_2 | | 보조 옵션 (없으면 `-`) |

### level_exp_table.csv
| 컬럼 | 타입 | 설명 |
|------|------|------|
| level | int | 레벨 (1~50) |
| required_exp | int | 해당 레벨→다음 레벨 필요 XP |
| cumulative_exp | int | 누적 XP (참고용, 서버 미사용) |
| stat_points | int | 레벨업 시 지급 스탯 포인트 (기본 5) |
| chapter_range | str | 해당 레벨의 챕터 구간 (참고용, 서버 미사용) |
