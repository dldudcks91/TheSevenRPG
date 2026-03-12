/**
 * TheSevenRPG — App Router & Screen Manager
 * 해시 기반 SPA 라우팅, 화면 전환
 */
const Toast = (() => {
    let container = null;

    function init() {
        container = document.getElementById('toast-container');
    }

    /**
     * 토스트 메시지 표시
     * @param {string} message
     * @param {'success'|'warning'|'error'|'info'} type
     * @param {number} duration - ms (기본 3초)
     */
    function show(message, type = 'info', duration = 3000) {
        if (!container) init();

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        // show 애니메이션
        requestAnimationFrame(() => toast.classList.add('show'));

        // 자동 제거
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    return { init, show };
})();

const Loading = (() => {
    let overlay = null;
    let count = 0;

    function init() {
        overlay = document.getElementById('loading-overlay');
    }

    function show() {
        if (!overlay) init();
        count++;
        overlay.classList.add('show');
    }

    function hide() {
        if (!overlay) init();
        count = Math.max(0, count - 1);
        if (count === 0) {
            overlay.classList.remove('show');
        }
    }

    return { init, show, hide };
})();

const App = (() => {
    // 화면 레지스트리: { name: { mount(container), unmount() } }
    const screens = {};
    let currentScreen = null;
    let appContainer = null;

    /** 화면 등록 */
    function registerScreen(name, screenModule) {
        screens[name] = screenModule;
    }

    /** 화면 전환 */
    function navigate(screenName) {
        window.location.hash = '#' + screenName;
    }

    /** 해시 변경 핸들러 */
    function handleHashChange() {
        const hash = window.location.hash.slice(1) || 'login';

        // 세션 없으면 login으로 (login 제외)
        if (hash !== 'login' && !Session.isLoggedIn()) {
            navigate('login');
            return;
        }

        // 이미 로그인된 상태에서 login 해시면 town으로
        if (hash === 'login' && Session.isLoggedIn()) {
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

    /** 앱 초기화 */
    function init() {
        appContainer = document.getElementById('app');
        Toast.init();
        Loading.init();

        // 해시 이벤트 바인딩
        window.addEventListener('hashchange', handleHashChange);

        // 최초 라우팅
        handleHashChange();

        console.log('[App] TheSevenRPG 클라이언트 초기화 완료');
    }

    return { init, registerScreen, navigate };
})();

// DOM 로드 후 앱 시작
document.addEventListener('DOMContentLoaded', () => App.init());
