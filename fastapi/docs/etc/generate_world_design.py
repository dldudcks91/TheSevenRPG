from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth

pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
pdfmetrics.registerFont(TTFont("MalgunBd", "C:/Windows/Fonts/malgunbd.ttf"))

W, H = A4
MARGIN = 36

CHAPTERS = [
    {
        "num": "Chapter 1",
        "sin": "분노 / Wrath",
        "region": "불타는 전장",
        "subtitle": "Burning Battlefield",
        "color": (0.80, 0.15, 0.10),
        "bg": (0.25, 0.05, 0.03),
        "types": "Demon → Normal → Undead",
        "monster_pool": "Goblin · Orc · Imp\nWolf · Troll\nSkeleton",
        "boss": "전장의 군주 — 분노에 물든 대장군",
        "atmo": [
            "끝나지 않는 전쟁이 대지를 갈아엎은 곳",
            "불길과 연기가 하늘을 가리고",
            "쓰러진 병사들의 원한이 전장을 배회한다",
        ],
    },
    {
        "num": "Chapter 2",
        "sin": "나태 / Sloth",
        "region": "망각의 늪",
        "subtitle": "Swamp of Oblivion",
        "color": (0.35, 0.45, 0.25),
        "bg": (0.08, 0.12, 0.05),
        "types": "Undead → Demon → Normal",
        "monster_pool": "Zombie · Ghost\nGoblin · Imp\nYeti · Troll",
        "boss": "늪의 지배자 — 움직임을 잃어버린 고대의 정령",
        "atmo": [
            "짙은 안개가 모든 방향감각을 잃게 만드는 곳",
            "시간이 멈춘 듯 모든 것이 천천히 썩어가며",
            "한번 발을 디디면 빠져나오기 힘든 망각의 땅",
        ],
    },
    {
        "num": "Chapter 3",
        "sin": "탐욕 / Greed",
        "region": "황금의 폐허",
        "subtitle": "Golden Ruins",
        "color": (0.75, 0.58, 0.05),
        "bg": (0.20, 0.14, 0.02),
        "types": "Normal → Undead → Demon",
        "monster_pool": "Lizardman · Golem\nSkeleton · Vampire\nImp · Goblin",
        "boss": "황금 수호자 — 보물에 집착한 나머지 보물이 된 왕",
        "atmo": [
            "찬란했던 고대 왕국이 탐욕으로 무너진 자리",
            "금과 보석이 가득하지만 모두 저주에 걸려있으며",
            "부를 지키려 한 자들이 유물이 되어 배회한다",
        ],
    },
    {
        "num": "Chapter 4",
        "sin": "시기 / Envy",
        "region": "저주받은 숲",
        "subtitle": "Cursed Forest",
        "color": (0.15, 0.50, 0.30),
        "bg": (0.03, 0.12, 0.07),
        "types": "Normal → Demon → Undead",
        "monster_pool": "Wolf · Lizardman\nSuccubus · Orc\nGhost · Zombie",
        "boss": "숲의 거울 — 침입자의 모습을 복사하는 시기의 화신",
        "atmo": [
            "뒤틀린 나무들이 침입자를 향해 가지를 뻗는 곳",
            "다른 존재의 힘을 탐내는 그림자들이 배회하며",
            "자신이 아닌 것이 되고 싶어 변형된 생물들의 땅",
        ],
    },
    {
        "num": "Chapter 5",
        "sin": "폭식 / Gluttony",
        "region": "심연의 동굴",
        "subtitle": "Caverns of the Abyss",
        "color": (0.45, 0.20, 0.55),
        "bg": (0.10, 0.04, 0.14),
        "types": "Undead → Normal → Demon",
        "monster_pool": "Zombie · Lich\nYeti · Golem\nGargoyle · Orc",
        "boss": "심연의 입 — 모든 것을 집어삼키는 폭식의 화신",
        "atmo": [
            "끝없이 이어지는 동굴, 나아갈수록 더 깊어지는 어둠",
            "이 동굴은 스스로 성장하며 모든 것을 소화한다",
            "들어온 자들의 흔적조차 삼켜버린 살아있는 미로",
        ],
    },
    {
        "num": "Chapter 6",
        "sin": "색욕 / Lust",
        "region": "타락한 궁전",
        "subtitle": "Corrupted Palace",
        "color": (0.75, 0.20, 0.45),
        "bg": (0.18, 0.04, 0.10),
        "types": "Demon → Undead → Normal",
        "monster_pool": "Succubus · Imp\nVampire · Ghost\nLizardman · Troll",
        "boss": "궁전의 여왕 — 욕망을 먹고 신이 된 색욕의 화신",
        "atmo": [
            "화려하게 장식된 궁전이지만 모든 것이 부패해있다",
            "아름다움 뒤에 숨겨진 함정과 유혹이 가득하며",
            "자신의 욕망에 잠식된 자들이 하수인으로 배회한다",
        ],
    },
    {
        "num": "Chapter 7",
        "sin": "오만 / Pride",
        "region": "신의 폐허",
        "subtitle": "Ruins of God",
        "color": (0.80, 0.75, 0.40),
        "bg": (0.18, 0.16, 0.04),
        "types": "Demon → Normal → Undead",
        "monster_pool": "Gargoyle · Orc\nGolem · Yeti\nLich · Vampire",
        "boss": "타락한 신 — 스스로를 신이라 칭하다 추락한 오만의 끝",
        "atmo": [
            "신이 살았던 곳, 혹은 신이 되려 했던 자의 흔적",
            "거대한 석상과 폐허가 잃어버린 영광을 증언하며",
            "모든 죄의 근원이 잠들어 있는 최후의 땅",
        ],
    },
]


def draw_chapter_card(c, ch, x, y, card_w, card_h):
    r, g, b = ch["color"]
    br, bg_, bb = ch["bg"]

    # 배경
    c.setFillColorRGB(br, bg_, bb)
    c.roundRect(x, y, card_w, card_h, 8, fill=1, stroke=0)

    # 상단 컬러 배너
    banner_h = card_h * 0.28
    c.setFillColorRGB(r, g, b)
    c.roundRect(x, y + card_h - banner_h, card_w, banner_h, 8, fill=1, stroke=0)
    c.setFillColorRGB(br, bg_, bb)
    c.rect(x, y + card_h - banner_h, card_w, banner_h * 0.4, fill=1, stroke=0)

    # Chapter 번호
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Malgun", 7)
    c.drawString(x + 10, y + card_h - 16, ch["num"])

    # 죄종명
    c.setFont("MalgunBd", 13)
    c.drawString(x + 10, y + card_h - 32, ch["sin"])

    # 지역명 (한글)
    c.setFont("MalgunBd", 10)
    c.setFillColorRGB(r + 0.2, g + 0.2, b + 0.2)
    c.drawString(x + 10, y + card_h - banner_h + 7, ch["region"])

    # subtitle
    c.setFont("Malgun", 7)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawString(x + 10, y + card_h - banner_h - 5, ch["subtitle"])

    # 구분선
    c.setStrokeColorRGB(r, g, b)
    c.setLineWidth(0.5)
    c.line(x + 8, y + card_h - banner_h - 13, x + card_w - 8, y + card_h - banner_h - 13)

    # 분위기 텍스트
    c.setFont("Malgun", 7)
    c.setFillColorRGB(0.82, 0.82, 0.82)
    atmo_y = y + card_h - banner_h - 23
    for line in ch["atmo"]:
        c.drawString(x + 10, atmo_y, line)
        atmo_y -= 10

    # 구분선2
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.line(x + 8, atmo_y + 4, x + card_w - 8, atmo_y + 4)

    # 몬스터 타입 순서
    c.setFont("MalgunBd", 7)
    c.setFillColorRGB(r, g, b)
    c.drawString(x + 10, atmo_y - 6, "스테이지 타입 순서")
    c.setFont("Malgun", 7)
    c.setFillColorRGB(0.75, 0.75, 0.75)
    c.drawString(x + 10, atmo_y - 16, ch["types"])

    # 몬스터 풀
    c.setFont("MalgunBd", 7)
    c.setFillColorRGB(r, g, b)
    c.drawString(x + 10, atmo_y - 28, "몬스터 풀")
    c.setFont("Malgun", 6.5)
    c.setFillColorRGB(0.75, 0.75, 0.75)
    pool_lines = ch["monster_pool"].split("\n")
    pool_y = atmo_y - 38
    for line in pool_lines:
        c.drawString(x + 10, pool_y, line)
        pool_y -= 9

    # 보스
    c.setStrokeColorRGB(0.3, 0.3, 0.3)
    c.line(x + 8, pool_y + 4, x + card_w - 8, pool_y + 4)
    c.setFont("MalgunBd", 7)
    c.setFillColorRGB(r + 0.1, g + 0.1, b + 0.1)
    c.drawString(x + 10, pool_y - 6, "챕터 보스")
    c.setFont("Malgun", 6.5)
    c.setFillColorRGB(0.85, 0.85, 0.85)

    boss_text = ch["boss"]
    max_w = card_w - 20
    words = boss_text
    if stringWidth(words, "Malgun", 6.5) > max_w:
        mid = len(words) // 2
        split = words.rfind(" ", 0, mid) if " " in words[:mid] else mid
        c.drawString(x + 10, pool_y - 16, words[:split])
        c.drawString(x + 10, pool_y - 25, words[split:])
    else:
        c.drawString(x + 10, pool_y - 16, words)


def main():
    output = "c:/Users/user/Desktop/python_text/git/TheSevenRPG/fastapi/docs/game_design/TheSevenRPG_WorldDesign.pdf"
    c = canvas.Canvas(output, pagesize=A4)

    # 표지
    c.setFillColorRGB(0.06, 0.04, 0.10)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # 제목
    c.setFillColorRGB(0.85, 0.75, 0.30)
    c.setFont("MalgunBd", 28)
    c.drawCentredString(W / 2, H - 80, "TheSevenRPG")
    c.setFont("MalgunBd", 16)
    c.setFillColorRGB(0.75, 0.65, 0.20)
    c.drawCentredString(W / 2, H - 105, "세계 설계 — 7챕터 지역 개요")

    # 구분선
    c.setStrokeColorRGB(0.5, 0.4, 0.1)
    c.setLineWidth(1)
    c.line(MARGIN, H - 115, W - MARGIN, H - 115)

    # 카드 배치: 2열 × 4행 (7개 + 1빈칸)
    cols = 2
    col_gap = 12
    row_gap = 12
    card_w = (W - MARGIN * 2 - col_gap) / cols
    card_h = (H - 130 - MARGIN - row_gap * 3) / 4

    for i, ch in enumerate(CHAPTERS):
        col = i % cols
        row = i // cols
        x = MARGIN + col * (card_w + col_gap)
        y = H - 130 - (row + 1) * card_h - row * row_gap
        draw_chapter_card(c, ch, x, y, card_w, card_h)

    # 하단
    c.setFont("Malgun", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawCentredString(W / 2, MARGIN - 10, "TheSevenRPG · World Design v1.0 · 2026")

    c.save()
    print(f"저장 완료: {output}")


if __name__ == "__main__":
    main()
