# 몬스터 설계

> 설계 규칙: [monster_guide.md](monster_guide.md)
> 몬스터 스탯 데이터: `fastapi/meta_data/monster_info.csv`

---

## 정예 몬스터 특성 시스템

정예 = 노말 유닛 + **죄종 고유 특성 1개** + **공통 특성 2개** (총 3개)

### 죄종 고유 특성 (7종 — 접두사당 1개)

| 접두사 | 특성명 | 효과 | 카운터 |
|--------|--------|------|--------|
| 분노의 | **격분** | HP 30% 이하 시 공격력 ×2, 공속 +50% | 30% 전에 끝내기 |
| 나태의 | **태만** | 공격속도 -50%, 공격력 ×2 | HP/방어로 한방 버티기 |
| 색욕의 | **유혹** | 타격 시 플레이어 공격력 10% 흡수 (정예 +10%, 플레이어 -10%, 스택) | 회피로 피격 줄이기, 속전속결 |
| 시기의 | **박탈** | 치명타/회피 발동 시 무효화, 정상 피해로 변환 | 순수 공방 싸움 |
| 오만의 | **불가침** | 모든 상태이상 면역 | 스탯으로 압도 |
| 폭식의 | **탐식** | 매 타격마다 공격력 +2% 영구 누적 | 속전속결 |
| 탐욕의 | **도박** | 피해 0.2~1.8배 랜덤 + 처치 시 드롭 +1 | HP 여유 + 리스크 감수 보상 |

### 공통 특성 풀 (16종 — 이 중 2개 랜덤)

**스탯 강화 (8종)**

| 특성 | 효과 |
|------|------|
| 강인한 | HP +50% |
| 단단한 | 방어력 +50% |
| 거대한 | 사이즈 +1단계, HP +20% |
| 날랜 | 공격속도 +30% |
| 흉포한 | 공격력 +30% |
| 민첩한 | 회피율 +30% |
| 정확한 | 명중률 +30% |
| 치명적인 | 치명타 확률 +20%, 치명타 데미지 +50% |

**전투 규칙 (8종)**

| 특성 | 효과 |
|------|------|
| 재생하는 | 매초 HP 1% 회복 |
| 가시의 | 받은 피해 15% 반사 |
| 경화의 | 피격마다 방어력 +1% 영구 누적 |
| 선제의 | 전투 시작 시 선제 공격 1회 (100% 명중) |
| 보복의 | 피격 시 30% 확률 즉시 반격 1회 |
| 폭발하는 | 사망 시 최대HP 50% 피해 |
| 저주받은 | 타격 시 30% 확률 랜덤 상태이상 부여 |
| 흡혈의 | 피해의 20% HP 회복 |

### 조합 예시

```
"분노의 골렘 파수꾼" [격분 / 단단한 / 재생하는]
→ 방어력 높고 회복하는데, HP 30% 이하가 되면 공격력 폭발

"시기의 임프 마법사" [박탈 / 날랜 / 정확한]
→ 빠르게 때리면서 치명타/회피를 봉인. 순수 스탯 싸움

"탐욕의 오크 광전사" [도박 / 흉포한 / 치명적인]
→ 피해가 랜덤이지만 터지면 사망 위험. 처치 시 보너스 드롭
```

### 총 변형 수
- 고유 7종 × C(16,2) = 7 × 120 = **840가지**

> 수치는 밸런싱 시 조정 예정

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

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 1101 | 고블린 척후병 | Demon | Goblin | 1 | 소형. 선봉·잡병. 빠르게 달려드는 선두 | `ch1_goblin_scout` |
| 1102 | 고블린 전사 | Demon | Goblin | 1 | 소형. 무기를 든 정규 고블린 병사 | `ch1_goblin_warrior` |
| 1103 | 오크 전사 | Demon | Orc | 2 | 중형. 강력한 한 방. 이 스테이지의 위협적인 존재 | `ch1_orc_warrior` |

**스테이지 2 — 핏빛 교전지대 (Normal)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 1201 | 인간 보병 | Normal | Human | 1 | 소~중형. 기본 전사. 검+방패 정규 병사 | `ch1_human_infantry` |
| 1202 | 인간 창병 | Normal | Human | 1 | 소~중형. 긴 창을 든 돌격 병사. 공격적 | `ch1_human_spearman` |
| 1203 | 트롤 돌격병 | Normal | Troll | 2 | 중~대형. 이 스테이지의 위협. 방어 높고 묵직한 강타 | `ch1_troll_charger` |

**스테이지 3 — 원한의 묘지 (Undead)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 1301 | 스켈레톤 전사 | Undead | Skeleton | 1 | 소~중형. 검+방패 근접. 묘지에서 일어난 기본 해골 병사 | `ch1_skeleton_warrior` |
| 1302 | 스켈레톤 궁수 | Undead | Skeleton | 1 | 소~중형. 원거리 물리. 묘지 뒤편에서 쏘는 해골 사수 | `ch1_skeleton_archer` |
| 1303 | 스켈레톤 기사 | Undead | Skeleton | 2 | 중~대형. 해골 말을 탄 기마 전사. 이 스테이지의 위협 | `ch1_skeleton_knight` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 |
|----------|------|--------|------|-------------|-------------|----------|
| 1 | 파멸의 군주 | 아바돈 (Abaddon) | 요한계시록 | Demon | Orc | 무저갱의 왕 "파괴자". 유명세★5 연관도★5. 분노/파괴의 직결 상징. Orc=거대한 파괴의 화신 |
| 2 | 천의 목소리 | 레기온 (Legion) | 신약 마가복음 | Normal | Human | "우리는 군단이라 하라". 유명세★5. 하나의 몸에 천 개의 분노가 깃든 타락 인간. Human=군단이 깃든 인간 병사 |
| 3 | 머리 없는 전쟁귀 | 둘라한 (Dullahan) | 아일랜드 민속 | Undead | Skeleton | 목 없는 기사. 유명세★4 연관도★4. 전장+묘지 테마 양쪽 커버. Skeleton=해골 기마 전사 |
| 보스 | 불의 심복 | 몰록 (Moloch) | 구약 레위기·열왕기 | Demon | Gargoyle | 아이를 불에 태워 바치게 한 우상. 유명세★4 연관도★4. 실낙원에서 사탄의 측근. 자발적 추종자=사탄의 문지기. Gargoyle=날개+뿔의 거대한 악마 |

**보스 스테이지 — 사탄의 제단 (Demon)**

> 배경: 사탄에게 향하는 몰록의 제단. 불꽃과 제물의 잔해가 널린 의식의 장소.
> 배경 아트 프롬프트: `16-bit pixel art background, dark hellish sacrificial altar at the end of a burning battlefield, massive stone altar stained with blood and ash at center, towering Moloch idol statue with bull horns in the background engulfed in flames, rows of burning braziers lining a path of blackened stone leading to the altar, scattered bones and charred offerings on the ground, rivers of molten lava flowing beneath cracked floor, blood-red sky filled with smoke and embers, oppressive atmosphere of dread and fire, dark fantasy RPG battle stage`

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 1401 | 제단의 화염마 | Demon | Imp | 1 | 소형. 제단의 불꽃을 관리하는 임프. 장난스럽고 날렵 | `ch1_imp_firetender` |
| 1402 | 몰록의 제물관 | Demon | Imp | 2 | 중형. 의식을 집행하는 임프 사제. 횃불과 의복 착용 | `ch1_imp_offerings` |
| 1403 | 몰록의 심판관 | Demon | Imp | 3 | 대형. 제물의 자격을 판결하는 대임프. 위압적인 상위 개체 | `ch1_imp_judge` |

**몬스터 아트 프롬프트**
- 제단의 화염마: `16-bit pixel art, tiny imp fire tender crouching beside a burning brazier, blowing flames with puffed cheeks, carrying an iron fire poker, body glowing orange-red like living coal, small bat wings flickering with sparks, mischievous grin with sharp teeth, white background, fantasy RPG enemy sprite`
- 몰록의 제물관: `16-bit pixel art, small demonic imp priest wearing tattered crimson robes, holding a burning ritual torch, horns curved like a ram, face illuminated by hellfire glow, ash and embers floating around, charred skin with glowing cracks, white background, fantasy RPG enemy sprite`
- 몰록의 심판관: `16-bit pixel art, tall imposing arch-imp judge standing upright with arms crossed, wearing ornate black and gold ceremonial armor with Moloch burning sigil on chest, crown of twisted iron horns wreathed in dark flames, glowing molten eyes staring down with cold authority, holding a massive flaming gavel in one hand, long spiked tail coiled behind, taller and more muscular than lesser imps, radiating an aura of hellfire, white background, fantasy RPG enemy sprite`

**챕터 보스**: 사탄 (Demon)

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

**챕터 고유 인스턴스**

**스테이지 1 — 변형의 경계 (Normal)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 2101 | 독늑대 척후 | Normal | Wolf | 1 | 소~중형. 빠른 선봉. 독에 변형된 날렵한 늑대 | `ch2_wolf_scout` |
| 2102 | 도마뱀 저주사 | Normal | Lizardman | 1 | 소~중형. 독 주술. 원거리 마법형 | `ch2_lizardman_hexer` |
| 2103 | 도마뱀 돌격병 | Normal | Lizardman | 2 | 중~대형. 독에 의해 비대해진 거대 도마뱀 전사. 위협 | `ch2_lizardman_charger` |

**스테이지 2 — 독무의 심림 (Demon)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 2201 | 서큐버스 유혹마 | Demon | Succubus | 1 | 중형. 시기심을 부추기는 마법. 디버프형 | `ch2_succubus_enchantress` |
| 2202 | 서큐버스 독술사 | Demon | Succubus | 1 | 중형. 독안개 마법 공격. 원거리 | `ch2_succubus_poisoner` |
| 2203 | 오크 탈취자 | Demon | Orc | 2 | 중~대형. 남의 힘을 탐내 변형된 야만 전사. 위협 | `ch2_orc_usurper` |

**스테이지 3 — 부패한 뿌리 (Undead)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 2301 | 수목 원혼 | Undead | Ghost | 1 | 소~중형. 나무에 깃든 원한의 영혼. 마법 공격 | `ch2_ghost_treespirit` |
| 2302 | 울부짖는 유령 | Undead | Ghost | 1 | 소~중형. 시기의 울음소리 저주. 디버프형 | `ch2_ghost_wailer` |
| 2303 | 뿌리 좀비 | Undead | Zombie | 2 | 중~대형. 썩은 뿌리에 얽힌 거대한 시체. 위협 | `ch2_zombie_rotroot` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 |
|----------|------|--------|------|-------------|-------------|----------|
| 1 | 독의 지배자 | 사마엘 (Samael) | 탈무드/조하르 | Normal | Lizardman | 죽음의 천사, 독의 천사. 유명세★5 연관도★4. 에덴의 뱀=파충류→Lizardman. Ch2 중독 상태이상과 직결 |
| 2 | 시기의 어머니 | 아비주 (Abyzou) | 솔로몬의 유언 | Demon | Succubus | 불임 저주, 타인의 아이를 시기하여 살해. 연관도★5. 시기 그 자체의 악마. Succubus=저주 여성형 |
| 3 | 부패한 곡성 | 밴시 (Banshee) | 아일랜드 민속 | Undead | Ghost | 죽음 예고 울음소리. 유명세★5 연관도★5. 시기의 울음·원한. Ghost=여성 원혼 완벽 매칭 |

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

**디자인 방향**
- 공통: 황금빛 저주, 모래에 오염된 고대 유물, 탐욕에 물든 형상
- Normal: 사막 폐허에서 보물을 지키거나 약탈하는 생물
- Undead: 보물과 함께 묻힌 저주받은 망자들
- Demon: 황금에 미친 악마, 보물고의 수호자

**챕터 고유 인스턴스**

**스테이지 1 — 모래에 묻힌 폐허 (Normal)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 3101 | 사막 도마뱀 약탈자 | Normal | Lizardman | 1 | 소~중형. 빠른 근접. 폐허의 보물 사냥꾼 | `ch3_lizardman_raider` |
| 3102 | 사막 도마뱀 주술사 | Normal | Lizardman | 1 | 소~중형. 모래 마법. 원거리 | `ch3_lizardman_shaman` |
| 3103 | 사암 골렘 | Normal | Golem | 2 | 중~대형. 폐허에서 깨어난 거대 석상. 위협 | `ch3_golem_sandstone` |

**스테이지 2 — 저주받은 지하묘지 (Undead)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 3201 | 해골 수호병 | Undead | Skeleton | 1 | 소~중형. 묘지 수호. 근접 전사 | `ch3_skeleton_guardian` |
| 3202 | 해골 석궁병 | Undead | Skeleton | 1 | 소~중형. 원거리 물리. 지하묘지 함정 지킴이 | `ch3_skeleton_crossbow` |
| 3203 | 뱀파이어 귀족 | Undead | Vampire | 2 | 중~대형. 지하묘지의 흡혈 지배자. 위협 | `ch3_vampire_noble` |

**스테이지 3 — 황금 보물고 (Demon)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 3301 | 황금 임프 | Demon | Imp | 1 | 소형. 빠른 마법 공격. 보물고의 마법 수비수 | `ch3_imp_goldfire` |
| 3302 | 고블린 약탈병 | Demon | Goblin | 1 | 소형. 잔꾀형 근접. 보물 약탈자 | `ch3_goblin_looter` |
| 3303 | 고블린 금고지기 | Demon | Goblin | 2 | 중~대형. 황금 갑옷의 거대 고블린 대장. 위협 | `ch3_goblin_vaultkeeper` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 |
|----------|------|--------|------|-------------|-------------|----------|
| 1 | 모래에 묻힌 신 | 다곤 (Dagon) | 사무엘상/블레셋 | Normal | Golem | 반인반어 고대 신. 유명세★4 연관도★4. 사막 폐허의 고대 신전에서 깨어난 석상. Golem=움직이는 신상 |
| 2 | 탐욕의 뱃사공 | 카론 (Charon) | 그리스 신화 | Undead | Skeleton | 스틱스 강의 뱃사공, 동전 요구. 유명세★4 연관도★4. "대가를 치르지 않으면 건너지 못한다"=탐욕. Skeleton=해골 뱃사공 |
| 3 | 황금의 거래자 | 메피스토펠레스 (Mephistopheles) | 파우스트 전설 | Demon | Gargoyle | 영혼 거래의 아이콘. 유명세★5 연관도★5. 탐욕의 최종 상징. Gargoyle=날개 달린 위엄있는 악마 |

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

**디자인 방향**
- 공통: 얼어붙은 외형, 서리/빙결 효과, 느리고 둔중하거나 유령처럼 차가운
- Undead: 영원히 얼어붙어 멈추지 못하는 망자들
- Demon: 빙하 요새를 점거한 동토의 악마 군단
- Normal: 극한의 추위에 적응한 거대 생물

**챕터 고유 인스턴스**

**스테이지 1 — 얼어붙은 평원 (Undead)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 4101 | 서리 원혼 | Undead | Ghost | 1 | 소~중형. 냉기 마법 공격. 얼어붙은 영혼 | `ch4_ghost_frostwraith` |
| 4102 | 동결 곡성귀 | Undead | Ghost | 1 | 소~중형. 빙결 저주. 울부짖는 디버프형 | `ch4_ghost_frostwailer` |
| 4103 | 빙결 좀비 | Undead | Zombie | 2 | 중~대형. 얼음에 묻혀있던 거대한 시체. 위협 | `ch4_zombie_frozen` |

**스테이지 2 — 빙하 요새 (Demon)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 4201 | 서리 고블린 병사 | Demon | Goblin | 1 | 소형. 빙하 요새의 경비병. 근접 | `ch4_goblin_frostguard` |
| 4202 | 얼음 임프 | Demon | Imp | 1 | 소형. 냉기 마법. 원거리 | `ch4_imp_icecaster` |
| 4203 | 고블린 빙하대장 | Demon | Goblin | 2 | 중~대형. 얼음 갑옷의 거대 고블린 대장. 위협 | `ch4_goblin_glaciercaptain` |

**스테이지 3 — 영구동결의 심부 (Normal)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 |
|------------|------|-------------|-------------|-----------|------|---------|
| 4301 | 예티 척후 | Normal | Yeti | 1 | 중형. 설인 정찰병. 빠른 근접 | `ch4_yeti_scout` |
| 4302 | 예티 투석병 | Normal | Yeti | 1 | 중형. 얼음 덩이를 던지는 원거리 | `ch4_yeti_hurler` |
| 4303 | 트롤 빙하거인 | Normal | Troll | 2 | 대형. 얼어붙은 피부의 거대 트롤. 위협 | `ch4_troll_glacier` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 |
|----------|------|--------|------|-------------|-------------|----------|
| 1 | 동토의 설녀 | 유키온나 (Yuki-onna) | 일본 민속 | Undead | Ghost | 눈보라 속 유령 여인, 얼려 죽임. 유명세★4 연관도★5. Ch4 빙결 상태이상 직결. Ghost=유령 여인 |
| 2 | 빙하의 태공 | 아스타로스 (Astaroth) | 고에티아 #29 | Demon | Gargoyle | 게으름·허영의 악마. 유명세★4 연관도★4. 날개 달린 타락천사. Gargoyle=날개 달린 석상 악마 |
| 3 | 얼어붙은 바람왕 | 파주주 (Pazuzu) | 메소포타미아 | Normal | Troll | 남서풍의 왕. 유명세★5. 한때 바람을 지배했으나 동토에 영원히 얼어붙은 존재 — 강제된 정지=나태의 거울. Troll=얼어붙어 둔중해진 거대 형체 |

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
