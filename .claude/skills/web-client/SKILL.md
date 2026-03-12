---
name: web-client
description: "웹 RPG 클라이언트 개발 가이드. Phaser.js 전투 애니메이션 + HTML/CSS UI. 서버 시뮬레이션 결과를 클라이언트에서 재생하는 뷰어 패턴. 모바일 확장 대비 설계."
---

# Web Client 개발 가이드

## 아키텍처 원칙

### 클라이언트 = 뷰어
- 전투 로직은 서버에서 시뮬레이션, 결과를 `battle_log[]`로 반환
- 클라이언트는 battle_log를 순서대로 재생 (애니메이션/연출)
- 클라이언트에 게임 로직 없음 → 치팅 원천 차단

### 기술 분담
| 영역 | 기술 | 용도 |
|------|------|------|
| 전투 화면 | Phaser.js | 스프라이트 애니메이션, 이펙트, 전투 연출 |
| UI | HTML/CSS | 인벤토리, 스탯, 메뉴, 대화창 |
| 통신 | fetch API | `POST /api`로 서버 요청 |

## Phaser.js 전투 연출

### 씬 구조
```
BootScene       → 에셋 프리로드
BattleScene     → 전투 연출 (battle_log 재생)
ResultScene     → 전투 결과/보상 표시
```

### battle_log 재생 패턴
```javascript
// 서버에서 받은 battle_log를 타이머로 순차 재생
playBattleLog(log) {
    let index = 0;
    this.time.addEvent({
        delay: 600,
        repeat: log.length - 1,
        callback: () => {
            const action = log[index++];
            this.executeAction(action);
        }
    });
}
```

### 에셋 관리
- 스프라이트시트: 캐릭터/몬스터 애니메이션
- KTX2 + Basis Universal 압축 (용량 60~75% 절감)
- 레이지 로딩: 현재 챕터 에셋만 로드, 다음 챕터는 백그라운드 프리로드
- 오브젝트 풀링: 데미지 텍스트, 이펙트 파티클 재사용

## HTML/CSS UI 규칙

### 레이아웃
- 모바일 퍼스트 (portrait 기준 설계)
- 터치 타겟: 최소 44px × 44px
- `pointer` 이벤트 사용 (`click` 대신 `pointerdown`)
- 반응형: CSS Grid/Flexbox, 고정 px 금지

### UI 컴포넌트
```
inventory-panel     인벤토리 그리드
stat-panel          캐릭터 스탯
stage-select        스테이지 선택 화면
dialog-box          NPC 대화창
result-modal        전투 결과 모달
```

### CSS 변수로 테마 관리
```css
:root {
    --color-wrath: #dc2626;     /* 1장 분노 */
    --color-envy: #16a34a;      /* 2장 시기 */
    --color-greed: #ca8a04;     /* 3장 탐욕 */
    --color-sloth: #6b7280;     /* 4장 나태 */
    --color-gluttony: #ea580c;  /* 5장 폭식 */
    --color-lust: #db2777;      /* 6장 색욕 */
    --color-pride: #7c3aed;     /* 7장 오만 */
}
```

## 서버 통신 패턴

### API 호출
```javascript
async function apiCall(apiCode, data = {}) {
    const res = await fetch('/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_no: getUserNo(),
            api_code: apiCode,
            data: data
        })
    });
    return res.json();
}
```

### 에러 핸들링
- 네트워크 에러 → 재시도 (최대 3회, 지수 백오프)
- `success: false` → UI에 message 표시
- 세션 만료 → 로그인 화면으로 리다이렉트

## 모바일 확장 대비

### PWA 준비
- `manifest.json`: 앱 이름, 아이콘, `display: standalone`
- Service Worker: 오프라인 에셋 캐싱
- HTTPS 필수

### 앱 래핑 (향후)
- Capacitor로 네이티브 앱 빌드
- 웹 코드 변경 최소화 (REST API + 반응형이면 거의 그대로)

## 성능 체크리스트

- [ ] 초기 로딩 3초 이내
- [ ] 전투 씬 60 FPS 유지
- [ ] 에셋 총 용량 챕터당 5MB 이하
- [ ] 탭 비활성화 시 애니메이션 일시정지 (`visibilitychange` 이벤트)
- [ ] 메모리 릭 방지: 씬 전환 시 리스너/타이머 정리
