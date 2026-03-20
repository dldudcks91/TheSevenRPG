"""
TheSevenRPG 장비 아이콘 생성기
16x16 도트 아이콘 — 다크 판타지 스타일
출력: fastapi/public/img/icons/equip/
"""

from PIL import Image

# === 색상 팔레트 (다크 판타지) ===
T = (0, 0, 0, 0)           # 투명
K = (20, 18, 22, 255)       # 아웃라인 (거의 검정)
D1 = (45, 42, 50, 255)      # 다크 스틸 1
D2 = (65, 60, 72, 255)      # 다크 스틸 2
D3 = (90, 85, 100, 255)     # 다크 스틸 3 (밝은면)
S1 = (120, 115, 130, 255)   # 실버 하이라이트
S2 = (160, 155, 170, 255)   # 밝은 하이라이트
R1 = (140, 30, 30, 255)     # 크림슨 다크
R2 = (180, 50, 40, 255)     # 크림슨
R3 = (220, 80, 60, 255)     # 크림슨 밝은
B1 = (50, 35, 25, 255)      # 가죽/나무 어두운
B2 = (75, 55, 40, 255)      # 가죽/나무
B3 = (100, 75, 55, 255)     # 가죽/나무 밝은
G1 = (30, 100, 40, 255)     # 독 녹색 어두운
G2 = (50, 140, 60, 255)     # 독 녹색
P1 = (80, 40, 120, 255)     # 보라 어두운
P2 = (110, 60, 160, 255)    # 보라
A1 = (140, 110, 40, 255)    # 앰버/골드 어두운
A2 = (180, 150, 50, 255)    # 앰버/골드
A3 = (220, 190, 80, 255)    # 골드 하이라이트
I1 = (80, 140, 180, 255)    # 아이스 블루
I2 = (130, 190, 220, 255)   # 아이스 밝은
W = (200, 195, 210, 255)    # 화이트 계열


def create_icon(pixels_data, filename, scale=1):
    """16x16 도트 아이콘 생성. scale>1이면 확대 저장."""
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(pixels_data):
        for x, color in enumerate(row):
            if color != T:
                img.putpixel((x, y), color)
    if scale > 1:
        img = img.resize((16 * scale, 16 * scale), Image.NEAREST)
    img.save(filename)
    return img


# ============================================================
# 1. 한손검 (One-Handed Sword) — 대각선 배치, 크림슨 포인트
# ============================================================
sword = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, S2,T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, S2,S1,T, T],
    [T, T, T, T, T, T, T, T, T, T, T, S1,D3,K, T, T],
    [T, T, T, T, T, T, T, T, T, T, D3,D2,K, T, T, T],
    [T, T, T, T, T, T, T, T, T, S1,D2,K, T, T, T, T],
    [T, T, T, T, T, T, T, T, S1,D2,K, T, T, T, T, T],
    [T, T, T, T, T, T, T, D3,D2,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, D3,D2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, D3,D2,K, T, T, T, T, T, T, T, T],
    [T, T, T, T, R2,D3,K, T, T, T, T, T, T, T, T, T],
    [T, T, T, R1,A2,R2,K, T, T, T, T, T, T, T, T, T],
    [T, T, T, K, R1,A1,R1,K, T, T, T, T, T, T, T, T],
    [T, T, T, T, K, B2,K, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, K, B1,K, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, R1,T, T, T, T, T, T, T],
]

# ============================================================
# 2. 대검 (Greatsword) — 세로 중앙, 넓은 칼날, 보라 룬
# ============================================================
greatsword = [
    [T, T, T, T, T, T, S2,S1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, S1,D3,D2,D3,K, T, T, T, T, T, T],
    [T, T, T, T, T, S1,D3,P2,D2,K, T, T, T, T, T, T],
    [T, T, T, T, K, S1,D3,D2,D2,D1,K, T, T, T, T, T],
    [T, T, T, T, K, D3,D2,P1,D2,D1,K, T, T, T, T, T],
    [T, T, T, T, K, D3,D2,D1,D2,D1,K, T, T, T, T, T],
    [T, T, T, T, K, S1,D3,P2,D2,D1,K, T, T, T, T, T],
    [T, T, T, T, K, D3,D2,D1,D2,D1,K, T, T, T, T, T],
    [T, T, T, T, T, K, D3,D2,D1,K, T, T, T, T, T, T],
    [T, T, T, T, T, K, D3,P1,D1,K, T, T, T, T, T, T],
    [T, T, T, K, D1,K, D2,D1,K, D1,K, T, T, T, T, T],
    [T, T, T, T, K, K, D2,K, K, K, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, D1,K, T, T, T, T, T, T, T],
]

# ============================================================
# 3. 도끼 (Axe) — 초승달 날, 앰버/골드 엣지
# ============================================================
axe = [
    [T, T, T, T, T, T, T, T, K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, D2,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, D3,D2,K, T, T, T, T, T, T],
    [T, T, T, T, K, K, D2,D3,D1,K, T, T, T, T, T, T],
    [T, T, T, K, D2,A2,D3,D2,D1,K, T, T, T, T, T, T],
    [T, T, K, D1,D2,A3,S1,D2,K, T, T, T, T, T, T, T],
    [T, T, K, D1,A2,A3,D3,D2,K, T, T, T, T, T, T, T],
    [T, T, T, K, D2,A2,D3,K, B2,K, T, T, T, T, T, T],
    [T, T, T, T, K, K, K, K, B1,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, B3,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, K, T, T, T, T, T, T, T],
]

# ============================================================
# 4. 창 (Spear) — 세로 긴 형태, 아이스블루 촉
# ============================================================
spear = [
    [T, T, T, T, T, T, T, K, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, I1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, K, I1,I2,I1,K, T, T, T, T, T, T],
    [T, T, T, T, K, I1,S1,I2,S1,K, T, T, T, T, T, T],
    [T, T, T, T, T, K, D3,S1,D3,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, D2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, K, D1,K, D1,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B3,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, T, T, T, T, T, T, T, T],
]

# ============================================================
# 5. 둔기 (Mace) — 무거운 머리, 녹색 독 액센트
# ============================================================
mace = [
    [T, T, T, T, T, T, K, K, K, K, T, T, T, T, T, T],
    [T, T, T, T, T, K, D2,D3,D2,D1,K, T, T, T, T, T],
    [T, T, T, T, K, D1,D3,S1,D3,D2,K, T, T, T, T, T],
    [T, T, T, T, K, D2,G1,D2,G1,D2,K, T, T, T, T, T],
    [T, T, T, T, K, D3,S1,D3,S1,D3,K, T, T, T, T, T],
    [T, T, T, T, K, D1,G2,D2,G2,D1,K, T, T, T, T, T],
    [T, T, T, T, K, D2,D3,S1,D3,D2,K, T, T, T, T, T],
    [T, T, T, T, T, K, D1,D2,D1,K, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, K, K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B1,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B2,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, K, B3,K, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, K, T, T, T, T, T, T, T, T],
]

# ============================================================
# 6. 중갑 (Heavy Armor) — 정면 흉갑, 레드 글로우
# ============================================================
armor_heavy = [
    [T, T, T, T, T, K, K, K, K, K, K, T, T, T, T, T],
    [T, T, T, T, K, D2,D3,S1,D3,D2,D1,K, T, T, T, T],
    [T, T, T, K, D1,D2,D3,D3,D3,D2,D1,K, T, T, T, T],
    [T, T, K, D1,D2,D3,S1,S1,S1,D3,D2,D1,K, T, T, T],
    [T, K, D1,D2,K, D3,R2,R3,R2,D3,K, D2,D1,K, T, T],
    [T, K, D2,D3,K, D2,D3,R2,D3,D2,K, D3,D2,K, T, T],
    [T, T, K, D3,D2,D3,D2,D3,D2,D3,D2,D3,K, T, T, T],
    [T, T, K, D2,D3,R1,D3,D2,D3,R1,D3,D2,K, T, T, T],
    [T, T, K, D1,D2,D3,D2,D3,D2,D3,D2,D1,K, T, T, T],
    [T, T, T, K, D1,D2,R1,D3,R1,D2,D1,K, T, T, T, T],
    [T, T, T, K, D1,D2,D3,D2,D3,D2,D1,K, T, T, T, T],
    [T, T, T, K, D1,D2,D2,R1,D2,D2,D1,K, T, T, T, T],
    [T, T, T, T, K, D1,D2,D2,D2,D1,K, T, T, T, T, T],
    [T, T, T, T, K, D1,D1,D2,D1,D1,K, T, T, T, T, T],
    [T, T, T, T, T, K, K, K, K, K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# ============================================================
# 7. 경갑 (Light Armor) — 가죽 브리간딘, 스터드 포인트
# ============================================================
armor_light = [
    [T, T, T, T, T, K, K, K, K, K, K, T, T, T, T, T],
    [T, T, T, T, K, B2,B3,B3,B3,B2,B1,K, T, T, T, T],
    [T, T, T, K, B1,B2,B3,B3,B3,B2,B1,K, T, T, T, T],
    [T, T, K, B1,B2,S1,B2,B3,B2,S1,B2,B1,K, T, T, T],
    [T, K, B1,B2,B3,B2,B3,B3,B3,B2,B3,B2,B1,K, T, T],
    [T, K, B2,B3,B2,S1,B2,B3,B2,S1,B2,B3,B2,K, T, T],
    [T, T, K, B2,B3,B2,B3,B2,B3,B2,B3,B2,K, T, T, T],
    [T, T, K, B1,B2,S1,B2,B3,B2,S1,B2,B1,K, T, T, T],
    [T, T, K, B1,B2,B2,B3,B2,B3,B2,B2,B1,K, T, T, T],
    [T, T, T, K, B1,S1,B2,B3,B2,S1,B1,K, T, T, T, T],
    [T, T, T, K, B1,B2,B2,B2,B2,B2,B1,K, T, T, T, T],
    [T, T, T, K, B1,B1,S1,B2,S1,B1,B1,K, T, T, T, T],
    [T, T, T, T, K, B1,B1,B2,B1,B1,K, T, T, T, T, T],
    [T, T, T, T, K, B1,B1,B1,B1,B1,K, T, T, T, T, T],
    [T, T, T, T, T, K, K, K, K, K, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# ============================================================
# 8. 생존형 투구 (Survival Helmet) — 폐쇄형, 블루 룬
# ============================================================
helmet_survival = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, K, K, K, K, K, K, T, T, T, T, T],
    [T, T, T, T, K, D3,S1,S1,S1,D3,D2,K, T, T, T, T],
    [T, T, T, K, D2,D3,S1,S2,S1,D3,D2,D1,K, T, T, T],
    [T, T, T, K, D2,D3,I1,D3,I1,D3,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,D3,D3,D3,D3,D3,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,D3,D3,D3,D3,D3,D2,D1,K, T, T, T],
    [T, T, K, K, K, K, D2,D2,D2,K, K, K, K, T, T, T],
    [T, T, K, D1,D1,K, K, K, K, K, D1,D1,K, T, T, T],
    [T, T, K, D1,D2,D1,D2,D2,D2,D1,D2,D1,K, T, T, T],
    [T, T, T, K, D1,D2,D2,D2,D2,D2,D1,K, T, T, T, T],
    [T, T, T, K, D1,D1,D1,D1,D1,D1,D1,K, T, T, T, T],
    [T, T, T, T, K, K, K, K, K, K, K, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# ============================================================
# 9. 공격형 투구 (Attack Helmet) — 뿔 달린 오픈페이스
# ============================================================
helmet_attack = [
    [T, T, T, K, T, T, T, T, T, T, T, K, T, T, T, T],
    [T, T, T, K, K, T, T, T, T, T, K, K, T, T, T, T],
    [T, T, T, T, K, K, K, K, K, K, K, T, T, T, T, T],
    [T, T, T, K, D2,D3,S1,S1,S1,D3,D2,K, T, T, T, T],
    [T, T, K, D1,D2,D3,S1,S2,S1,D3,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,R2,D3,R3,D3,R2,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,D3,D3,D3,D3,D3,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,D3,P1,D3,P1,D3,D2,D1,K, T, T, T],
    [T, T, K, K, K, K, K, K, K, K, K, K, K, T, T, T],
    [T, T, T, K, D1,D1,T, T, T, D1,D1,K, T, T, T, T],
    [T, T, T, T, K, K, T, T, T, K, K, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# ============================================================
# 10. 명중형 장갑 (Accuracy Gloves) — 가죽 건틀릿, 앰버 보석
# ============================================================
gloves_accuracy = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, K, K, K, T, T, T, K, K, K, T, T, T, T],
    [T, T, K, B2,B3,B2,K, T, K, B2,B3,B2,K, T, T, T],
    [T, T, K, B1,A2,B2,K, T, K, B2,A2,B1,K, T, T, T],
    [T, T, K, B2,B3,B2,K, T, K, B2,B3,B2,K, T, T, T],
    [T, T, K, B1,B2,B1,K, T, K, B1,B2,B1,K, T, T, T],
    [T, K, B1,B2,B2,B1,K, T, K, B1,B2,B2,B1,K, T, T],
    [T, K, B1,B2,B1,K, K, T, K, K, B1,B2,B1,K, T, T],
    [T, K, B1,B1,K, T, T, T, T, T, K, B1,B1,K, T, T],
    [T, K, B1,K, K, T, T, T, T, T, K, K, B1,K, T, T],
    [T, T, K, K, T, T, T, T, T, T, T, K, K, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# ============================================================
# 11. 속도형 장갑 (Speed Gloves) — 슬림, 녹색 위습
# ============================================================
gloves_speed = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, G2,T, T, T, T, T],
    [T, T, T, K, K, K, T, T, T, K, K, K, T, T, T, T],
    [T, T, K, D1,D2,D1,K, T, K, D1,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,D1,K, G1,K, D1,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,D1,K, T, K, D1,D2,D1,K, T, T, T],
    [T, T, K, D1,D2,D1,K, T, K, D1,D2,D1,K, T, T, T],
    [T, K, D1,D1,D2,D1,K, T, K, D1,D2,D1,D1,K, T, T],
    [T, K, K, D1,D1,K, K, T, K, K, D1,D1,K, K, T, T],
    [T, T, K, K, K, T, T, T, T, T, K, K, K, T, T, T],
    [T, G1,T, T, T, T, T, T, T, T, T, T, T, G1,T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# ============================================================
# 12. 회피형 신발 (Evasion Boots) — 어쌔신 부츠, 보라 그림자
# ============================================================
boots_evasion = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, K, K, T, T, T, T, T, K, K, T, T, T, T, T],
    [T, T, K, B2,K, T, T, T, K, B2,K, T, T, T, T, T],
    [T, T, K, B1,K, T, T, T, K, B1,K, T, T, T, T, T],
    [T, T, K, B2,K, T, T, T, K, B2,K, T, T, T, T, T],
    [T, T, K, B1,D1,K, T, K, D1,B1,K, T, T, T, T, T],
    [T, T, K, B2,D2,K, T, K, D2,B2,K, T, T, T, T, T],
    [T, T, K, B1,D1,K, T, K, D1,B1,K, T, T, T, T, T],
    [T, T, K, B2,B1,K, T, K, B1,B2,K, T, T, T, T, T],
    [T, T, K, B1,B2,K, T, K, B2,B1,K, T, T, T, T, T],
    [T, K, B1,B2,B1,K, T, K, B1,B2,B1,K, T, T, T, T],
    [T, K, K, B1,K, K, T, K, K, B1,K, K, T, T, T, T],
    [T, T, P1,K, K, P1,T, P1,K, K, P1,T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]

# ============================================================
# 13. 마법저항 신발 (Magic Resist Boots) — 중장 부츠, 아이스 룬
# ============================================================
boots_magicresist = [
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
    [T, T, K, K, K, T, T, T, K, K, K, T, T, T, T, T],
    [T, T, K, D2,D1,K, T, K, D1,D2,K, T, T, T, T, T],
    [T, T, K, D3,D2,K, T, K, D2,D3,K, T, T, T, T, T],
    [T, T, K, D2,D1,K, T, K, D1,D2,K, T, T, T, T, T],
    [T, T, K, D3,I1,K, T, K, I1,D3,K, T, T, T, T, T],
    [T, T, K, D2,I2,D1,K,K,D1,I2,D2,K, T, T, T, T],
    [T, T, K, D3,I1,D2,K,K,D2,I1,D3,K, T, T, T, T],
    [T, T, K, D2,D2,D1,K,K,D1,D2,D2,K, T, T, T, T],
    [T, T, K, D1,D2,D1,K,K,D1,D2,D1,K, T, T, T, T],
    [T, K, D1,D2,D2,D1,K,K,D1,D2,D2,D1,K, T, T, T],
    [T, K, K, D1,D1,K, K,K,K, D1,D1,K, K, T, T, T],
    [T, T, K, K, K, K, T, T, K, K, K, K, T, T, T, T],
    [T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T],
]


# ============================================================
# 생성 실행
# ============================================================
import os

# 출력 디렉터리
out_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "public", "img", "icons", "equip")
os.makedirs(out_dir, exist_ok=True)

SCALE = 4  # 16→64px 확대본도 함께 저장

icons = {
    "weapon_sword":       sword,
    "weapon_greatsword":  greatsword,
    "weapon_axe":         axe,
    "weapon_spear":       spear,
    "weapon_mace":        mace,
    "armor_heavy":        armor_heavy,
    "armor_light":        armor_light,
    "helmet_survival":    helmet_survival,
    "helmet_attack":      helmet_attack,
    "gloves_accuracy":    gloves_accuracy,
    "gloves_speed":       gloves_speed,
    "boots_evasion":      boots_evasion,
    "boots_magicresist":  boots_magicresist,
}

for name, data in icons.items():
    # 원본 16x16
    path_16 = os.path.join(out_dir, f"{name}_16.png")
    create_icon(data, path_16, scale=1)

    # 확대 64x64 (Nearest Neighbor → 도트 유지)
    path_64 = os.path.join(out_dir, f"{name}_64.png")
    create_icon(data, path_64, scale=SCALE)

    print(f"  ✓ {name}")

print(f"\n완료! 총 {len(icons)}종 × 2사이즈 = {len(icons)*2}개 아이콘")
print(f"출력 경로: {out_dir}")
