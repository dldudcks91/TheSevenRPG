/**
 * TheSevenRPG — Equip Tab (장비 탭)
 * 장착 슬롯 5개 + 코스트 바 + 세트 요약 + 아이콘 그리드 + 비교 팝업
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { formatGold, escapeHtml } from '../../utils.js';
import { getEquipName, getEquipSlot } from '../../meta-data.js';
import Popup from '../../popup.js';

const EQUIP_SLOTS = [
    { key: 'weapon',  icon: '\u2694',     label: '무기' },
    { key: 'armor',   icon: '\u{1F6E1}',  label: '갑옷' },
    { key: 'helmet',  icon: '\u{1FA96}',  label: '투구' },
    { key: 'gloves',  icon: '\u{1F9E4}',  label: '장갑' },
    { key: 'boots',   icon: '\u{1F462}',  label: '신발' },
];

const RARITY_LABEL = { normal: '일반', magic: '매직', rare: '레어', craft: '크래프트', unique: '유니크' };

const OPTION_LABEL = {
    atk: '공격력', def: '방어력', hp: 'HP', atk_speed: '공격속도',
    accuracy: '명중', evasion: '회피', crit_rate: '치명타확률', crit_damage: '치명타데미지',
};

const EquipTab = {
    el: null,
    _unsubscribers: [],
    _currentFilter: 'all',

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="tab-equip">
                <div class="equip-section">
                    <div class="equip-section-title">장착 장비</div>
                    <div class="equip-slots" id="eq-slots">
                        ${EQUIP_SLOTS.map(s => `
                            <div class="eq-slot" data-action="slot-click" data-slot="${s.key}" data-popup-trigger>
                                <span class="eq-slot-icon">${s.icon}</span>
                                <span class="eq-slot-label">${s.label}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="equip-cost-bar">
                    <span class="equip-cost-text" id="eq-cost-text">코스트: 0 / 0</span>
                    <div class="equip-cost-gauge">
                        <div class="equip-cost-fill" id="eq-cost-fill" style="width:0%"></div>
                    </div>
                </div>

                <div class="equip-set-summary" id="eq-set-summary"></div>

                <div class="equip-section">
                    <div class="equip-filter-bar">
                        <span class="equip-count" id="eq-unequip-count">미장착 0개</span>
                        <div class="equip-filters">
                            <button class="eq-filter active" data-action="filter" data-filter="all">전체</button>
                            <button class="eq-filter" data-action="filter" data-filter="weapon">무기</button>
                            <button class="eq-filter" data-action="filter" data-filter="armor">방어구</button>
                        </div>
                    </div>
                    <div class="equip-grid" id="eq-grid"></div>
                </div>

                <div class="equip-footer">
                    <span id="eq-inv-count">0 / 100</span>
                    <button class="btn" data-action="expand" style="font-size:var(--font-size-xs)">인벤 확장</button>
                </div>
            </div>
        `;

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        // 호버 이벤트 (비교 팝업)
        this._handleHover = this._onHover.bind(this);
        this._handleHoverOut = this._onHoverOut.bind(this);
        el.addEventListener('pointerenter', this._handleHover, true);
        el.addEventListener('pointerleave', this._handleHoverOut, true);

        this._unsubscribers.push(
            Store.subscribe('inventory.items', () => this._render()),
        );

        this._currentFilter = 'all';
        this._loadData();
    },

    unmount() {
        if (this._handleEvent) this.el.removeEventListener('pointerdown', this._handleEvent);
        if (this._handleHover) this.el.removeEventListener('pointerenter', this._handleHover, true);
        if (this._handleHoverOut) this.el.removeEventListener('pointerleave', this._handleHoverOut, true);
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
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
            case 'expand':
                this._doExpand();
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
        }
    },

    _onHover(e) {
        const target = e.target.closest('[data-action="item-hover"]');
        if (!target || Popup.isPinned()) return;
        this._showComparePopup(target.dataset.uid, target);
    },

    _onHoverOut(e) {
        const target = e.target.closest('[data-action="item-hover"]');
        if (!target || Popup.isPinned()) return;
        Popup.hide();
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

        this.el.querySelector('#eq-cost-text').textContent = `코스트: ${currentCost} / ${maxCost}`;
        this.el.querySelector('#eq-cost-fill').style.width = pct + '%';
    },

    _renderSetSummary(items) {
        const equipped = items.filter(i => i.equip_slot);
        // 세트 포인트 계산 (접두/접미에서 죄종 추출)
        const setPoints = {};
        equipped.forEach(item => {
            if (item.set_id) {
                setPoints[item.set_id] = (setPoints[item.set_id] || 0) + 1;
            }
        });

        const el = this.el.querySelector('#eq-set-summary');
        const entries = Object.entries(setPoints).filter(([, v]) => v > 0);
        if (entries.length === 0) {
            el.textContent = '';
        } else {
            el.textContent = '세트: ' + entries.map(([k, v]) => `${k}${v}`).join(' ');
        }
    },

    _renderGrid(items) {
        const unequipped = items.filter(i => !i.equip_slot);
        const filtered = this._filterItems(unequipped);

        this.el.querySelector('#eq-unequip-count').textContent = `미장착 ${unequipped.length}개`;

        const grid = this.el.querySelector('#eq-grid');
        if (filtered.length === 0) {
            const MIN_EMPTY = 20;
            grid.innerHTML = '<div class="eq-icon empty"></div>'.repeat(MIN_EMPTY);
            return;
        }

        const MIN_SLOTS = 20;
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

        const emptyCount = Math.max(0, MIN_SLOTS - filtered.length);
        const emptyHtml = '<div class="eq-icon empty"></div>'.repeat(emptyCount);

        grid.innerHTML = itemsHtml + emptyHtml;

        // 호버 이벤트 재연결
        grid.querySelectorAll('[data-action="item-click"]').forEach(el => {
            el.dataset.action = 'item-click';
            el.setAttribute('data-action', 'item-hover');
            // pointerdown은 item-click으로 처리 (별도)
        });
    },

    _renderInvCount(items) {
        const max = Store.get('user.max_inventory') || 100;
        this.el.querySelector('#eq-inv-count').textContent = `${items.length} / ${max}`;
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

        const html = this._buildItemPopupHtml(item, '착용중') +
            `<div class="popup-actions">
                <button class="btn" data-action="unequip" data-uid="${item.item_uid}">해제</button>
                <button class="btn" data-action="sell" data-uid="${item.item_uid}">판매</button>
            </div>`;

        Popup.showSingle(html, anchorEl, { pinned: true });
    },

    _showComparePopup(uid, anchorEl, pinned = false) {
        const items = Store.get('inventory.items') || [];
        const item = items.find(i => i.item_uid === uid);
        if (!item) return;

        const slot = getEquipSlot(item.base_item_id);
        const equipped = items.find(i => i.equip_slot === slot);

        const leftHtml = equipped
            ? `<div class="popup-header">\u25C0 착용중</div>` + this._buildItemPopupHtml(equipped)
            : `<div class="popup-header">\u25C0 착용중</div><div class="popup-info">비어있음</div>`;

        const rightHtml = `<div class="popup-header">미착용 \u25B6</div>` +
            this._buildItemPopupHtml(item, null, equipped) +
            `<div class="popup-actions">
                <button class="btn btn-primary" data-action="equip" data-uid="${item.item_uid}" data-slot="${slot}">장착</button>
                <button class="btn" data-action="sell" data-uid="${item.item_uid}">판매</button>
            </div>`;

        Popup.showCompare(leftHtml, rightHtml, anchorEl, { pinned });
    },

    _buildItemPopupHtml(item, label, compareItem) {
        const name = this._getItemName(item);
        const rarity = RARITY_LABEL[item.rarity] || item.rarity;
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
            const label = OPTION_LABEL[key] || key;
            let colorClass = 'neutral';

            if (compareOpts) {
                const cmpVal = compareOpts[key] || 0;
                if (val > cmpVal) colorClass = 'up';
                else if (val < cmpVal) colorClass = 'down';
            }

            html += `
                <div class="popup-option-row">
                    <span>${label}</span>
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
        if (item.prefix_id) name = `${item.prefix_id} ${name}`;
        if (item.suffix_id) name += ` [${item.suffix_id}]`;
        return name;
    },
};

export default EquipTab;
