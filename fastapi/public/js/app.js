/**
 * TheSevenRPG — App Router & Screen Manager
 * ES Module 엔트리, 해시 기반 SPA 라우팅
 */
import { isLoggedIn } from './session.js';
import { loadMetaData } from './meta-data.js';
import LoginScreen from './screens/login.js';
import TownScreen from './screens/town.js';
import InventoryScreen from './screens/inventory.js';
import StageSelectScreen from './screens/stage-select.js';
import IdleFarmScreen from './screens/idle-farm.js';
import CardsScreen from './screens/cards.js';
import BattleScreen from './screens/battle.js';

// ── Screen 레지스트리 ──
const screens = {
    'login': LoginScreen,
    'town': TownScreen,
    'inventory': InventoryScreen,
    'stage-select': StageSelectScreen,
    'idle-farm': IdleFarmScreen,
    'cards': CardsScreen,
    'battle': BattleScreen,
};

let currentScreen = null;
let appContainer = null;
let _isHidden = false;

/** 화면 전환 (해시 변경) */
export function navigate(screenName) {
    window.location.hash = '#' + screenName;
}

/** 해시 변경 핸들러 */
function handleHashChange() {
    const hash = window.location.hash.slice(1) || 'login';

    // 세션 없으면 login으로 (login 제외)
    if (hash !== 'login' && !isLoggedIn()) {
        navigate('login');
        return;
    }

    // 이미 로그인된 상태에서 login 해시면 town으로
    if (hash === 'login' && isLoggedIn()) {
        navigate('town');
        return;
    }

    switchScreen(hash);
}

/** 화면 전환 실행 */
function switchScreen(name) {
    if (!screens[name]) {
        console.warn(`[App] 화면 "${name}" 미등록`);
        return;
    }

    // 현재 화면 언마운트
    if (currentScreen && screens[currentScreen] && screens[currentScreen].unmount) {
        screens[currentScreen].unmount();
    }

    // 기존 화면 DOM 비활성화
    const existing = appContainer.querySelector('.screen.active');
    if (existing) {
        existing.classList.remove('active');
    }

    currentScreen = name;

    // 새 화면 마운트
    let screenEl = appContainer.querySelector(`[data-screen="${name}"]`);
    if (!screenEl) {
        screenEl = document.createElement('div');
        screenEl.className = 'screen';
        screenEl.dataset.screen = name;
        appContainer.appendChild(screenEl);
    }

    screens[name].mount(screenEl);
    screenEl.classList.add('active');
}

// ── visibilitychange: 탭 비활성 시 Phaser 일시정지 ──

function handleVisibilityChange() {
    _isHidden = document.hidden;

    if (!currentScreen || !screens[currentScreen]) return;

    const screen = screens[currentScreen];

    if (_isHidden) {
        // 탭 비활성 → 현재 Screen에 onPause가 있으면 호출
        if (typeof screen.onPause === 'function') {
            screen.onPause();
        }
    } else {
        // 탭 활성 → 현재 Screen에 onResume이 있으면 호출
        if (typeof screen.onResume === 'function') {
            screen.onResume();
        }
    }
}

/** 탭 비활성 상태 조회 (Screen에서 사용 가능) */
export function isAppHidden() {
    return _isHidden;
}

// ── Service Worker 등록 ──

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(() => console.log('[App] Service Worker 등록 완료'))
            .catch((err) => console.warn('[App] Service Worker 등록 실패:', err));
    }
}

// ── 앱 초기화 ──
async function init() {
    appContainer = document.getElementById('app');

    // 메타데이터 로드 (API 1002는 PUBLIC — 로그인 전이라도 가능)
    await loadMetaData();

    window.addEventListener('hashchange', handleHashChange);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    handleHashChange();

    registerServiceWorker();

    console.log('[App] TheSevenRPG 클라이언트 초기화 완료');
}

document.addEventListener('DOMContentLoaded', () => init());
