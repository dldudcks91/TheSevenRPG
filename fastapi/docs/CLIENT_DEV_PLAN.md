# TheSevenRPG — 클라이언트 개발 계획서

> 최초 작성: 2026-03-13
> 최종 업데이트: 2026-04-21 (Phase C17 — Idle 횡스크롤 전투 개편 Iter 1~3 완료)
> 화면 기획서: `fastapi/docs/game_design/SCREEN_DESIGN.md`
> 기준 서버 계획서: `fastapi/docs/SERVER_DEV_PLAN.md`
> 개발 가이드: `.claude/skills/web-client/skill.md`

---

## 현황 요약

### Phase C1~C7 (구 버전): ✅ 전체 완성 → ⚠️ 구조 개편 예정

기존 구현은 **화면별 분리 구조** (Login/Town/Inventory/StageSelect/Battle/Cards 각각 독립 Screen).
새 기획은 **좌우 분할 2화면 구조** (Login + Main)로 전면 개편.

**기존 코드 중 재활용 가능한 것:**
| 파일 | 재활용 | 비고 |
|------|--------|------|
| `api.js` | ✅ 그대로 | apiCall, 세션 인증, 재시도 |
| `store.js` | ✅ 그대로 | pub/sub 상태 관리 |
| `session.js` | ✅ 그대로 | localStorage 세션 |
| `utils.js` | ✅ 그대로 | DOM 헬퍼, 포맷터 |
| `meta-data.js` | ✅ 그대로 | 메타데이터 로드/룩업 |
| `variables.css` | ✅ 그대로 | CSS 변수 |
| `screens/login.js` | ✅ 거의 그대로 | 로그인 화면 |
| `login.css` | ✅ 거의 그대로 | 로그인 스타일 |
| `screens/battle.js` | ⚠️ 부분 재활용 | Phaser BattleScene 로직은 유지, 외부 래퍼 변경 |
| `app.js` | ❌ 재작성 | 해시 라우터 → 2화면 전환으로 변경 |
| `common.css` | ⚠️ 수정 | 좌우 분할 레이아웃 추가 |
| `screens/town.js` | ❌ 재작성 | 마을 뷰 → 우측 메인뷰 컴포넌트로 변경 |
| `screens/inventory.js` | ❌ 재작성 | 전체 화면 → 좌측 장비 탭으로 변경 |
| `screens/stage-select.js` | ❌ 재작성 | 전체 화면 → 우측 마을 모드에 통합 |
| `screens/cards.js` | ❌ 재작성 | 전체 화면 → 좌측 스킬/도감 탭으로 분리 |
| `town.css` 외 컴포넌트 CSS | ❌ 재작성 | 레이아웃 전면 변경 |

**삭제된 코드:**
- `screens/idle-farm.js` — 삭제 완료
- `css/components/idle-farm.css` — 삭제 완료

### 서버 API 현황

| api_code | 설명 | 상태 |
|----------|------|------|
| 1002 | 게임 데이터 로드 | ✅ |
| 1003 | 회원가입/로그인 | ✅ |
| 1004 | 유저 정보 조회 | ✅ |
| 1005 | 스탯 리셋 | ✅ |
| 2001 | 장비 장착 | ✅ |
| 2002 | 장비 해제 | ✅ |
| 2003 | 인벤토리 조회 | ✅ |
| 2004 | 아이템 판매 | ✅ |
| 2005 | 인벤토리 확장 | ✅ |
| 2007 | 도감 목록 조회 | ✅ |
| 2008 | 스킬 장착 | ✅ |
| 2009 | 스킬 해제 | ✅ |
| 3001 | 전투 시뮬레이션 | ✅ |
| 3002 | 몬스터 킬 & 드롭 | ✅ |
| 3003 | 스테이지 입장 | ✅ |
| 3004 | 스테이지 클리어 | ✅ |

### 그래픽 리소스 현황

| 리소스 | 상태 |
|--------|------|
| 챕터 배경 이미지 7종 | ✅ 보유 |
| 1챕터 스테이지 배경 3종 | ✅ 보유 |
| 캐릭터/몬스터 스프라이트 | 미작업 |
| 전투 이펙트 | 미작업 |
| NPC/시설 아트 | 미작업 |
| 사운드/BGM | 미기획 |

---

## 기술 스택

| 영역 | 기술 | 용도 |
|------|------|------|
| 전투 연출 | Phaser.js (CDN) | 스프라이트 애니메이션, battle_log 재생 |
| UI | HTML/CSS | 좌측 패널 탭, 우측 메인뷰, 팝업 |
| 통신 | fetch API | `POST /api` 단일 게이트웨이, 세션 헤더 |
| PWA | manifest + SW | 오프라인 캐시 (향후) |

---

## 새 디렉토리 구조

```
fastapi/public/
├── index.html                    # SPA 엔트리 (2화면: Login + Main)
├── css/
│   ├── variables.css             # CSS 변수 (재활용)
│   ├── common.css                # 공통 + 좌우 분할 레이아웃
│   └── components/
│       ├── login.css             # Login 화면 (재활용)
│       ├── top-bar.css           # 상단 바
│       ├── left-panel.css        # 좌측 패널 공통 (탭 바, 스크롤)
│       ├── tab-stat.css          # 스탯 탭
│       ├── tab-equip.css         # 장비 탭
│       ├── tab-item.css          # 아이템 탭
│       ├── tab-skill.css         # 스킬 탭
│       ├── tab-collection.css    # 도감 탭
│       ├── popup.css             # 비교 팝업 / 단독 팝업 공통
│       ├── town-view.css         # 우측 마을 모드
│       └── battle-view.css       # 우측 전투 모드
├── js/
│   ├── app.js                    # 앱 초기화 (2화면 전환: Login ↔ Main)
│   ├── api.js                    # 서버 통신 (재활용)
│   ├── session.js                # 세션 관리 (재활용)
│   ├── store.js                  # 상태 관리 (재활용)
│   ├── utils.js                  # DOM 헬퍼 (재활용)
│   ├── meta-data.js              # 메타데이터 (재활용)
│   ├── popup.js                  # 팝업 매니저 (호버/클릭/닫기 공통)
│   ├── screens/
│   │   └── login.js              # Login 화면 (재활용)
│   ├── main/
│   │   ├── top-bar.js            # 상단 바 컴포넌트
│   │   ├── left-panel.js         # 좌측 패널 (탭 전환 관리)
│   │   ├── tabs/
│   │   │   ├── stat.js           # 스탯 탭
│   │   │   ├── equip.js          # 장비 탭
│   │   │   ├── item.js           # 아이템 탭
│   │   │   ├── skill.js          # 스킬 탭
│   │   │   └── collection.js     # 도감 탭
│   │   └── views/
│   │       ├── town-view.js      # 우측 마을 모드
│   │       └── battle-view.js    # 우측 전투 모드 (Phaser 포함)
│   └── main.js                   # Main 화면 조립 (상단바 + 좌측 + 우측)
├── manifest.json
└── sw.js
```

---

## 개발 Phase (새 구조)

### Phase C8 — 레이아웃 기반 재구축
**목적**: 좌우 분할 레이아웃 골격 완성. 2화면(Login/Main) 전환.
**상태**: [x] 완료

**작업 내용**
- `app.js` 재작성: 해시 라우터 제거, Login ↔ Main 2화면 전환
- `main.js` 신규: Main 화면 조립 (상단바 + 좌측 패널 + 우측 뷰)
- `common.css` 수정: 좌우 분할 레이아웃 (좌측 350px 고정 + 우측 flex)
- `top-bar.js/css` 신규: 상단 바 (닉네임/레벨/스탯칩/EXP바/골드/로그아웃)
- `left-panel.js/css` 신규: 5탭 바 + 탭 내용 컨테이너 (빈 상태)
- `login.js` 수정: `#town` 이동 → Main 화면 전환으로 변경

**완료 기준**
- 로그인 → Main 전환 동작
- 상단 바에 유저 정보 표시 (API 1004)
- 좌측 5탭 클릭 시 활성 탭 전환 (내용은 빈 상태)
- 우측 영역 빈 상태로 표시

---

### Phase C9 — 좌측 스탯 탭
**목적**: 스탯 배분 + 전투 스탯 + 세트 보너스 상세.
**상태**: [x] 완료

**작업 내용**
- `tabs/stat.js` + `tab-stat.css` 신규
- 캐릭터 정보 (레벨/경험치/골드)
- 스탯 배분 UI: 5종 스탯 + [+] 버튼 (SP 차감)
- 전투 스탯: 장비 반영된 최종 수치
- 세트 보너스: 죄종별 포인트 바 + 브레이크포인트 효과 (활성=초록/미활성=회색)
- [스탯 리셋] 버튼 → 확인 팝업 → API 1005

**연동 API**: `1004`, `1005`

---

### Phase C10 — 좌측 장비 탭
**목적**: 장착 슬롯 + 아이콘 그리드 + 비교 팝업.
**상태**: [x] 완료

**작업 내용**
- `tabs/equip.js` + `tab-equip.css` 신규
- `popup.js` + `popup.css` 신규 (공통 팝업 매니저)
- 장착 슬롯 5개 (일자, 등급 보더)
- 코스트 바 (현재/최대)
- 세트 포인트 요약 한 줄
- 필터 탭 (전체/무기/방어구)
- 미장착 장비 정사각형 아이콘 그리드 (부위 아이콘 + 등급 보더 + 레벨)
- 비교 팝업: 미장착 호버 → 착용중 vs 미착용 나란히, 수치 상승=초록/하락=빨강
- 단독 팝업: 장착 슬롯 클릭 → 착용 장비 상세 + [해제][판매]
- 인벤토리 카운트 + [인벤 확장]

**연동 API**: `2001`~`2005`

---

### Phase C11 — 좌측 스킬 탭
**목적**: 스킬 슬롯 장착/해제. 장비 탭과 동일한 UI 패턴.
**상태**: [x] 완료

**작업 내용**
- `tabs/skill.js` + `tab-skill.css` 신규
- 장착 스킬 슬롯 4개 (일자, 해금/잠김/빈)
- 미장착 스킬 아이콘 그리드 (⚡ + 약어)
- 비교 팝업: 미장착 호버 → 장착중 vs 미장착 나란히
- 단독 팝업: 슬롯 클릭 → 장착 스킬 상세 + [해제]
- 잠김 슬롯 클릭 → "Lv.N에 해금됩니다" 토스트

**연동 API**: `2007`, `2008`, `2009`

---

### Phase C12 — 좌측 도감 탭
**목적**: 카드 수집 현황 열람 (순수 열람). 도감 그룹/패시브 확인.
**상태**: [x] 완료

**작업 내용**
- `tabs/collection.js` + `tab-collection.css` 신규
- 챕터 필터 탭
- 도감 그룹 (스테이지별 노말3+보스1)
  - 합산 Lv, 패시브 단계 표시
- 카드 아이콘: 몬스터명, 도감 Lv, 카드수/필요수, 미수집=??
- 카드 클릭 팝업: 도감 레벨, Lv별 스킬/보너스
- 그룹 패시브 클릭 팝업: 단계별 효과, 활성/미달성

**연동 API**: `2007`

---

### Phase C13 — 우측 마을 모드
**목적**: 마을 허브. 배경 이미지 위 투명 핫스팟으로 NPC/출정문 배치.
**상태**: [x] 완료

**작업 내용**
- `views/town-view.js` + `town-view.css` 재작성
- 마을 배경 이미지 (`background_town.png`) 전체 채움 (우하단 20px 여백)
- NPC 투명 핫스팟: 호버 시 테두리 발광 + 라벨 표시, 미해금 시 잠김 처리
- 출정문 클릭 → 마을 배경 위 스테이지 선택 팝업 오버레이 표시
- 팝업 내 챕터 탭 + 스테이지 리스트 + [입장] → 전투 모드 전환
- `views/stage-select-view.js` 생성 (현재 미사용, 팝업으로 대체)

**연동 API**: `3003`

---

### Phase C14 — 우측 전투 모드
**목적**: Phaser 전투 연출. 서버 battle_log 재생. 스테이지별 배경 + 캐릭터/몬스터 이미지.
**상태**: [x] 완료 (2026-03-19: Wave indicator UI 구현 완료)

**작업 내용**
- `views/battle-view.js` + `battle-view.css` 신규
- 기존 `battle.js`의 Phaser BattleScene 로직 이식
- 스테이지별 배경 이미지 (`background_stage_{stageId}.png`)
- 캐릭터/몬스터 이미지 스프라이트 (`character.png`, `monster_{monsterIdx}.png`)
- 이미지 없으면 사각형 폴백
- 상단: 스테이지명 + Wave 진행 (**4개 점 + 연결선 인디케이터 추가**)
- HUD: Player/Monster HP 바
- Phaser 아레나: 공격 모션, 데미지/미스/크리티컬 팝업
- 전투 로그: 하단 200px 고정
- 결과 오버레이: 승패 + EXP/골드/레벨업
- [재도전] / [마을로] 버튼
- 전투 중 좌측 패널 유지 (장비 변경은 서버 차단)

**연동 API**: `3001`, `3004`

**최근 업데이트**
- Wave indicator: 비활성=회색, 활성=노란색 글로우 효과
- CSS: `.bv-wave-indicator` (flex), `.bv-wave-dot` (12px 원형), `.bv-wave-line` (연결선)
- JS: `_createWaveIndicator(waveCount)`, `_updateWaveIndicator(currentWaveIndex)` 메서드 추가

---

### Phase C15 — 아이템 탭 (Phase 18 이후)
**목적**: 스택형 아이템(포션/광석/낙인/퀘재) 관리.
**상태**: [x] 스켈레톤 완료 ("준비 중" 표시) — 본격 구현은 서버 Phase 18 이후

**작업 내용**
- `tabs/item.js` + `tab-item.css` 신규
- 카테고리 필터 (포션/광석/낙인/퀘재)
- 정사각형 아이콘 그리드 (아이템 아이콘 + 수량 뱃지)
- 호버/클릭 팝업 (이름, 효과, 보유 수량, [사용])
- Phase 18 전까지 "준비 중" 표시

---

### Phase C15.5 — 스토리 씬 & LPC 스프라이트 (2026-03-20)
**목적**: 게임 시작 시퀀스 완성 + LPC 캐릭터 스프라이트 시스템 도입.
**상태**: [x] 완료

**씬 흐름 변경**
```
Prologue → Walking Scene → Tutorial Battle → Main
```

**LPC 스프라이트 에셋**
- Universal LPC Spritesheet 전체 에셋 도입 (288,141 파일, ~303MB)
- `fastapi/public/img/lpc/assets/` — .gitignore 등록 (git 제외)
- 64x64 프레임 기반, 레이어 합성 방식 (body + head + hair + legs + cape + boots)
- `lpc-preview.html` — 기존 프리뷰 도구 (프리셋별 합성 & 애니메이션 확인)

**Walking Scene (신규)**
- `scenes/walking.js` + `components/walking.css`
- LPC 레이어 합성 → 캔버스 애니메이션 (walk north, 8FPS)
- 바알 캐릭터: body/head/hair(bangslong)/pants/boots/cape(maroon)
- 어둠 배경 + 붉은 불씨 파티클 + 4단계 텍스트 연출
- 13초 자동 진행 or 클릭 스킵

**프롤로그 개선**
- 붉은 불씨 파티클 이펙트 추가 (`.prologue-particles`)
- SKIP 버튼 추가 (우상단, 프롤로그 전체 스킵)

**Top Bar — 씬 다시보기**
- ▶ 버튼 추가 (설정 버튼 좌측)
- 모달에서 프롤로그 / 걸어가는 씬 선택
- push/pop 방식 — 씬 종료 후 메인 화면 자동 복귀
- `replay: true` 데이터 전달로 정상 흐름과 구분

**i18n**
- `story-ko.js`에 `walking_texts`, `walking_skip` 추가

**연동 API**: `(미정)`, `2011`

---

### Phase C17 — Idle 횡스크롤 전투 개편 (2026-04-21)
**목적**: 정적 대치 전투를 "오른쪽에서 몬스터 스폰 → 캐릭터가 걸어가며 조우 → 평타 교환" 형태의 idle 오토배틀로 전환.
**상태**: [x] Iter 1~3 완료 / [ ] Iter 4(속도·일시정지 UI) 미착수

**핵심 원칙**
- 서버 API(3001/3003/3004), BattleManager, StageManager 등 서버 로직은 **완전 불변**. 클라이언트만 수정.
- 전투 공식·결과·드롭은 서버 `battle_log`를 그대로 재생. 이동/조우 좌표는 순수 시각 좌표.
- 웨이브 구조([일반3+정예1]×3 + 보스) 유지. 한 웨이브 안에서 몬스터가 순차 스폰.

**신규 파일**
| 경로 | 역할 |
|------|------|
| `js/sprites/lpc-manifest.js` | 캐릭터 레이어/애니 스펙, 몬스터 매니페스트, 스폰 사이즈 배수 |
| `js/sprites/lpc-sprite.js` | LPC 레이어 합성(`composeLpcSheet`) + Phaser 스프라이트 래퍼 |
| `js/sprites/static-sprite.js` | PNG 기반 `StaticSprite` + `RectSprite` (LpcSprite와 동일 시그니처) |
| `js/main/views/idle-battle-scene.js` | Phaser Scene. `playMob(data, monsterIdx, spawnType)` 4페이즈 FSM |
| `js/main/views/pace-ctrl.js` | 속도/일시정지 래퍼 skeleton (Iter 4에서 UI 연결) |

**수정 파일**
- `js/main/views/battle-view.js` — 내부 `BattlePhaserScene` 제거 → `IdleBattleScene` 위임. 플로팅 로그, 웨이브 배너 추가
- `css/components/battle-view.css` — `.bv-arena` → `.bv-stage`. 배경 가로 스크롤(`bvBgScroll`), 플로팅 로그, 웨이브 배너
- `js/scenes/walking.js` — `composeLpcSheet` 공용 모듈 사용으로 리팩토링 (시각 동일)

**Iter 별 상세**
| Iter | 범위 | 상태 |
|------|------|------|
| 1 | 스켈레톤 + PNG 폴백. 횡스크롤·조우·평타 교환·사망 FSM 동작 | [x] |
| 2 | LPC 공용 모듈 도입. 플레이어를 LpcSprite로 전환. walking.js 회귀 | [x] |
| 3 | `MONSTER_MANIFEST` 구조 확정, 몬스터 3단 폴백, 스폰 크기 배수, 플로팅 로그, 웨이브 배너 | [x] |
| 4 | 속도 1x/2x/3x + 일시정지 UI, IR 문서 세부 sync | [ ] |

**LPC 에셋 현황**
- `fastapi/tools/lpc_download.py`가 body/head/legs (male/female) + 무기/방패 다운로드
- `lpc-manifest.js`의 `CHARACTER_LAYERS`는 body/head/legs 3파츠만 사용. cape/eyes/hair/feet은 다운로드 스크립트 확장 후 추가 예정.
- `MONSTER_MANIFEST`는 비어있음. 엔트리를 채우면 해당 몬스터가 LPC로 렌더됨.

**관련 IR 문서**
- `fastapi/docs/ir/battle.md` "재생 방식 (클라, idle 횡스크롤)" 섹션 참조.

**연동 API (불변)**: `3001`, `3003`, `3004`

---

### Phase C16 — 통합 테스트 & 폴리싱
**목적**: 전체 흐름 검증 + UI 다듬기.
**상태**: [ ] 미착수 (2026-03-19: 버그 발견 — "이미 진행중인 전투" 메시지)

**작업 내용**
- 로그인 → Main → 스탯배분 → 장비장착 → 스테이지입장 → 전투 → 결과 전체 흐름
- 좌측 탭 전환 시 데이터 유지/갱신 확인
- 전투 중 좌측 패널 확인 전용 동작 검증
- 팝업 호버/클릭/닫기 엣지 케이스
- SW 프리캐시 목록 업데이트
- 메모리 릭 점검 (Phaser 생성/파괴 반복)

**발견된 버그**
- 클라이언트 "이미 진행중인 전투가 있다는데" 메시지 → Store 상태 미초기화 추정
- 서버 로그는 정상, 클라이언트 battle.stage_id 상태 잔존 가능성
- C16 통합테스트 시 Store 초기화 로직 검증 필요

---

## 개발 순서

```
=== Phase C1~C7 (구 버전 — 완료, 개편 대상) ===

=== Phase C8~ (새 구조 — 좌우 분할 5탭) ===
Phase C8  (레이아웃 기반)     [x] 2화면 전환, 좌우 분할 골격
    ↓
Phase C9  (스탯 탭)          [x] 스탯 배분 + 전투스탯 + 세트보너스
    ↓
Phase C10 (장비 탭)          [x] 아이콘 그리드 + 비교 팝업  ★핵심
    ↓
Phase C11 (스킬 탭)          [x] 장비 탭과 동일 패턴
    ↓
Phase C12 (도감 탭)          [x] 열람 전용, 그룹 패시브
    ↓
Phase C13 (마을 모드)        [x] 스테이지 선택 + NPC 영역
    ↓
Phase C14 (전투 모드)        [x] Phaser 이식 + 결과 오버레이
    ↓
Phase C15 (아이템 탭)        [x] 스켈레톤 (서버 Phase 18 이후 본격)
    ↓
Phase C15.5 (스토리 씬)      [x] Walking Scene + 프롤로그 개선 + 씬 다시보기
    ↓
Phase C17 (idle 횡스크롤 전투) [x] Iter 1~3 / [ ] Iter 4 속도·일시정지
    ↓
Phase C16 (통합/폴리싱)      [ ] 전체 흐름 검증
```

---

## 서버-클라이언트 Phase 의존 관계

```
서버 Phase 1~12 (완성) ──┬──→ 클라 C8  (레이아웃)    ← API 1004
                         ├──→ 클라 C9  (스탯 탭)     ← API 1004, 1005
                         ├──→ 클라 C10 (장비 탭)     ← API 2001~2005
                         ├──→ 클라 C11 (스킬 탭)     ← API 2007~2009
                         ├──→ 클라 C12 (도감 탭)     ← API 2007
                         ├──→ 클라 C13 (마을 모드)   ← API 3003
                         └──→ 클라 C14 (전투 모드)   ← API 3001, 3004

서버 Phase 18 (재료) ────→ 클라 C15 (아이템 탭)   ← API (미정), 2011
```

---

*마지막 업데이트: 2026-04-21*
