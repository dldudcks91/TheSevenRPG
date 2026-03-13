/**
 * TheSevenRPG — Town Hub Screen (죄악의 성)
 * API 1004: 유저 정보 로드, 방치 파밍 상태 표시
 */
import { apiCall } from '../api.js';
import { Store } from '../store.js';
import { showLoading, hideLoading, formatGold } from '../utils.js';
import { clearSession } from '../session.js';

const TownScreen = {
    el: null,
    refs: {},
    _unsubscribers: [],
    _idleTimerInterval: null,

    mount(el) {
        this.el = el;

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="town-screen">
                    <button class="town-logout" data-action="logout">로그아웃</button>

                    <!-- 상단: 캐릭터 정보 -->
                    <div class="town-header">
                        <div class="town-header-row">
                            <div>
                                <span class="char-name" id="char-name">-</span>
                                <span class="char-level" id="char-level">Lv.1</span>
                            </div>
                            <div class="char-gold" id="char-gold">0 G</div>
                        </div>
                        <div class="town-exp-bar">
                            <div class="fill" id="exp-fill" style="width: 0%"></div>
                        </div>
                        <div class="town-stats" id="stat-chips"></div>
                    </div>

                    <!-- 중앙: 메뉴 -->
                    <div class="town-menu">
                        <div class="town-title">죄악의 성</div>
                        <div class="town-menu-grid">
                            <button class="town-menu-btn" data-action="navigate" data-screen="stage-select">
                                <span class="menu-icon">&#9876;</span>
                                <span class="menu-label">스테이지</span>
                            </button>
                            <button class="town-menu-btn" data-action="navigate" data-screen="inventory">
                                <span class="menu-icon">&#128188;</span>
                                <span class="menu-label">인벤토리</span>
                            </button>
                            <button class="town-menu-btn" data-action="navigate" data-screen="idle-farm">
                                <span class="menu-icon">&#9202;</span>
                                <span class="menu-label">방치 파밍</span>
                            </button>
                            <button class="town-menu-btn" data-action="navigate" data-screen="cards">
                                <span class="menu-icon">&#127183;</span>
                                <span class="menu-label">카드 도감</span>
                            </button>
                        </div>
                    </div>

                    <!-- 하단: 방치 파밍 상태 -->
                    <div class="town-idle-bar" id="idle-bar">
                        <span class="idle-status" id="idle-status">방치 파밍: 비활성</span>
                        <span class="idle-timer" id="idle-timer"></span>
                    </div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        // refs 캐싱
        this.refs = {
            charName: el.querySelector('#char-name'),
            charLevel: el.querySelector('#char-level'),
            charGold: el.querySelector('#char-gold'),
            expFill: el.querySelector('#exp-fill'),
            statChips: el.querySelector('#stat-chips'),
            idleStatus: el.querySelector('#idle-status'),
            idleTimer: el.querySelector('#idle-timer'),
        };

        // 이벤트 위임
        this._handleEvent = this.handleEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        // Store 구독
        this._unsubscribers.push(
            Store.subscribe('user.name', (name) => {
                this.refs.charName.textContent = name;
            }),
            Store.subscribe('user.level', (level) => {
                this.refs.charLevel.textContent = `Lv.${level}`;
            }),
            Store.subscribe('user.gold', (gold) => {
                this.refs.charGold.textContent = formatGold(gold);
            }),
            Store.subscribe('user.exp', (exp) => {
                const expPercent = exp > 0 ? Math.min(100, (exp % 1000) / 10) : 0;
                this.refs.expFill.style.width = expPercent + '%';
            }),
            Store.subscribe('user.stat_points', (sp) => {
                this._renderStatChips();
            }),
            Store.subscribe('idle.active', () => {
                this._renderIdleStatus();
            }),
        );

        // 초기 데이터 로드
        this.loadData();
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];

        if (this._idleTimerInterval) {
            clearInterval(this._idleTimerInterval);
            this._idleTimerInterval = null;
        }
    },

    handleEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;

        switch (action) {
            case 'navigate':
                window.location.hash = '#' + target.dataset.screen;
                break;
            case 'logout':
                clearSession();
                window.location.hash = '#login';
                break;
        }
    },

    async loadData() {
        showLoading();
        try {
            const result = await apiCall(1004, {});
            if (result?.success) {
                const d = result.data;

                // Store에 반영 → 구독 콜백으로 UI 자동 갱신
                Store.set('user.name', d.user_name);
                Store.set('user.level', d.level);
                Store.set('user.gold', d.gold);
                Store.set('user.exp', d.exp);
                Store.set('user.stat_points', d.stat_points);

                // 스탯
                Store.merge(d.stats, 'stats');

                // 방치 파밍
                if (d.idle_farm) {
                    Store.set('idle.active', d.idle_farm.active);
                    Store.set('idle.stage_id', d.idle_farm.stage_id);
                    Store.set('idle.elapsed_seconds', d.idle_farm.elapsed_seconds);
                } else {
                    Store.set('idle.active', false);
                }

                // 스탯 칩은 여러 Store 키에 의존하므로 로드 완료 후 직접 렌더
                this._renderStatChips();
                this._renderIdleStatus();
            }
        } finally {
            hideLoading();
        }
    },

    _renderStatChips() {
        const stats = [
            { label: 'STR', key: 'stats.str' },
            { label: 'DEX', key: 'stats.dex' },
            { label: 'VIT', key: 'stats.vit' },
            { label: 'LUK', key: 'stats.luck' },
            { label: 'COST', key: 'stats.cost' },
        ];

        this.refs.statChips.innerHTML = stats.map(s =>
            `<div class="stat-chip"><span>${s.label}</span> <span class="stat-value">${Store.get(s.key) ?? 0}</span></div>`
        ).join('');

        const sp = Store.get('user.stat_points');
        if (sp > 0) {
            this.refs.statChips.innerHTML +=
                `<div class="stat-chip" style="color:var(--color-warning);"><span>SP</span> <span class="stat-value">${sp}</span></div>`;
        }
    },

    _renderIdleStatus() {
        const active = Store.get('idle.active');

        // 기존 타이머 정리
        if (this._idleTimerInterval) {
            clearInterval(this._idleTimerInterval);
            this._idleTimerInterval = null;
        }

        if (!active) {
            this.refs.idleStatus.textContent = '방치 파밍: 비활성';
            this.refs.idleStatus.classList.remove('active');
            this.refs.idleTimer.textContent = '';
            return;
        }

        const stageId = Store.get('idle.stage_id');
        this.refs.idleStatus.textContent = `방치 파밍 중 (스테이지 ${stageId})`;
        this.refs.idleStatus.classList.add('active');

        let elapsed = Store.get('idle.elapsed_seconds') || 0;

        const updateTimer = () => {
            const h = Math.floor(elapsed / 3600);
            const m = Math.floor((elapsed % 3600) / 60);
            const s = elapsed % 60;
            this.refs.idleTimer.textContent =
                `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
            elapsed++;
        };

        updateTimer();
        this._idleTimerInterval = setInterval(updateTimer, 1000);
    },
};

export default TownScreen;
