# 몬스터 디자인 가이드

> 시스템/수치 설계 → `GAME_DESIGN.md` §13
> 몬스터 스탯 데이터 → `fastapi/meta_data/monster_info.csv`
> 이 문서는 **외형·서사·아트 디자인** 논의용

---

## 설계 원칙

### 베이스 vs 인스턴스
- **베이스(Base)**: 내부 분류 클래스. 스탯 설계·드롭 가중치·역할의 기준.
- **인스턴스(Instance)**: 플레이어에게 보이는 실제 몬스터. 챕터마다 고유 이름·외형·서사.
- 같은 Skeleton 베이스라도 Ch1의 스켈레톤과 Ch3의 스켈레톤은 **다른 존재**처럼 보여야 한다.

### 챕터 테마 연동
- 각 챕터의 지역 테마·죄악·상태이상이 몬스터 외형에 녹아있어야 한다.
- 예: Ch1 분노(화상) → 불꽃에 그을리고 분노에 물든 형태
- **스테이지 배경 이름도 참고한다** — 몬스터는 그 배경 위에 자연스럽게 존재해야 한다
- 예: "파멸의 진영" → 군사 진영의 악마 병사 / "핏빛 교전지대" → 전투 한복판의 전사 / "원한의 묘지" → 묘지에서 되살아난 언데드

### 전투 기반
- **1:1 자동전투** — 몬스터는 플레이어와 1대1로 싸우는 단일 전투 단위로 설계

### 스테이지 구성
- 1스테이지 = 노말 몬스터 3종 고정 설계
- 정예는 **런타임에 랜덤 생성** — 스테이지 내 노말 3종 중 랜덤 유닛 + 랜덤 접두사 조합
- 정예는 미리 정의하지 않는다

### 네이밍 규칙
- **노말**: `[몬스터 이름] [역할]` — 예: 고블린 전사, 오크 돌격병, 스켈레톤 궁수
- **정예**: `[접두사] [몬스터 이름] [역할]` — 런타임 조합, 사전 정의 없음

---

## 몬스터 베이스 16종

### Normal (자연 생물·피조물)

| 베이스 | 크기 | 역할 | 외형 특징 |
|--------|------|------|----------|
| Wolf | 소~중형 | 고속 딜러 | 사나운 야생 늑대 |
| Yeti | 중~대형 | 강타·돌격형 | 설산의 거대 설인 |
| Troll | 대형 | 방어 극대화 | 둔중하고 두꺼운 피부의 거인 |
| Lizardman | 소~중형 | 균형형 | 직립 도마뱀 전사·주술사 |
| Golem | 중~대형 | 극단적 방어 | 돌·철로 만들어진 무기물 |
| Human | 중형 | 균형형 전사 | 죄악에 물든 타락한 인간 병사. 챕터마다 다른 죄악에 오염된 형태로 등장 |

### Demon (지옥·마법 계열)

| 베이스 | 크기 | 역할 | 외형 특징 |
|--------|------|------|----------|
| Imp | 소형 | 빠른 마법형 | 작고 날렵한 소악마 |
| Goblin | 소형 | 잔꾀·집단형 | 무리 지어 다니는 소형 악마 병사 |
| Succubus | 중형 | 디버프·마법형 | 유혹적 외형의 마녀 |
| Gargoyle | 중~대형 | 방어형 | 날개 달린 석상 악마 |
| Orc | 중~대형 | 야만 강타형 | 거대하고 야만적인 전사 |

### Undead (죽어서 되살아난 존재)

| 베이스 | 크기 | 역할 | 외형 특징 |
|--------|------|------|----------|
| Skeleton | 소~중형 | 밸런스형 | 무장한 해골 전사·궁수 |
| Zombie | 중~대형 | 느린 고체력 | 썩고 무거운 시체 |
| Ghost | 소~중형 | 물리방어↓ 마법저항↑ | 반투명한 원혼 |
| Vampire | 중~대형 | 흡혈 공격형 | 귀족적 외형의 흡혈귀 |
| Lich | 중~대형 | 마법 극대화 | 마법에 집착한 불사 마법사 |

---

## 챕터별 몬스터 풀 & 인스턴스 설계

### Chapter 1 — 분노 「불타는 전장」
> 죄악: 분노 / 상태이상: 화상 / 챕터 보스: 사탄
> 서사: 사탄의 분노가 스며든 끝나지 않는 전장. 죽은 자들이 이유도 없이 싸운다.

**스테이지 구성**
| 스테이지 | 타입 | 지역명 | 베이스 풀 |
|----------|------|--------|----------|
| 1 | Demon | 파멸의 진영 | Goblin · Orc · Imp |
| 2 | Normal | 핏빛 교전지대 | Human · Troll |
| 3 | Undead | 원한의 묘지 | Skeleton |

**디자인 방향**
- 공통: 불꽃에 그을린 흔적, 분노로 일그러진 표정·자세
- Demon: 사탄의 군기(軍旗)를 달고 싸우는 악마 병사
- Normal: 전장의 열기에 오염된 살아있는 전사들
- Undead: 죽었지만 분노에 묶여 멈추지 못하는 해골 병사들

**챕터 고유 인스턴스**

**스테이지 1 — 파멸의 진영 (Demon)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 1101 | 고블린 척후병 | Demon | Goblin | 1 | 소형. 선봉·잡병. 빠르게 달려드는 선두 | `ch1_goblin_scout` | `16-bit pixel art, small green goblin soldier in ragged leather armor, wielding a short dagger, hunched aggressive stance facing left, scorched burn marks on skin and armor, ember sparks around feet, white background, fantasy RPG enemy sprite` |
| 1102 | 고블린 전사 | Demon | Goblin | 1 | 소형. 무기를 든 정규 고블린 병사 | `ch1_goblin_warrior` | `16-bit pixel art, small green goblin soldier in iron helmet and chest plate, wielding a rusty sword and cracked shield, upright combat stance facing left, battle-worn fire-scorched armor, red glowing eyes filled with rage, white background, fantasy RPG enemy sprite` |
| 1103 | 오크 전사 | Demon | Orc | 2 | 중형. 강력한 한 방. 이 스테이지의 위협적인 존재 | `ch1_orc_warrior` | `16-bit pixel art, large muscular orc warrior in heavy battle-scarred iron armor, wielding a massive war axe with both hands, towering intimidating stance facing left, flames scorching pauldrons, veins bulging with uncontrollable wrath, white background, fantasy RPG enemy sprite` |

**스테이지 2 — 핏빛 교전지대 (Normal)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 1201 | 인간 보병 | Normal | Human | 1 | 소~중형. 기본 전사. 검+방패 정규 병사 | `ch1_human_infantry` | `16-bit pixel art, corrupted human soldier in battered iron armor, wielding a blood-stained sword and cracked shield, upright combat stance facing left, veins visible on neck and arms pulsing with rage, helmet cracked and scorched, wild bloodshot eyes, white background, fantasy RPG enemy sprite` |
| 1202 | 인간 창병 | Normal | Human | 1 | 소~중형. 긴 창을 든 돌격 병사. 공격적 | `ch1_human_spearman` | `16-bit pixel art, corrupted human spearman in scorched leather armor, thrusting a long iron-tipped spear forward facing left, aggressive lunging stance, burn scars across exposed arms, jaw clenched in uncontrollable wrath, torn cape trailing behind, white background, fantasy RPG enemy sprite` |
| 1203 | 트롤 돌격병 | Normal | Troll | 2 | 중~대형. 이 스테이지의 위협. 방어 높고 묵직한 강타 | `ch1_troll_charger` | `16-bit pixel art, massive battle-scarred troll in crude iron pauldrons, charging stance with a large spiked club raised facing left, thick grey warty skin covered in slash wounds and ember burns, sunken rage-filled eyes glowing faintly red, towering hulking silhouette, white background, fantasy RPG enemy sprite` |

**스테이지 3 — 원한의 묘지 (Undead)** *(미완성)*

**스테이지 보스** *(고에티아 배정)*

| 구역 | 보스명 | 고에티아 | 타입 | 베이스 |
|------|--------|---------|------|--------|
| 1구역 화염의 선봉장 | 레라제 (Leraje) | #14 | Demon | Goblin |
| 2구역 맹세를 삼킨 장수 | 하겐티 (Haagenti) | #48 | Normal | Troll |
| 3구역 이름 잃은 전쟁귀 | 사브녹 (Sabnock) | #43 | Undead | Skeleton |

---

### Chapter 2 — 시기 「뒤틀린 숲」
> 죄악: 시기 / 상태이상: 중독 / 챕터 보스: 레비아탄
> 서사: 레비아탄의 시기와 후회가 스며든 숲. 나무들이 서로를 향해 자란다.

**스테이지 구성**
| 스테이지 | 타입 | 지역명 | 베이스 풀 |
|----------|------|--------|----------|
| 1 | Normal | 변형의 경계 | Wolf · Lizardman |
| 2 | Demon | 독무의 심림 | Succubus · Orc |
| 3 | Undead | 부패한 뿌리 | Ghost · Zombie |

**디자인 방향**
- 공통: 독성 녹색빛, 뒤틀리고 비대칭적인 외형
- Normal: 숲의 독기에 오염되어 변형 중인 생물
- Demon: 타인의 힘을 탐내어 흉내 내는 악마
- Undead: 뿌리에 얽혀 썩어가는 원혼

**챕터 고유 인스턴스** *(미완성)*

**스테이지 보스** *(미정)*

---

### Chapter 3 — 탐욕 「황금의 사막」
> 죄악: 탐욕 / 상태이상: 스턴 / 챕터 보스: 맘몬
> 서사: 모래에 묻힌 고대 왕국. 황금은 번쩍이지만 모두 저주가 걸려있다.

**스테이지 구성**
| 스테이지 | 타입 | 지역명 | 베이스 풀 |
|----------|------|--------|----------|
| 1 | Normal | 모래에 묻힌 폐허 | Lizardman · Golem |
| 2 | Undead | 저주받은 지하묘지 | Skeleton · Vampire |
| 3 | Demon | 황금 보물고 | Imp · Goblin |

**챕터 고유 인스턴스** *(미완성)*

**스테이지 보스** *(미정)*

---

### Chapter 4 — 나태 「망각의 동토」
> 죄악: 나태 / 상태이상: 빙결 / 챕터 보스: 벨페고르
> 서사: 모든 것이 얼어붙어 멈춘 동토. 시간이 정지한 듯 눈보라만 영원히 몰아친다.

**스테이지 구성**
| 스테이지 | 타입 | 지역명 | 베이스 풀 |
|----------|------|--------|----------|
| 1 | Undead | 얼어붙은 평원 | Zombie · Ghost |
| 2 | Demon | 빙하 요새 | Goblin · Imp |
| 3 | Normal | 영구동결의 심부 | Yeti · Troll |

**챕터 고유 인스턴스** *(미완성)*

**스테이지 보스** *(미정)*

---

### Chapter 5 — 폭식 「심연의 동굴」
> 죄악: 폭식 / 상태이상: 침식 / 챕터 보스: 바알제붑
> 서사: 끝없이 이어지는 살아있는 미로. 모든 것을 삼키는 동굴.

**스테이지 구성**
| 스테이지 | 타입 | 지역명 | 베이스 풀 |
|----------|------|--------|----------|
| 1 | Undead | 탐식의 입구 | Zombie · Lich |
| 2 | Normal | 맥동하는 미로 | Yeti · Golem |
| 3 | Demon | 소화의 심연 | Gargoyle · Orc |

**챕터 고유 인스턴스** *(미완성)*

**스테이지 보스** *(미정)*

---

### Chapter 6 — 색욕 「타락한 궁전」
> 죄악: 색욕 / 상태이상: 매혹 / 챕터 보스: 아스모데우스
> 서사: 화려하지만 부패한 궁전. 유혹과 함정, 욕망에 잠식된 하수인들.

**스테이지 구성**
| 스테이지 | 타입 | 지역명 | 베이스 풀 |
|----------|------|--------|----------|
| 1 | Demon | 부패한 정원 | Succubus · Imp |
| 2 | Undead | 유혹의 회랑 | Vampire · Ghost |
| 3 | Normal | 욕망의 왕좌 | Lizardman · Troll |

**챕터 고유 인스턴스** *(미완성)*

**스테이지 보스** *(미정)*

---

### Chapter 7 — 오만 「신의 폐허」
> 죄악: 오만 / 상태이상: 심판 / 챕터 보스: 루시퍼
> 서사: 신의 궁전이 무너진 폐허. 신성한 빛이 오염된 최후의 땅.

**스테이지 구성**
| 스테이지 | 타입 | 지역명 | 베이스 풀 |
|----------|------|--------|----------|
| 1 | Demon | 천상의 계단 | Gargoyle · Orc |
| 2 | Normal | 무너진 신전 | Golem · Yeti |
| 3 | Undead | 오만의 왕좌 | Lich · Vampire |

**챕터 고유 인스턴스** *(미완성)*

**스테이지 보스** *(미정)*
