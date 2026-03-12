# Diablo 2 무기 베이스 참고자료

> 무기 베이스 스탯 설계 참고용. WSM(Weapon Speed Modifier): 낮을수록 빠름.
> 실제 공격 프레임은 캐릭터 기본공속 + IAS로 결정됨.

---

## WSM 속도 기준

| WSM | 체감 속도 |
|-----|---------|
| -30 이하 | 매우 빠름 |
| -20 ~ -10 | 빠름 |
| 0 | 보통 |
| +10 ~ +20 | 느림 |
| +30 이상 | 매우 느림 |

---

## 검 (Sword) — 1H

| 이름 | 등급 | 데미지 | WSM |
|------|------|--------|-----|
| Short Sword | Normal | 2–7 | 0 |
| Scimitar | Normal | 2–6 | -20 |
| Sabre | Normal | 3–8 | -10 |
| Falchion | Normal | 9–17 | +20 |
| Broad Sword | Normal | 7–14 | 0 |
| Long Sword | Normal | 3–19 | 0 |
| War Sword | Normal | 8–20 | 0 |
| Gladius | Exceptional | 8–22 | 0 |
| Cutlass | Exceptional | 8–21 | -20 |
| Shamshir | Exceptional | 10–24 | -10 |
| Tulwar | Exceptional | 16–35 | +20 |
| Battle Sword | Exceptional | 16–34 | 0 |
| Rune Sword | Exceptional | 10–42 | 0 |
| Falcata | Elite | 31–59 | 0 |
| Ataghan | Elite | 26–46 | -20 |
| Elegant Blade | Elite | 33–45 | -10 |
| Hydra Edge | Elite | 28–68 | +20 |
| **Phase Blade** | Elite | 31–35 | **-30** |
| Conquest Sword | Elite | 37–53 | 0 |
| Cryptic Sword | Elite | 5–59 | 0 |

---

## 양손검 (Sword) — 2H

| 이름 | 등급 | 데미지 (1H/2H) | WSM |
|------|------|--------------|-----|
| Two-Handed Sword | Normal | 2–9 / 8–17 | 0 |
| Claymore | Normal | 5–12 / 13–30 | +10 |
| Bastard Sword | Normal | 7–19 / 7–34 | +20 |
| Great Sword | Normal | 5–23 / 10–37 | **+30** |
| Espandon | Exceptional | 8–26 / 18–40 | 0 |
| Gothic Sword | Exceptional | 14–40 / 14–58 | +20 |
| Zweihander | Exceptional | 19–35 / 19–58 | +20 |
| Executioner Sword | Exceptional | 24–40 / 24–65 | **+30** |
| Legend Sword | Elite | 22–56 / 50–94 | 0 |
| Balrog Blade | Elite | 15–75 / 55–118 | 0 |
| Colossus Sword | Elite | 26–70 / 25–65 | +20 |
| **Colossus Blade** | Elite | 25–65 / 46–100 | **+30** |

---

## 도끼 (Axe) — 1H

| 이름 | 등급 | 데미지 | WSM |
|------|------|--------|-----|
| Hand Axe | Normal | 3–6 | 0 |
| Axe | Normal | 4–11 | +10 |
| Double Axe | Normal | 5–13 | -10 |
| Military Pick | Normal | 7–11 | -10 |
| War Axe | Normal | 10–18 | -10 |
| Hatchet | Exceptional | 10–21 | 0 |
| Cleaver | Exceptional | 10–33 | +10 |
| Twin Axe | Exceptional | 13–38 | -10 |
| Naga | Exceptional | 16–45 | -10 |
| Tomahawk | Elite | 33–58 | 0 |
| Ettin Axe | Elite | 33–66 | -10 |
| **Berserker Axe** | Elite | 24–71 | **-10** |

---

## 도끼 (Axe) — 2H

| 이름 | 등급 | 데미지 | WSM |
|------|------|--------|-----|
| Large Axe | Normal | 6–13 | 0 |
| Battle Axe | Normal | 12–32 | +10 |
| Great Axe | Normal | 9–26 | +20 |
| Giant Axe | Normal | 22–45 | +20 |
| Tabar | Exceptional | 24–77 | +10 |
| Gothic Axe | Exceptional | 18–70 | +20 |
| Ancient Axe | Exceptional | 43–85 | +20 |
| Feral Axe | Elite | 25–123 | 0 |
| Silver-Edged Axe | Elite | 62–110 | 0 |
| Decapitator | Elite | 49–137 | +10 |
| **Glorious Axe** | Elite | 60–124 | +20 |

---

## 창 (Spear)

| 이름 | 등급 | 데미지 (1H/2H) | WSM |
|------|------|--------------|-----|
| Spear | Normal | 3–8 / 3–15 | 0 |
| Trident | Normal | 9–15 / 9–15 | -10 |
| **Brandistock** | Normal | 7–17 / 7–17 | **-30** |
| Spetum | Normal | 15–23 / 15–23 | 0 |
| Pike | Normal | 14–63 / 14–63 | +20 |
| Lance | Exceptional | 27–114 / 27–114 | +20 |
| Hyperion Spear | Elite | 35–119 / 35–119 | +20 |
| Stygian Pike | Elite | 29–144 / 29–144 | +20 |
| Mancatcher | Elite | 42–92 / 42–92 | 0 |

---

## 핵심 설계 인사이트

| 관찰 | 내용 |
|------|------|
| 속도 범위 | WSM -30 (Phase Blade) ~ +30 (Great Sword/Colossus Blade) |
| 데미지-속도 트레이드오프 | 빠른 무기 = 낮은 최대뎀, 느린 무기 = 높은 최대뎀 |
| 도끼의 분산도 | 가장 큰 데미지 분산 (Hand Axe 3–6 vs Feral Axe 25–123) |
| 창의 특징 | 대부분 느림(+20), Brandistock(-30)만 예외적으로 빠름 |
| 베이스별 극단 | Phase Blade(빠르고 분산 작음) vs Colossus Blade(느리고 분산 큼) |
| D2의 핵심 | 베이스 선택 자체가 빌드 방향 결정 — implicit 없이도 개성 충분 |

---

*참고: 수치는 메모리 기반이므로 일부 오차 있을 수 있음. 검증 필요 시 [diablo2.io/base](https://diablo2.io/base/) 참조*
