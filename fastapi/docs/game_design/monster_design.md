# 몬스터 설계

> 설계 규칙: [monster_guide.md](monster_guide.md)
> 몬스터 스탯 데이터: `fastapi/meta_data/monster_info.csv`

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

**스테이지 3 — 원한의 묘지 (Undead)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 1301 | 스켈레톤 전사 | Undead | Skeleton | 1 | 소~중형. 검+방패 근접. 묘지에서 일어난 기본 해골 병사 | `ch1_skeleton_warrior` | `16-bit pixel art, undead skeleton warrior with fully exposed white bare bones, no armor on torso, wielding a chipped sword and battered shield, upright combat stance facing left, pale white bone texture with ember cracks glowing orange, hollow eye sockets burning with red ghostly flame, tattered war cape singed by fire hanging from shoulder bones, graveyard dirt clinging to joints, white background, fantasy RPG enemy sprite` |
| 1302 | 스켈레톤 궁수 | Undead | Skeleton | 1 | 소~중형. 원거리 물리. 묘지 뒤편에서 쏘는 해골 사수 | `ch1_skeleton_archer` | `16-bit pixel art, undead skeleton archer with fully exposed white bare ribcage and spine, no armor on body, drawing a cracked longbow with a flaming arrow nocked, aiming stance facing left, pale white bone texture with faint orange embers smoldering between exposed ribs, skull jaw hanging slightly open, quiver of charred arrows strapped to bare spine, white background, fantasy RPG enemy sprite` |
| 1303 | 스켈레톤 기사 | Undead | Skeleton | 2 | 중~대형. 해골 말을 탄 기마 전사. 이 스테이지의 위협 | `ch1_skeleton_knight` | `16-bit pixel art, undead skeleton knight riding a skeletal warhorse, fully exposed white bare bones on both rider and mount, no armor on bodies except a dark ornate Japanese kabuto helmet with curved horns on the rider skull, rider wielding a long tattered lance facing left, pale white bone texture, hollow eye sockets burning with red ghostly flame on both rider and horse, tattered war banner trailing from lance, graveyard dirt on hooves, white background, fantasy RPG enemy sprite` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 | 아트 프롬프트 |
|----------|------|--------|------|-------------|-------------|----------|-------------|
| 1 | 파멸의 군주 | 아바돈 (Abaddon) | 요한계시록 | Demon | Orc | 무저갱의 왕 "파괴자". 유명세★5 연관도★5. 분노/파괴의 직결 상징. Orc=거대한 파괴의 화신 | `16-bit pixel art, massive demonic destroyer king in heavy spiked black armor, wielding a colossal jagged greatsword wreathed in hellfire, towering muscular build with curved ram horns and burning crimson eyes, tattered dark cape billowing with ember sparks, scorched battlefield debris at feet, white background, fantasy RPG boss sprite` |
| 2 | 천의 목소리 | 레기온 (Legion) | 신약 마가복음 | Normal | Human | "우리는 군단이라 하라". 유명세★5. 하나의 몸에 천 개의 분노가 깃든 타락 인간. Human=군단이 깃든 인간 병사 | `16-bit pixel art, corrupted human warrior possessed by a thousand souls, contorted muscular body in cracked bloodstained armor, multiple ghostly faces emerging from torso and shoulders screaming in rage, wielding a massive war hammer, wild bloodshot eyes with dark veins spreading across skin, faint spectral aura of trapped souls swirling around the body, white background, fantasy RPG boss sprite` |
| 3 | 머리 없는 전쟁귀 | 둘라한 (Dullahan) | 아일랜드 민속 | Undead | Skeleton | 목 없는 기사. 유명세★4 연관도★4. 전장+묘지 테마 양쪽 커버. Skeleton=해골 기마 전사 | `16-bit pixel art, headless skeleton knight riding a skeletal black warhorse, carrying own burning skull in left hand held high, wielding a spectral whip made of spine bones in right hand, tattered dark armor with ember cracks glowing orange, hollow skull eyes burning with intense red ghostly flame, graveyard mist swirling at horse hooves, white background, fantasy RPG boss sprite` |

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

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 2101 | 독늑대 척후 | Normal | Wolf | 1 | 소~중형. 빠른 선봉. 독에 변형된 날렵한 늑대 | `ch2_wolf_scout` | `16-bit pixel art, mutated wolf with patches of toxic green fur and exposed veins, hunched aggressive stalking stance facing left, asymmetric body with one eye larger than the other, dripping green venom from fangs, twisted spine with bony protrusions, dark forest fog around paws, white background, fantasy RPG enemy sprite` |
| 2102 | 도마뱀 저주사 | Normal | Lizardman | 1 | 소~중형. 독 주술. 원거리 마법형 | `ch2_lizardman_hexer` | `16-bit pixel art, upright lizardman shaman with mottled green and purple scales, holding a twisted wooden staff dripping with poison, hunched casting stance facing left, one arm visibly larger and more mutated than the other, glowing toxic green runes on skin, tattered vine robes, white background, fantasy RPG enemy sprite` |
| 2103 | 도마뱀 돌격병 | Normal | Lizardman | 2 | 중~대형. 독에 의해 비대해진 거대 도마뱀 전사. 위협 | `ch2_lizardman_charger` | `16-bit pixel art, massive mutated lizardman warrior with grotesquely swollen muscles and asymmetric limbs, wielding a heavy bone club with one enlarged arm, charging stance facing left, dark green scales cracked with toxic purple veins, jaw distorted and oversized, towering hulking silhouette, white background, fantasy RPG enemy sprite` |

**스테이지 2 — 독무의 심림 (Demon)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 2201 | 서큐버스 유혹마 | Demon | Succubus | 1 | 중형. 시기심을 부추기는 마법. 디버프형 | `ch2_succubus_enchantress` | `16-bit pixel art, envious succubus enchantress with pale green skin and dark twisted horns, wearing tattered black robes with vine-like patterns, casting a green hypnotic spell from raised hands facing left, jealous glowing green eyes, asymmetric bat wings one larger than the other, toxic mist curling around feet, white background, fantasy RPG enemy sprite` |
| 2202 | 서큐버스 독술사 | Demon | Succubus | 1 | 중형. 독안개 마법 공격. 원거리 | `ch2_succubus_poisoner` | `16-bit pixel art, poison succubus witch with sickly green-tinged skin, hurling a glob of toxic purple venom from clawed hands facing left, wearing a dark corset with thorny vine decorations, venomous snake coiled around one arm, sharp fangs visible in a snarl, poisonous fog trailing behind, white background, fantasy RPG enemy sprite` |
| 2203 | 오크 탈취자 | Demon | Orc | 2 | 중~대형. 남의 힘을 탐내 변형된 야만 전사. 위협 | `ch2_orc_usurper` | `16-bit pixel art, massive orc usurper with mismatched stolen armor pieces from different warriors, wielding two different weapons — a stolen knight sword in one hand and a stolen mace in the other, hulking stance facing left, envious green glowing eyes, toxic green veins pulsing across grey skin, trophies of defeated foes hanging from belt, white background, fantasy RPG enemy sprite` |

**스테이지 3 — 부패한 뿌리 (Undead)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 2301 | 수목 원혼 | Undead | Ghost | 1 | 소~중형. 나무에 깃든 원한의 영혼. 마법 공격 | `ch2_ghost_treespirit` | `16-bit pixel art, translucent ghostly spirit trapped inside a twisted dead tree trunk, upper body emerging from bark with spectral green glow, reaching out with wispy clawed hands facing left, hollow eyes weeping green ectoplasm, dark roots growing through the transparent body, white background, fantasy RPG enemy sprite` |
| 2302 | 울부짖는 유령 | Undead | Ghost | 1 | 소~중형. 시기의 울음소리 저주. 디버프형 | `ch2_ghost_wailer` | `16-bit pixel art, wailing female ghost with long flowing spectral hair, mouth wide open in an endless shriek facing left, translucent pale green body with dark root-like veins visible inside, tattered burial shroud wrapped in dead vines, tears of green poison streaming from hollow eyes, white background, fantasy RPG enemy sprite` |
| 2303 | 뿌리 좀비 | Undead | Zombie | 2 | 중~대형. 썩은 뿌리에 얽힌 거대한 시체. 위협 | `ch2_zombie_rotroot` | `16-bit pixel art, massive rotting zombie entangled in thick dead tree roots growing through its body, lumbering stance facing left, bloated decayed flesh with patches of toxic green fungus, one arm replaced entirely by a thick gnarled root used as a club, hollow jaw hanging open, dirt and moss covering shoulders, white background, fantasy RPG enemy sprite` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 | 아트 프롬프트 |
|----------|------|--------|------|-------------|-------------|----------|-------------|
| 1 | 독의 지배자 | 사마엘 (Samael) | 탈무드/조하르 | Normal | Lizardman | 죽음의 천사, 독의 천사. 유명세★5 연관도★4. 에덴의 뱀=파충류→Lizardman. Ch2 중독 상태이상과 직결 | `16-bit pixel art, fallen angel in serpentine form — tall reptilian humanoid with dark iridescent scales, tattered angelic wings now blackened and dripping venom, wielding a curved poisoned blade, aristocratic stance facing left, crown of twisted thorns on serpent-like head, toxic green mist emanating from body, six glowing green eyes, white background, fantasy RPG boss sprite` |
| 2 | 시기의 어머니 | 아비주 (Abyzou) | 솔로몬의 유언 | Demon | Succubus | 불임 저주, 타인의 아이를 시기하여 살해. 연관도★5. 시기 그 자체의 악마. Succubus=저주 여성형 | `16-bit pixel art, jealous demon mother with wild dark hair writhing like snakes, pale sickly skin with green veins of envy visible beneath, tattered dark robes with thorny vine patterns, casting a green curse from elongated clawed fingers facing left, hollow envious eyes glowing toxic green, spectral chains of stolen souls trailing behind, white background, fantasy RPG boss sprite` |
| 3 | 부패한 곡성 | 밴시 (Banshee) | 아일랜드 민속 | Undead | Ghost | 죽음 예고 울음소리. 유명세★5 연관도★5. 시기의 울음·원한. Ghost=여성 원혼 완벽 매칭 | `16-bit pixel art, spectral banshee queen with flowing white hair and mouth torn open in an eternal wail, translucent pale body wrapped in rotting roots and dead vines, hovering above ground facing left, shockwave of green spectral sound rippling outward from mouth, hollow eyes streaming with ghostly green tears, tattered burial gown fused with dark tree bark, white background, fantasy RPG boss sprite` |

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

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 3101 | 사막 도마뱀 약탈자 | Normal | Lizardman | 1 | 소~중형. 빠른 근접. 폐허의 보물 사냥꾼 | `ch3_lizardman_raider` | `16-bit pixel art, desert lizardman raider with sandy brown scales and golden jewelry stolen from ruins, wielding a curved scimitar and small round shield, crouched aggressive stance facing left, golden armband and necklace glinting with cursed glow, tattered desert cloth wrapped around waist, sand dust at feet, white background, fantasy RPG enemy sprite` |
| 3102 | 사막 도마뱀 주술사 | Normal | Lizardman | 1 | 소~중형. 모래 마법. 원거리 | `ch3_lizardman_shaman` | `16-bit pixel art, desert lizardman shaman with pale sand-colored scales, holding a golden staff topped with a cursed gemstone, casting stance with sand particles swirling around facing left, ancient Egyptian-style golden headdress, hieroglyph tattoos glowing faintly on scales, tattered linen robes, white background, fantasy RPG enemy sprite` |
| 3103 | 사암 골렘 | Normal | Golem | 2 | 중~대형. 폐허에서 깨어난 거대 석상. 위협 | `ch3_golem_sandstone` | `16-bit pixel art, massive sandstone golem assembled from ancient ruin blocks with hieroglyph carvings glowing gold on its body, towering stance facing left, cracked stone surface with golden cursed light seeping through fractures, one arm formed from a broken stone pillar, ancient crown fragment embedded in head, sand cascading from joints, white background, fantasy RPG enemy sprite` |

**스테이지 2 — 저주받은 지하묘지 (Undead)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 3201 | 해골 수호병 | Undead | Skeleton | 1 | 소~중형. 묘지 수호. 근접 전사 | `ch3_skeleton_guardian` | `16-bit pixel art, undead skeleton guardian in ancient Egyptian-style bronze armor with golden curse markings, wielding a khopesh sword and tall rectangular shield, upright defensive stance facing left, golden light glowing from eye sockets, cobwebs and tomb dust on bones, tattered linen wrappings on limbs, white background, fantasy RPG enemy sprite` |
| 3202 | 해골 석궁병 | Undead | Skeleton | 1 | 소~중형. 원거리 물리. 지하묘지 함정 지킴이 | `ch3_skeleton_crossbow` | `16-bit pixel art, undead skeleton crossbowman crouching behind a golden-trimmed repeating crossbow, aiming stance facing left, ancient bronze chest piece with curse engravings, bolt quiver strapped to spine with golden-tipped bolts, jaw wired shut with golden wire, cobwebs between ribs, white background, fantasy RPG enemy sprite` |
| 3203 | 뱀파이어 귀족 | Undead | Vampire | 2 | 중~대형. 지하묘지의 흡혈 지배자. 위협 | `ch3_vampire_noble` | `16-bit pixel art, aristocratic vampire lord in ornate golden-trimmed black robes and jeweled crown, pale skin with golden cursed veins visible, elongated fangs bared in a predatory smile facing left, one hand extended with sharp claws dripping blood, red cape lined with gold, towering regal presence, ancient Egyptian jewelry adorning neck and wrists, white background, fantasy RPG enemy sprite` |

**스테이지 3 — 황금 보물고 (Demon)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 3301 | 황금 임프 | Demon | Imp | 1 | 소형. 빠른 마법 공격. 보물고의 마법 수비수 | `ch3_imp_goldfire` | `16-bit pixel art, small golden-skinned imp crackling with cursed golden fire in both hands, mischievous hovering stance facing left, tiny bat wings with golden membrane, sharp grin with golden teeth, wearing a tiny crown of stolen coins, molten gold dripping from fingertips, white background, fantasy RPG enemy sprite` |
| 3302 | 고블린 약탈병 | Demon | Goblin | 1 | 소형. 잔꾀형 근접. 보물 약탈자 | `ch3_goblin_looter` | `16-bit pixel art, greedy goblin soldier draped in stolen golden chains and jewelry, wielding a jagged dagger in one hand and clutching a stolen golden goblet in the other, hunched sneaking stance facing left, bulging sack of treasure on back, golden light reflecting off beady envious eyes, white background, fantasy RPG enemy sprite` |
| 3303 | 고블린 금고지기 | Demon | Goblin | 2 | 중~대형. 황금 갑옷의 거대 고블린 대장. 위협 | `ch3_goblin_vaultkeeper` | `16-bit pixel art, massive goblin vault captain in heavy golden plate armor with ornate engravings, wielding a giant golden war hammer with both hands, imposing stance facing left, oversized golden crown tilted on head, thick golden chains as belt, cursed golden glow emanating from armor cracks, towering hulking build for a goblin, white background, fantasy RPG enemy sprite` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 | 아트 프롬프트 |
|----------|------|--------|------|-------------|-------------|----------|-------------|
| 1 | 모래에 묻힌 신 | 다곤 (Dagon) | 사무엘상/블레셋 | Normal | Golem | 반인반어 고대 신. 유명세★4 연관도★4. 사막 폐허의 고대 신전에서 깨어난 석상. Golem=움직이는 신상 | `16-bit pixel art, ancient stone idol of Dagon awakened — massive humanoid golem with fish-scale carved stone surface, upper body human-like lower body merging into stone pillar base, wielding a colossal stone trident, towering stance facing left, ancient Philistine hieroglyphs glowing gold across body, cracked stone revealing cursed golden light within, sand and rubble falling from joints, crown of coral and gold on stone head, white background, fantasy RPG boss sprite` |
| 2 | 탐욕의 뱃사공 | 카론 (Charon) | 그리스 신화 | Undead | Skeleton | 스틱스 강의 뱃사공, 동전 요구. 유명세★4 연관도★4. "대가를 치르지 않으면 건너지 못한다"=탐욕. Skeleton=해골 뱃사공 | `16-bit pixel art, skeletal ferryman Charon in tattered dark hooded robes standing on a ghostly boat bow, wielding a long oar-staff with a scythe blade at the tip, bony hand extended demanding payment facing left, hollow eye sockets glowing with dim golden light, ancient golden coins embedded in skull and ribcage, dark spectral river mist swirling below, white background, fantasy RPG boss sprite` |
| 3 | 황금의 거래자 | 메피스토펠레스 (Mephistopheles) | 파우스트 전설 | Demon | Gargoyle | 영혼 거래의 아이콘. 유명세★5 연관도★5. 탐욕의 최종 상징. Gargoyle=날개 달린 위엄있는 악마 | `16-bit pixel art, tall elegant demon lord Mephistopheles with dark bat wings spread wide, wearing a luxurious black suit with golden trim and a golden pocket watch chain, one hand holding a glowing golden contract scroll the other gesturing invitingly facing left, sharp aristocratic features with a confident smirk, curved horns polished like obsidian, golden eyes burning with cunning intelligence, white background, fantasy RPG boss sprite` |

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

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 4101 | 서리 원혼 | Undead | Ghost | 1 | 소~중형. 냉기 마법 공격. 얼어붙은 영혼 | `ch4_ghost_frostwraith` | `16-bit pixel art, frozen ghostly wraith with crystallized ice forming on translucent pale blue body, casting a beam of freezing energy from outstretched hands facing left, hollow eyes glowing cold blue, ice crystals forming in the air around the floating figure, tattered frost-covered burial shroud, white background, fantasy RPG enemy sprite` |
| 4102 | 동결 곡성귀 | Undead | Ghost | 1 | 소~중형. 빙결 저주. 울부짖는 디버프형 | `ch4_ghost_frostwailer` | `16-bit pixel art, wailing frost specter with mouth frozen open in an eternal scream, translucent icy blue body with visible frozen organs inside, hovering stance facing left, shockwave of ice crystals rippling from its scream, long frozen hair spiked with icicles, frost spreading on the ground below, white background, fantasy RPG enemy sprite` |
| 4103 | 빙결 좀비 | Undead | Zombie | 2 | 중~대형. 얼음에 묻혀있던 거대한 시체. 위협 | `ch4_zombie_frozen` | `16-bit pixel art, massive frozen zombie with thick layer of ice encasing half its body, lumbering stance facing left with one arm raised as a frozen club, pale blue-grey frozen flesh with frost crystals covering shoulders and head, jaw frozen partially open revealing icy teeth, chunks of ice and snow clinging to bloated frame, towering hulking silhouette, white background, fantasy RPG enemy sprite` |

**스테이지 2 — 빙하 요새 (Demon)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 4201 | 서리 고블린 병사 | Demon | Goblin | 1 | 소형. 빙하 요새의 경비병. 근접 | `ch4_goblin_frostguard` | `16-bit pixel art, frost goblin soldier in crude ice-crystal armor plates, wielding an icicle spear and small ice shield, alert guard stance facing left, blue-tinged green skin with frost patterns on face, breath visible in cold air, ice fortress wall pattern on shield, white background, fantasy RPG enemy sprite` |
| 4202 | 얼음 임프 | Demon | Imp | 1 | 소형. 냉기 마법. 원거리 | `ch4_imp_icecaster` | `16-bit pixel art, small ice imp with pale blue crystalline skin, hurling a shard of magical ice from raised claws facing left, tiny frost-covered bat wings buzzing, sharp icicle horns on head, mischievous frozen grin, trail of snowflakes following hand motion, white background, fantasy RPG enemy sprite` |
| 4203 | 고블린 빙하대장 | Demon | Goblin | 2 | 중~대형. 얼음 갑옷의 거대 고블린 대장. 위협 | `ch4_goblin_glaciercaptain` | `16-bit pixel art, massive frost goblin captain in heavy ice-crystal full plate armor with glacial blue glow, wielding a giant ice greataxe with both hands, commanding stance facing left, oversized frozen iron crown with icicle spikes, thick blue-tinged skin visible at joints, cold mist emanating from armor gaps, towering hulking build, white background, fantasy RPG enemy sprite` |

**스테이지 3 — 영구동결의 심부 (Normal)**

| monster_idx | 이름 | monster_type | monster_base | size_type | 역할 | 리소스명 | 아트 프롬프트 |
|------------|------|-------------|-------------|-----------|------|---------|-------------|
| 4301 | 예티 척후 | Normal | Yeti | 1 | 중형. 설인 정찰병. 빠른 근접 | `ch4_yeti_scout` | `16-bit pixel art, medium-sized young yeti scout with white shaggy fur, crouched aggressive stance on all fours facing left, sharp ice-blue eyes peering forward, frost clinging to fur, powerful but lean build compared to adult yeti, sharp claws scraping against frozen ground, white background, fantasy RPG enemy sprite` |
| 4302 | 예티 투석병 | Normal | Yeti | 1 | 중형. 얼음 덩이를 던지는 원거리 | `ch4_yeti_hurler` | `16-bit pixel art, medium-sized yeti hurler standing upright winding up to throw a massive chunk of ice with one arm facing left, white and grey shaggy fur with icicles hanging from arms, determined ice-blue eyes, other arm holding a second ice boulder ready, frost breath visible from snarling mouth, white background, fantasy RPG enemy sprite` |
| 4303 | 트롤 빙하거인 | Normal | Troll | 2 | 대형. 얼어붙은 피부의 거대 트롤. 위협 | `ch4_troll_glacier` | `16-bit pixel art, colossal glacier troll with skin entirely encased in thick glacial ice armor, lumbering stance facing left wielding a massive frozen stone pillar as a club, pale blue frozen skin visible through ice cracks, tiny frost-filled eyes deep in frozen skull, icicle stalactites hanging from chin and shoulders, towering hulking silhouette dwarfing other creatures, white background, fantasy RPG enemy sprite` |

**스테이지 보스**

| 스테이지 | 칭호 | 보스명 | 출전 | monster_type | monster_base | 선정 근거 | 아트 프롬프트 |
|----------|------|--------|------|-------------|-------------|----------|-------------|
| 1 | 동토의 설녀 | 유키온나 (Yuki-onna) | 일본 민속 | Undead | Ghost | 눈보라 속 유령 여인, 얼려 죽임. 유명세★4 연관도★5. Ch4 빙결 상태이상 직결. Ghost=유령 여인 | `16-bit pixel art, ethereal Yuki-onna snow woman ghost hovering above frozen ground, flowing long black hair whipping in a blizzard wind, pale white translucent skin with an eerily beautiful face, wearing a tattered white kimono dissolving into snowflakes at the hem, hands extended releasing a deadly blizzard of ice crystals facing left, hollow ice-blue eyes with frozen tears, snowstorm swirling around her figure, white background, fantasy RPG boss sprite` |
| 2 | 빙하의 태공 | 아스타로스 (Astaroth) | 고에티아 #29 | Demon | Gargoyle | 게으름·허영의 악마. 유명세★4 연관도★4. 날개 달린 타락천사. Gargoyle=날개 달린 석상 악마 | `16-bit pixel art, fallen angel duke Astaroth with massive frost-covered dark stone wings spread wide, riding atop a frozen dragon-like beast, holding a frozen viper in one hand, aristocratic yet corrupted face with ice crystals forming on skin, heavy dark armor covered in glacial frost, foul frozen mist emanating from body, cold blue glowing eyes filled with apathy, white background, fantasy RPG boss sprite` |
| 3 | 얼어붙은 바람왕 | 파주주 (Pazuzu) | 메소포타미아 | Normal | Troll | 남서풍의 왕. 유명세★5. 한때 바람을 지배했으나 동토에 영원히 얼어붙은 존재 — 강제된 정지=나태의 거울. Troll=얼어붙어 둔중해진 거대 형체 | `16-bit pixel art, ancient wind king Pazuzu frozen in eternal stillness — massive chimeric body with lion torso and eagle talons entirely encased in thick glacial ice with cracks revealing dark skin beneath, four frost-shattered wings frozen mid-spread, scorpion tail frozen solid pointing upward, face frozen in a silent roar with icicles hanging from horns and jaw, faint blue glow of trapped wind energy pulsing within the ice shell, towering colossal silhouette, white background, fantasy RPG boss sprite` |

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
