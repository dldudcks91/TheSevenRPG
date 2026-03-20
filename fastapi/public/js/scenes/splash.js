/**
 * TheSevenRPG — Splash Scene
 * 타이틀 표시 + 메타데이터 로딩 + 자동 전환
 */
import { loadMetaData } from '../meta-data.js';
import { isLoggedIn } from '../session.js';
import { SceneManager } from '../scene-manager.js';
import { t } from '../i18n/index.js';

const SplashScene = {
    el: null,
    refs: {},

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="splash-screen">
                <div class="splash-title-area">
                    <h1 class="splash-title">THE SEVEN</h1>
                    <p class="splash-subtitle">${t('splash_title')}</p>
                </div>
                <div class="splash-loading-area">
                    <div class="splash-progress-track">
                        <div class="splash-progress-bar" id="splash-progress"></div>
                    </div>
                    <p class="splash-status" id="splash-status">${t('splash_init')}</p>
                </div>
            </div>
        `;

        this.refs = {
            progress: el.querySelector('#splash-progress'),
            status: el.querySelector('#splash-status'),
        };

        this._load();
    },

    unmount() {
        this.refs = {};
    },

    /** @private 메타데이터 로딩 + 씬 전환 */
    async _load() {
        try {
            this._setProgress(10, t('splash_loading'));
            await loadMetaData();
            this._setProgress(80, t('splash_ready'));

            // 로딩 완료 표시 잠깐 보여주기
            await this._delay(400);
            this._setProgress(100, t('splash_start'));
            await this._delay(300);

            // 세션 유무에 따라 다음 씬 결정
            if (isLoggedIn()) {
                SceneManager.replace('main');
            } else {
                SceneManager.replace('login');
            }
        } catch (err) {
            console.error('[Splash] Loading failed:', err);
            this._setProgress(0, t('splash_fail'));
        }
    },

    /** @private */
    _setProgress(percent, text) {
        if (this.refs.progress) {
            this.refs.progress.style.width = `${percent}%`;
        }
        if (this.refs.status) {
            this.refs.status.textContent = text;
        }
    },

    /** @private */
    _delay(ms) {
        return new Promise(r => setTimeout(r, ms));
    },
};

export default SplashScene;
