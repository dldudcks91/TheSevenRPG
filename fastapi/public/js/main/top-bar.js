/**
 * TheSevenRPG — Top Bar Component
 * 닉네임, 레벨, 스탯 칩, EXP 바, 골드, 로그아웃
 */
import { Store } from '../store.js';
import { formatGold } from '../utils.js';
import { clearSession } from '../session.js';
import { SceneManager } from '../scene-manager.js';
import { t, getLang, setLang, onLangChange } from '../i18n/index.js';

const TopBar = {
    el: null,
    refs: {},
    _unsubscribers: [],

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="top-bar">
                <div class="top-bar-row">
                    <div class="top-bar-left">
                        <span class="top-bar-name" id="tb-name">-</span>
                        <span class="top-bar-level" id="tb-level">Lv.1</span>
                    </div>
                    <div class="top-bar-stats" id="tb-stats"></div>
                    <div class="top-bar-right">
                        <span class="top-bar-gold" id="tb-gold">0 G</span>
                        <button class="top-bar-replay" data-action="replay-scene" title="씬 다시보기">\u25B6</button>
                        <button class="top-bar-settings" data-action="settings">\u2699</button>
                        <button class="top-bar-logout" data-action="logout">${t('logout')}</button>
                    </div>
                </div>
                <div class="top-bar-exp">
                    <div class="top-bar-exp-fill" id="tb-exp-fill" style="width: 0%"></div>
                </div>
            </div>
        `;

        this.refs = {
            name: el.querySelector('#tb-name'),
            level: el.querySelector('#tb-level'),
            stats: el.querySelector('#tb-stats'),
            gold: el.querySelector('#tb-gold'),
            expFill: el.querySelector('#tb-exp-fill'),
        };

        // 이벤트 위임 (el + 설정 모달용 document)
        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);
        document.addEventListener('pointerdown', this._handleEvent);

        // Store 구독
        this._unsubscribers.push(
            Store.subscribe('user.name', (v) => { this.refs.name.textContent = v; }),
            Store.subscribe('user.level', (v) => { this.refs.level.textContent = `Lv.${v}`; }),
            Store.subscribe('user.gold', (v) => { this.refs.gold.textContent = formatGold(v); }),
            Store.subscribe('user.exp', () => { this._renderExp(); }),
            Store.subscribe('user.stat_points', () => { this._renderStats(); }),
            Store.subscribe('stats.str', () => { this._renderStats(); }),
            Store.subscribe('stats.dex', () => { this._renderStats(); }),
            Store.subscribe('stats.vit', () => { this._renderStats(); }),
            Store.subscribe('stats.luck', () => { this._renderStats(); }),
            Store.subscribe('stats.cost', () => { this._renderStats(); }),
        );
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
            document.removeEventListener('pointerdown', this._handleEvent);
        }
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'logout':
                clearSession();
                SceneManager.resetTo('login');
                break;
            case 'settings':
                this._showSettings();
                break;
            case 'replay-scene':
                this._showReplayModal();
                break;
            case 'replay-select':
                this._hideReplayModal();
                SceneManager.push(target.dataset.scene, { replay: true });
                break;
            case 'close-replay':
                this._hideReplayModal();
                break;
            case 'lang-select':
                setLang(target.dataset.lang);
                location.reload();
                break;
            case 'close-settings':
                this._hideSettings();
                break;
        }
    },

    _renderStats() {
        const stats = [
            { label: 'STR', key: 'stats.str' },
            { label: 'DEX', key: 'stats.dex' },
            { label: 'VIT', key: 'stats.vit' },
            { label: 'LUK', key: 'stats.luck' },
            { label: 'COST', key: 'stats.cost' },
        ];

        let html = stats.map(s =>
            `<span class="top-bar-stat-chip"><span>${s.label}</span> <span class="stat-val">${Store.get(s.key) ?? 0}</span></span>`
        ).join('');

        const sp = Store.get('user.stat_points');
        if (sp > 0) {
            html += `<span class="top-bar-stat-chip sp"><span>SP</span> <span class="stat-val">${sp}</span></span>`;
        }

        this.refs.stats.innerHTML = html;
    },

    _showSettings() {
        if (document.getElementById('settings-modal')) return;
        const lang = getLang();
        const modal = document.createElement('div');
        modal.id = 'settings-modal';
        modal.className = 'settings-overlay';
        modal.innerHTML = `
            <div class="settings-box">
                <div class="settings-title">${t('settings_title')}</div>
                <div class="settings-row">
                    <span class="settings-label">${t('settings_language')}</span>
                    <div class="settings-lang-btns">
                        <button class="settings-lang-btn ${lang === 'ko' ? 'active' : ''}" data-action="lang-select" data-lang="ko">한국어</button>
                        <button class="settings-lang-btn ${lang === 'en' ? 'active' : ''}" data-action="lang-select" data-lang="en">English</button>
                    </div>
                </div>
                <button class="btn settings-close" data-action="close-settings">${t('settings_close')}</button>
            </div>
        `;
        document.body.appendChild(modal);
    },

    _hideSettings() {
        const modal = document.getElementById('settings-modal');
        if (modal) modal.remove();
    },

    _showReplayModal() {
        if (document.getElementById('replay-modal')) return;
        const modal = document.createElement('div');
        modal.id = 'replay-modal';
        modal.className = 'settings-overlay';
        modal.innerHTML = `
            <div class="settings-box">
                <div class="settings-title">씬 다시보기</div>
                <div class="replay-list">
                    <button class="btn replay-btn" data-action="replay-select" data-scene="prologue">프롤로그</button>
                    <button class="btn replay-btn" data-action="replay-select" data-scene="walking">걸어가는 씬</button>
                </div>
                <button class="btn settings-close" data-action="close-replay">${t('settings_close')}</button>
            </div>
        `;
        document.body.appendChild(modal);
    },

    _hideReplayModal() {
        const modal = document.getElementById('replay-modal');
        if (modal) modal.remove();
    },

    _renderExp() {
        const exp = Store.get('user.exp') || 0;
        const pct = exp > 0 ? Math.min(100, (exp % 1000) / 10) : 0;
        this.refs.expFill.style.width = pct + '%';
    },
};

export default TopBar;
