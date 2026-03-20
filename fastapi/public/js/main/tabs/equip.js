/**
 * TheSevenRPG — Equip Tab (장비 탭)
 * 장착 슬롯 5개 + 코스트 바 + 세트 요약 + 아이콘 그리드 + 비교 팝업
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { formatGold, escapeHtml, setupEventDelegation, teardown } from '../../utils.js';
import { getEquipName, getEquipSlot, getSetBonus } from '../../meta-data.js';
import Popup from '../../popup.js';
import { t, sinName, rarityName, slotName } from '../../i18n/index.js';

const EQUIP_SLOTS = [
    { key: 'weapon',  icon: '\u2694' },
    { key: 'armor',   icon: '\u{1F6E1}' },
    { key: 'helmet',  icon: '\u{1FA96}' },
    { key: 'gloves',  icon: '\u{1F9E4}' },
    { key: 'boots',   icon: '\u{1F462}' },
];

const OPTION_LABEL_KEYS = {
    // 기본 스탯
    base_atk: 'opt_base_atk', base_aspd: 'opt_base_aspd',
    atk: 'opt_atk', def: 'opt_def', hp: 'opt_hp',
    mdef: 'opt_mdef', atk_speed: 'opt_atk_speed',
    accuracy: 'opt_accuracy', evasion: 'opt_evasion',
    crit_rate: 'opt_crit_rate', crit_damage: 'opt_crit_damage',
    // 접두사/접미사 옵션
    atk_damage: 'opt_atk_damage',
    hp_bonus: 'opt_hp_bonus', hp_regen: 'opt_hp_regen',
    defense: 'opt_defense', magic_resist: 'opt_magic_resist',
    reflect_damage: 'opt_reflect_damage', crushing_blow: 'opt_crushing_blow',
    life_steal: 'opt_life_steal', def_ignore: 'opt_def_ignore',
    cc_reduction: 'opt_cc_reduction', counter_dmg: 'opt_counter_dmg',
    status_chance: 'opt_status_chance',
    atk_per_lv: 'opt_atk_per_lv', def_per_lv: 'opt_def_per_lv',
    all_skill_lv: 'opt_all_skill_lv', all_stats: 'opt_all_stats',
    gold_find: 'opt_gold_find', item_find: 'opt_item_find',
    fhr: 'opt_fhr',
};

const EquipTab = {
    el: null,
    _unsubscribers: [],
    _currentFilter: 'all',

    mount(el) {
        setupEventDelegation(this, el);

        el.innerHTML = `
            <div class="tab-equip">
                <div class="equip-section">
                    <div class="equip-section-title">${t('equip_equipped')}</div>
                    <div class="equip-slots" id="eq-slots">
                        ${EQUIP_SLOTS.map(s => `
                            <div class="eq-slot" data-action="slot-click" data-slot="${s.key}" data-popup-trigger>
                                <span class="eq-slot-icon">${s.icon}</span>
                                <span class="eq-slot-label">${slotName(s.key)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="equip-cost-bar">
                    <span class="equip-cost-text" id="eq-cost-text">${t('equip_cost')}: 0 / 0</span>
                    <div class="equip-cost-gauge">
                        <div class="equip-cost-fill" id="eq-cost-fill" style="width:0%"></div>
                    </div>
                </div>

                <div class="equip-section">
                    <div class="equip-filter-bar">
                        <span class="equip-count" id="eq-unequip-count">${t('equip_unequipped')} 0${t('equip_count_unit')}</span>
                        <div class="equip-filters">
                            <button class="eq-filter active" data-action="filter" data-filter="all">${t('equip_filter_all')}</button>
                            <button class="eq-filter" data-action="filter" data-filter="weapon">${t('equip_filter_weapon')}</button>
                            <button class="eq-filter" data-action="filter" data-filter="armor">${t('equip_filter_armor')}</button>
                        </div>
                    </div>
                    <div class="equip-grid" id="eq-grid"></div>
                </div>

                <div class="equip-footer">
                    <span id="eq-inv-count">0 / 21</span>
                </div>

                <div class="equip-section equip-set-section">
                    <div class="equip-section-title">${t('equip_set_bonus')}</div>
                    <div class="equip-set-summary" id="eq-set-summary"></div>
                </div>
            </div>
        `;

        // 팝업 내 버튼도 처리 (팝업은 body에 붙으므로 별도 리스너)
        this._handlePopupEvent = this._onPopupEvent.bind(this);
        document.addEventListener('pointerdown', this._handlePopupEvent);

        this._unsubscribers.push(
            Store.subscribe('inventory.items', () => this._render()),
        );

        this._currentFilter = 'all';
        this._loadData();
    },

    unmount() {
        teardown(this);
        if (this._handlePopupEvent) document.removeEventListener('pointerdown', this._handlePopupEvent);
        Popup.hide();
    },

    async _loadData() {
        const result = await apiCall(2003, {});
        if (result?.success) {
            Store.set('inventory.items', result.data.items);
        }
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'slot-click':
                this._onSlotClick(target.dataset.slot, target);
                break;
            case 'filter':
                this._setFilter(target.dataset.filter);
                break;
            case 'equip':
                this._doEquip(target.dataset.uid, target.dataset.slot);
                break;
            case 'unequip':
                this._doUnequip(target.dataset.uid);
                break;
            case 'sell':
                this._doSell(target.dataset.uid);
                break;
            case 'item-click':
                this._onItemClick(target.dataset.uid, target);
                break;
            case 'set-box-click':
                this._onSetBoxClick(target);
                break;
        }
    },

    _onPopupEvent(e) {
        const popupContainer = document.getElementById('popup-container');
        if (!popupContainer || !popupContainer.contains(e.target)) return;

        const target = e.target.closest('[data-action]');
        if (!target) return;

        e.stopPropagation();

        switch (target.dataset.action) {
            case 'equip':
                this._doEquip(target.dataset.uid, target.dataset.slot);
                break;
            case 'unequip':
                this._doUnequip(target.dataset.uid);
                break;
            case 'sell':
                this._doSell(target.dataset.uid);
                break;
        }
    },

    // ── 렌더링 ──

    _render() {
        const items = Store.get('inventory.items') || [];
        this._renderSlots(items);
        this._renderCost(items);
        this._renderSetSummary(items);
        this._renderGrid(items);
        this._renderInvCount(items);
    },

    _renderSlots(items) {
        const equipped = items.filter(i => i.equip_slot);

        EQUIP_SLOTS.forEach(slot => {
            const slotEl = this.el.querySelector(`[data-slot="${slot.key}"]`);
            if (!slotEl) return;

            const item = equipped.find(i => i.equip_slot === slot.key);
            slotEl.className = 'eq-slot';
            slotEl.dataset.action = 'slot-click';
            slotEl.dataset.popupTrigger = '';

            if (item) {
                slotEl.classList.add('filled', `rarity-${item.rarity}`);
            }
        });
    },

    _renderCost(items) {
        const equipped = items.filter(i => i.equip_slot);
        const currentCost = equipped.reduce((sum, i) => sum + (i.item_cost || 0), 0);
        const level = Store.get('user.level') || 1;
        const costStat = Store.get('stats.cost') || 0;
        const maxCost = level + costStat * 2;
        const pct = maxCost > 0 ? Math.min(100, (currentCost / maxCost) * 100) : 0;

        this.el.querySelector('#eq-cost-text').textContent = `${t('equip_cost')}: ${currentCost} / ${maxCost}`;
        this.el.querySelector('#eq-cost-fill').style.width = pct + '%';
    },

    _calcSetPoints(items) {
        const equipped = items.filter(i => i.equip_slot);
        const setPoints = {};
        equipped.forEach(item => {
            const sins = new Set();
            if (item.prefix_id) sins.add(item.prefix_id.toLowerCase());
            if (item.suffix_id) sins.add(item.suffix_id.toLowerCase());
            sins.forEach(sin => {
                setPoints[sin] = (setPoints[sin] || 0) + 1;
            });
        });
        // TODO: basic_sin 추가 (Store에서 가져오기)
        const basicSin = Store.get('user.basic_sin');
        if (basicSin) {
            const sin = basicSin.toLowerCase();
            setPoints[sin] = (setPoints[sin] || 0) + 1;
        }
        return setPoints;
    },

    _renderSetSummary(items) {
        const setPoints = this._calcSetPoints(items);
        const el = this.el.querySelector('#eq-set-summary');

        const SINS = [
            { key: 'wrath',    color: 'var(--color-wrath)' },
            { key: 'envy',     color: 'var(--color-envy)' },
            { key: 'greed',    color: 'var(--color-greed)' },
            { key: 'sloth',    color: 'var(--color-sloth)' },
            { key: 'gluttony', color: 'var(--color-gluttony)' },
            { key: 'lust',     color: 'var(--color-lust)' },
            { key: 'pride',    color: 'var(--color-pride)' },
        ];
        const MAX_POINTS = 6;
        const BREAKPOINTS = [2, 4, 6];

        let html = '';
        SINS.forEach(sin => {
            const pts = setPoints[sin.key] || 0;
            const active = pts > 0;

            let boxes = '';
            for (let i = 1; i <= MAX_POINTS; i++) {
                const filled = i <= pts;
                const isBp = BREAKPOINTS.includes(i);
                const bpEffect = isBp ? getSetBonus(sin.key, i) : null;

                boxes += `<div class="set-box ${filled ? 'filled' : ''} ${isBp ? 'bp' : ''}"
                    data-action="set-box-click"
                    data-sin="${sin.key}"
                    data-bp="${isBp ? i : 0}"
                    data-box-idx="${i}"
                    data-popup-trigger
                    style="${filled ? `border-color:${sin.color}` : ''}"
                    title="${isBp && bpEffect ? `${i}세트: ${bpEffect.effect_name}` : ''}">
                    <span class="set-box-bp">${i}</span>
                </div>`;
            }

            html += `
                <div class="set-row ${active ? '' : 'inactive'}">
                    <span class="set-label" style="color:${active ? sin.color : 'var(--text-muted)'}">${sinName(sin.key)}</span>
                    <div class="set-boxes">${boxes}</div>
                    <span class="set-pts">${pts > 0 ? pts : '0'}</span>
                </div>
            `;
        });

        el.innerHTML = html;
    },

    _onSetBoxClick(target) {
        const sin = target.dataset.sin;
        const bp = parseInt(target.dataset.bp);
        if (!bp) return; // 브레이크포인트 칸(2,4,6)만 팝업
        const effect = getSetBonus(sin, bp);

        const sinLabel = sinName(sin);

        const items = Store.get('inventory.items') || [];
        const setPoints = this._calcSetPoints(items);
        const pts = setPoints[sin] || 0;
        const isActive = pts >= bp;

        let html = `<div class="set-popup">`;
        html += `<div class="set-popup-title" style="color:var(--color-${sin})">${sinLabel} ${bp}세트</div>`;

        if (effect && effect.status === 'confirmed') {
            html += `<div class="set-popup-name ${isActive ? 'active' : ''}">${effect.effect_name}</div>`;
            html += `<div class="set-popup-desc">${effect.effect_desc}</div>`;
        } else if (effect && effect.status === 'pending') {
            html += `<div class="set-popup-name">${t('set_undecided')}</div>`;
            html += `<div class="set-popup-desc">${t('set_undecided_desc')}</div>`;
        } else {
            html += `<div class="set-popup-name">???</div>`;
        }

        html += `<div class="set-popup-status">${isActive ? '\u2726 ' + t('set_active') : `${t('set_need_points')}: ${bp} (${t('set_current')} ${pts})`}</div>`;
        html += `</div>`;

        Popup.showSingle(html, target, { pinned: true, position: 'right' });
    },

    _renderGrid(items) {
        const unequipped = items.filter(i => !i.equip_slot);
        const filtered = this._filterItems(unequipped);

        this.el.querySelector('#eq-unequip-count').textContent = `${t('equip_unequipped')} ${unequipped.length}${t('equip_count_unit')}`;

        const MAX_SLOTS = 21;
        const grid = this.el.querySelector('#eq-grid');
        if (filtered.length === 0) {
            grid.innerHTML = '<div class="eq-icon empty"></div>'.repeat(MAX_SLOTS);
            return;
        }
        const itemsHtml = filtered.map(item => {
            const slot = getEquipSlot(item.base_item_id);
            const slotInfo = EQUIP_SLOTS.find(s => s.key === slot);
            const icon = slotInfo ? slotInfo.icon : '?';

            return `
                <div class="eq-icon rarity-${item.rarity}"
                     data-action="item-click"
                     data-uid="${item.item_uid}"
                     data-popup-trigger
                     title="${this._getItemName(item)}">
                    <span class="eq-icon-part">${icon}</span>
                    <span class="eq-icon-level">+${item.item_level}</span>
                </div>
            `;
        }).join('');

        const emptyCount = Math.max(0, MAX_SLOTS - filtered.length);
        const emptyHtml = '<div class="eq-icon empty"></div>'.repeat(emptyCount);

        grid.innerHTML = itemsHtml + emptyHtml;
    },

    _renderInvCount(items) {
        const unequipped = items.filter(i => !i.equip_slot);
        this.el.querySelector('#eq-inv-count').textContent = `${unequipped.length} / 21`;
    },

    _filterItems(items) {
        switch (this._currentFilter) {
            case 'weapon':
                return items.filter(i => getEquipSlot(i.base_item_id) === 'weapon');
            case 'armor':
                return items.filter(i => getEquipSlot(i.base_item_id) !== 'weapon');
            default:
                return items;
        }
    },

    _setFilter(filter) {
        this._currentFilter = filter;
        this.el.querySelectorAll('.eq-filter').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        this._render();
    },

    // ── 팝업 ──

    _onItemClick(uid, anchorEl) {
        this._showComparePopup(uid, anchorEl, true);
    },

    _onSlotClick(slotKey, anchorEl) {
        const items = Store.get('inventory.items') || [];
        const item = items.find(i => i.equip_slot === slotKey);
        if (!item) return;

        const html = this._buildItemPopupHtml(item, t('popup_equipped')) +
            `<div class="popup-actions">
                <button class="btn" data-action="unequip" data-uid="${item.item_uid}">${t('unequip_btn')}</button>
                <button class="btn" data-action="sell" data-uid="${item.item_uid}">${t('sell_btn')}</button>
            </div>`;

        Popup.showSingle(html, anchorEl, { pinned: true, position: 'right' });
    },

    _showComparePopup(uid, anchorEl, pinned = false) {
        const items = Store.get('inventory.items') || [];
        const item = items.find(i => i.item_uid === uid);
        if (!item) return;

        const slot = getEquipSlot(item.base_item_id);
        const equipped = items.find(i => i.equip_slot === slot);

        const leftHtml = equipped
            ? `<div class="popup-header">\u25C0 ${t('popup_equipped')}</div>` + this._buildItemPopupHtml(equipped)
            : `<div class="popup-header">\u25C0 ${t('popup_equipped')}</div><div class="popup-info">${t('popup_empty')}</div>`;

        const rightHtml = `<div class="popup-header">${t('popup_unequipped')} \u25B6</div>` +
            this._buildItemPopupHtml(item, null, equipped) +
            `<div class="popup-actions">
                <button class="btn btn-primary" data-action="equip" data-uid="${item.item_uid}" data-slot="${slot}">${t('equip_btn')}</button>
                <button class="btn" data-action="sell" data-uid="${item.item_uid}">${t('sell_btn')}</button>
            </div>`;

        Popup.showCompare(leftHtml, rightHtml, anchorEl, { pinned, position: 'right' });
    },

    _buildItemPopupHtml(item, label, compareItem) {
        const name = this._getItemName(item);
        const rarity = rarityName(item.rarity);
        const opts = item.dynamic_options || {};
        const compareOpts = compareItem ? (compareItem.dynamic_options || {}) : null;

        let html = `
            <div class="popup-name rarity-${item.rarity}">${escapeHtml(name)}</div>
            <div class="popup-info">${rarity} \u00B7 Lv.${item.item_level} \u00B7 Cost ${item.item_cost}</div>
            <div class="popup-divider"></div>
        `;

        // 옵션
        const allKeys = new Set([...Object.keys(opts), ...(compareOpts ? Object.keys(compareOpts) : [])]);
        for (const key of allKeys) {
            const val = opts[key] || 0;
            const optLabel = OPTION_LABEL_KEYS[key] ? t(OPTION_LABEL_KEYS[key]) : key;
            let colorClass = 'neutral';

            if (compareOpts) {
                const cmpVal = compareOpts[key] || 0;
                if (val > cmpVal) colorClass = 'up';
                else if (val < cmpVal) colorClass = 'down';
            }

            html += `
                <div class="popup-option-row">
                    <span>${optLabel}</span>
                    <span class="popup-option-value ${colorClass}">+${val}</span>
                </div>
            `;
        }

        return html;
    },

    // ── API 액션 ──

    async _doEquip(uid, slot) {
        const result = await apiCall(2001, { item_uid: uid, equip_slot: slot });
        if (result?.success) {
            Popup.hide();
            await this._loadData();
        }
    },

    async _doUnequip(uid) {
        const result = await apiCall(2002, { item_uid: uid });
        if (result?.success) {
            Popup.hide();
            await this._loadData();
        }
    },

    async _doSell(uid) {
        const result = await apiCall(2004, { item_uid: uid });
        if (result?.success) {
            Store.set('user.gold', result.data.total_gold);
            const items = (Store.get('inventory.items') || []).filter(i => i.item_uid !== uid);
            Store.set('inventory.items', items);
            Popup.hide();
        }
    },

    async _doExpand() {
        const result = await apiCall(2005, {});
        if (result?.success) {
            Store.set('user.gold', result.data.total_gold);
            Store.set('user.max_inventory', result.data.max_inventory);
            this._render();
        }
    },

    // ── 유틸 ──

    _getItemName(item) {
        let name = getEquipName(item.base_item_id);
        if (item.prefix_id) name = `[${sinName(item.prefix_id)}] ${name}`;
        if (item.suffix_id) name += ` [${sinName(item.suffix_id)}]`;
        return name;
    },
};

export default EquipTab;
