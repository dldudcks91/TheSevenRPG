/**
 * TheSevenRPG — Prologue Scene
 * 5씬 텍스트 내레이션. 회원가입 후 최초 1회만 표시.
 * 클릭/탭으로 텍스트 한 줄씩 진행, 씬 전환.
 */
import { SceneManager } from '../scene-manager.js';
import { t } from '../i18n/index.js';
import story from '../i18n/story-ko.js';

const PrologueScene = {
    el: null,
    refs: {},

    /** 현재 씬/라인 인덱스 */
    _sceneIdx: 0,
    _lineIdx: 0,
    /** 타이핑 진행 중 여부 */
    _typing: false,
    /** 현재 타이핑 타이머 */
    _typeTimer: null,

    _replayMode: false,

    mount(el, data) {
        this.el = el;
        this._sceneIdx = 0;
        this._lineIdx = 0;
        this._replayMode = data?.replay === true;

        const scenes = story.prologue_scenes;

        el.innerHTML = `
            <div class="prologue-screen" data-action="advance">
                <div class="prologue-particles" id="pro-particles"></div>
                <div class="prologue-header">
                    <span class="prologue-scene-num" id="pro-scene-num">1 / ${scenes.length}</span>
                    <span class="prologue-title" id="pro-title"></span>
                    <button class="prologue-skip" data-action="skip">SKIP ▸▸</button>
                </div>
                <div class="prologue-body" id="pro-body"></div>
                <div class="prologue-footer">
                    <span class="prologue-hint" id="pro-hint">${t('prologue_click')}</span>
                </div>
            </div>
        `;

        this.refs = {
            sceneNum: el.querySelector('#pro-scene-num'),
            title: el.querySelector('#pro-title'),
            body: el.querySelector('#pro-body'),
            hint: el.querySelector('#pro-hint'),
        };

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._handleKeydown = this._onKeydown.bind(this);
        document.addEventListener('keydown', this._handleKeydown);

        this._createParticles();
        this._renderScene();
    },

    unmount() {
        if (this._handleEvent) this.el.removeEventListener('pointerdown', this._handleEvent);
        if (this._handleKeydown) document.removeEventListener('keydown', this._handleKeydown);
        if (this._typeTimer) clearTimeout(this._typeTimer);
        this.refs = {};
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;
        if (target.dataset.action === 'skip') { this._showChapterEnter(); return; }
        if (target.dataset.action === 'advance') this._advance();
    },

    _onKeydown(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this._advance();
        }
    },

    /** 클릭 시 동작: 타이핑 중이면 즉시 완료, 아니면 다음 라인 */
    _advance() {
        if (this._typing) {
            this._finishTyping();
            return;
        }
        this._nextLine();
    },

    /** 현재 씬 렌더링 (새 씬 시작) */
    _renderScene() {
        const scenes = story.prologue_scenes;
        const scene = scenes[this._sceneIdx];
        this._lineIdx = 0;

        this.refs.sceneNum.textContent = `${this._sceneIdx + 1} / ${scenes.length}`;
        this.refs.title.textContent = scene.title;
        this.refs.body.innerHTML = '';
        this.refs.hint.textContent = t('prologue_click');

        this._showNextLine();
    },

    /** 다음 라인 표시 */
    _nextLine() {
        const scenes = story.prologue_scenes;
        const scene = scenes[this._sceneIdx];

        if (this._lineIdx < scene.lines.length) {
            this._showNextLine();
        } else {
            // 현재 씬 끝 → 다음 씬 or 완료
            this._sceneIdx++;
            if (this._sceneIdx < scenes.length) {
                this._fadeToNextScene();
            } else {
                this._showChapterEnter();
            }
        }
    },

    /** 라인 하나를 타이핑 효과로 표시 */
    _showNextLine() {
        const scenes = story.prologue_scenes;
        const scene = scenes[this._sceneIdx];
        const line = scene.lines[this._lineIdx];
        this._lineIdx++;

        // 빈 줄은 즉시 추가
        if (!line) {
            const br = document.createElement('div');
            br.className = 'prologue-line prologue-blank';
            this.refs.body.appendChild(br);
            this._scrollToBottom();
            // 빈 줄 후 자동으로 다음 라인
            this._nextLine();
            return;
        }

        const lineEl = document.createElement('div');
        lineEl.className = 'prologue-line';
        this.refs.body.appendChild(lineEl);

        // 타이핑 효과
        this._typing = true;
        this._currentLineEl = lineEl;
        this._currentText = line;
        this._currentCharIdx = 0;
        this._typeNextChar();
    },

    /** 한 글자씩 타이핑 */
    _typeNextChar() {
        if (this._currentCharIdx >= this._currentText.length) {
            this._typing = false;
            this._scrollToBottom();
            return;
        }

        this._currentLineEl.textContent =
            this._currentText.substring(0, this._currentCharIdx + 1);
        this._currentCharIdx++;
        this._scrollToBottom();

        this._typeTimer = setTimeout(() => this._typeNextChar(), 40);
    },

    /** 타이핑 즉시 완료 */
    _finishTyping() {
        if (this._typeTimer) clearTimeout(this._typeTimer);
        this._currentLineEl.textContent = this._currentText;
        this._typing = false;
        this._scrollToBottom();
    },

    /** 씬 전환 (페이드) */
    _fadeToNextScene() {
        const body = this.refs.body;
        body.classList.add('prologue-fade-out');

        setTimeout(() => {
            body.classList.remove('prologue-fade-out');
            this._renderScene();
        }, 400);
    },

    /** 마지막: walking 씬으로 전환 */
    _showChapterEnter() {
        if (this._replayMode) { SceneManager.pop(); return; }
        SceneManager.replace('walking');
    },

    /** body 스크롤 최하단 */
    _scrollToBottom() {
        const body = this.refs.body;
        body.scrollTop = body.scrollHeight;
    },

    /** 불씨 파티클 */
    _createParticles() {
        const container = this.el.querySelector('#pro-particles');
        if (!container) return;
        for (let i = 0; i < 12; i++) {
            const p = document.createElement('div');
            p.className = 'prologue-particle';
            p.style.left = `${10 + Math.random() * 80}%`;
            p.style.bottom = `${Math.random() * 20}%`;
            p.style.animationDelay = `${Math.random() * 5}s`;
            p.style.animationDuration = `${4 + Math.random() * 4}s`;
            container.appendChild(p);
        }
    },
};

export default PrologueScene;
