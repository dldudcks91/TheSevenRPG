# TheSevenRPG — 몬스터 픽셀아트 프롬프트

> **Part 1**: 몬스터 베이스 범용 프롬프트 (약/중/강 3단계, 15종 × 3 = 45개)
> **Part 2**: 챕터별 고유 인스턴스 프롬프트 (챕터 테마 반영)
> 몬스터 설계 스펙: → `fastapi/docs/game_design/monster_design.md` 참조

> 공통 스타일: `16-bit pixel art`, `RPG monster sprite`, `dark fantasy`,
> `white background`, `facing left`, `full body`
> 강도 표현: 약(small/worn) → 중(standard) → 강(large/armored/elite)

---

## TYPE: NORMAL — 자연 생물 및 피조물

---

### Wolf (고속 딜러)

**Wolf — 약 (Lv1)**
```
16-bit pixel art, small dark wolf, lean hungry silhouette, matted gray fur,
glowing pale yellow eyes, crouched low ready to sprint, scarred muzzle,
color palette: dark gray, charcoal, pale yellow eyes, fantasy RPG enemy sprite, white background, facing left, full body
```

**Wolf — 중 (Lv2)**
```
16-bit pixel art, mid-sized dark wolf, muscular build, sleek black-gray fur,
bright amber eyes, battle-scarred body, sharp fangs visible, aggressive stance,
color palette: dark gray, black, amber, fantasy RPG enemy sprite, white background, facing left, full body
```

**Wolf — 강 (Lv3)**
```
16-bit pixel art, large alpha wolf, massive imposing frame, dark fur with red-tinged markings,
glowing blood-red eyes, spiked bone collar, battle-worn scars across body,
aura of dark energy, color palette: black, dark red, blood red eyes,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Yeti (강타·돌격형)

**Yeti — 약 (Lv1)**
```
16-bit pixel art, small yeti, hunched posture, dirty matted white-gray fur,
small sunken dark eyes, ragged and thin, worn primitive appearance,
color palette: dirty white, ash gray, dark brown, fantasy RPG enemy sprite, white background, facing left, full body
```

**Yeti — 중 (Lv2)**
```
16-bit pixel art, large yeti, broad muscular build, thick shaggy gray-white fur,
dark sunken eyes, massive fists raised, primitive bone bracers on wrists,
imposing charging stance, color palette: gray-white, bone, dark gray,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Yeti — 강 (Lv3)**
```
16-bit pixel art, massive elite yeti, enormous hulking frame, dark gray fur with icy blue sheen,
glowing pale blue eyes, heavy stone and bone armor on shoulders,
veins visible under fur, ground-shattering stance,
color palette: dark gray, icy blue, bone white,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Troll (방어 극대화)

**Troll — 약 (Lv1)**
```
16-bit pixel art, small troll, hunched lumpy body, warty greenish-gray skin,
dull vacant eyes, clutching a crude rock, barely armored,
color palette: murky green, dark gray, brown,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Troll — 중 (Lv2)**
```
16-bit pixel art, large troll, heavily built thick body, rough stone-like dark green skin,
small beady eyes, crude wooden shield strapped to forearm, club in hand,
natural armor-like skin texture, color palette: dark green, stone gray, brown,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Troll — 강 (Lv3)**
```
16-bit pixel art, enormous elite troll, mountain-like body covered in natural rock plating,
deep green-gray skin hardened like stone, glowing green regeneration runes etched into skin,
massive spiked stone club, near-impenetrable posture,
color palette: dark green, charcoal, glowing sickly green runes,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Lizardman (균형형 — 전사+주술사)

**Lizardman — 약 (Lv1)**
```
16-bit pixel art, small lizardman, lean reptilian humanoid, dull dark green scales,
carrying a crude bone spear, simple tribal wrappings, narrow slit pupils,
color palette: dark olive green, bone, brown leather,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Lizardman — 중 (Lv2)**
```
16-bit pixel art, lizardman warrior-shaman, medium build, dark teal scaly skin,
wearing bone and hide armor, holding a spear and a glowing totem,
tribal face markings, yellow slit eyes,
color palette: dark teal, bone white, dull gold totem glow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Lizardman — 강 (Lv3)**
```
16-bit pixel art, elite lizardman warlord, powerful armored build, deep dark blue-green scales,
ornate bone plate armor with tribal carvings, dual wielding enchanted spear and staff,
glowing purple shamanic runes on scales, commanding presence,
color palette: dark teal, deep purple glow, bone, dark gold,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Golem (무기물 — 극단적 방어)

**Golem — 약 (Lv1)**
```
16-bit pixel art, small crumbling stone golem, crude lumpy shape, cracked gray stone body,
dim fading light in eye sockets, missing chunks of stone, barely held together,
color palette: cracked gray, dark stone, faint dull glow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Golem — 중 (Lv2)**
```
16-bit pixel art, stone golem, solid rectangular body of dark stone blocks,
glowing amber core visible in chest cavity, heavy arms like pillars,
moss and dirt embedded in stone surface,
color palette: dark stone gray, amber core glow, earthy brown,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Golem — 강 (Lv3)**
```
16-bit pixel art, massive fortress golem, enormous body of dark iron-reinforced stone,
blazing orange core pulsating in chest, rune engravings glowing across entire surface,
impenetrable fortress-like silhouette, slow but absolute,
color palette: near-black stone, iron dark, blazing orange core, rune gold,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

## TYPE: DEMON — 지옥/마법 계열 존재

---

### Imp (빠른 마법형)

**Imp — 약 (Lv1)**
```
16-bit pixel art, tiny imp, small winged demon, scrawny red-dark skin, oversized head,
small curved horns, mischievous grin, tiny clawed hands,
color palette: dark red, deep maroon, pale yellow eyes,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Imp — 중 (Lv2)**
```
16-bit pixel art, imp caster, small winged demon hovering, dark crimson skin,
glowing purple magic orb in hand, sharp horns, tattered dark wings,
sinister glowing eyes, casting pose,
color palette: dark crimson, deep purple magic, black wings,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Imp — 강 (Lv3)**
```
16-bit pixel art, elite imp sorcerer, small but radiating dark power, black-crimson skin,
large curved horns wreathed in purple flame, dark wings spread wide,
summoning dark sigil, eyes burning violet, small but terrifying presence,
color palette: black, dark crimson, violet flame, glowing purple sigil,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Goblin (잔꾀·집단형)

**Goblin — 약 (Lv1)**
```
16-bit pixel art, small goblin, scrawny hunched figure, dull sickly green skin,
wearing scraps of stolen cloth, clutching a rusty dagger, beady yellow eyes,
sneaky cowardly posture, color palette: murky green, rust brown, dirty yellow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Goblin — 중 (Lv2)**
```
16-bit pixel art, goblin raider, lean cunning build, dark green skin, wearing patchwork leather armor,
carrying a short sword and crude bomb, calculating eyes, wicked grin,
color palette: dark green, dark leather brown, rusty metal,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Goblin — 강 (Lv3)**
```
16-bit pixel art, goblin warchief, stocky commanding figure, deep olive green skin,
wearing looted mismatched heavy armor pieces, wielding a cleaver and a shield with a skull emblem,
scarred face with red war paint, fierce eyes,
color palette: dark olive green, dark iron, red war paint, skull motif,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Succubus (디버프·마법형)

**Succubus — 약 (Lv1)**
```
16-bit pixel art, lesser succubus, slender demonic female figure, pale ashen skin,
small dark wings, basic dark robe, faint hypnotic eyes, subtle dark aura,
color palette: pale ash, dark maroon, faint purple aura,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Succubus — 중 (Lv2)**
```
16-bit pixel art, succubus enchantress, alluring but sinister demonic figure,
pale skin with dark purple veins, large dark wings half-spread,
casting a purple debuff curse, glowing violet eyes, dark elegant attire,
color palette: pale lavender-gray skin, deep purple, black wings, violet glow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Succubus — 강 (Lv3)**
```
16-bit pixel art, elite succubus queen, commanding dark demonic figure,
deep crimson and black skin markings, massive dark feathered wings fully spread,
surrounded by swirling dark curse sigils, burning violet eyes,
dark crown of bone horns, radiating corruption,
color palette: deep crimson, void black, burning violet, bone white horns,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Gargoyle (방어형)

**Gargoyle — 약 (Lv1)**
```
16-bit pixel art, small gargoyle, crouched stone-like winged creature, rough gray stone skin,
dim glowing eyes, folded cracked wings, small horns, dormant appearance,
color palette: cold stone gray, dark shadow, faint dim glow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Gargoyle — 중 (Lv2)**
```
16-bit pixel art, gargoyle sentinel, medium build stone demon, dark granite skin texture,
wide stone wings spread, glowing orange eyes, natural stone armor plating on body,
defensive stance, color palette: dark granite, shadow gray, orange ember eyes,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Gargoyle — 강 (Lv3)**
```
16-bit pixel art, elite gargoyle fortress, massive stone demon, near-black obsidian-like skin,
enormous thick wings like castle walls, infernal orange-red glow from cracks in stone body,
impenetrable stone plate natural armor, terrifying guardian stance,
color palette: obsidian black, dark stone, infernal orange-red cracks,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Orc (야만 강타형)

**Orc — 약 (Lv1)**
```
16-bit pixel art, small orc, stocky primitive build, dull gray-green skin, barely clothed in hides,
carrying a crude wooden club, small tusks, dull aggressive eyes,
color palette: gray-green, dark hide brown, bone,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Orc — 중 (Lv2)**
```
16-bit pixel art, orc berserker, muscular heavy build, dark gray-green skin,
wearing crude iron armor, wielding a massive axe, prominent tusks,
blood-stained and battle-scarred, furious expression,
color palette: dark gray-green, iron gray, dried blood dark red,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Orc — 강 (Lv3)**
```
16-bit pixel art, elite orc warlord, enormous brutish figure, deep dark green skin,
covered in heavy spiked black iron armor, massive double-headed axe,
glowing red war tattoos covering arms and face, berserker rage aura,
color palette: dark green, black iron, blood red glowing tattoos,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

## TYPE: UNDEAD — 죽어서 되살아난 존재

---

### Skeleton (밸런스형)

**Skeleton — 약 (Lv1)**
```
16-bit pixel art, small skeleton, thin rattling bones, yellowed old bone,
holding a cracked sword, hollow dark eye sockets with faint glow,
barely held together, shambling stance,
color palette: aged bone yellow, dark shadow, faint pale glow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Skeleton — 중 (Lv2)**
```
16-bit pixel art, skeleton warrior, complete bone frame, dark yellowed bones,
wearing rusted chainmail, carrying a sword and cracked shield,
purple soul-fire burning in eye sockets, disciplined undead stance,
color palette: bone white, rusted iron, purple soul-fire,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Skeleton — 강 (Lv3)**
```
16-bit pixel art, elite skeleton knight, imposing armored skeleton, dark reinforced bone frame,
wearing blackened plate armor with purple runes, wielding a cursed greatsword,
intense purple soul-fire eyes, dark undead energy crackling around weapon,
color palette: darkened bone, black plate armor, glowing purple runes,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Zombie (느린 고체력)

**Zombie — 약 (Lv1)**
```
16-bit pixel art, small zombie, hunched shambling corpse, pale gray-green decaying skin,
tattered rags, missing limbs partially, empty hollow eyes,
slow lurching posture, color palette: pale gray-green, decay brown, dark shadow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Zombie — 중 (Lv2)**
```
16-bit pixel art, zombie brute, large bloated undead corpse, dark sickly green-gray skin,
visible rotting wounds and exposed bone, dragging a heavy limb as weapon,
cloudy dead eyes, overwhelming decayed mass,
color palette: dark sickly green, necrotic gray, dark brown decay,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Zombie — 강 (Lv3)**
```
16-bit pixel art, elite zombie titan, enormous decayed undead mass, dark gray-green bloated body,
fused bone armor protrusions growing from rotting flesh, dark necrotic aura,
thick chains embedded in body, empty glowing sickly green eyes,
virtually unkillable appearance, color palette: near-black decay, sickly green glow, bone protrusions,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Ghost (물리방어↓ 마법저항↑)

**Ghost — 약 (Lv1)**
```
16-bit pixel art, small ghost, translucent pale wisp, barely visible ethereal form,
faint sorrowful face, fading in and out of visibility, hovering slightly above ground,
color palette: translucent pale white, cold blue, near-invisible edges,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Ghost — 중 (Lv2)**
```
16-bit pixel art, ghost specter, floating ethereal figure, semi-transparent pale blue-white form,
distorted screaming face, dark shadowy core, tattered spirit robes,
cold magical aura, color palette: pale blue, cold white, dark void core,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Ghost — 강 (Lv3)**
```
16-bit pixel art, elite ghost wraith, large powerful ethereal entity, deep blue-black translucent form,
multiple distorted faces swirling within, crackling dark magical energy,
near-untouchable presence, cold necrotic aura that distorts surroundings,
color palette: deep cold blue, void black, pale white soul glow,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Vampire (흡혈 공격형)

**Vampire — 약 (Lv1)**
```
16-bit pixel art, lesser vampire, pale gaunt humanoid, sunken dark eyes, small fangs,
tattered dark nobleman's coat, hunched predatory stance,
faint blood-red glow in eyes, color palette: pale gray skin, dark maroon coat, blood red,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Vampire — 중 (Lv2)**
```
16-bit pixel art, vampire hunter, elegant deadly figure, marble pale skin,
dark elegant armor with blood-red trim, glowing crimson eyes,
bat-like dark cloak spread like wings, blood dripping from clawed hands,
color palette: pale white, void black, blood crimson, dark maroon,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Vampire — 강 (Lv3)**
```
16-bit pixel art, elite vampire lord, commanding aristocratic dark figure, flawlessly pale skin,
black full plate armor with crimson rune engravings, massive dark cape like demon wings,
deep blood-red glowing eyes, surrounded by blood mist aura,
ancient terrifying noble bearing,
color palette: void black armor, blood red runes, pale white, blood crimson mist,
fantasy RPG enemy sprite, white background, facing left, full body
```

---

### Lich (마법 극대화)

**Lich — 약 (Lv1)**
```
16-bit pixel art, lesser lich, skeletal robed figure, yellowed bones visible under tattered dark robes,
dim glowing green eye sockets, clutching a cracked staff,
faint necrotic aura, color palette: aged bone, dark tattered gray, dim green glow,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Lich — 중 (Lv2)**
```
16-bit pixel art, lich sorcerer, skeletal undead mage, dark ornate robes with glowing runes,
bright green-blue soul fire in eye sockets, hovering off the ground,
summoning dark necrotic spellcraft, staff crackling with death magic,
color palette: void black robes, glowing rune gold, soul-fire blue-green,
fantasy RPG enemy sprite, white background, facing left, full body
```

**Lich — 강 (Lv3)**
```
16-bit pixel art, elite lich archmage, ancient impossibly powerful skeletal mage,
dark crown of black bone, elaborate dark robes with swirling death runes,
twin soul-fire eyes blazing intense violet-green, surrounded by orbiting dark magic sigils,
phylactery orb floating at chest radiating necrotic energy,
color palette: void black, glowing violet-green, gold rune detail, bone white,
fantasy RPG enemy sprite, white background, facing left, full body
```

---
---

# Part 2 — 챕터별 고유 인스턴스 프롬프트

> 공통 스타일: `16-bit pixel art`, `facing left`, `white background`, `fantasy RPG enemy sprite`
> 보스: `fantasy RPG boss sprite`
> 각 인스턴스는 베이스 종족을 기반으로 챕터 테마(죄악/상태이상/환경)를 반영

---

## Chapter 1 — 분노 「불타는 전장」

> 테마: 불꽃에 그을린 흔적, 분노로 일그러진 표정·자세

### 스테이지 1 — 파멸의 진영 (Demon)

**ch1_goblin_scout** — 고블린 척후병
```
16-bit pixel art, small green goblin soldier in ragged leather armor, wielding a short dagger, hunched aggressive stance facing left, scorched burn marks on skin and armor, ember sparks around feet, white background, fantasy RPG enemy sprite
```

**ch1_goblin_warrior** — 고블린 전사
```
16-bit pixel art, small green goblin soldier in iron helmet and chest plate, wielding a rusty sword and cracked shield, upright combat stance facing left, battle-worn fire-scorched armor, red glowing eyes filled with rage, white background, fantasy RPG enemy sprite
```

**ch1_orc_warrior** — 오크 전사
```
16-bit pixel art, large muscular orc warrior in heavy battle-scarred iron armor, wielding a massive war axe with both hands, towering intimidating stance facing left, flames scorching pauldrons, veins bulging with uncontrollable wrath, white background, fantasy RPG enemy sprite
```

### 스테이지 2 — 핏빛 교전지대 (Normal)

**ch1_human_infantry** — 인간 보병
```
16-bit pixel art, corrupted human soldier in battered iron armor, wielding a blood-stained sword and cracked shield, upright combat stance facing left, veins visible on neck and arms pulsing with rage, helmet cracked and scorched, wild bloodshot eyes, white background, fantasy RPG enemy sprite
```

**ch1_human_spearman** — 인간 창병
```
16-bit pixel art, corrupted human spearman in scorched leather armor, thrusting a long iron-tipped spear forward facing left, aggressive lunging stance, burn scars across exposed arms, jaw clenched in uncontrollable wrath, torn cape trailing behind, white background, fantasy RPG enemy sprite
```

**ch1_troll_charger** — 트롤 돌격병
```
16-bit pixel art, massive battle-scarred troll in crude iron pauldrons, charging stance with a large spiked club raised facing left, thick grey warty skin covered in slash wounds and ember burns, sunken rage-filled eyes glowing faintly red, towering hulking silhouette, white background, fantasy RPG enemy sprite
```

### 스테이지 3 — 원한의 묘지 (Undead)

**ch1_skeleton_warrior** — 스켈레톤 전사
```
16-bit pixel art, undead skeleton warrior with fully exposed white bare bones, no armor on torso, wielding a chipped sword and battered shield, upright combat stance facing left, pale white bone texture with ember cracks glowing orange, hollow eye sockets burning with red ghostly flame, tattered war cape singed by fire hanging from shoulder bones, graveyard dirt clinging to joints, white background, fantasy RPG enemy sprite
```

**ch1_skeleton_archer** — 스켈레톤 궁수
```
16-bit pixel art, undead skeleton archer with fully exposed white bare ribcage and spine, no armor on body, drawing a cracked longbow with a flaming arrow nocked, aiming stance facing left, pale white bone texture with faint orange embers smoldering between exposed ribs, skull jaw hanging slightly open, quiver of charred arrows strapped to bare spine, white background, fantasy RPG enemy sprite
```

**ch1_skeleton_knight** — 스켈레톤 기사
```
16-bit pixel art, undead skeleton knight riding a skeletal warhorse, fully exposed white bare bones on both rider and mount, no armor on bodies except a dark ornate Japanese kabuto helmet with curved horns on the rider skull, rider wielding a long tattered lance facing left, pale white bone texture, hollow eye sockets burning with red ghostly flame on both rider and horse, tattered war banner trailing from lance, graveyard dirt on hooves, white background, fantasy RPG enemy sprite
```

### Ch1 보스

**아바돈 (Abaddon)** — 파멸의 군주
```
16-bit pixel art, massive demonic destroyer king in heavy spiked black armor, wielding a colossal jagged greatsword wreathed in hellfire, towering muscular build with curved ram horns and burning crimson eyes, tattered dark cape billowing with ember sparks, scorched battlefield debris at feet, white background, fantasy RPG boss sprite
```

**레기온 (Legion)** — 천의 목소리
```
16-bit pixel art, corrupted human warrior possessed by a thousand souls, contorted muscular body in cracked bloodstained armor, multiple ghostly faces emerging from torso and shoulders screaming in rage, wielding a massive war hammer, wild bloodshot eyes with dark veins spreading across skin, faint spectral aura of trapped souls swirling around the body, white background, fantasy RPG boss sprite
```

**둘라한 (Dullahan)** — 머리 없는 전쟁귀
```
16-bit pixel art, headless skeleton knight riding a skeletal black warhorse, carrying own burning skull in left hand held high, wielding a spectral whip made of spine bones in right hand, tattered dark armor with ember cracks glowing orange, hollow skull eyes burning with intense red ghostly flame, graveyard mist swirling at horse hooves, white background, fantasy RPG boss sprite
```

**몰록 (Moloch)** — 불의 심복
```
16-bit pixel art, massive gargoyle demon gatekeeper with obsidian-black stone skin cracked with molten orange veins, enormous curved bull horns wreathed in hellfire, broad heavy wings folded like fortress walls behind towering muscular frame, wielding a colossal bronze sacrificial brazier-mace burning with eternal flame, standing in an immovable guardian stance facing left, infernal orange glow pouring from chest cavity like a furnace, eyes burning solid white-hot with fanatical devotion, white background, fantasy RPG boss sprite
```

**사탄 (Satan)** — Ch1 챕터 보스 · 추방자의 복수
```
16-bit pixel art, fallen demon king Satan in shattered obsidian armor with molten cracks bleeding hellfire, colossal muscular frame towering above all other enemies, wielding a massive jagged black greatsword wreathed in roaring crimson flames with both hands, six curved horns crowning a scarred brutal face with burning white-hot eyes of pure rage, tattered burning cape trailing like a wildfire behind, ground cracking and melting beneath clawed feet, aura of uncontrollable wrath distorting the air around him, white background, fantasy RPG chapter boss sprite
```

---

## Chapter 2 — 시기 「뒤틀린 숲」

> 테마: 독성 녹색빛, 뒤틀리고 비대칭적인 외형

### 스테이지 1 — 변형의 경계 (Normal)

**ch2_wolf_scout** — 독늑대 척후
```
16-bit pixel art, mutated wolf with patches of toxic green fur and exposed veins, hunched aggressive stalking stance facing left, asymmetric body with one eye larger than the other, dripping green venom from fangs, twisted spine with bony protrusions, dark forest fog around paws, white background, fantasy RPG enemy sprite
```

**ch2_lizardman_hexer** — 도마뱀 저주사
```
16-bit pixel art, upright lizardman shaman with mottled green and purple scales, holding a twisted wooden staff dripping with poison, hunched casting stance facing left, one arm visibly larger and more mutated than the other, glowing toxic green runes on skin, tattered vine robes, white background, fantasy RPG enemy sprite
```

**ch2_lizardman_charger** — 도마뱀 돌격병
```
16-bit pixel art, massive mutated lizardman warrior with grotesquely swollen muscles and asymmetric limbs, wielding a heavy bone club with one enlarged arm, charging stance facing left, dark green scales cracked with toxic purple veins, jaw distorted and oversized, towering hulking silhouette, white background, fantasy RPG enemy sprite
```

### 스테이지 2 — 독무의 심림 (Demon)

**ch2_succubus_enchantress** — 서큐버스 유혹마
```
16-bit pixel art, envious succubus enchantress with pale green skin and dark twisted horns, wearing tattered black robes with vine-like patterns, casting a green hypnotic spell from raised hands facing left, jealous glowing green eyes, asymmetric bat wings one larger than the other, toxic mist curling around feet, white background, fantasy RPG enemy sprite
```

**ch2_succubus_poisoner** — 서큐버스 독술사
```
16-bit pixel art, poison succubus witch with sickly green-tinged skin, hurling a glob of toxic purple venom from clawed hands facing left, wearing a dark corset with thorny vine decorations, venomous snake coiled around one arm, sharp fangs visible in a snarl, poisonous fog trailing behind, white background, fantasy RPG enemy sprite
```

**ch2_orc_usurper** — 오크 탈취자
```
16-bit pixel art, massive orc usurper with mismatched stolen armor pieces from different warriors, wielding two different weapons — a stolen knight sword in one hand and a stolen mace in the other, hulking stance facing left, envious green glowing eyes, toxic green veins pulsing across grey skin, trophies of defeated foes hanging from belt, white background, fantasy RPG enemy sprite
```

### 스테이지 3 — 부패한 뿌리 (Undead)

**ch2_ghost_treespirit** — 수목 원혼
```
16-bit pixel art, translucent ghostly spirit trapped inside a twisted dead tree trunk, upper body emerging from bark with spectral green glow, reaching out with wispy clawed hands facing left, hollow eyes weeping green ectoplasm, dark roots growing through the transparent body, white background, fantasy RPG enemy sprite
```

**ch2_ghost_wailer** — 울부짖는 유령
```
16-bit pixel art, wailing female ghost with long flowing spectral hair, mouth wide open in an endless shriek facing left, translucent pale green body with dark root-like veins visible inside, tattered burial shroud wrapped in dead vines, tears of green poison streaming from hollow eyes, white background, fantasy RPG enemy sprite
```

**ch2_zombie_rotroot** — 뿌리 좀비
```
16-bit pixel art, massive rotting zombie entangled in thick dead tree roots growing through its body, lumbering stance facing left, bloated decayed flesh with patches of toxic green fungus, one arm replaced entirely by a thick gnarled root used as a club, hollow jaw hanging open, dirt and moss covering shoulders, white background, fantasy RPG enemy sprite
```

### Ch2 보스

**사마엘 (Samael)** — 독의 지배자
```
16-bit pixel art, fallen angel in serpentine form — tall reptilian humanoid with dark iridescent scales, tattered angelic wings now blackened and dripping venom, wielding a curved poisoned blade, aristocratic stance facing left, crown of twisted thorns on serpent-like head, toxic green mist emanating from body, six glowing green eyes, white background, fantasy RPG boss sprite
```

**아비주 (Abyzou)** — 시기의 어머니
```
16-bit pixel art, jealous demon mother with wild dark hair writhing like snakes, pale sickly skin with green veins of envy visible beneath, tattered dark robes with thorny vine patterns, casting a green curse from elongated clawed fingers facing left, hollow envious eyes glowing toxic green, spectral chains of stolen souls trailing behind, white background, fantasy RPG boss sprite
```

**밴시 (Banshee)** — 부패한 곡성
```
16-bit pixel art, spectral banshee queen with flowing white hair and mouth torn open in an eternal wail, translucent pale body wrapped in rotting roots and dead vines, hovering above ground facing left, shockwave of green spectral sound rippling outward from mouth, hollow eyes streaming with ghostly green tears, tattered burial gown fused with dark tree bark, white background, fantasy RPG boss sprite
```

**레비아탄 (Leviathan)** — Ch2 챕터 보스 · 말을 꺼낸 놈
```
16-bit pixel art, ancient sea serpent demon Leviathan in humanoid form — tall sinuous figure with dark iridescent sea-green and black scales covering entire body, long coiling serpentine tail trailing behind, wearing tattered royal robes stolen from a king with torn golden trim now corroded green, one hand clutching a broken crown the other open with toxic green envy-mist seeping between clawed fingers facing left, narrow venomous slit-pupil eyes glowing with hollow jealous green light, twisted coral-like horns curving back from skull, expression of bitter regret and unfulfilled longing, white background, fantasy RPG chapter boss sprite
```

---

## Chapter 3 — 탐욕 「황금의 사막」

> 테마: 황금빛 저주, 모래에 오염된 고대 유물, 탐욕에 물든 형상

### 스테이지 1 — 모래에 묻힌 폐허 (Normal)

**ch3_lizardman_raider** — 사막 도마뱀 약탈자
```
16-bit pixel art, desert lizardman raider with sandy brown scales and golden jewelry stolen from ruins, wielding a curved scimitar and small round shield, crouched aggressive stance facing left, golden armband and necklace glinting with cursed glow, tattered desert cloth wrapped around waist, sand dust at feet, white background, fantasy RPG enemy sprite
```

**ch3_lizardman_shaman** — 사막 도마뱀 주술사
```
16-bit pixel art, desert lizardman shaman with pale sand-colored scales, holding a golden staff topped with a cursed gemstone, casting stance with sand particles swirling around facing left, ancient Egyptian-style golden headdress, hieroglyph tattoos glowing faintly on scales, tattered linen robes, white background, fantasy RPG enemy sprite
```

**ch3_golem_sandstone** — 사암 골렘
```
16-bit pixel art, massive sandstone golem assembled from ancient ruin blocks with hieroglyph carvings glowing gold on its body, towering stance facing left, cracked stone surface with golden cursed light seeping through fractures, one arm formed from a broken stone pillar, ancient crown fragment embedded in head, sand cascading from joints, white background, fantasy RPG enemy sprite
```

### 스테이지 2 — 저주받은 지하묘지 (Undead)

**ch3_skeleton_guardian** — 해골 수호병
```
16-bit pixel art, undead skeleton guardian in ancient Egyptian-style bronze armor with golden curse markings, wielding a khopesh sword and tall rectangular shield, upright defensive stance facing left, golden light glowing from eye sockets, cobwebs and tomb dust on bones, tattered linen wrappings on limbs, white background, fantasy RPG enemy sprite
```

**ch3_skeleton_crossbow** — 해골 석궁병
```
16-bit pixel art, undead skeleton crossbowman crouching behind a golden-trimmed repeating crossbow, aiming stance facing left, ancient bronze chest piece with curse engravings, bolt quiver strapped to spine with golden-tipped bolts, jaw wired shut with golden wire, cobwebs between ribs, white background, fantasy RPG enemy sprite
```

**ch3_vampire_noble** — 뱀파이어 귀족
```
16-bit pixel art, aristocratic vampire lord in ornate golden-trimmed black robes and jeweled crown, pale skin with golden cursed veins visible, elongated fangs bared in a predatory smile facing left, one hand extended with sharp claws dripping blood, red cape lined with gold, towering regal presence, ancient Egyptian jewelry adorning neck and wrists, white background, fantasy RPG enemy sprite
```

### 스테이지 3 — 황금 보물고 (Demon)

**ch3_imp_goldfire** — 황금 임프
```
16-bit pixel art, small golden-skinned imp crackling with cursed golden fire in both hands, mischievous hovering stance facing left, tiny bat wings with golden membrane, sharp grin with golden teeth, wearing a tiny crown of stolen coins, molten gold dripping from fingertips, white background, fantasy RPG enemy sprite
```

**ch3_goblin_looter** — 고블린 약탈병
```
16-bit pixel art, greedy goblin soldier draped in stolen golden chains and jewelry, wielding a jagged dagger in one hand and clutching a stolen golden goblet in the other, hunched sneaking stance facing left, bulging sack of treasure on back, golden light reflecting off beady envious eyes, white background, fantasy RPG enemy sprite
```

**ch3_goblin_vaultkeeper** — 고블린 금고지기
```
16-bit pixel art, massive goblin vault captain in heavy golden plate armor with ornate engravings, wielding a giant golden war hammer with both hands, imposing stance facing left, oversized golden crown tilted on head, thick golden chains as belt, cursed golden glow emanating from armor cracks, towering hulking build for a goblin, white background, fantasy RPG enemy sprite
```

### Ch3 보스

**다곤 (Dagon)** — 모래에 묻힌 신
```
16-bit pixel art, ancient stone idol of Dagon awakened — massive humanoid golem with fish-scale carved stone surface, upper body human-like lower body merging into stone pillar base, wielding a colossal stone trident, towering stance facing left, ancient Philistine hieroglyphs glowing gold across body, cracked stone revealing cursed golden light within, sand and rubble falling from joints, crown of coral and gold on stone head, white background, fantasy RPG boss sprite
```

**카론 (Charon)** — 탐욕의 뱃사공
```
16-bit pixel art, skeletal ferryman Charon in tattered dark hooded robes standing on a ghostly boat bow, wielding a long oar-staff with a scythe blade at the tip, bony hand extended demanding payment facing left, hollow eye sockets glowing with dim golden light, ancient golden coins embedded in skull and ribcage, dark spectral river mist swirling below, white background, fantasy RPG boss sprite
```

**메피스토펠레스 (Mephistopheles)** — 황금의 거래자
```
16-bit pixel art, tall elegant demon lord Mephistopheles with dark bat wings spread wide, wearing a luxurious black suit with golden trim and a golden pocket watch chain, one hand holding a glowing golden contract scroll the other gesturing invitingly facing left, sharp aristocratic features with a confident smirk, curved horns polished like obsidian, golden eyes burning with cunning intelligence, white background, fantasy RPG boss sprite
```

**맘몬 (Mammon)** — Ch3 챕터 보스 · 은 30개의 거래
```
16-bit pixel art, wretched demon of greed Mammon sitting on a crumbling throne of golden coins and treasure, emaciated yet imposing figure in once-luxurious robes now tattered and stained, skeletal hands overflowing with cursed golden coins that melt through bony fingers, hollow despairing eyes glowing dim gold with deep regret, a heavy chain of thirty silver coins wrapped around neck like a noose, piles of useless gold crumbling to sand around the throne, hunched defeated posture facing left, aura of golden dust and despair, white background, fantasy RPG chapter boss sprite
```

---

## Chapter 4 — 나태 「망각의 동토」

> 테마: 얼어붙은 외형, 서리/빙결 효과, 느리고 둔중하거나 유령처럼 차가운

### 스테이지 1 — 얼어붙은 평원 (Undead)

**ch4_ghost_frostwraith** — 서리 원혼
```
16-bit pixel art, frozen ghostly wraith with crystallized ice forming on translucent pale blue body, casting a beam of freezing energy from outstretched hands facing left, hollow eyes glowing cold blue, ice crystals forming in the air around the floating figure, tattered frost-covered burial shroud, white background, fantasy RPG enemy sprite
```

**ch4_ghost_frostwailer** — 동결 곡성귀
```
16-bit pixel art, wailing frost specter with mouth frozen open in an eternal scream, translucent icy blue body with visible frozen organs inside, hovering stance facing left, shockwave of ice crystals rippling from its scream, long frozen hair spiked with icicles, frost spreading on the ground below, white background, fantasy RPG enemy sprite
```

**ch4_zombie_frozen** — 빙결 좀비
```
16-bit pixel art, massive frozen zombie with thick layer of ice encasing half its body, lumbering stance facing left with one arm raised as a frozen club, pale blue-grey frozen flesh with frost crystals covering shoulders and head, jaw frozen partially open revealing icy teeth, chunks of ice and snow clinging to bloated frame, towering hulking silhouette, white background, fantasy RPG enemy sprite
```

### 스테이지 2 — 빙하 요새 (Demon)

**ch4_goblin_frostguard** — 서리 고블린 병사
```
16-bit pixel art, frost goblin soldier in crude ice-crystal armor plates, wielding an icicle spear and small ice shield, alert guard stance facing left, blue-tinged green skin with frost patterns on face, breath visible in cold air, ice fortress wall pattern on shield, white background, fantasy RPG enemy sprite
```

**ch4_imp_icecaster** — 얼음 임프
```
16-bit pixel art, small ice imp with pale blue crystalline skin, hurling a shard of magical ice from raised claws facing left, tiny frost-covered bat wings buzzing, sharp icicle horns on head, mischievous frozen grin, trail of snowflakes following hand motion, white background, fantasy RPG enemy sprite
```

**ch4_goblin_glaciercaptain** — 고블린 빙하대장
```
16-bit pixel art, massive frost goblin captain in heavy ice-crystal full plate armor with glacial blue glow, wielding a giant ice greataxe with both hands, commanding stance facing left, oversized frozen iron crown with icicle spikes, thick blue-tinged skin visible at joints, cold mist emanating from armor gaps, towering hulking build, white background, fantasy RPG enemy sprite
```

### 스테이지 3 — 영구동결의 심부 (Normal)

**ch4_yeti_scout** — 예티 척후
```
16-bit pixel art, medium-sized young yeti scout with white shaggy fur, crouched aggressive stance on all fours facing left, sharp ice-blue eyes peering forward, frost clinging to fur, powerful but lean build compared to adult yeti, sharp claws scraping against frozen ground, white background, fantasy RPG enemy sprite
```

**ch4_yeti_hurler** — 예티 투석병
```
16-bit pixel art, medium-sized yeti hurler standing upright winding up to throw a massive chunk of ice with one arm facing left, white and grey shaggy fur with icicles hanging from arms, determined ice-blue eyes, other arm holding a second ice boulder ready, frost breath visible from snarling mouth, white background, fantasy RPG enemy sprite
```

**ch4_troll_glacier** — 트롤 빙하거인
```
16-bit pixel art, colossal glacier troll with skin entirely encased in thick glacial ice armor, lumbering stance facing left wielding a massive frozen stone pillar as a club, pale blue frozen skin visible through ice cracks, tiny frost-filled eyes deep in frozen skull, icicle stalactites hanging from chin and shoulders, towering hulking silhouette dwarfing other creatures, white background, fantasy RPG enemy sprite
```

### Ch4 보스

**유키온나 (Yuki-onna)** — 동토의 설녀
```
16-bit pixel art, ethereal Yuki-onna snow woman ghost hovering above frozen ground, flowing long black hair whipping in a blizzard wind, pale white translucent skin with an eerily beautiful face, wearing a tattered white kimono dissolving into snowflakes at the hem, hands extended releasing a deadly blizzard of ice crystals facing left, hollow ice-blue eyes with frozen tears, snowstorm swirling around her figure, white background, fantasy RPG boss sprite
```

**아스타로스 (Astaroth)** — 빙하의 태공
```
16-bit pixel art, fallen angel duke Astaroth with massive frost-covered dark stone wings spread wide, riding atop a frozen dragon-like beast, holding a frozen viper in one hand, aristocratic yet corrupted face with ice crystals forming on skin, heavy dark armor covered in glacial frost, foul frozen mist emanating from body, cold blue glowing eyes filled with apathy, white background, fantasy RPG boss sprite
```

**파주주 (Pazuzu)** — 얼어붙은 바람왕
```
16-bit pixel art, ancient wind king Pazuzu frozen in eternal stillness — massive chimeric body with lion torso and eagle talons entirely encased in thick glacial ice with cracks revealing dark skin beneath, four frost-shattered wings frozen mid-spread, scorpion tail frozen solid pointing upward, face frozen in a silent roar with icicles hanging from horns and jaw, faint blue glow of trapped wind energy pulsing within the ice shell, towering colossal silhouette, white background, fantasy RPG boss sprite
```

**벨페고르 (Belphegor)** — Ch4 챕터 보스 · 알면서 방관한 자
```
16-bit pixel art, slothful demon lord Belphegor sitting motionless on a frozen throne of solid ice, massive heavy body slumped in absolute apathy, thick frost-covered dark fur robes draped over hunched shoulders, eyes half-closed with dim pale blue glow of someone who has given up, one arm dangling lifelessly off the throne armrest, thick chains of ice growing from throne into body as if the seat itself is consuming him, icicles hanging from curved horns and beard, frozen breath hanging in still air, expression of absolute indifference and resignation facing left, white background, fantasy RPG chapter boss sprite
```

---

## Chapter 5 — 폭식 「심연의 동굴」

> 테마: 살아있는 동굴, 침식/소화, 끝없는 굶주림

### Ch5 챕터 보스

**바알제붑 (Beelzebub)** — Ch5 챕터 보스 · 모든 것의 시작
```
16-bit pixel art, lord of flies Beelzebub as a massive bloated insectoid demon, grotesquely swollen abdomen pulsating with consumed souls visible through translucent chitinous skin, upper body humanoid with four clawed arms reaching forward in desperate hunger, enormous tattered fly wings buzzing behind, compound eyes glowing sickly amber with mindless craving, gaping maw lined with rows of crushing teeth dripping acidic saliva that dissolves the ground below, swarm of dark flies orbiting the body, hunched forward ravenous stance facing left, cavern walls of living flesh in background dissolving, white background, fantasy RPG chapter boss sprite
```

---

## Chapter 6 — 색욕 「타락한 궁전」

> 테마: 퇴폐한 화려함, 거짓된 아름다움, 조종과 배신

### Ch6 챕터 보스

**아스모데우스 (Asmodeus)** — Ch6 챕터 보스 · 처음부터 적이었던 자
```
16-bit pixel art, master spy demon Asmodeus in deceptively beautiful humanoid form, tall elegant figure with flawless pale skin and an unsettlingly perfect face hiding cold calculation, wearing ornate dark royal armor with hidden angelic silver runes beneath the surface betraying true allegiance, three pairs of wings — one angelic white one demonic black one skeletal bare — representing triple nature of deception, wielding a thin rapier that shifts between holy silver and demonic obsidian, crown of roses with hidden thorns drawing blood from temples, eyes split vertically — one golden angelic one crimson demonic, confident smirk of someone who was never on your side facing left, white background, fantasy RPG chapter boss sprite
```

---

## Chapter 7 — 오만 「신의 폐허」

> 테마: 무너진 천상, 신성의 잔해, 비극적 충성

### Ch7 챕터 보스

**루시퍼 (Lucifer)** — Ch7 챕터 보스 · 배신이 아니었다
```
16-bit pixel art, fallen morning star Lucifer in battle-worn angelic form — tall majestic figure with cracked golden armor revealing wounded flesh beneath, twelve magnificent wings once pure white now half-shattered and bleeding golden light from broken feathers, wielding a massive holy lance crackling with fading divine energy in one hand, other hand reaching out in a gesture of sorrowful farewell, face beautiful but etched with exhaustion and grief — eyes burning soft gold with tears of light streaming down, halo above head cracked and flickering between radiance and darkness, standing alone in ruins of a heavenly battlefield, the most powerful yet most tragic presence, white background, fantasy RPG chapter boss sprite
```
