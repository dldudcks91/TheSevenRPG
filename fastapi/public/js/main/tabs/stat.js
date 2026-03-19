/**
 * TheSevenRPG — Stat Tab (스탯 탭)
 * 캐릭터 정보 + 스탯 배분 + 전투 스탯 + 세트 보너스
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { formatGold } from '../../utils.js';
import { t } from '../../i18n/index.js';

const StatTab = {
    el: null,
    _unsubscribers: [],

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="tab-stat">
                <div class="stat-section">
                    <div class="stat-section-title">${t('stat_char_info')}</div>
                    <div class="stat-info-grid">
                        <div class="stat-info-row">
                            <span>${t('stat_level')}</span>
                            <span id="ts-level">1</span>
                        </div>
                        <div class="stat-info-row">
                            <span>${t('stat_exp')}</span>
                            <span id="ts-exp">0 / 0</span>
                        </div>
                        <div class="stat-info-row">
                            <span>${t('stat_gold')}</span>
                            <span id="ts-gold" class="gold-text">0 G</span>
                        </div>
                    </div>
                </div>

                <div class="stat-section">
                    <div class="stat-section-title">
                        ${t('stat_alloc')}
                        <span class="stat-sp" id="ts-sp"></span>
                    </div>
                    <div class="stat-alloc-list" id="ts-alloc">
                    </div>
                </div>

                <div class="stat-section">
                    <div class="stat-section-title">${t('stat_combat')}</div>
                    <div class="stat-combat-grid" id="ts-combat">
                    </div>
                </div>

                <div class="stat-section">
                    <button class="stat-reset-btn" data-action="reset-stats">${t('stat_reset')}</button>
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
            Store.subscribe('inventory.items', () => this._render()),
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
            { key: 'str',  label: 'STR',  storeKey: 'stats.str',  desc: t('stat_str_desc') },
            { key: 'dex',  label: 'DEX',  storeKey: 'stats.dex',  desc: t('stat_dex_desc') },
            { key: 'vit',  label: 'VIT',  storeKey: 'stats.vit',  desc: t('stat_vit_desc') },
            { key: 'luck', label: 'LUK',  storeKey: 'stats.luck', desc: t('stat_luck_desc') },
            { key: 'cost', label: 'COST', storeKey: 'stats.cost', desc: t('stat_cost_desc') },
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
        const str  = Store.get('stats.str') || 10;
        const dex  = Store.get('stats.dex') || 10;
        const vit  = Store.get('stats.vit') || 10;
        const luck = Store.get('stats.luck') || 10;
        const cost = Store.get('stats.cost') || 10;
        const level = Store.get('user.level') || 1;

        // 장비 옵션 합산
        const items = Store.get('inventory.items') || [];
        const equipped = items.filter(i => i.equip_slot);

        let iAtkPct = 0, iAspdPct = 0, iHpPct = 0;
        let iAcc = 0, iEva = 0, iCritCh = 0, iCritDmg = 0;
        let iDef = 0, iMdef = 0;
        let baseWpnAtk = 10, baseWpnAspd = 1.0;

        equipped.forEach(item => {
            const o = item.dynamic_options || {};
            iAtkPct  += o.atk_pct || 0;
            iAspdPct += o.aspd_pct || 0;
            iHpPct   += o.hp_pct || o.hp_bonus || 0;
            iAcc     += o.acc || o.accuracy || 0;
            iEva     += o.eva || o.evasion || 0;
            iCritCh  += o.crit_chance || o.crit_rate || 0;
            iCritDmg += o.crit_dmg || o.crit_damage || 0;
            iDef     += o.def || 0;
            iMdef    += o.mdef || 0;
            if (item.equip_slot === 'weapon') {
                baseWpnAtk  = o.base_atk || 10;
                baseWpnAspd = o.base_aspd || 1.0;
            }
        });

        const maxHp    = Math.floor((100 + vit * 10) * (1 + iHpPct / 100));
        const attack   = (baseWpnAtk * (1 + str * 0.005) * (1 + iAtkPct / 100)).toFixed(1);
        const atkSpeed = (baseWpnAspd * (1 + dex * 0.003) * (1 + iAspdPct / 100)).toFixed(2);
        const accRaw   = dex * 5 + iAcc;
        const evaRaw   = luck * 5 + iEva;
        const critChRaw = luck * 5 + iCritCh;
        const acc      = (accRaw * 0.001).toFixed(3);
        const eva      = (evaRaw * 0.001).toFixed(3);
        const critCh   = (critChRaw * 0.001 * 100).toFixed(1);
        const critDmg  = (1.5 + luck * 0.003 + iCritDmg).toFixed(2);
        const defense  = iDef.toFixed(0);
        const mdef     = iMdef.toFixed(0);
        const maxCost  = level + cost * 2;

        const combatStats = [
            { label: t('combat_hp'),          value: maxHp },
            { label: t('combat_atk'),         value: attack },
            { label: t('combat_aspd'),        value: atkSpeed },
            { label: t('combat_acc'),         value: acc },
            { label: t('combat_eva'),         value: eva },
            { label: t('combat_crit_ch'),     value: `${critCh}%` },
            { label: t('combat_crit_dmg'),    value: `x${critDmg}` },
            { label: t('combat_def'),         value: defense },
            { label: t('combat_mdef'),        value: mdef },
            { label: t('combat_max_cost'),    value: maxCost },
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
        if (!confirm(t('stat_reset_confirm'))) return;

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
