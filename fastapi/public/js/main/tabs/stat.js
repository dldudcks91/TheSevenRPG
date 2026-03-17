/**
 * TheSevenRPG — Stat Tab (스탯 탭)
 * 캐릭터 정보 + 스탯 배분 + 전투 스탯 + 세트 보너스
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { formatGold } from '../../utils.js';

const StatTab = {
    el: null,
    _unsubscribers: [],

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="tab-stat">
                <div class="stat-section">
                    <div class="stat-section-title">캐릭터 정보</div>
                    <div class="stat-info-grid">
                        <div class="stat-info-row">
                            <span>레벨</span>
                            <span id="ts-level">1</span>
                        </div>
                        <div class="stat-info-row">
                            <span>경험치</span>
                            <span id="ts-exp">0 / 0</span>
                        </div>
                        <div class="stat-info-row">
                            <span>골드</span>
                            <span id="ts-gold" class="gold-text">0 G</span>
                        </div>
                    </div>
                </div>

                <div class="stat-section">
                    <div class="stat-section-title">
                        스탯 배분
                        <span class="stat-sp" id="ts-sp"></span>
                    </div>
                    <div class="stat-alloc-list" id="ts-alloc">
                    </div>
                </div>

                <div class="stat-section">
                    <div class="stat-section-title">전투 스탯</div>
                    <div class="stat-combat-grid" id="ts-combat">
                    </div>
                </div>

                <div class="stat-section">
                    <div class="stat-section-title">세트 보너스</div>
                    <div class="stat-set-list" id="ts-sets">
                        <div class="stat-set-empty">장비를 장착하면 세트 효과가 표시됩니다</div>
                    </div>
                </div>

                <div class="stat-section">
                    <button class="stat-reset-btn" data-action="reset-stats">스탯 리셋</button>
                </div>
            </div>
        `;

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        // Store 구독
        this._unsubscribers.push(
            Store.subscribe('user.level', () => this._render()),
            Store.subscribe('user.exp', () => this._render()),
            Store.subscribe('user.gold', () => this._render()),
            Store.subscribe('user.stat_points', () => this._render()),
            Store.subscribe('stats.str', () => this._render()),
            Store.subscribe('stats.dex', () => this._render()),
            Store.subscribe('stats.vit', () => this._render()),
            Store.subscribe('stats.luck', () => this._render()),
            Store.subscribe('stats.cost', () => this._render()),
        );

        this._render();
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'add-stat':
                this._addStat(target.dataset.stat);
                break;
            case 'reset-stats':
                this._resetStats();
                break;
        }
    },

    _render() {
        const level = Store.get('user.level') || 1;
        const exp = Store.get('user.exp') || 0;
        const gold = Store.get('user.gold') || 0;
        const sp = Store.get('user.stat_points') || 0;

        // 캐릭터 정보
        this.el.querySelector('#ts-level').textContent = level;
        this.el.querySelector('#ts-exp').textContent = `${exp.toLocaleString()}`;
        this.el.querySelector('#ts-gold').textContent = formatGold(gold);

        // SP 표시
        const spEl = this.el.querySelector('#ts-sp');
        spEl.textContent = sp > 0 ? `(SP: ${sp})` : '';
        spEl.className = sp > 0 ? 'stat-sp has-points' : 'stat-sp';

        // 스탯 배분
        const stats = [
            { key: 'str',  label: 'STR',  storeKey: 'stats.str',  desc: '공격력 +0.5%' },
            { key: 'dex',  label: 'DEX',  storeKey: 'stats.dex',  desc: '공속 +0.3%, 명중 +5' },
            { key: 'vit',  label: 'VIT',  storeKey: 'stats.vit',  desc: 'HP +10' },
            { key: 'luck', label: 'LUK',  storeKey: 'stats.luck', desc: '치확 +5, 회피 +5' },
            { key: 'cost', label: 'COST', storeKey: 'stats.cost', desc: '최대코스트 +2' },
        ];

        this.el.querySelector('#ts-alloc').innerHTML = stats.map(s => {
            const val = Store.get(s.storeKey) ?? 0;
            return `
                <div class="stat-alloc-row">
                    <div class="stat-alloc-info">
                        <span class="stat-alloc-label">${s.label}</span>
                        <span class="stat-alloc-desc">${s.desc}</span>
                    </div>
                    <div class="stat-alloc-right">
                        <span class="stat-alloc-value">${val}</span>
                        ${sp > 0
                            ? `<button class="stat-add-btn" data-action="add-stat" data-stat="${s.key}">+</button>`
                            : `<span class="stat-add-btn disabled">+</span>`
                        }
                    </div>
                </div>
            `;
        }).join('');

        // 전투 스탯 (계산값은 서버에서 받아야 정확하지만, 클라이언트 추정으로 표시)
        this._renderCombatStats();
    },

    _renderCombatStats() {
        const vit = Store.get('stats.vit') || 0;
        const hp = 100 + vit * 10;

        const combatStats = [
            { label: 'HP',       value: `${hp}` },
            { label: '공격력',    value: '-' },
            { label: '공격속도',  value: '-' },
            { label: '명중률',    value: '-' },
            { label: '회피율',    value: '-' },
            { label: '치명타',    value: '-' },
        ];

        this.el.querySelector('#ts-combat').innerHTML = combatStats.map(s => `
            <div class="stat-combat-row">
                <span>${s.label}</span>
                <span class="stat-combat-value">${s.value}</span>
            </div>
        `).join('');
    },

    async _addStat(statKey) {
        // TODO: 스탯 추가 API 호출 (현재 서버에 개별 스탯 추가 API 없음)
        // 임시: Store 직접 변경
        const storeKey = `stats.${statKey}`;
        const current = Store.get(storeKey) || 0;
        const sp = Store.get('user.stat_points') || 0;
        if (sp <= 0) return;

        Store.set(storeKey, current + 1);
        Store.set('user.stat_points', sp - 1);
    },

    async _resetStats() {
        if (!confirm('스탯을 리셋하시겠습니까?\n골드가 소비됩니다.')) return;

        const result = await apiCall(1005, {});
        if (result?.success) {
            const d = result.data;
            Store.set('user.gold', d.gold);
            Store.set('user.stat_points', d.stat_points);
            Store.set('stats.str', d.stats.str);
            Store.set('stats.dex', d.stats.dex);
            Store.set('stats.vit', d.stats.vit);
            Store.set('stats.luck', d.stats.luck);
            Store.set('stats.cost', d.stats.cost);
        }
    },
};

export default StatTab;
