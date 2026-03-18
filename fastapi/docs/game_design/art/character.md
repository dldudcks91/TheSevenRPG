# TheSevenRPG — 캐릭터 픽셀아트 프롬프트

> **주인공**: 바알 (Baal) — 대악마의 왕, 인간 여성의 몸으로 추락
> 스토리 참조: → `fastapi/docs/game_design/story/story_guide.md`
> 몬스터 아트: → `fastapi/docs/game_design/art/monster.md`

> 공통 스타일: `16-bit pixel art`, `dark fantasy RPG protagonist sprite`,
> `white background`, `facing left`, `full body`

---

## 디자인 컨셉

**"차가운 여자"** — 감정을 모르기 때문에 차가운 존재. 챕터 진행에 따라 균열이 생긴다.

### 핵심 디자인 요소

| 요소 | 방향 | 이유 |
|------|------|------|
| **성별** | 여성 | "대악마의 왕 = 남성" 고정관념 파괴, 감정 아크와 조화 |
| **머리** | 긴 흑발, 정돈되지 않은 채로 흘러내림 | 왕이었으나 추락한 상태 |
| **체형** | 마르고 날렵, 키는 평균~약간 큼 | 인간의 몸이지만 자세가 압도적 |
| **표정** | 무표정 ~ 약간의 경멸 | 인간 세계에 관심 없는 존재 |
| **눈** | 금색 — 유일한 비인간적 요소 | 픽셀아트에서 눈 색으로 차별화 |
| **피부** | 창백 | 차가운 인상 + 낙인 문양 대비 |
| **낙인** | 가슴/쇄골 중심 → 챕터마다 전신으로 확산 | 성장의 시각적 지표, 7죄종 색상 |
| **복장** | 소박(초반) → 어둡고 날카로운 갑옷(후반) | 장비 파밍 시스템과 연동 |

### 감정 아크와 외형 변화

| 시점 | 감정 | 외형 변화 |
|------|------|-----------|
| 프롤로그 | 무감정, 이해불가 | 상처투성이, 낙인만 희미하게 |
| Ch1~2 | 분노, 의문 | 백발 줄기 발생, 낙인 확산, 눈 발광 |
| Ch3~5 | 회의, 감사, 인간성 자각 | 이색안(금/붉은), 다색 낙인, 어둠 오라 |
| Ch6~7 | 분노→슬픔→결의 | 흑백발, 전신 낙인, 빛의 왕관, 눈물 |

---

## 인게임 스프라이트 — 성장 단계별

---

### Stage A — 추락 직후 (프롤로그 ~ Ch1 초반)

```
16-bit pixel art, young woman with long unkempt black hair falling
past shoulders, pale cold skin, sharp golden eyes with an inhuman
emotionless gaze, lean slim build standing with unconsciously regal
posture, wearing torn dirty peasant clothes — a tattered gray tunic
and rough cloth pants, barefoot, faint crimson stigma mark barely
visible on collarbone, holding a crude salvaged short sword loosely
at her side, expression blank and indifferent, dark fantasy RPG
protagonist sprite, white background, facing left, full body
```

---

### Stage B — 분노 각성 (Ch1 ~ Ch2)

```
16-bit pixel art, young woman with long black hair with a single
streak of white near the temple, pale cold skin, sharp golden eyes
now faintly glowing, lean athletic build in an upright commanding
stance, wearing dark fitted leather armor over a black long-sleeved
tunic, crimson stigma markings spreading from collarbone down the
left arm in vein-like patterns glowing faintly red, wielding a
dark iron sword with confidence, expression cold and piercing with
a hint of suppressed rage, dark fantasy RPG protagonist sprite,
white background, facing left, full body
```

---

### Stage C — 힘의 회복 (Ch3 ~ Ch5)

```
16-bit pixel art, young woman with long black hair streaked with
white strands blowing slightly, pale skin with faintly visible dark
vein patterns on neck, heterochromatic eyes — left eye golden right
eye deep crimson, lean powerful build in a dominant stance, wearing
dark layered armor — black leather chest piece with dark metal
pauldron on left shoulder, stigma markings covering both arms and
neck in layered colors — red and green and gold vein-like patterns
pulsing with absorbed sin, dark energy faintly radiating from body,
wielding a refined dark blade, expression cold and unreadable but
eyes burning with intensity, dark fantasy RPG protagonist sprite,
white background, facing left, full body
```

---

### Stage D — 대악마 복귀 (Ch6 ~ Ch7)

```
16-bit pixel art, young woman with long flowing black and white
hair whipping upward with dark energy, pale luminous skin covered
in intricate stigma markings across entire body glowing in seven
shifting colors — red blue gold green amber violet white, both eyes
blazing solid gold radiating light, lean figure now clad in elegant
dark demonic armor that looks grown rather than worn — organic black
plate with sharp edges and subtle horn-like ridges on shoulders,
a faint crown of light hovering above head — not horns but a
fractured halo-like ring of dark energy, wielding a massive dark
greatsword crackling with seven-colored sin energy, stance absolute
and commanding like a returning king, expression still cold but eyes
carrying visible grief and resolve, dark fantasy RPG protagonist
sprite, white background, facing left, full body
```

---

## 스토리 일러스트용

---

### 프롤로그 씬4 — 마을에서 눈을 뜨는 장면

```
16-bit pixel art, young woman lying on a simple wooden bed in a
dim village hut, long black hair spread across a rough pillow,
pale skin with fresh wounds and bruises, eyes barely open revealing
a sliver of cold gold iris staring at the ceiling with zero emotion,
faint crimson stigma mark glowing softly on exposed collarbone,
an old villager's weathered hand offering a wooden cup of water
at the edge of frame, dark muted interior colors — brown wood
and dim candlelight, dark fantasy RPG scene illustration,
pixel art style
```

---

### Ch7 엔딩 — 처음으로 우는 장면

```
16-bit pixel art, young woman kneeling alone in the ruins of a
heavenly battlefield, long black and white hair falling over her
face, full dark demonic armor cracked and battle-damaged, seven-
colored stigma markings flickering unstably across skin, head
bowed with both hands on the ground, single visible eye — golden
— with a tear of light rolling down a cold pale cheek, a broken
holy lance lying beside her on shattered marble floor, faint
golden feathers scattered around from a fallen angel, vast empty
ruined cathedral in background, dark fantasy RPG scene illustration,
pixel art style
```
