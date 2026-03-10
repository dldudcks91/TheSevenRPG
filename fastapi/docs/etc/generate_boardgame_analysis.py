# -*- coding: utf-8 -*-
"""
RPG 보드게임 아이템 구조 분석 PDF 생성 스크립트
유명 RPG 보드게임 10종의 아이템/획득 구조를 5가지 관점에서 분석
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 한글 폰트 등록
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/malgunbd.ttf"
pdfmetrics.registerFont(TTFont("Malgun", FONT_PATH))
pdfmetrics.registerFont(TTFont("MalgunBold", FONT_BOLD_PATH))

# 색상 정의
COLOR_TITLE   = HexColor("#1a1a2e")
COLOR_SECTION = HexColor("#16213e")
COLOR_ACCENT  = HexColor("#c0392b")
COLOR_TEXT    = HexColor("#2c2c2c")
COLOR_LIGHT   = HexColor("#555555")
COLOR_BG      = HexColor("#f5f0eb")
COLOR_DIVIDER = HexColor("#cccccc")
COLOR_SUB     = HexColor("#7d5a44")
COLOR_LABEL   = HexColor("#2e6b4f")

WIDTH, HEIGHT = A4
MARGIN_LEFT   = 22 * mm
MARGIN_RIGHT  = 22 * mm
MARGIN_TOP    = 20 * mm
MARGIN_BOTTOM = 18 * mm
CONTENT_WIDTH = WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# ============================================================
# 분석 관점 정의
# ============================================================

PERSPECTIVES = [
    "1. 획득 의식의 설계 — '어떻게 손에 넣는가' 자체가 경험이 되는가",
    "2. 아이템-세계관 결합도 — 아이템이 테마/스토리와 얼마나 유기적으로 연결되는가",
    "3. 결정론적 통제 구조 — 원하는 아이템을 얼마나 의도적으로 노릴 수 있는가",
    "4. 아이템 간 상호작용 밀도 — 아이템·스킬 간 콤보/시너지가 얼마나 촘촘한가",
    "5. 획득 후 흐름 — 손에 넣은 후 장착·강화·분해·재순환 경로가 얼마나 설계되어 있는가",
]

# ============================================================
# 게임 데이터 — 보드게임 10종
# ============================================================

GAMES = [
    {
        "title": "Gloomhaven",
        "subtitle": "캠페인 레거시 RPG의 정점 — 선택과 은퇴가 만드는 아이템 순환",
        "year": "2017 · Cephalofair Games",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "시나리오 클리어 후 '로드 이벤트'와 '시티 이벤트' 덱에서 카드를 뽑아 결과를 받는다. "
                    "같은 시나리오도 이벤트 결과에 따라 아이템 보상이 달라짐.",
                    "상점(Gloomhaven 도시) 해금: 새 시나리오를 열면 상점 아이템 덱이 늘어난다. "
                    "카드를 구매해 가져가면 그 카드는 덱에서 빠짐 → '재고 개념'으로 플레이어 간 희소성 경쟁 발생.",
                    "시나리오 보물 상자: 필드 특정 타일에 고정 배치. '이 상자를 열려면 자물쇠 해제 카드가 필요' 같은 조건 달성형.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "아이템 카드에는 짧은 플레이버 텍스트가 있지만 효과가 핵심. 세계관 결합은 '중간' 수준.",
                    "단, 캐릭터 은퇴(Retirement) 시스템과 연결: 특정 개인 퀘스트를 달성해 은퇴하면 "
                    "새 캐릭터 클래스가 해금되고, 은퇴 캐릭터의 아이템이 파티에 남겨진다. "
                    "아이템이 캐릭터의 '유산'이 되는 서사적 구조.",
                    "도시 번영도(Prosperity)가 오르면 고급 아이템이 상점에 등장. 마을 성장과 아이템 풀 확장이 연동.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "상점 구매는 완전 결정론적 — 골드만 있으면 원하는 아이템을 살 수 있다.",
                    "시나리오 보물은 위치 고정이라 사전에 알면 타겟팅 가능. 단, 보물 카드 내용은 랜덤.",
                    "이벤트 보상은 2지선다 카드 선택 후 결과 확인 → 선택권이 있지만 결과는 모름. "
                    "중간 결정론: '어떤 카드를 뽑느냐'는 통제 불가, '어떤 선택지를 고르느냐'는 통제 가능.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "아이템은 '머리/몸/다리/한손×2/소도구' 슬롯으로 구분. 슬롯당 1개만 장착.",
                    "아이템에는 소모형(1회 사용 후 뒤집기)과 재충전형(휴식 후 회복)이 있어 전투 중 자원 관리가 핵심.",
                    "클래스 카드(손패)와 아이템의 시너지가 빌드 핵심. 예: '이동 후 공격' 카드 + "
                    "이동력 부츠 = 레인지 확장 콤보. 아이템-클래스 카드 간 상호작용이 메인.",
                    "아이템끼리 직접 콤보는 적지만, '소모 슬롯 관리'가 전술 깊이를 만든다.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "판매: 구매가의 50%로 도시 상점에 되팔 수 있다. 팔면 상점 덱에 복귀 → 다른 플레이어가 살 수 있음.",
                    "은퇴 시 이전: 캐릭터 은퇴 시 장착 아이템을 파티 공용 풀에 넘겨 다음 캐릭터가 물려받는다.",
                    "업그레이드 없음: 아이템 자체는 성장하지 않는다. '더 좋은 아이템을 사서 교체'가 성장 방식.",
                    "저주받은 아이템(Curse Item): 일부 아이템은 저주 카드를 덱에 섞는 부작용. "
                    "강력하지만 확률 덱을 오염시키는 트레이드오프.",
                ],
            },
        ],
    },
    {
        "title": "Kingdom Death: Monster",
        "subtitle": "생존과 공포 — 사냥→해체→제작의 완전한 자급자족 루프",
        "year": "2015 · Kingdom Death",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "몬스터 사냥(Hunt Phase) → 전투(Showdown) → 해체(Butcher Phase): "
                    "몬스터를 처치하면 시체를 해체해 부위별 재료를 얻는 의식적 구조.",
                    "해체는 '해체 카드 덱'을 순서대로 뽑는 방식. 같은 몬스터도 해체 때마다 다른 부위를 얻음.",
                    "재료 수집 → 정착지 '크래프팅' 액션으로 장비 제작. 제작 레시피는 '이노베이션 트리'로 해금.",
                    "스토리 이벤트(Lantern Year 이벤트): 특정 연도에 발생하는 고정 이벤트로 "
                    "희귀 아이템/레시피를 주기도 하고 빼앗기도 한다.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "최고 수준의 결합도. 몬스터의 이름과 신체 부위가 장비 이름에 직접 반영. "
                    "예: White Lion의 발톱(Claw) → White Lion Coat, Lion Skin Boots. "
                    "어디서 온 재료인지가 장비 정체성 자체.",
                    "장비 세트마다 '아머 키워드' 보유: Beast/Bone/Leather 등. "
                    "세계관의 생존 공포 테마가 재료 출처를 통해 장비에 스며들어 있음.",
                    "아이템 카드 아트가 독립적 세계관 구축. 기능을 넘어 수집 욕구를 자극하는 설계.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "사냥: 몬스터 선택은 플레이어가 결정(어느 몬스터를 사냥할지). "
                    "단 해체 결과는 덱 드로우라 부분 랜덤.",
                    "특정 재료가 필요하면 '그 재료를 주는 몬스터'를 골라 반복 사냥. 타겟 파밍 가능.",
                    "레시피 해금은 이노베이션 카드 선택으로 어느 정도 방향 통제 가능.",
                    "치명적 랜덤 요소: 사냥 중 '이벤트 카드' 발동으로 서바이버 사망 또는 아이템 소실. "
                    "아이템을 얻으러 가다가 오히려 잃을 수 있는 극단적 불확실성.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "아머 세트 보너스: 같은 세트 4부위 이상 장착 시 세트 효과 발동. "
                    "예: 라이온 세트 완성 시 공격 실패 시에도 재굴림 옵션.",
                    "아머 키워드 시너지: Beast 키워드 장비가 많을수록 특정 스킬 파워업. "
                    "세계관 테마(Beast Mastery)가 기계적 시너지로 연결.",
                    "Fighting Art + 장비 콤보: 캐릭터 고유 전투 기술과 장비 키워드 매칭. "
                    "예: 쌍검 Fighting Art는 '쌍검 장착 시' 추가 공격 발동.",
                    "저장 한도(Gear Grid 9칸): 부위 제한이 아닌 그리드 공간 제한 → "
                    "작은 아이템을 많이 vs 큰 아이템을 적게 선택의 물리적 트레이드오프.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "파손(Break): 일부 장비는 사용 시 파손 카드를 받음. 쌓이면 장비 파괴. 소모 개념이 강함.",
                    "분해 없음, 대신 재사용: 사망한 서바이버의 장비는 정착지 공용 풀로. 사망이 아이템 순환 트리거.",
                    "업그레이드 제작: 기본 재료 장비 → 상위 재료 장비로 교체하는 것이 성장. "
                    "같은 슬롯을 더 좋은 버전으로 교체하는 방식.",
                    "정착지 저장 한도: 재료 저장 상자 크기 제한이 있어 '너무 많이 모아도 못 씀'. "
                    "욕심을 제어하는 물리적 제약.",
                ],
            },
        ],
    },
    {
        "title": "Descent: Journeys in the Dark (2판)",
        "subtitle": "오버로드 vs 영웅 — 비대칭 아이템 경제의 대결",
        "year": "2012 · Fantasy Flight Games",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "미션 완료 보상: 영웅이 미션에서 이기면 보물 카드를 뽑고, 지면 오버로드가 강화된다. "
                    "승리 여부가 아이템 획득의 전제.",
                    "상점(Conquest 포인트 소비): 마을에 돌아오면 상점 카드 덱에서 X장을 뽑아 구매 가능. "
                    "덱에 없으면 못 사는 '재고 한정' 구조.",
                    "탐색 카드(Search Token): 던전 내 특정 위치의 탐색 토큰을 발동하면 탐색 카드를 드로우. "
                    "미니 보물 상자 개념. 내용은 열어봐야 알 수 있음.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "판타지 클리셰 아이템명이 많아 세계관 결합도는 낮은 편.",
                    "단, 직업(클래스) 전용 장비 카드가 존재: 마법사 전용 지팡이류, 전사 전용 무기류. "
                    "클래스 정체성은 장비로 강화됨.",
                    "오버로드의 '강화 카드'는 반대편 관점: 영웅이 아이템을 모을수록 몬스터도 강해진다. "
                    "아이템 성장이 전쟁의 균형추 역할이라는 서사적 긴장감.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "상점 카드 드로우: 몇 장을 뽑을지는 정해져 있으나 무엇이 나올지는 랜덤 → '선택 풀 내 최선'.",
                    "클래스 카드 업그레이드: 직업별 스킬 트리는 경험치(XP) 소모로 결정론적 구매. "
                    "아이템보다 클래스 카드가 더 통제 가능한 성장 경로.",
                    "타겟 파밍 개념 없음: 특정 아이템만 노리는 구조 X. 나오면 사는 방식.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "부위 슬롯: 손(×2)/몸/머리/발 + 소도구. 슬롯 제한으로 조합 선택 발생.",
                    "무기 특성(Surges): 공격 주사위 굴림에서 Surge가 나오면 아이템 특수 효과 발동. "
                    "아이템 능력을 Surge와 얼마나 잘 활용하느냐가 전술 핵심.",
                    "파티 시너지: 탱커가 적을 묶고, 레인저 아이템으로 원거리 처치. "
                    "아이템보다 역할 분담이 시너지의 중심.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "판매 없음(캠페인 모드): 한 번 구매한 아이템은 캠페인 내내 보유. 처분 개념 없음.",
                    "클래스 카드와 장비를 조합해 '빌드' 완성이 목표. 최적 조합 발견이 플레이 동기.",
                    "분실 리스크: 일부 시나리오에서 패배 시 아이템 소실 페널티. '잃지 않는 것'도 전략.",
                ],
            },
        ],
    },
    {
        "title": "Mage Knight",
        "subtitle": "덱빌딩 × 탐험 — 카드가 곧 아이템이고 아이템이 곧 덱이다",
        "year": "2011 · WizKids",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "레벨업 시 고급 액션 카드 추가: 레벨이 오르면 '고급 액션 덱'에서 카드를 뽑아 "
                    "덱에 영구 추가. 카드가 능력이자 아이템.",
                    "스펠(Spell) 획득: 마법 탑 정복 시 스펠 카드를 받음. '탑 공략 성공'이 전제 조건.",
                    "유물(Artifact) 탐색: 유적 타일 탐험으로 유물 카드 발견. 탐험이 아이템 획득 의식.",
                    "용병(Unit) 고용: 마을에서 골드로 유닛 카드를 고용. 유닛도 아이템처럼 덱을 지원.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "카드 이름과 아트가 마나/마법/기사 세계관을 충실히 반영. '드래곤의 눈물', '룬 검' 등.",
                    "마나 결정 시스템: 5색 마나(불/얼음/흰/초록/금)를 소비해 카드를 강화. "
                    "마나 색이 스펠의 원소 테마와 직결되어 세계관 몰입도 높음.",
                    "개인 퀘스트: 각 Mage Knight 캐릭터가 고유 플레이버와 초기 덱 구성을 가짐. "
                    "캐릭터 정체성이 아이템(카드) 조합에 영향.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "레벨업 카드 선택: 2장 공개 중 1장 선택. 완전 랜덤이 아닌 '제한 선택'.",
                    "마을 상점: 공개된 카드 중 원하는 것을 골드로 구매. 재고가 바뀌면 다시 선택.",
                    "타겟팅의 핵심: '어느 타일을 탐험하느냐'로 얻을 아이템 종류를 어느 정도 방향 통제. "
                    "스펠 원하면 탑, 유물 원하면 유적.",
                    "덱 오염 리스크: 도시 패배 시 '상처(Wound) 카드'가 덱에 추가. 강한 아이템 추구 중 "
                    "덱이 쓰레기로 오염되는 역선택 위험.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "카드 조합이 전부: 기본 카드(1~2값) + 고급 카드 + 스펠을 연결해 '10+값 행동'을 만드는 것이 핵심.",
                    "마나 연동: 스펠 카드는 마나를 소비해 강화. 마나 결정 운영이 덱 시너지를 결정.",
                    "유닛 카드: 소환해 전투 지원. 유닛과 스펠을 조합하면 전투력 폭발.",
                    "덱 밀도 관리: 덱이 너무 커지면 사용률이 낮아짐 → '좋은 카드만 남기고 나쁜 카드를 버리는 것'이 전략.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "덱에서 제거 불가(기본): 한 번 추가된 카드는 게임 종료까지 덱에 남음. "
                    "선택의 영구성이 만드는 긴장감.",
                    "상처 카드 제거: 수도원 방문 시 상처 카드를 덱에서 제거 가능. '덱 정화'가 회복 행위.",
                    "게임 종료 후 점수 계산: 아이템 자체보다 '무엇을 달성했는가'로 승패 결정. "
                    "아이템은 수단, 목표(점수)가 별도 존재.",
                ],
            },
        ],
    },
    {
        "title": "Arkham Horror: The Card Game",
        "subtitle": "커스텀 덱빌딩 LCG — 덱 구성이 곧 캐릭터 빌드",
        "year": "2016 · Fantasy Flight Games",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "시나리오 보상: 클리어 후 '경험치(XP)'를 획득. XP로 덱에 업그레이드 카드를 추가.",
                    "캠페인 해금: 특정 시나리오 결과에 따라 특수 카드가 해금 or 영구 봉인. "
                    "스토리 선택이 카드 풀에 직접 영향.",
                    "카드 구매 없음(LCG 방식): 모든 카드는 패키지로 제공. '무엇을 살지'가 아니라 "
                    "'무엇을 덱에 넣을지'가 선택.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "최고 수준: 크툴루 신화 세계관을 카드 텍스트와 이름에 철저히 반영. "
                    "장비 카드 '단검'도 '엘더 사인이 새겨진 단검'으로 서사화.",
                    "저주/봉인 시스템: 특정 카드는 카오스 토큰 결과가 나쁠수록 부작용 발동. "
                    "세계관의 '인간이 통제할 수 없는 공포'가 기계적으로 구현.",
                    "캐릭터 특성(Trait): Guardian/Seeker/Rogue 등 클래스별로 접근 가능 카드 풀이 다름. "
                    "캐릭터 정체성이 아이템 선택지를 제한.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "덱 구성(Deckbuilding)이 핵심 결정론: 시나리오 시작 전 30장 덱을 직접 설계. "
                    "원하는 카드를 원하는 만큼(한도 내) 넣을 수 있음.",
                    "XP 업그레이드: 기본 카드를 상위 버전으로 교체하는 결정론적 성장. "
                    "'어떤 카드를 먼저 업그레이드하는가'가 전략.",
                    "카오스 토큰: 판정 시 뽑는 토큰은 랜덤. 덱이 아무리 잘 설계되어도 '운의 바람'이 존재.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "슬롯 시스템: 손(×2)/몸/동맹자/악세(×2)/비밀지식. 슬롯당 1장만 플레이 가능.",
                    "카드 간 시너지가 극도로 풍부: '이 카드가 플레이 중일 때 다른 카드 효과 +2' 형태의 "
                    "조건부 시너지가 수십 가지.",
                    "수사관 능력(Ability): 각 캐릭터 고유 능력이 특정 카드 타입을 강화. "
                    "덱 구성 시 능력과 카드 조합을 맞추는 것이 빌드의 핵심.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "소모 카드(Consumable): 한 번 사용 후 버리는 카드(물약 등). 캠페인 진행 중 소비됨.",
                    "정신력/체력 피해: 피해를 받으면 덱에서 카드를 버려야 함. 강한 카드가 먼저 소모되는 고통.",
                    "캠페인 영구 사망: 캐릭터가 정신/체력을 모두 잃으면 트라우마 페널티 or 영구 사망. "
                    "모든 카드 잃음 → 리셋. 획득한 것이 사라지는 극적 흐름.",
                    "캠페인 결과 반영: 이번 시나리오에서 소비한 카드는 다음 시나리오에서 회복. "
                    "캠페인 단위 자원 관리.",
                ],
            },
        ],
    },
    {
        "title": "Dungeon Crawl Classics RPG",
        "subtitle": "OSR의 부활 — 예측 불가한 마법과 운명의 아이템",
        "year": "2012 · Goodman Games",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "레벨 0 '깔때기' 던전: 다수의 레벨 0 캐릭터로 던전 시작, 살아남은 자만 레벨 1이 됨. "
                    "생존이 아이템 획득의 전제 조건.",
                    "마법 아이템 판별 의식: 아이템을 주워도 효과를 모름. '판별 마법'을 쓰거나 직접 사용해봐야 알 수 있음. "
                    "미지의 아이템을 사용하는 것 자체가 긴장감 있는 의식.",
                    "보물 테이블 롤: GM이 랜덤 보물 테이블에서 주사위를 굴려 아이템 결정. "
                    "구체적 아이템보다 '테이블에서 무엇이 나올까'의 기대감.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "매우 높음: 마법 아이템은 고유한 이름과 저주를 가짐. 제조자와 역사가 있는 유물 개념.",
                    "패트런 시스템: 신/악마와 계약한 마법사는 패트런 고유 마법을 사용. "
                    "아이템(마법)이 세계관 신화와 직결.",
                    "저주 아이템: 착용 시 저주가 발동되며 벗을 수 없음. 세계관의 '탐욕에 대한 경고'가 기계화.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "최소 결정론: 보물은 GM의 테이블 롤로 결정. 플레이어가 원하는 아이템을 타겟팅하는 개념 없음.",
                    "마법 발동 변동성: 마법사가 주문 시전 시 주사위 결과에 따라 약화/강화/대재앙 중 랜덤 발동. "
                    "같은 마법이 매번 다른 결과.",
                    "클래스 선택이 핵심 결정론: '어떤 직업으로 플레이하느냐'가 가장 큰 통제 요소.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "단순한 편: 아이템은 개별 효과 중심. 복잡한 콤보 시스템보다 상황별 판단이 핵심.",
                    "마법 아이템의 독특한 효과: '한 달에 한 번만 사용 가능', '특정 이름을 말해야 발동' 등 "
                    "규칙 밖의 창의적 제약이 상호작용 만들어냄.",
                    "무기 크리티컬 테이블: 무기 종류마다 다른 크리티컬 테이블. 같은 검도 단검과 대검이 다른 방식으로 치명타.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "파손 없음(기본): 아이템은 영구적. 단, 저주 아이템은 '제거 퀘스트'가 별도 발생.",
                    "판매/거래: 마을에서 금화로 교환 가능. 금화로 더 좋은 장비 구매 or 모험 자금.",
                    "레거시 없음: 캐릭터 사망 시 아이템은 파티에 남거나 던전에 방치. 인수인계 여부는 파티 결정.",
                    "마법 아이템 연구: 일부 시스템에서 마법 아이템을 분해해 마법 서적에 기록 가능. "
                    "획득→연구→재현 사이클.",
                ],
            },
        ],
    },
    {
        "title": "Sword & Sorcery",
        "subtitle": "불멸 영웅 — 사망이 아닌 약화로 순환하는 아이템 경제",
        "year": "2017 · Ares Games",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "스토리 클리어 보상: 각 미션 말미에 '스토리 보물 카드'를 뽑음. 시나리오 성공 여부에 따라 뽑는 장 수가 다름.",
                    "상점(영혼 점수 소비): 미션 사이 마을에서 영혼 점수를 소모해 아이템 구매. "
                    "킬 vs 쇼핑의 자원 선택.",
                    "필드 보물 상자: 던전 내 보물 상자 토큰 발동. '탐색 액션'을 사용해야 열 수 있음.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "영웅별 고유 장비: 각 캐릭터 전용 유물 아이템 존재. 예: 마법사 영웅은 '불꽃의 지팡이' 스타터.",
                    "불멸 시스템과 아이템 연동: 영웅이 사망해도 '유령 상태'로 다음 미션 시작. "
                    "부활 시 아이템 일부 회수 가능. 죽어도 모든 걸 잃지 않는 설계.",
                    "영혼 점수(Soul): 적을 처치해 영혼을 모으고, 그 영혼으로 장비를 구매. "
                    "판타지 세계관의 '영혼 수집'이 경제 시스템으로 구현.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "상점 구매: 영혼 점수만 충분하면 공개된 아이템을 선택 구매. 중간 결정론.",
                    "보물 카드 드로우: 장르 특성상 랜덤 드로우. 좋은 카드를 원한다고 노릴 방법 없음.",
                    "영웅 성장(파워 크리스탈): XP와 별개로 파워 크리스탈로 능력을 확정 업그레이드. "
                    "아이템 외 성장은 결정론적.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "슬롯: 무기/방어구/악세사리. 슬롯 수가 적어 선택이 명확.",
                    "파워 조합: 아이템 효과 + 영웅 능력의 조합. 예: '공격 후 이동' 영웅 능력 + "
                    "'이동 시 보조 공격' 아이템 = 히트앤런 전술.",
                    "멀티플레이어 시너지: 협동 플레이 시 '다른 영웅이 인접해 있을 때 효과 발동' 아이템. "
                    "아이템이 협동 전술을 유도하는 설계.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "캠페인 지속: 아이템은 캠페인 내내 유지. '좋은 아이템을 모아 캠페인 마지막 보스에 도전'이 목표.",
                    "판매 가능: 영혼 점수로 환산해 판매 후 다른 아이템 구매.",
                    "영웅 사망 시 패널티: 부활 시 가장 값비싼 아이템 1개 잃음. '사망 리스크 관리'가 아이템 보호와 연결.",
                    "강화 없음: 아이템은 고정 스탯. 성장은 '더 좋은 아이템으로 교체'.",
                ],
            },
        ],
    },
    {
        "title": "Gloomhaven: Jaws of the Lion",
        "subtitle": "Gloomhaven 입문판 — 단순화된 구조로 핵심만 남긴 아이템 철학",
        "year": "2020 · Cephalofair Games",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "시나리오 보상 단순화: 매 시나리오 클리어 시 정해진 골드+아이템 조합 제공. "
                    "랜덤 요소 최소화.",
                    "캐릭터 고유 아이템 트리: Jaws of the Lion 4 캐릭터 각각 전용 아이템 풀. "
                    "성장 경로가 명확하게 설계됨.",
                    "스티커 해금: 시나리오 북 스티커 시스템으로 새 콘텐츠(아이템 포함)를 물리적으로 해금. "
                    "보드게임의 레거시 메커니즘을 간략화.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "원작 Gloomhaven보다 세계관 집중도 높음: 4 캐릭터의 스토리가 아이템 획득 맥락 제공.",
                    "Red Guard(방패 캐릭터)의 아이템은 방어/보호 테마. Demolitionist는 폭발물 관련 아이템. "
                    "클래스 정체성과 아이템 테마가 일치.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "원작보다 결정론 높음: 시나리오를 클리어하면 정해진 보상을 받음. 랜덤 드로우 최소화.",
                    "골드 구매: 상점에서 원하는 아이템 구매. 단, 해금된 아이템만 구매 가능.",
                    "캐릭터 고유 카드 업그레이드: XP로 고유 카드를 결정론적으로 업그레이드.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "원작 대비 단순화: 아이템 종류와 수가 적어 콤보보다 역할 수행에 집중.",
                    "4인 파티 시너지: 각 캐릭터가 뚜렷한 역할(탱/딜/힐/버프)을 가지고, "
                    "아이템이 그 역할을 강화하는 방식.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "은퇴 없음(Jaws of the Lion은 캐릭터 고정): 아이템 순환이 원작보다 단순.",
                    "캠페인 진행에 따라 자연스럽게 아이템 풀이 성장. 관리 부담 최소화.",
                    "판매 가능: 원작과 동일하게 50% 가격으로 반환.",
                ],
            },
        ],
    },
    {
        "title": "Folklore: The Affliction",
        "subtitle": "스토리 중심 협동 — 이야기가 아이템 출처를 정당화하는 게임",
        "year": "2017 · Greenbrier Games",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "인카운터 해결 보상: 챕터 내 특정 이벤트(수수께끼, 전투, 대화)를 해결하면 아이템 카드 제공.",
                    "마을 상인: 챕터 사이 마을 방문 시 상인 카드 덱에서 구매. 마을에 따라 다른 상인 풀.",
                    "퀘스트 완료 보상: 사이드 퀘스트 카드 완료 시 특수 보상. 선택형 콘텐츠가 추가 아이템 제공.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "높음: 19세기 유럽 민담/공포 테마(뱀파이어, 늑대인간, 마녀 등). "
                    "아이템이 민담 맥락에서 등장. '성수가 담긴 성배', '은탄환' 등.",
                    "아이템이 스토리 챕터와 연동: 특정 챕터에서만 얻을 수 있는 아이템이 "
                    "그 챕터의 스토리와 직결.",
                    "저주 아이템: 오염된 아이템은 사용할수록 플레이어 캐릭터에게 '고통(Affliction)'을 쌓음. "
                    "세계관 테마가 기계적으로 구현.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "챕터 선형 구조: 정해진 챕터 순서가 아이템 흐름을 결정. 타겟 파밍 개념 없음.",
                    "상인 구매: 공개된 카드 중 선택 구매. 중간 결정론.",
                    "퀘스트 선택: 어떤 사이드 퀘스트를 먼저 할지 선택 → 보상 방향 일부 통제 가능.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "클래스 특성 + 아이템 키워드 매칭: '기사' 클래스가 '방어' 키워드 아이템 장착 시 시너지.",
                    "세트 수집 개념: 같은 스토리 출처 아이템을 모으면 추가 효과 발동.",
                    "전반적으로 시너지 밀도는 낮고 스토리 몰입이 우선. "
                    "복잡한 콤보보다 '이 아이템을 가지고 스토리를 진행'하는 것이 목표.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "캠페인 영구 보유: 한 번 얻은 아이템은 캠페인 내내 유지.",
                    "고통(Affliction) 해제: 오염 아이템을 '정화 의식'으로 해제. 아이템 관리가 서사적 행위.",
                    "챕터 종료 시 정리: 챕터별로 사용한 아이템 소모 여부 확인. 소모형 아이템 관리.",
                ],
            },
        ],
    },
    {
        "title": "Middara: Unintentional Malum",
        "subtitle": "애니메이션 스타일 캠페인 — 방대한 장비 + JRPG식 성장의 보드게임화",
        "year": "2020 · Succubus Publishing",
        "sections": [
            {
                "heading": "1. 획득 의식의 설계",
                "bullets": [
                    "상점 시스템(고급): 마을 방문 시 대형 상점 카드 덱에서 X장을 공개해 구매. "
                    "Descent와 유사하지만 아이템 종류가 훨씬 방대.",
                    "미션 드롭: 적 처치 시 장비 드롭 카드를 뽑음. 강한 적일수록 고급 장비 드롭 테이블.",
                    "레시피 제작: 재료를 모아 제작소에서 특수 아이템 제작. 레시피 카드는 별도 획득.",
                    "스토리 보상: 캠페인 분기 선택에 따른 독점 보상 아이템 존재.",
                ],
            },
            {
                "heading": "2. 아이템-세계관 결합도",
                "bullets": [
                    "JRPG 스타일 세계관: 아이템 이름과 아트가 애니메이션 판타지 테마. "
                    "캐릭터별 전용 무기 스킨(아트 변경) 존재.",
                    "동반자(Companion) 시스템: 스토리 동반자 캐릭터가 고유 장비 세트 보유. "
                    "서사 관계가 아이템 구조에 반영.",
                    "스킬 트리 + 장비 연동: 캐릭터 스킬 업그레이드가 특정 장비 효과를 강화. "
                    "성장 서사가 기계적 장비 시너지로 이어짐.",
                ],
            },
            {
                "heading": "3. 결정론적 통제 구조",
                "bullets": [
                    "미션 드롭의 랜덤성 + 타겟팅: '이 적을 잡으면 이 테이블에서 뽑는다'는 사전 공개. "
                    "어떤 적을 집중 공략할지 선택 가능.",
                    "상점 구매: 재고 내에서 원하는 것 선택. 중간~높은 결정론.",
                    "캠페인 분기: 어떤 스토리 분기를 선택하느냐에 따라 독점 아이템이 달라짐. "
                    "선택의 결과가 아이템 풀에 영향.",
                ],
            },
            {
                "heading": "4. 아이템 간 상호작용 밀도",
                "bullets": [
                    "가장 높은 수준의 보드게임 중 하나: 부위별 슬롯(10+) × 스킬 트리 × 장비 특성 태그. "
                    "디지털 RPG 수준의 빌드 다양성.",
                    "태그 시스템: 아이템에 'Fire/Ice/Holy' 등 태그 부여. 캐릭터 스킬이 '특정 태그 아이템 장착 시' 발동.",
                    "세트 보너스: 동일 세트 장비 조합 시 추가 효과. 3부위 세트, 5부위 세트 등.",
                    "무기 콤보: 쌍수 무기 조합에 따라 다른 콤보 효과. 예: 단검+단검 vs 단검+방패 전혀 다른 플레이.",
                ],
            },
            {
                "heading": "5. 획득 후 흐름",
                "bullets": [
                    "강화 시스템: 장비에 '강화 슬롯'이 있어 재료를 소모해 스탯 업. 디지털 RPG 강화 시스템 완전 보드게임화.",
                    "분해: 불필요 장비를 분해해 강화 재료 획득. 드롭 → 분해 → 강화 순환.",
                    "판매: 상점에서 금화로 환산 판매. 환율이 높지 않아 '판매보다 분해'가 합리적 선택.",
                    "무기 레벨링: 같은 무기를 계속 사용하면 숙련도 증가 → 추가 효과 해금. "
                    "무기 교체 vs 숙련도 포기의 딜레마.",
                ],
            },
        ],
    },
]

# ============================================================
# PDF 렌더링 유틸
# ============================================================

def new_page(c_obj, page_num):
    c_obj.showPage()
    page_num += 1
    # 배경
    c_obj.setFillColor(HexColor("#faf7f4"))
    c_obj.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    # 상단 띠
    c_obj.setFillColor(COLOR_SECTION)
    c_obj.rect(0, HEIGHT - 12 * mm, WIDTH, 12 * mm, fill=1, stroke=0)
    # 하단 페이지 번호
    c_obj.setFillColor(COLOR_LIGHT)
    c_obj.setFont("Malgun", 8)
    c_obj.drawCentredString(WIDTH / 2, MARGIN_BOTTOM - 8, f"- {page_num} -")
    return page_num


def draw_cover(c_obj):
    """표지 페이지"""
    # 배경
    c_obj.setFillColor(COLOR_TITLE)
    c_obj.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)

    # 상단 장식 띠
    c_obj.setFillColor(COLOR_ACCENT)
    c_obj.rect(0, HEIGHT - 30 * mm, WIDTH, 6 * mm, fill=1, stroke=0)
    c_obj.setFillColor(HexColor("#7d2020"))
    c_obj.rect(0, HEIGHT - 36 * mm, WIDTH, 3 * mm, fill=1, stroke=0)

    # 메인 타이틀
    c_obj.setFillColor(HexColor("#ffffff"))
    c_obj.setFont("MalgunBold", 26)
    c_obj.drawCentredString(WIDTH / 2, HEIGHT - 80 * mm, "RPG 보드게임 아이템 구조 분석")

    c_obj.setFont("MalgunBold", 18)
    c_obj.setFillColor(COLOR_ACCENT)
    c_obj.drawCentredString(WIDTH / 2, HEIGHT - 95 * mm, "유명 보드게임 10종 × 5대 관점")

    # 구분선
    c_obj.setStrokeColor(COLOR_ACCENT)
    c_obj.setLineWidth(1.5)
    c_obj.line(MARGIN_LEFT + 20 * mm, HEIGHT - 103 * mm, WIDTH - MARGIN_RIGHT - 20 * mm, HEIGHT - 103 * mm)

    # 분석 관점 목록
    c_obj.setFont("MalgunBold", 11)
    c_obj.setFillColor(HexColor("#e0d0c0"))
    c_obj.drawCentredString(WIDTH / 2, HEIGHT - 115 * mm, "[ 분석 5대 관점 ]")

    c_obj.setFont("Malgun", 10)
    c_obj.setFillColor(HexColor("#ccbbaa"))
    perspectives_short = [
        "1. 획득 의식의 설계",
        "2. 아이템-세계관 결합도",
        "3. 결정론적 통제 구조",
        "4. 아이템 간 상호작용 밀도",
        "5. 획득 후 흐름",
    ]
    for i, p in enumerate(perspectives_short):
        c_obj.drawCentredString(WIDTH / 2, HEIGHT - 128 * mm - i * 13, p)

    # 게임 목록
    c_obj.setFont("MalgunBold", 10)
    c_obj.setFillColor(HexColor("#e0d0c0"))
    c_obj.drawCentredString(WIDTH / 2, HEIGHT - 210 * mm, "[ 분석 대상 게임 ]")

    c_obj.setFont("Malgun", 9)
    c_obj.setFillColor(HexColor("#bbaa99"))
    game_list_left = [
        "① Gloomhaven",
        "② Kingdom Death: Monster",
        "③ Descent: Journeys in the Dark",
        "④ Mage Knight",
        "⑤ Arkham Horror: The Card Game",
    ]
    game_list_right = [
        "⑥ Dungeon Crawl Classics RPG",
        "⑦ Sword & Sorcery",
        "⑧ Gloomhaven: Jaws of the Lion",
        "⑨ Folklore: The Affliction",
        "⑩ Middara: Unintentional Malum",
    ]
    col_x_left  = WIDTH / 2 - 55 * mm
    col_x_right = WIDTH / 2 + 5 * mm
    for i in range(5):
        y = HEIGHT - 222 * mm - i * 12
        c_obj.drawString(col_x_left,  y, game_list_left[i])
        c_obj.drawString(col_x_right, y, game_list_right[i])

    # 하단 서명
    c_obj.setFont("Malgun", 8)
    c_obj.setFillColor(HexColor("#887766"))
    c_obj.drawCentredString(WIDTH / 2, MARGIN_BOTTOM + 5 * mm, "TheSevenRPG 기획팀 내부 참고용 · 2026")


def draw_game(c_obj, game, page_num):
    """게임 1개를 다중 페이지에 걸쳐 렌더링"""
    # 새 페이지 시작
    c_obj.showPage()
    page_num += 1

    # 배경
    c_obj.setFillColor(HexColor("#faf7f4"))
    c_obj.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)

    # 상단 게임 헤더 배경
    c_obj.setFillColor(COLOR_TITLE)
    c_obj.rect(0, HEIGHT - 38 * mm, WIDTH, 38 * mm, fill=1, stroke=0)

    # 게임 타이틀
    c_obj.setFont("MalgunBold", 16)
    c_obj.setFillColor(HexColor("#ffffff"))
    c_obj.drawString(MARGIN_LEFT, HEIGHT - 17 * mm, game["title"])

    # 서브타이틀
    c_obj.setFont("Malgun", 9)
    c_obj.setFillColor(HexColor("#ccbbaa"))
    c_obj.drawString(MARGIN_LEFT, HEIGHT - 26 * mm, game["subtitle"])

    # 연도
    c_obj.setFont("Malgun", 8)
    c_obj.setFillColor(HexColor("#aaaaaa"))
    c_obj.drawRightString(WIDTH - MARGIN_RIGHT, HEIGHT - 17 * mm, game["year"])

    # 페이지 번호
    c_obj.setFont("Malgun", 8)
    c_obj.setFillColor(HexColor("#888888"))
    c_obj.drawCentredString(WIDTH / 2, MARGIN_BOTTOM - 8, f"- {page_num} -")

    y = HEIGHT - 45 * mm
    bottom_limit = MARGIN_BOTTOM + 10 * mm

    for section in game["sections"]:
        # 섹션 들어갈 공간 예측 (헤딩 + 최소 1 bullet)
        needed = 12 + 14 + 5  # heading + 1 bullet + gap
        if y - needed < bottom_limit:
            # 새 페이지
            c_obj.showPage()
            page_num += 1
            c_obj.setFillColor(HexColor("#faf7f4"))
            c_obj.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
            c_obj.setFillColor(COLOR_SECTION)
            c_obj.rect(0, HEIGHT - 12 * mm, WIDTH, 12 * mm, fill=1, stroke=0)
            c_obj.setFont("MalgunBold", 9)
            c_obj.setFillColor(HexColor("#ccbbaa"))
            c_obj.drawString(MARGIN_LEFT, HEIGHT - 8 * mm, f"↑ {game['title']} (계속)")
            c_obj.setFont("Malgun", 8)
            c_obj.setFillColor(HexColor("#888888"))
            c_obj.drawCentredString(WIDTH / 2, MARGIN_BOTTOM - 8, f"- {page_num} -")
            y = HEIGHT - 18 * mm

        # 섹션 헤딩 배경
        c_obj.setFillColor(COLOR_SECTION)
        c_obj.roundRect(MARGIN_LEFT - 2, y - 10, CONTENT_WIDTH + 4, 14, 3, fill=1, stroke=0)
        c_obj.setFont("MalgunBold", 10)
        c_obj.setFillColor(HexColor("#ffffff"))
        c_obj.drawString(MARGIN_LEFT + 2, y - 7, section["heading"])
        y -= 18

        # bullets
        for bullet in section["bullets"]:
            # 긴 텍스트 줄 나누기
            lines = wrap_text(bullet, "Malgun", 9, CONTENT_WIDTH - 10)
            needed_h = len(lines) * 13 + 4
            if y - needed_h < bottom_limit:
                c_obj.showPage()
                page_num += 1
                c_obj.setFillColor(HexColor("#faf7f4"))
                c_obj.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
                c_obj.setFillColor(COLOR_SECTION)
                c_obj.rect(0, HEIGHT - 12 * mm, WIDTH, 12 * mm, fill=1, stroke=0)
                c_obj.setFont("MalgunBold", 9)
                c_obj.setFillColor(HexColor("#ccbbaa"))
                c_obj.drawString(MARGIN_LEFT, HEIGHT - 8 * mm, f"↑ {game['title']} (계속)")
                c_obj.setFont("Malgun", 8)
                c_obj.setFillColor(HexColor("#888888"))
                c_obj.drawCentredString(WIDTH / 2, MARGIN_BOTTOM - 8, f"- {page_num} -")
                y = HEIGHT - 18 * mm

            # bullet 점
            c_obj.setFillColor(COLOR_ACCENT)
            c_obj.circle(MARGIN_LEFT + 3, y - 3, 2, fill=1, stroke=0)
            # 텍스트
            c_obj.setFont("Malgun", 9)
            c_obj.setFillColor(COLOR_TEXT)
            for li, line in enumerate(lines):
                c_obj.drawString(MARGIN_LEFT + 9, y, line)
                y -= 13
            y -= 2

        y -= 6  # 섹션 간격

    return page_num


def wrap_text(text, font_name, font_size, max_width):
    """텍스트를 max_width에 맞게 줄 나누기"""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    words = text.split(' ')
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if stringWidth(test, font_name, font_size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [text]


# ============================================================
# 메인 실행
# ============================================================

def main():
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "RPG_BoardGame_Item_Analysis.pdf"
    )
    c_obj = canvas.Canvas(output_path, pagesize=A4)

    # 표지
    draw_cover(c_obj)

    # 게임별 페이지
    page_num = 1
    for game in GAMES:
        page_num = draw_game(c_obj, game, page_num)

    c_obj.save()
    print(f"PDF 생성 완료: {output_path}")
    print(f"총 게임 수: {len(GAMES)}")


if __name__ == "__main__":
    main()
