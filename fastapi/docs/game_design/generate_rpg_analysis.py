# -*- coding: utf-8 -*-
"""
RPG 아이템 & 파밍 구조 분석 PDF 생성 스크립트
10개 유명 RPG 게임의 아이템/파밍 구조를 5가지 관점에서 분석
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
COLOR_TITLE = HexColor("#1a1a2e")
COLOR_SECTION = HexColor("#16213e")
COLOR_ACCENT = HexColor("#e94560")
COLOR_TEXT = HexColor("#2c2c2c")
COLOR_LIGHT = HexColor("#666666")
COLOR_BG = HexColor("#f0f0f0")
COLOR_DIVIDER = HexColor("#cccccc")

WIDTH, HEIGHT = A4  # 595 x 842 points
MARGIN_LEFT = 25 * mm
MARGIN_RIGHT = 25 * mm
MARGIN_TOP = 20 * mm
MARGIN_BOTTOM = 15 * mm
CONTENT_WIDTH = WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# ============================================================
# 게임 데이터
# ============================================================

GAMES = [
    {
        "title": "Diablo 2: Resurrected",
        "subtitle": "파밍 RPG의 원형 — 랜덤 드롭과 룬워드의 정수",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(13종), 방어구(머리/몸/장갑/벨트/신발), 방패, 악세서리(반지/목걸이)",
                    "등급: Normal → Exceptional → Elite (베이스 3단계) × White/Magic/Rare/Set/Unique",
                    "베이스 아이템이 방어력·데미지 범위를 결정 → Elite 베이스가 핵심",
                    "접사 시스템: Magic(접두1+접미1), Rare(접두3+접미3), Unique/Set은 고정 효과",
                    "소켓 수는 베이스 아이템 종류·난이도·몬스터에 의해 결정됨",
                    "좋은 장비 = Elite 베이스 + 높은 접사 티어 or 강력한 룬워드 조합",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "룬(Rune): El~Zod 33종. 단독 소켓 삽입 or 룬워드 조합의 핵심 재료",
                    "주얼(Jewel): Magic~Rare 등급, 소켓에 삽입하여 커스텀 옵션 부여",
                    "차암(Charm): 인벤토리에 보유만 해도 효과 발동 (Small/Large/Grand)",
                    "보석(Gem): 7종×5등급, 소켓 삽입용. 큐브 조합 재료로도 사용",
                    "열쇠/기관: 우버 트리스트럼 진입 재료 (공포/증오/파괴의 열쇠 → 기관)",
                    "골드, 에센스(리스펙 재료), 토큰 등 소모성 재화",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "룬 → 룬워드: 특정 베이스+특정 룬 조합 = 최강 장비 생성 (Enigma, Infinity 등)",
                    "룬 → 단독 삽입: 개별 룬도 저항/데미지 등 유용한 옵션 제공",
                    "차암 → 직접 장착: 인벤토리에 넣어 스탯/저항/스킬 보너스 획득",
                    "주얼/보석 → 소켓 삽입: 장비 소켓에 넣어 추가 옵션 부여",
                    "고급 룬(HR) → 거래 화폐: Ist, Vex, Ohm, Ber, Jah 등이 사실상 화폐 역할",
                    "에센스 4종 → 토큰 오브 앱솔루션: 스킬/스탯 리셋 아이템",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "호라드릭 큐브: 아이템 조합 시스템 — 업그레이드, 리롤, 수리 등 40+ 레시피",
                    "룬 업그레이드: 하위 룬 3개 → 상위 룬 1개 (El~Amn), 이후 2개+보석 조합",
                    "크래프팅: 특정 재료 조합 → 고정 접사 + 랜덤 접사를 가진 장비 생성",
                    "리롤: Magic/Rare 아이템의 접사를 큐브로 재생성",
                    "소켓 추가: 라자크 퀘스트(1회) or 큐브 레시피(랜덤 수)",
                    "분해 개념 없음 — 불필요한 장비는 NPC 판매 or 버림",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "타겟 파밍: 특정 보스가 특정 유니크를 드롭 (메피스토→오큘러스, 바알→그리폰)",
                    "MF(Magic Find): 스탯으로 Magic/Rare/Set/Unique 드롭률 직접 조절",
                    "난이도 3단계(Normal/Nightmare/Hell) + Area Level이 드롭 가능 아이템 결정",
                    "무제한 파밍: 시간 제한 없이 보스런·카우런·피트런 등 반복 가능",
                    "거래 경제: 자유 거래 기반, HR이 화폐 → 파밍 동기가 거래에도 연결",
                    "TC(Treasure Class) 시스템: 몬스터별 드롭 테이블이 정교하게 분류됨",
                ]
            },
        ]
    },
    {
        "title": "Diablo 3: Reaper of Souls",
        "subtitle": "세트 아이템 중심 설계와 무한 스케일링 파밍",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(메인핸드/오프핸드), 방어구 6부위, 악세서리(반지2/목걸이1)",
                    "등급: Normal → Magic → Rare → Legendary → Ancient → Primal Ancient",
                    "세트 아이템이 핵심: 2/4/6세트 효과가 데미지를 수천~수만% 증폭",
                    "주요 옵션: 주스탯+체력+치명타+치명타데미지+쿨타임감소 (옵션 풀이 좁음)",
                    "Ancient은 Legendary의 상위 스탯 롤, Primal은 모든 옵션이 최대치",
                    "좋은 장비 = 맞는 세트 + Ancient 등급 + 올바른 옵션 조합",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "레전더리/세트 장비 자체가 핵심 파밍 대상 (범용 드롭 풀)",
                    "피의 파편(Blood Shard): 카다라에게 도박으로 장비 획득하는 재화",
                    "데스 브레스(Death's Breath): 크래프팅 핵심 재료, 엘리트 몹 드롭",
                    "보석(Gem): 루비/토파즈/에메랄드/다이아/자수정 — 소켓 삽입",
                    "보석감정석(Ramaladni's Gift): 무기에 소켓 1개 무료 추가 (초희귀)",
                    "부서진 왕관 등 특수 보석류 + 칼데세의 절망(Caldesann) 증강 재료",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "레전더리 → 카나이 큐브 추출: 장비 고유 효과를 큐브에 저장 (최대 3개 동시 적용)",
                    "피의 파편 → 카다라 도박: 특정 부위를 지정하여 레전더리 노림",
                    "데스 브레스 → 리롤/크래프팅: 큐브 레시피의 핵심 소모 재료",
                    "보석 → 소켓 삽입: 무기(에메랄드=치명타), 방어구(주스탯), 악세서리(쿨감 등)",
                    "레전더리 보석 → 그레이터 리프트 클리어 시 업그레이드, 악세서리 소켓에 장착",
                    "칼데세 증강: 고레벨 보석 + 장비 → 주스탯 영구 추가 (엔드게임 핵심)",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "카나이 큐브: D2 호라드릭 큐브의 확장판 — 추출/변환/리롤/업그레이드 등",
                    "옵션 리롤(Enchant): 장비의 옵션 1개를 선택하여 반복 리롤 (미스틱 NPC)",
                    "Rare → Legendary 업그레이드: 큐브 레시피로 Rare를 Legendary로 변환",
                    "세트 변환: 같은 세트 내 다른 부위로 변환 가능",
                    "보석 결합: 하위 보석 3개 → 상위 보석 1개 (주얼러 NPC)",
                    "칼데세 증강: 레전더리 보석 Lv + Ancient 장비 → 주스탯 추가 (비파괴적)",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "그레이터 리프트(GR): 무한 스케일링 던전, 티어가 높을수록 보상 증가",
                    "스마트 드롭: 현재 클래스에 맞는 주스탯 장비가 우선 드롭 (타겟 파밍 약화)",
                    "타겟 파밍 부재 → 대량 드롭·빠른 식별·분해 루프가 핵심",
                    "시즌 시스템: 매 시즌 신규 캐릭터로 리셋, 시즌 보너스/테마 제공",
                    "파라곤 레벨: 무한 레벨 시스템, 주스탯 지속 성장 → 파밍 동기 유지",
                    "카다라 도박 + 큐브 변환으로 원하는 부위를 간접적으로 타겟팅",
                ]
            },
        ]
    },
    {
        "title": "Diablo 4",
        "subtitle": "템퍼링·마스터워킹으로 진화한 크래프팅 시스템",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(메인/오프), 방어구 5부위, 악세서리(반지2/목걸이1)",
                    "등급: Normal → Magic → Rare → Legendary → Unique → Mythic",
                    "GA(Greater Affix): 옵션이 1.5배 증폭된 특수 접사, 최대 3GA 가능",
                    "아이템 파워(IP): 장비 레벨 — 높을수록 기본 스탯 범위 상승",
                    "접사 시스템: 접두/접미 각 2개, Legendary는 고유 측면(Aspect) 추가",
                    "좋은 장비 = 높은 IP + 3GA + 맞는 접사 조합 + 좋은 Aspect 롤",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "장비 자체: Legendary/Unique 파밍이 기본 (특히 GA붙은 장비)",
                    "재료: 가죽/광석/허브 등 등급별 크래프팅 재료",
                    "템퍼링 레시피(Tempering Manual): 특정 접사 풀을 해금하는 드롭 아이템",
                    "마스터워킹 재료: 고급 던전(Pit)에서 드롭, 장비 수치 강화용",
                    "오벌(Obols): 몬스터·이벤트에서 획득, 도박 NPC용 재화",
                    "물약 업그레이드 재료, 인챈트 재료 등 소모성 자원",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "Aspect 추출: 레전더리 장비에서 Aspect를 분리 → 다른 장비에 각인",
                    "템퍼링: 장비에 새로운 접사를 추가 (최대 2회, 레시피 필요, 시행 횟수 제한)",
                    "마스터워킹: 장비의 모든 접사 수치를 단계적으로 상승 (+5%씩, 4단계마다 25%)",
                    "오벌 → 도박: 특정 부위를 지정하여 장비 획득 시도",
                    "인챈트: 접사 1개를 리롤 (D3 미스틱과 유사)",
                    "소켓 추가: 주얼러에서 소켓 생성, 보석 삽입으로 저항/데미지 강화",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "템퍼링(Tempering): 핵심 시스템 — 제한된 시행 내에 원하는 접사를 노림",
                    "마스터워킹(Masterworking): 재료 소모 → 전체 접사 수치 강화 (최대 12단계)",
                    "인챈트(Enchant): 접사 1개를 랜덤 리롤 (반복 시 비용 증가)",
                    "Aspect 각인: 코덱스(고정 최저값) or 추출 Aspect(드롭 롤 유지)를 장비에 부여",
                    "분해: 장비 → 크래프팅 재료 변환 (역방향 흐름)",
                    "강화 확률 요소: 템퍼링 시행 제한, 마스터워킹 4단계마다 랜덤 대폭 상승 대상",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "The Pit(구덩이): 무한 스케일링 던전, 마스터워킹 재료의 유일한 공급처",
                    "헬타이드(Helltide): 시간 제한 오픈월드 이벤트, 특수 상자에서 타겟 파밍",
                    "인페르날 호드: 대규모 웨이브 클리어, GA 장비 집중 드롭",
                    "월드 티어 4단계: WT3부터 Sacred, WT4부터 Ancestral 등급 해금",
                    "시즌 메카닉: 매 시즌 고유 파밍 시스템 추가 (감염체, 뱀파이어 능력 등)",
                    "거래 제한: Legendary 귀속, Unique 귀속 → 직접 파밍 강제",
                ]
            },
        ]
    },
    {
        "title": "Path of Exile",
        "subtitle": "커런시 크래프팅의 극한 — 가장 복잡한 파밍 생태계",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(1H/2H/완드/셉터 등), 방어구 6부위, 악세서리(반지2/목걸이/벨트)",
                    "등급: Normal → Magic → Rare → Unique (+ Influenced/Fractured/Synthesised)",
                    "베이스 타입이 극도로 중요: 아머/에바/ES 기반 + iLvl이 접사 티어 결정",
                    "접사: 접두 최대 3개 + 접미 최대 3개 = 총 6개 모드, 각 모드에 티어 존재",
                    "인플루언스: Elder/Shaper/Conqueror 등이 특수 접사 풀을 추가",
                    "좋은 장비 = 높은 iLvl + 맞는 베이스 + 고티어 접사 6개 조합",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "커런시(Currency): 40종+ — Chaos Orb, Exalted Orb, Divine Orb 등",
                    "맵(Map): 엔드게임 콘텐츠의 핵심, 맵 자체가 파밍 아이템",
                    "카드(Divination Card): 특정 지역 드롭, 일정 수 모으면 특정 아이템으로 교환",
                    "에센스(Essence): 몬스터에서 획득, 보장된 접사로 크래프팅",
                    "화석(Fossil): 딜브 전용, 특정 접사를 가중/배제하는 크래프팅 재료",
                    "스칼렛 오일/촉매/파편/스플린터 등 수십 종의 전문 재료",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "커런시 → 크래프팅: Chaos(접사 전체 리롤), Exalted(접사 추가), Annul(접사 제거)",
                    "커런시 → 거래 화폐: Chaos/Divine이 플레이어간 거래의 기준 화폐",
                    "맵 → 엔드게임 진행: Atlas Passive로 특화 파밍 전략 설계",
                    "카드 → 타겟 파밍: 특정 유니크/베이스를 노릴 수 있는 간접 수단",
                    "에센스/화석 → 결정론적 크래프팅: 원하는 접사를 높은 확률로 노림",
                    "다단계 사용: 커런시 크래프팅 → 실패 → 다시 파밍 → 재시도 (순환 루프)",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "커런시 크래프팅: Transmute→Augment→Regal→Exalt→Annul 단계별 정밀 작업",
                    "메타크래프팅: 접사 잠금(Prefix/Suffix Cannot Be Changed) 후 리롤",
                    "에센스 크래프팅: 1개 접사 보장 + 나머지 랜덤",
                    "화석 크래프팅: 특정 접사 태그 가중/배제 → 원하는 조합 확률 극대화",
                    "하베스트 크래프팅: 타겟 리롤(생명력 접사만 리롤 등), 가장 결정론적",
                    "벤치 크래프팅: 마스터 벤치에서 고정 접사 추가 (빈 접사 슬롯에)",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "Atlas Passive Tree: 맵 드롭/보스 출현/리그 메카닉을 플레이어가 커스텀",
                    "맵 모드/줌: 위험도↑ = 보상↑, IIQ/IIR로 드롭량·품질 조절",
                    "타겟 파밍: 카드(특정 지역), 보스(특정 유니크), 리그 메카닉(특정 커런시)",
                    "리그 메카닉: 매 시즌 신규 파밍 시스템 (딜브/하베스트/얼티메이텀 등)",
                    "SSF vs Trade: 트레이드 리그에서는 거래가 최대 효율, SSF는 자급자족",
                    "무제한 파밍 + 극도로 깊은 아이템 시스템 = 수백~수천 시간 분량",
                ]
            },
        ]
    },
    {
        "title": "MapleStory",
        "subtitle": "확률 강화의 대명사 — 주문서·큐브·스타포스 3축 시스템",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기, 보조무기, 엠블렘, 방어구 5부위, 악세서리(얼굴/눈/귀/반지/펜던트/벨트)",
                    "등급: 레어(파란) → 에픽(보라) → 유니크(노란) → 레전더리(초록)",
                    "장비 레벨(Req Level)이 기본 스탯 결정, 150렙+ 장비가 엔드게임",
                    "잠재능력(Potential): 큐브로 부여/변경, 등급별 옵션 풀이 다름",
                    "추가잠재능력(Bonus Potential): 에디셔널 큐브로 별도 관리",
                    "좋은 장비 = 높은 레벨 베이스 + 레전더리 잠재(보공%/총뎀) + 고성 스타포스",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "메소(Meso): 기본 재화, 강화·큐브·거래 모든 곳에 소모",
                    "큐브: 잠재능력 등급 상승/옵션 변경 (레드큐브/블랙큐브/에디셔널큐브)",
                    "주문서(Scroll): 장비에 고정 스탯 추가 (혼돈의 주문서, 놀라운 주문서 등)",
                    "스타포스 강화 재료: 메소 소모 (고성으로 갈수록 천문학적 비용)",
                    "불꽃(Flame/보너스 스탯): 추가 옵션을 리롤하는 환생의 불꽃",
                    "심볼(Arcane Symbol/Sacred Symbol): 아케인 리버 이후 스탯 증가 재료",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "큐브 → 잠재능력 변경: 보공%/총뎀%/크리티컬데미지% 등 핵심 옵션 노림",
                    "주문서 → 장비 기본 스탯 추가: 공격력/마력/올스탯 등을 영구 부여",
                    "스타포스 → 기본 스탯 추가 + 착용 조건 충족 (특정 사냥터 입장 조건)",
                    "메소 → 거래소 구매 + 강화 비용 (모든 행위의 기반 재화)",
                    "불꽃 → 추가옵션 리롤: 올스탯/공마 조합을 노림",
                    "심볼 → 아케인 포스/세이크리드 포스 상승: 사냥 효율에 직결",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "스타포스 강화: 0~25성, 15성 이상 실패 시 하락/파괴 가능 (순수 확률)",
                    "큐브 리롤: 레어→에픽→유니크→레전더리 등급 승급 + 옵션 리롤 (확률)",
                    "주문서 작: 성공/실패/파괴 확률 (이노센트 주문서로 초기화 가능)",
                    "에디셔널 잠재능력: 별도 큐브 계열로 관리, 본잠재+추가잠재 이중 구조",
                    "장비 트랜스퍼: 장비 간 스타포스 이전 (파괴 위험 경감 용도)",
                    "전체 과정이 확률 기반 — 기대값 계산이 핵심 (수십~수백억 메소 소요)",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "사냥 효율 = DPM × 이동속도 × 맵 구조 → '효율 사냥터'에서 장시간 반복",
                    "보스 결정석(Boss Crystal): 주간 보스 클리어 후 판매 = 주간 수입원",
                    "일일/주간 제한: 보스 입장 횟수, 심볼 퀘스트 등이 게이팅",
                    "메소 파밍 vs 아이템 파밍: 순수 메소 수급 → 큐브/강화 비용 충당이 주 루프",
                    "경매장(옥션): 플레이어 간 자유 거래, 메소가 기준 화폐",
                    "버닝/이벤트: 성장 가속 이벤트가 파밍 루프의 효율에 큰 영향",
                ]
            },
        ]
    },
    {
        "title": "Lost Ark",
        "subtitle": "호닝 기반 수직 성장과 레이드 중심 보상 구조",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기1, 방어구5(머리/어깨/상의/하의/장갑), 악세서리(목걸이/귀고리2/반지2)",
                    "등급: 일반 → 고급 → 희귀 → 영웅 → 전설 → 유물 → 고대 → 초월",
                    "장비 세트: 레이드별 고유 세트 효과 (발탄/비아키스/아브렐슈드 등)",
                    "악세서리: 특성(치명/특화/신속) + 각인(스킬 효과) 조합이 핵심",
                    "보석: 스킬별 데미지/쿨타임 보석을 장착하여 스킬 강화",
                    "좋은 장비 = 높은 호닝 단계 + 맞는 세트 + 고품질 악세 + 적합한 각인 조합",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "파괴석/수호석: 호닝의 기본 재료, 카오스 던전에서 대량 획득",
                    "돌파석(파괴석/수호석 결정): 호닝 확률 보정 재료",
                    "골드: 레이드 클리어 보상, 거래소 기준 화폐",
                    "보석: 1~10레벨, 3개 합성 → 1레벨 상승. 카오스 던전/보스에서 드롭",
                    "각인서: 전투/직업 각인을 배우는 아이템, 유물 각인서가 고가",
                    "카드: 카드 세트 효과로 추가 스탯 (특정 보스 추가 데미지 등)",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "파괴석/수호석 → 호닝: 장비 레벨 상승의 유일한 경로",
                    "골드 → 거래소 구매 + 호닝 비용 + 보석 구매 등 범용 재화",
                    "보석 → 스킬 강화: 데미지 보석/쿨타임 보석을 스킬에 장착",
                    "각인서 → 각인 활성화: 12포인트 이상 모아야 효과 발동 (5/10/15 단계)",
                    "카드 → 세트 효과: 특정 카드 조합으로 보스전 추가 데미지 등",
                    "에스더 무기 재료 → 최상위 무기 제작 (레이드 보스 드롭 + 제작)",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "호닝(Honing): 핵심 강화 — 재료+골드+확률, 실패 시 장인의 기운 누적",
                    "호닝 확률: 초반 100% → 고레벨로 갈수록 급격히 하락 (1~5%대)",
                    "보석 합성: 동레벨 보석 3개 → 상위 1개 (10레벨까지)",
                    "악세서리 각인: 돌 세공으로 어빌리티 스톤에 각인 부여 (확률 깎기)",
                    "품질 강화: 골드 소모로 장비 품질(0~100) 올리기 시도",
                    "엘릭서: 방어구에 추가 효과 부여 (듀얼 세트 효과 → 40레벨 필요)",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "일일/주간 게이팅: 카오스 던전(일2회), 가디언 토벌(일2회), 레이드(주1회)",
                    "레이드 중심: 군단장/어비스 레이드가 최대 보상 → 스케줄 파밍",
                    "골드 수급원이 제한적: 레이드 골드+거래소 판매가 주 수입",
                    "원정대 시스템: 다캐릭(6캐릭) 운영 → 재화 수급 극대화",
                    "거래소: 악세서리/보석/각인서 자유 거래, 골드 기준",
                    "수직 진행 중심: 아이템 레벨(GS)이 콘텐츠 입장 조건 → 호닝이 강제됨",
                ]
            },
        ]
    },
    {
        "title": "Monster Hunter: World / Rise",
        "subtitle": "소재 파밍 → 장비 제작의 순수 크래프팅 루프",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(14종 카테고리), 방어구 5부위(머리/몸/팔/허리/다리), 호석(장식주 슬롯)",
                    "등급 체계 없음 — 몬스터별 고유 장비 세트 존재 (리오레우스, 네르기간테 등)",
                    "무기 트리: 기본 무기 → 소재로 강화 → 분기별 최종 무기 (몬스터별 파생)",
                    "방어구 스킬: 각 부위에 고정 스킬 포인트 (공격+2, 회심강화+1 등)",
                    "장식주(Decoration): 슬롯에 삽입하여 추가 스킬 부여 (1~4슬롯 크기)",
                    "좋은 장비 = 원하는 스킬 조합을 맞출 수 있는 방어구 세트 + 적합한 무기 속성",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "몬스터 소재: 고유 부위 파괴/포획/토벌로 획득 (비늘/갈기/보석/역린 등)",
                    "광석/뼈: 필드 채집, 기본 무기/방어구 재료",
                    "장식주(Jewel): 고난이도 퀘스트/몰아치기에서 랜덤 드롭 (MHW 기준)",
                    "호석(Talisman): MH Rise — 랜덤 스킬+슬롯 조합, 연금술로 획득",
                    "천린의 용상석/대용상석: 최상위 제작 재료 (고난이도 전용)",
                    "MR(마스터랭크) 소재: 상위 버전 소재, 최종 장비 제작에 필수",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "소재 → 장비 제작: 대장간에서 직접 무기/방어구 제작 (결정론적)",
                    "소재 → 장비 강화: 무기 트리 진행, 방어구 레벨업",
                    "장식주 → 스킬 커스터마이징: 슬롯에 삽입하여 빌드 완성",
                    "호석 → 빌드 핵심: 좋은 호석 하나가 빌드 자유도를 극대화 (Rise)",
                    "소재 교환: 특정 NPC에서 잉여 소재를 다른 소재로 변환",
                    "거래 시스템 없음 → 모든 것을 직접 파밍해야 함",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "장비 제작: 소재 확보 → 대장간에서 제작 (100% 성공, 확률 요소 없음)",
                    "무기 강화: 무기 트리를 따라 단계별 강화, 분기점에서 선택",
                    "방어구 강화: 아머 스피어로 방어력 수치 상승 (단순 수치 강화)",
                    "커스텀 강화(MHW): 최종 무기에 추가 옵션 부여 (체력회복/회심/방어 등)",
                    "맞춤 강화(Rise): 최종 무기에 공격력/속성/회심 추가",
                    "확률 요소: 장식주 드롭과 호석 연금술만 랜덤 — 나머지 모두 결정론적",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "타겟 파밍 100%: 원하는 장비 = 해당 몬스터 반복 사냥 (명확한 목표)",
                    "부위 파괴 시스템: 꼬리 절단/머리 파괴 등으로 특정 소재 확률 상승",
                    "포획 vs 토벌: 포획 시 보상 테이블이 달라짐 (일부 소재는 토벌 전용)",
                    "조사 퀘스트(Investigation): 보상 슬롯에 금/은/동 → 희귀 소재 확률 상승",
                    "무제한 파밍: 같은 퀘스트 무한 반복 가능, 시간 제한 없음",
                    "멀티플레이 보너스: 파티 사냥 시 효율 상승 but 난이도도 스케일링",
                ]
            },
        ]
    },
    {
        "title": "Destiny 2",
        "subtitle": "퍽 랜덤롤과 마스터워크 — FPS와 RPG 파밍의 융합",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(키네틱/에너지/파워), 방어구 5부위(투구/건틀릿/흉갑/부츠/클래스)",
                    "등급: 커먼(흰) → 언커먼(녹) → 레어(파) → 레전더리(보라) → 엑조틱(금)",
                    "무기 랜덤롤: 같은 무기라도 퍽(Perk) 조합이 다름 → '갓롤' 추구",
                    "방어구 스탯: 이동성/회복력/탄력/훈련/지성/힘 6개 스탯 랜덤 분배",
                    "무기 퍽 구조: 배럴/매거진/특성1/특성2 각 슬롯에서 랜덤 선택",
                    "좋은 장비 = 원하는 퍽 2개 + 마스터워크 스탯 + 높은 총 스탯(방어구)",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "무기/방어구 자체: 랜덤롤 무기를 갓롤까지 파밍하는 것이 핵심",
                    "인핸스먼트 코어/프리즘: 마스터워크 및 장비 인퓨전 재료",
                    "어센던트 샤드: 최고급 강화 재료, 주간 획득 제한",
                    "모듈러 컴포넌트: 무기 모드 교체 비용",
                    "글리머(Glimmer): 기본 재화, 다양한 NPC 상호작용에 소모",
                    "엔그램(Engram): 드롭 아이템을 복호화하여 장비로 변환",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "무기 랜덤롤 → 직접 장착: 갓롤 무기를 얻으면 바로 사용",
                    "인핸스먼트 코어 → 마스터워크: 무기/방어구를 마스터워크로 강화",
                    "어센던트 샤드 → 엑조틱 업그레이드: 최상위 장비 인퓨전/마스터워크",
                    "모드(Mod) → 방어구 커스터마이징: 빌드에 맞는 모드 장착 (쿨타임·탄약 등)",
                    "인퓨전: 높은 파워 장비를 소모하여 기존 장비의 파워 레벨 상승",
                    "엑조틱 촉매(Catalyst): 엑조틱 무기에 추가 퍽/스탯 부여",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "마스터워크: 레전더리 무기/방어구의 스탯 강화 + 오브 생성 활성화",
                    "크래프팅(Lightfall~): 무기의 퍽 1~2개를 선택 가능하게 하는 시스템",
                    "인퓨전: 장비의 파워 레벨을 올리는 행위 (더 높은 장비를 재료로 소모)",
                    "모드 시스템: 방어구에 모드를 장착하여 빌드 세부 조정 (비파괴적, 자유 교체)",
                    "엑조틱 촉매: 특정 미션/킬 수 달성 → 촉매 완성 → 추가 효과 해금",
                    "분해: 불필요 장비 → 강화 재료 변환 (코어/프리즘 확률 획득)",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "주간 리셋: 레이드/던전/나이트폴 보상이 주 단위 초기화",
                    "타겟 파밍: 특정 활동 = 특정 무기 풀 (나이트폴 무기, 레이드 무기 등)",
                    "시즌 패스: 시즌별 신규 무기/모드/콘텐츠 → 파밍 대상 주기적 갱신",
                    "파워 레벨 캡: 시즌마다 상한 상승 → 인퓨전으로 따라가야 함",
                    "컬렉션 시스템: 모든 장비를 도감에 등록 → 수집 동기 부여",
                    "PvP(크루시블)·갬빗: PvE 외에도 파밍 경로 다변화",
                ]
            },
        ]
    },
    {
        "title": "Grim Dawn",
        "subtitle": "D2의 정신적 후계자 — 컨스텔레이션과 컴포넌트의 이중 레이어",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(1H/2H/방패/오프핸드), 방어구 6부위, 악세(반지2/목걸이/메달/벨트)",
                    "등급: Common → Magic(녹/노) → Rare(파) → Epic(보라) → Legendary(주황)",
                    "접사 시스템: Magic(접두+접미), Rare(접두+접미, 더 강력), Epic/Lego는 고정+접사",
                    "MI(Monster Infrequent): 특정 몬스터만 드롭하는 고유 베이스 아이템",
                    "세트 아이템: 2~5부위 세트 효과, 다수의 세트가 빌드 핵심",
                    "좋은 장비 = Legendary(빌드 핵심) + MI(좋은 접사) + 세트 효과 조합",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "컴포넌트(Component): 재료를 모아 완성, 장비에 부착하여 스탯/스킬 추가",
                    "증강(Augment): 팩션 명성으로 해금, 장비에 추가 저항/스탯 부여",
                    "렐릭(Relic): 설계도+재료로 제작, 전용 슬롯에 장착 (강력한 효과)",
                    "철/이더 크리스탈: 기본 크래프팅·분해 재료",
                    "설계도(Blueprint): 렐릭/컴포넌트 제작법, 드롭으로 해금",
                    "토템/열쇠: 특수 던전(로그라이크 던전, SR) 입장 재료",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "컴포넌트 → 장비 부착: 모든 장비에 1개씩 부착, 저항/스킬/스탯 추가",
                    "증강 → 장비 부착: 컴포넌트와 별도로 추가 부여 (팩션 상점 구매)",
                    "렐릭 → 전용 슬롯 장착: 강력한 패시브/스킬 부여 (빌드 핵심 아이템)",
                    "철/이더 → 크래프팅·분해: 장비 제작, 컴포넌트 완성에 소모",
                    "설계도 → 제작법 해금: 대장간에서 학습 후 영구 사용",
                    "발명가(Inventor NPC): 컴포넌트/증강 제거, 장비 분해",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "컴포넌트 조합: 부분 컴포넌트를 모아 완성품 제작 (결정론적)",
                    "렐릭 제작: 설계도 + 완성 컴포넌트 + 재료 → 렐릭 (확정 결과)",
                    "장비 제작: 대장간에서 일부 Legendary/Epic 직접 제작 가능 (설계도 필요)",
                    "분해: 장비 → 철/이더/컴포넌트 회수 (발명가 NPC)",
                    "컴포넌트/증강은 자유롭게 교체 가능 (비파괴적 시스템)",
                    "강화 확률 없음 — 크래프팅은 재료만 있으면 100% 성공",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "컨스텔레이션(Devotion): 봉헌 사당 → 별자리 포인트 → 빌드 핵심 패시브",
                    "MI 타겟 파밍: 특정 몬스터 반복 사냥 → 고유 MI + 좋은 접사 조합 노림",
                    "샤터드 렐름(SR): 무한 스케일링 로그라이크 던전, 높을수록 보상 증가",
                    "글래디에이터 크루서블: 웨이브 방어 모드, 축복으로 영구 보너스 획득",
                    "난이도 3단계: Normal → Elite → Ultimate, 동일 맵 재탐험",
                    "팩션 시스템: 팩션 명성 상승 → 상점 해금 → 증강/장비 구매 가능",
                ]
            },
        ]
    },
    {
        "title": "Last Epoch",
        "subtitle": "결정론적 크래프팅의 최전선 — 파밍과 제작의 균형",
        "sections": [
            {
                "heading": "1. 장비 구조",
                "bullets": [
                    "부위: 무기(1H/2H/오프핸드), 방어구 5부위, 악세(반지2/목걸이/벨트), 렐릭/아이돌",
                    "등급: Normal → Magic → Rare → Exalted → Unique → Legendary",
                    "접사: 접두 최대 2개 + 접미 최대 2개 = 4개, 각 접사에 티어(1~7) 존재",
                    "Exalted: T6~7 접사를 가진 특수 아이템 (크래프팅 베이스로 핵심)",
                    "Legendary: Unique + Exalted를 결합한 최상위 등급 (던전 보스 전용)",
                    "좋은 장비 = Exalted 베이스 + 고티어 접사 4개 + Legendary Potential(LP)",
                ]
            },
            {
                "heading": "2. 파밍 아이템 종류",
                "bullets": [
                    "글리프(Glyph): 크래프팅 시 사용, 특수 효과 부여 (안정화/보호/희망 등)",
                    "룬(Rune): 크래프팅 행위를 결정하는 아이템 (제거/정화/형상변환 등)",
                    "아이돌(Idol): 전용 슬롯에 장착, 다양한 크기·옵션 (1×1~2×2)",
                    "열쇠(Key): 던전 입장 재료 (시간의 균열, 영혼의 불꽃 등)",
                    "샤드(Shard): 접사의 파편, 장비 분해로 획득 → 크래프팅 재료",
                    "Exalted/Unique 장비 자체가 핵심 파밍 대상",
                ]
            },
            {
                "heading": "3. 파밍 아이템 사용처",
                "bullets": [
                    "룬+글리프 → 크래프팅: 접사 추가/제거/변경/업그레이드의 소모 재료",
                    "샤드 → 접사 부여: 원하는 접사를 직접 선택하여 장비에 추가",
                    "아이돌 → 전용 슬롯 장착: 빌드 특화 보너스 (스킬 강화, 방어 등)",
                    "열쇠 → 던전 입장: 각 던전별 고유 보상 (Legendary 제작, 엑살티드 획득 등)",
                    "Legendary Potential: Unique의 LP 수치만큼 Exalted 접사를 계승",
                    "모든 크래프팅 재료가 직접적으로 캐릭터 성장에 연결",
                ]
            },
            {
                "heading": "4. 강화·조합·크래프팅",
                "bullets": [
                    "접사 추가: 룬 오브 디스커버리 + 원하는 샤드 → 빈 슬롯에 직접 추가",
                    "접사 업그레이드: 기존 접사 티어를 1단계 올림 (T1→T2→...→T5까지 안전)",
                    "단조 잠재력(Forging Potential): 장비별 크래프팅 횟수, 소진 시 수정 불가",
                    "글리프 오브 호프: 엑살티드 접사를 보호하며 크래프팅",
                    "Legendary 제작: 시간의 균열에서 Unique(LP) + Exalted → Legendary 합성",
                    "결정론적 설계: 원하는 접사를 직접 선택, 확률은 티어 상승과 FP에만 존재",
                ]
            },
            {
                "heading": "5. 기타 파밍 구조",
                "bullets": [
                    "모노리스(Monolith): 엔드게임 맵 시스템, 타임라인별 고유 보스/보상",
                    "던전 3종: 각각 고유 보상 (Legendary 제작/접사 밀봉/유니크 변환)",
                    "아레나: 무한 웨이브, 깊은 웨이브일수록 드롭 증가",
                    "아이템 필터: 내장 필터 시스템으로 원하는 접사/베이스만 표시",
                    "드롭률 가중: 모노리스 타임라인별 특정 아이템 유형 편향",
                    "Cycle(시즌): 주기적 리셋, 시즌 메카닉으로 파밍 구조 변화",
                ]
            },
        ]
    },
]


def draw_page(c, game, page_num, total_pages):
    """한 게임의 분석 내용을 1페이지에 그린다."""
    y = HEIGHT - MARGIN_TOP

    # 상단 바
    c.setFillColor(COLOR_TITLE)
    c.rect(MARGIN_LEFT - 5, y - 2, CONTENT_WIDTH + 10, 3, fill=1, stroke=0)

    # 게임 타이틀
    y -= 22
    c.setFont("MalgunBold", 16)
    c.setFillColor(COLOR_TITLE)
    c.drawString(MARGIN_LEFT, y, game["title"])

    # 서브타이틀
    y -= 16
    c.setFont("Malgun", 9)
    c.setFillColor(COLOR_LIGHT)
    c.drawString(MARGIN_LEFT, y, game["subtitle"])

    y -= 10

    # 5개 섹션
    for section in game["sections"]:
        # 구분선
        y -= 6
        c.setStrokeColor(COLOR_DIVIDER)
        c.setLineWidth(0.5)
        c.line(MARGIN_LEFT, y, WIDTH - MARGIN_RIGHT, y)
        y -= 12

        # 섹션 제목
        c.setFont("MalgunBold", 9.5)
        c.setFillColor(COLOR_ACCENT)
        c.drawString(MARGIN_LEFT, y, section["heading"])
        y -= 4

        # 불릿 포인트
        c.setFont("Malgun", 7.2)
        c.setFillColor(COLOR_TEXT)
        for bullet in section["bullets"]:
            y -= 11
            # 불릿 기호
            c.drawString(MARGIN_LEFT + 4, y, "\u2022")
            # 텍스트 (긴 텍스트는 줄바꿈)
            text = bullet
            max_width = CONTENT_WIDTH - 14
            text_obj = c.beginText(MARGIN_LEFT + 12, y)
            text_obj.setFont("Malgun", 7.2)

            # 한 줄에 들어갈 수 있는지 체크하며 줄바꿈
            line = ""
            for char in text:
                test_line = line + char
                if c.stringWidth(test_line, "Malgun", 7.2) > max_width:
                    text_obj.textLine(line)
                    line = char
                    y -= 10
                else:
                    line = test_line
            if line:
                text_obj.textLine(line)
            c.drawText(text_obj)

    # 페이지 번호
    c.setFont("Malgun", 7)
    c.setFillColor(COLOR_LIGHT)
    page_label = f"-- {page_num} / {total_pages} --"
    c.drawCentredString(WIDTH / 2, MARGIN_BOTTOM - 5, page_label)

    # 하단 바
    c.setFillColor(COLOR_TITLE)
    c.rect(MARGIN_LEFT - 5, MARGIN_BOTTOM + 2, CONTENT_WIDTH + 10, 1.5, fill=1, stroke=0)


def draw_cover(c):
    """표지 페이지."""
    # 배경 상단 블록
    c.setFillColor(COLOR_TITLE)
    c.rect(0, HEIGHT - 250, WIDTH, 250, fill=1, stroke=0)

    # 제목
    c.setFont("MalgunBold", 28)
    c.setFillColor(HexColor("#ffffff"))
    c.drawCentredString(WIDTH / 2, HEIGHT - 120, "RPG 아이템 & 파밍 구조 분석")

    # 부제
    c.setFont("Malgun", 14)
    c.setFillColor(HexColor("#aaaacc"))
    c.drawCentredString(WIDTH / 2, HEIGHT - 155, "10개 유명 RPG 게임의 아이템 / 파밍 시스템 비교 분석")

    # 분석 관점
    y = HEIGHT - 310
    c.setFont("MalgunBold", 12)
    c.setFillColor(COLOR_SECTION)
    c.drawCentredString(WIDTH / 2, y, "분석 5대 관점")

    perspectives = [
        "1. 장비 구조 -- 베이스 아이템, 등급 체계, 접사 시스템",
        "2. 파밍 아이템 종류 -- 몬스터를 잡는 이유가 되는 수집 아이템",
        "3. 파밍 아이템 사용처 -- 캐릭터 성장과의 연결 경로",
        "4. 강화 / 조합 / 크래프팅 -- 장비를 개선하는 모든 시스템",
        "5. 기타 파밍 구조 -- 파밍을 지속하게 만드는 구조적 설계",
    ]

    c.setFont("Malgun", 10)
    c.setFillColor(COLOR_TEXT)
    for i, p in enumerate(perspectives):
        y -= 28
        c.drawCentredString(WIDTH / 2, y, p)

    # 게임 목록
    y -= 60
    c.setFont("MalgunBold", 11)
    c.setFillColor(COLOR_SECTION)
    c.drawCentredString(WIDTH / 2, y, "분석 대상 게임")

    games_list = [
        "Diablo 2  |  Diablo 3  |  Diablo 4  |  Path of Exile  |  MapleStory",
        "Lost Ark  |  Monster Hunter  |  Destiny 2  |  Grim Dawn  |  Last Epoch",
    ]

    c.setFont("Malgun", 9.5)
    c.setFillColor(COLOR_TEXT)
    for line in games_list:
        y -= 22
        c.drawCentredString(WIDTH / 2, y, line)

    # 하단 정보
    c.setFont("Malgun", 8)
    c.setFillColor(COLOR_LIGHT)
    c.drawCentredString(WIDTH / 2, MARGIN_BOTTOM + 30, "TheSevenRPG 기획 참고 자료")
    c.drawCentredString(WIDTH / 2, MARGIN_BOTTOM + 16, "2026.03")


def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "RPG_Item_Farming_Analysis.pdf")

    pdf = canvas.Canvas(output_path, pagesize=A4)
    pdf.setTitle("RPG Item & Farming Analysis")
    pdf.setAuthor("TheSevenRPG")

    # 표지
    draw_cover(pdf)
    pdf.showPage()

    # 게임별 페이지
    total = len(GAMES)
    for i, game in enumerate(GAMES):
        draw_page(pdf, game, i + 1, total)
        if i < total - 1:
            pdf.showPage()

    pdf.save()
    print(f"PDF 생성 완료: {output_path}")


if __name__ == "__main__":
    main()
