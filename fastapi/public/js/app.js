/**
 * TheSevenRPG — App Router & Screen Manager
 * ES Module 엔트리, 해시 기반 SPA 라우팅
 */
import { isLoggedIn } from './session.js';
import LoginScreen from './screens/login.js';
import TownScreen from './screens/town.js';
import InventoryScreen from './screens/inventory.js';
import StageSelectScreen from './screens/stage-select.js';
import IdleFarmScreen from './screens/idle-farm.js';
import CardsScreen from './screens/cards.js';

// ── Screen 레지스트리 ──
const screens = {
    'login': LoginScreen,
    'town': TownScreen,
    'inventory': InventoryScreen,
    'stage-select': StageSelectScreen,
    'idle-farm': IdleFarmScreen,
    'cards': CardsScreen,
};

let currentScreen = null;
let appContainer = null;

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

// ── 앱 초기화 ──
function init() {
    appContainer = document.getElementById('app');

    window.addEventListener('hashchange', handleHashChange);
    handleHashChange();

    console.log('[App] TheSevenRPG 클라이언트 초기화 완료');
}

document.addEventListener('DOMContentLoaded', () => init());
