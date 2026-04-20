/**
 * TheSevenRPG — Walking Scene
 * 프롤로그 종료 후, 캐릭터가 어둠 속을 걸어가는 연출.
 * LPC 스프라이트 레이어 합성 + walk 애니메이션 재생.
 */
import { SceneManager } from '../scene-manager.js';
import { t } from '../i18n/index.js';
import story from '../i18n/story-ko.js';
import { composeLpcSheet } from '../sprites/lpc-sprite.js';
import { CHARACTER_LAYERS, LPC_BASE_URL } from '../sprites/lpc-manifest.js';

const FRAME = 64;
const SCALE = 4;          // 64 * 4 = 256px 캐릭터
const DISPLAY = FRAME * SCALE;
const FPS = 8;
const WALK_DIR = 0;       // 0 = North (위로 걸어감)
const WALK_FRAMES = 9;

const TOTAL_DURATION = 13000;

const WalkingScene = {
    el: null,
    _animTimer: null,
    _textTimers: [],
    _endTimer: null,
    _frame: 0,
    _sheet: null,
    _canvas: null,
    _ctx: null,
    _done: false,
    _replayMode: false,

    async mount(el, data) {
        this.el = el;
        this._done = false;
        this._frame = 0;
        this._sheet = null;
        this._canvas = null;
        this._ctx = null;
        this._animTimer = null;
        this._textTimers = [];
        this._endTimer = null;
        this._replayMode = data?.replay === true;

        el.innerHTML = `
            <div class="walking-screen fade-in" data-action="skip">
                <div class="walking-bg"></div>
                <div class="walking-particles" id="walk-particles"></div>
                <canvas class="walking-character" id="walk-canvas"
                        width="${DISPLAY}" height="${DISPLAY}"></canvas>
                <div class="walking-text" id="walk-text"></div>
                <div class="walking-hint">${story.walking_skip}</div>
            </div>
        `;

        this._canvas = el.querySelector('#walk-canvas');
        this._ctx = this._canvas.getContext('2d');

        this._handleEvent = this._onEvent.bind(this);
        // 클릭 즉시 skip 방지 — mount 후 약간의 딜레이
        this._skipReady = false;
        setTimeout(() => {
            this._skipReady = true;
            el.addEventListener('pointerdown', this._handleEvent);
        }, 500);

        this._createParticles();

        await this._composeSheet();

        if (this._sheet) {
            this._startAnimation();
            this._scheduleTexts();
            this._endTimer = setTimeout(() => this._finish(), TOTAL_DURATION);
        } else {
            this._finish();
        }
    },

    unmount() {
        if (this._animTimer) clearInterval(this._animTimer);
        this._textTimers.forEach(t => clearTimeout(t));
        if (this._endTimer) clearTimeout(this._endTimer);
        if (this._handleEvent) this.el.removeEventListener('pointerdown', this._handleEvent);
        this._sheet = null;
        this._canvas = null;
        this._ctx = null;
    },

    _onEvent(e) {
        if (!this._skipReady) return;
        const target = e.target.closest('[data-action]');
        if (!target) return;
        if (target.dataset.action === 'skip') this._finish();
    },

    /** walk 시트 합성 (공용 composeLpcSheet 사용) */
    async _composeSheet() {
        this._sheet = await composeLpcSheet(CHARACTER_LAYERS, 'walk', LPC_BASE_URL);
    },

    /** walk 애니메이션 시작 */
    _startAnimation() {
        this._canvas.style.bottom = '-20%';

        this._animTimer = setInterval(() => {
            this._renderFrame();
            this._frame++;
        }, 1000 / FPS);

        this._canvas.style.transition = `bottom ${TOTAL_DURATION}ms linear`;
        requestAnimationFrame(() => {
            this._canvas.style.bottom = '120%';
        });
    },

    /** 프레임 렌더링 */
    _renderFrame() {
        if (!this._sheet || !this._ctx) return;

        const ctx = this._ctx;
        const f = this._frame % WALK_FRAMES;

        ctx.imageSmoothingEnabled = false;
        ctx.clearRect(0, 0, DISPLAY, DISPLAY);
        ctx.drawImage(
            this._sheet,
            f * FRAME, WALK_DIR * FRAME, FRAME, FRAME,
            0, 0, DISPLAY, DISPLAY
        );
    },

    /** 텍스트 스케줄 */
    _scheduleTexts() {
        const textEl = this.el.querySelector('#walk-text');
        const walkTexts = story.walking_texts;

        for (const item of walkTexts) {
            const timer = setTimeout(() => {
                textEl.classList.remove('visible');

                setTimeout(() => {
                    textEl.innerHTML = item.lines.map(line => {
                        if (!line) return '<br>';
                        const cls = item.accent
                            ? 'walking-text-line walking-text-accent'
                            : 'walking-text-line';
                        return `<div class="${cls}">${line}</div>`;
                    }).join('');
                    textEl.classList.add('visible');
                }, 300);
            }, item.at);

            this._textTimers.push(timer);
        }
    },

    /** 불씨 파티클 */
    _createParticles() {
        const container = this.el.querySelector('#walk-particles');
        if (!container) return;

        for (let i = 0; i < 15; i++) {
            const p = document.createElement('div');
            p.className = 'walking-particle';
            p.style.left = `${10 + Math.random() * 80}%`;
            p.style.bottom = `${Math.random() * 30}%`;
            p.style.animationDelay = `${Math.random() * 4}s`;
            p.style.animationDuration = `${3 + Math.random() * 3}s`;
            container.appendChild(p);
        }
    },

    /** 씬 종료 → tutorial-battle */
    _finish() {
        if (this._done) return;
        this._done = true;

        const screen = this.el.querySelector('.walking-screen');
        if (screen) {
            screen.classList.remove('fade-in');
            screen.classList.add('fade-out');
        }

        setTimeout(() => {
            if (this._replayMode) { SceneManager.pop(); return; }
            SceneManager.replace('tutorial-battle');
        }, 1000);
    },
};

export default WalkingScene;
