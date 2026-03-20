/**
 * TheSevenRPG — App Entry
 * SceneManager 기반 씬 관리
 *
 * Scene flow:
 *   Splash (title + loading) → Login (세션 없음) / Main (세션 있음)
 *   회원가입 → Prologue (5씬 내레이션) → Walking (걷기 연출) → Tutorial Battle → Main
 *   Main 내부: town ↔ battle ↔ forge ↔ shop (switchRightView로 관리)
 */
import { SceneManager } from './scene-manager.js';
import SplashScene from './scenes/splash.js';
import PrologueScene from './scenes/prologue.js';
import WalkingScene from './scenes/walking.js';
import TutorialBattleScene from './scenes/tutorial-battle.js';
import LoginScreen from './screens/login.js';
import MainScreen from './main.js';

// ── Scene 등록 ──
function registerScenes() {
    SceneManager.register('splash', SplashScene);
    SceneManager.register('prologue', PrologueScene);
    SceneManager.register('walking', WalkingScene);
    SceneManager.register('tutorial-battle', TutorialBattleScene);
    SceneManager.register('login', LoginScreen);
    SceneManager.register('main', MainScreen);
}

// ── visibilitychange ──
function handleVisibilityChange() {
    if (SceneManager.current() === 'main' && MainScreen.onVisibilityChange) {
        MainScreen.onVisibilityChange(document.hidden);
    }
}

// ── Service Worker ──
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(() => console.log('[App] Service Worker 등록 완료'))
            .catch((err) => console.warn('[App] Service Worker 등록 실패:', err));
    }
}

// ── 초기화 ──
async function init() {
    const appContainer = document.getElementById('app');

    SceneManager.init(appContainer);
    registerScenes();

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // 세션 만료 이벤트 → SceneManager로 로그인 화면 전환
    window.addEventListener('session-expired', () => {
        SceneManager.resetTo('login');
    });

    // Splash에서 메타데이터 로드 + 세션 체크 + 자동 전환
    await SceneManager.push('splash');

    registerServiceWorker();
    console.log('[App] TheSevenRPG 클라이언트 초기화 완료');
}

document.addEventListener('DOMContentLoaded', () => init());
