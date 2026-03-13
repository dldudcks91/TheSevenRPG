/**
 * TheSevenRPG — Inventory Screen
 * 장비 목록 조회, 장착/해제, 판매, 강화
 * API: 2001(장착), 2002(해제), 2003(조회), 2004(판매), 2005(확장), 2006(강화)
 */
import { apiCall } from '../api.js';
import { Store } from '../store.js';
import { showLoading, hideLoading, formatGold, escapeHtml } from '../utils.js';

// 장착 슬롯 정의
const EQUIP_SLOTS = [
    { key: 'weapon',  icon: '\u2694', label: '무기' },
    { key: 'armor',   icon: '\u{1F6E1}', label: '갑옷' },
    { key: 'helmet',  icon: '\u{1FA96}', label: '투구' },
    { key: 'gloves',  icon: '\u{1F9E4}', label: '장갑' },
    { key: 'boots',   icon: '\u{1F462}', label: '신발' },
];

// 등급 한글 표시
const RARITY_LABEL = {
    normal: '일반',
    magic: '매직',
    rare: '레어',
    unique: '유니크',
};

// 옵션 한글 표시
const OPTION_LABEL = {
    atk: '공격력',
    def: '방어력',
    hp: 'HP',
    atk_speed: '공격속도',
    accuracy: '명중',
    evasion: '회피',
    crit_rate: '치명타확률',
    crit_damage: '치명타데미지',
};

const InventoryScreen = {
    el: null,
    refs: {},
    _unsubscribers: [],
    _selectedItemUid: null,

    mount(el) {
        this.el = el;

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="inventory-screen">
                    <!-- 헤더 -->
                    <div class="inv-header">
                        <button class="inv-back-btn" data-action="back">\u2190</button>
                        <span class="inv-title">인벤토리</span>
                        <span class="inv-gold" id="inv-gold">0 G</span>
                    </div>

                    <!-- 장착 슬롯 -->
                    <div class="inv-equip-area">
                        <div class="inv-equip-label">장착 장비</div>
                        <div class="inv-equip-slots" id="inv-equip-slots">
                            ${EQUIP_SLOTS.map(s => `
                                <div class="equip-slot" data-action="slot-click" data-slot="${s.key}">
                                    <span class="slot-icon">${s.icon}</span>
                                    <span class="slot-label">${s.label}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- 탭 -->
                    <div class="inv-tab-bar">
                        <button class="inv-tab active" data-action="tab" data-tab="all">전체</button>
                        <button class="inv-tab" data-action="tab" data-tab="weapon">무기</button>
                        <button class="inv-tab" data-action="tab" data-tab="armor">방어구</button>
                        <button class="inv-tab" data-action="tab" data-tab="equipped">장착중</button>
                    </div>

                    <!-- 아이템 그리드 -->
                    <div class="inv-item-area">
                        <div class="inv-item-grid" id="inv-item-grid"></div>
                    </div>

                    <!-- 아이템 상세 -->
                    <div class="inv-detail-panel" id="inv-detail">
                        <div class="detail-header">
                            <span class="detail-name" id="detail-name"></span>
                            <button class="detail-close" data-action="detail-close">\u2715</button>
                        </div>
                        <div class="detail-info" id="detail-info"></div>
                        <div class="detail-options" id="detail-options"></div>
                        <div class="detail-actions" id="detail-actions"></div>
                    </div>

                    <!-- 하단 인벤 정보 -->
                    <div class="inv-footer">
                        <span id="inv-count">0 / 100</span>
                        <button class="inv-expand-btn" data-action="expand">인벤 확장</button>
                    </div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        // refs 캐싱
        this.refs = {
            gold: el.querySelector('#inv-gold'),
            equipSlots: el.querySelector('#inv-equip-slots'),
            itemGrid: el.querySelector('#inv-item-grid'),
            detailPanel: el.querySelector('#inv-detail'),
            detailName: el.querySelector('#detail-name'),
            detailInfo: el.querySelector('#detail-info'),
            detailOptions: el.querySelector('#detail-options'),
            detailActions: el.querySelector('#detail-actions'),
            invCount: el.querySelector('#inv-count'),
        };

        // 이벤트 위임
        this._handleEvent = this.handleEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        // Store 구독
        this._unsubscribers.push(
            Store.subscribe('user.gold', (gold) => {
                this.refs.gold.textContent = formatGold(gold);
            }),
            Store.subscribe('inventory.items', (items) => {
                this._renderItems(items);
                this._renderEquipSlots(items);
                this._renderInvCount(items);
            }),
        );

        // 상태 초기화
        this._selectedItemUid = null;
        this._currentTab = 'all';

        this.loadData();
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
        this._selectedItemUid = null;
    },

    handleEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;

        switch (action) {
            case 'back':
                window.location.hash = '#town';
                break;
            case 'tab':
                this._switchTab(target.dataset.tab);
                break;
            case 'select-item':
                this._selectItem(target.dataset.itemUid);
                break;
            case 'slot-click':
                this._onSlotClick(target.dataset.slot);
                break;
            case 'detail-close':
                this._closeDetail();
                break;
            case 'equip':
                this._doEquip(target.dataset.itemUid, target.dataset.slot);
                break;
            case 'unequip':
                this._doUnequip(target.dataset.itemUid);
                break;
            case 'sell':
                this._doSell(target.dataset.itemUid);
                break;
            case 'enhance':
                this._doEnhance(target.dataset.itemUid);
                break;
            case 'expand':
                this._doExpand();
                break;
        }
    },

    // ── 데이터 로드 ──
    async loadData() {
        showLoading();
        try {
            const result = await apiCall(2003, {});
            if (result?.success) {
                Store.set('inventory.items', result.data.items);
            }
        } finally {
            hideLoading();
        }
    },

    // ── 탭 전환 ──
    _switchTab(tab) {
        this._currentTab = tab;

        // 탭 버튼 활성화
        this.el.querySelectorAll('.inv-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tab);
        });

        // 아이템 다시 렌더
        const items = Store.get('inventory.items') || [];
        this._renderItems(items);
    },

    // ── 아이템 필터 ──
    _filterItems(items) {
        switch (this._currentTab) {
            case 'weapon':
                return items.filter(i => this._isWeapon(i));
            case 'armor':
                return items.filter(i => !this._isWeapon(i));
            case 'equipped':
                return items.filter(i => i.equip_slot);
            default:
                return items;
        }
    },

    _isWeapon(item) {
        // base_item_id 10xxxx = weapon
        return item.base_item_id >= 100000 && item.base_item_id < 200000;
    },

    // ── 아이템 그리드 렌더 ──
    _renderItems(items) {
        const filtered = this._filterItems(items || []);

        if (filtered.length === 0) {
            this.refs.itemGrid.innerHTML = '<div class="inv-item-empty">아이템이 없습니다</div>';
            return;
        }

        this.refs.itemGrid.innerHTML = filtered.map(item => {
            const name = this._getItemName(item);
            const isSelected = item.item_uid === this._selectedItemUid;
            const isEquipped = !!item.equip_slot;
            const optionStr = this._getOptionSummary(item);

            return `
                <div class="item-card rarity-${item.rarity} ${isSelected ? 'selected' : ''} ${isEquipped ? 'equipped' : ''}"
                     data-action="select-item"
                     data-item-uid="${item.item_uid}">
                    <div class="item-card-name">${escapeHtml(name)}</div>
                    <div class="item-card-info">
                        <span>${RARITY_LABEL[item.rarity] || item.rarity}</span>
                        <span>+${item.item_level}</span>
                    </div>
                    ${optionStr ? `<div class="item-card-options">${escapeHtml(optionStr)}</div>` : ''}
                </div>
            `;
        }).join('');
    },

    // ── 장착 슬롯 렌더 ──
    _renderEquipSlots(items) {
        const equipped = (items || []).filter(i => i.equip_slot);

        EQUIP_SLOTS.forEach(slot => {
            const slotEl = this.refs.equipSlots.querySelector(`[data-slot="${slot.key}"]`);
            if (!slotEl) return;

            const item = equipped.find(i => i.equip_slot === slot.key);

            // 기존 클래스 정리
            slotEl.className = 'equip-slot';
            slotEl.dataset.action = 'slot-click';
            slotEl.dataset.slot = slot.key;

            // 기존 아이템 이름 요소 제거
            const oldName = slotEl.querySelector('.slot-item-name');
            if (oldName) oldName.remove();

            if (item) {
                slotEl.classList.add('filled', `rarity-${item.rarity}`);
                const nameEl = document.createElement('span');
                nameEl.className = 'slot-item-name';
                nameEl.textContent = this._getItemName(item);
                slotEl.appendChild(nameEl);
            }
        });
    },

    // ── 인벤 카운트 ──
    _renderInvCount(items) {
        const count = (items || []).length;
        const max = Store.get('user.max_inventory') || 100;
        this.refs.invCount.textContent = `${count} / ${max}`;
    },

    // ── 아이템 선택 → 상세 패널 ──
    _selectItem(itemUid) {
        this._selectedItemUid = itemUid;

        const items = Store.get('inventory.items') || [];
        const item = items.find(i => i.item_uid === itemUid);
        if (!item) return;

        // 그리드 선택 표시 갱신
        this.refs.itemGrid.querySelectorAll('.item-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.itemUid === itemUid);
        });

        this._showDetail(item);
    },

    _showDetail(item) {
        const name = this._getItemName(item);
        const isEquipped = !!item.equip_slot;

        // 이름
        this.refs.detailName.textContent = name;
        this.refs.detailName.className = `detail-name rarity-${item.rarity}`;

        // 정보
        this.refs.detailInfo.textContent =
            `${RARITY_LABEL[item.rarity] || item.rarity} · Lv.${item.item_level} · Cost ${item.item_cost}` +
            (isEquipped ? ` · [${this._getSlotLabel(item.equip_slot)}]` : '');

        // 옵션
        const opts = item.dynamic_options || {};
        this.refs.detailOptions.innerHTML = Object.entries(opts).map(([k, v]) => `
            <div class="detail-option-row">
                <span>${OPTION_LABEL[k] || k}</span>
                <span class="option-value">+${v}</span>
            </div>
        `).join('');

        // 액션 버튼
        let actions = '';
        if (isEquipped) {
            actions += `<button class="btn" data-action="unequip" data-item-uid="${item.item_uid}">해제</button>`;
        } else {
            // 장착 가능 슬롯 결정
            const slot = this._getDefaultSlot(item);
            actions += `<button class="btn btn-primary" data-action="equip" data-item-uid="${item.item_uid}" data-slot="${slot}">장착</button>`;
            actions += `<button class="btn" data-action="sell" data-item-uid="${item.item_uid}">판매</button>`;
        }
        actions += `<button class="btn" data-action="enhance" data-item-uid="${item.item_uid}">강화</button>`;

        this.refs.detailActions.innerHTML = actions;

        // 패널 표시
        this.refs.detailPanel.classList.add('show');
    },

    _closeDetail() {
        this._selectedItemUid = null;
        this.refs.detailPanel.classList.remove('show');

        // 선택 표시 해제
        this.refs.itemGrid.querySelectorAll('.item-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
    },

    _onSlotClick(slotKey) {
        const items = Store.get('inventory.items') || [];
        const item = items.find(i => i.equip_slot === slotKey);
        if (item) {
            this._selectItem(item.item_uid);
        }
    },

    // ── API 액션들 ──

    async _doEquip(itemUid, slot) {
        const result = await apiCall(2001, { item_uid: itemUid, equip_slot: slot });
        if (result?.success) {
            await this.loadData();
            this._closeDetail();
        }
    },

    async _doUnequip(itemUid) {
        const result = await apiCall(2002, { item_uid: itemUid });
        if (result?.success) {
            await this.loadData();
            this._closeDetail();
        }
    },

    async _doSell(itemUid) {
        const result = await apiCall(2004, { item_uid: itemUid });
        if (result?.success) {
            Store.set('user.gold', result.data.total_gold);
            // 인벤토리에서 제거
            const items = (Store.get('inventory.items') || [])
                .filter(i => i.item_uid !== itemUid);
            Store.set('inventory.items', items);
            this._closeDetail();
        }
    },

    async _doEnhance(itemUid) {
        const result = await apiCall(2006, { item_uid: itemUid });
        if (result?.success) {
            Store.set('user.gold', result.data.total_gold);
            // 해당 아이템 갱신
            const items = (Store.get('inventory.items') || []).map(i => {
                if (i.item_uid === itemUid) {
                    return { ...i, item_level: result.data.item_level, dynamic_options: result.data.dynamic_options };
                }
                return i;
            });
            Store.set('inventory.items', items);
            // 상세 패널 갱신
            const updated = items.find(i => i.item_uid === itemUid);
            if (updated) this._showDetail(updated);
        }
    },

    async _doExpand() {
        const result = await apiCall(2005, {});
        if (result?.success) {
            Store.set('user.gold', result.data.total_gold);
            Store.set('user.max_inventory', result.data.max_inventory);
            const items = Store.get('inventory.items') || [];
            this._renderInvCount(items);
        }
    },

    // ── 유틸 ──

    _getItemName(item) {
        // base_item_id로 메타데이터 이름 매핑 (추후 개선)
        // 현재는 suffix/set 포함 간단 표시
        let name = `장비 #${item.base_item_id}`;
        if (item.suffix_id) name += ` [${item.suffix_id}]`;
        return name;
    },

    _getOptionSummary(item) {
        const opts = item.dynamic_options || {};
        const entries = Object.entries(opts);
        if (entries.length === 0) return '';
        return entries.map(([k, v]) => `${OPTION_LABEL[k] || k}+${v}`).join(' ');
    },

    _getSlotLabel(slotKey) {
        const slot = EQUIP_SLOTS.find(s => s.key === slotKey);
        return slot ? slot.label : slotKey;
    },

    _getDefaultSlot(item) {
        if (this._isWeapon(item)) return 'weapon';
        // 방어구는 base_item_id 기반 추정 (추후 메타데이터 매핑)
        const id = item.base_item_id;
        if (id >= 200000 && id < 300000) return 'armor';
        if (id >= 300000 && id < 400000) return 'helmet';
        if (id >= 400000 && id < 500000) return 'gloves';
        if (id >= 500000 && id < 600000) return 'boots';
        return 'armor'; // fallback
    },
};

export default InventoryScreen;
