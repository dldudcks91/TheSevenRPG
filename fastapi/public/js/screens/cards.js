/**
 * TheSevenRPG — Cards Screen
 * 카드 도감, 카드-장비 장착/해제
 * API: 2007(조회), 2008(장착), 2009(해제)
 */
import { apiCall } from '../api.js';
import { Store } from '../store.js';
import { showLoading, hideLoading, escapeHtml } from '../utils.js';
import { getMonsterName, getEquipName } from '../meta-data.js';

const CardsScreen = {
    el: null,
    refs: {},
    _unsubscribers: [],
    _selectedCardUid: null,

    mount(el) {
        this.el = el;

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="cards-screen">
                    <div class="cards-header">
                        <button class="cards-back-btn" data-action="back">\u2190</button>
                        <span class="cards-header-title">카드 도감</span>
                        <span class="cards-count" id="cards-count">0장</span>
                    </div>

                    <div class="cards-grid-area">
                        <div class="cards-grid" id="cards-grid"></div>
                    </div>

                    <!-- 카드 상세 -->
                    <div class="card-detail-panel" id="card-detail">
                        <div class="card-detail-header">
                            <span class="card-detail-name" id="card-detail-name"></span>
                            <button class="card-detail-close" data-action="detail-close">\u2715</button>
                        </div>
                        <div class="card-detail-info" id="card-detail-info"></div>
                        <div class="card-detail-equip-info" id="card-detail-equip"></div>
                        <div class="card-detail-actions" id="card-detail-actions"></div>

                        <!-- 장비 선택 목록 -->
                        <div class="card-equip-list" id="card-equip-list">
                            <div class="card-equip-list-title">장착할 장비 선택:</div>
                            <div class="card-equip-items" id="card-equip-items"></div>
                        </div>
                    </div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        this.refs = {
            count: el.querySelector('#cards-count'),
            grid: el.querySelector('#cards-grid'),
            detailPanel: el.querySelector('#card-detail'),
            detailName: el.querySelector('#card-detail-name'),
            detailInfo: el.querySelector('#card-detail-info'),
            detailEquip: el.querySelector('#card-detail-equip'),
            detailActions: el.querySelector('#card-detail-actions'),
            equipList: el.querySelector('#card-equip-list'),
            equipItems: el.querySelector('#card-equip-items'),
        };

        this._handleEvent = this.handleEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._unsubscribers.push(
            Store.subscribe('cards.list', (cards) => {
                this._renderCards(cards);
            }),
        );

        this._selectedCardUid = null;
        this.loadData();
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
        this._selectedCardUid = null;
    },

    handleEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'back':
                window.location.hash = '#town';
                break;
            case 'select-card':
                this._selectCard(target.dataset.cardUid);
                break;
            case 'detail-close':
                this._closeDetail();
                break;
            case 'show-equip-list':
                this._showEquipList();
                break;
            case 'equip-to-item':
                this._doEquip(target.dataset.itemUid);
                break;
            case 'unequip-card':
                this._doUnequip(target.dataset.cardUid);
                break;
        }
    },

    async loadData() {
        showLoading();
        try {
            const result = await apiCall(2007, {});
            if (result?.success) {
                Store.set('cards.list', result.data.cards);
            }
        } finally {
            hideLoading();
        }
    },

    _renderCards(cards) {
        this.refs.count.textContent = `${(cards || []).length}장`;

        if (!cards || cards.length === 0) {
            this.refs.grid.innerHTML = '<div class="cards-empty">보유한 카드가 없습니다</div>';
            return;
        }

        this.refs.grid.innerHTML = cards.map(card => {
            const isSelected = card.card_uid === this._selectedCardUid;
            const isEquipped = !!card.equipped_item;

            return `
                <div class="card-item ${isSelected ? 'selected' : ''} ${isEquipped ? 'equipped' : ''}"
                     data-action="select-card"
                     data-card-uid="${card.card_uid}">
                    <span class="card-icon">\u{1F0CF}</span>
                    <span class="card-name">${escapeHtml(getMonsterName(card.monster_idx))}</span>
                    ${isEquipped ? '<span class="card-equipped-label">장착중</span>' : ''}
                </div>
            `;
        }).join('');
    },

    _selectCard(cardUid) {
        this._selectedCardUid = cardUid;

        const cards = Store.get('cards.list') || [];
        const card = cards.find(c => c.card_uid === cardUid);
        if (!card) return;

        // 그리드 선택 표시
        this.refs.grid.querySelectorAll('.card-item').forEach(el => {
            el.classList.toggle('selected', el.dataset.cardUid === cardUid);
        });

        this._showDetail(card);
    },

    _showDetail(card) {
        const isEquipped = !!card.equipped_item;

        this.refs.detailName.textContent = `${getMonsterName(card.monster_idx)} 카드`;
        this.refs.detailInfo.textContent = `카드 ID: ${card.card_uid.slice(0, 8)}...`;

        if (isEquipped) {
            this.refs.detailEquip.textContent = `장착된 장비: ${card.equipped_item_name || card.equipped_item.slice(0, 8) + '...'}`;
        } else {
            this.refs.detailEquip.textContent = '미장착';
        }

        let actions = '';
        if (isEquipped) {
            actions = `<button class="btn" data-action="unequip-card" data-card-uid="${card.card_uid}">카드 해제</button>`;
        } else {
            actions = `<button class="btn btn-primary" data-action="show-equip-list">장비에 장착</button>`;
        }
        this.refs.detailActions.innerHTML = actions;

        // 장비 목록 숨기기
        this.refs.equipList.classList.remove('show');

        this.refs.detailPanel.classList.add('show');
    },

    _closeDetail() {
        this._selectedCardUid = null;
        this.refs.detailPanel.classList.remove('show');
        this.refs.equipList.classList.remove('show');

        this.refs.grid.querySelectorAll('.card-item.selected').forEach(el => {
            el.classList.remove('selected');
        });
    },

    _showEquipList() {
        // 장착 중인 장비 목록 가져오기
        const items = (Store.get('inventory.items') || []).filter(i => i.equip_slot);

        if (items.length === 0) {
            this.refs.equipItems.innerHTML = '<div style="color:var(--text-muted);font-size:var(--font-size-sm);padding:var(--spacing-sm)">장착 중인 장비가 없습니다</div>';
        } else {
            this.refs.equipItems.innerHTML = items.map(item => `
                <div class="card-equip-item" data-action="equip-to-item" data-item-uid="${item.item_uid}">
                    <span>${escapeHtml(getEquipName(item.base_item_id))} [${item.equip_slot}]</span>
                    <span style="color:var(--text-muted)">+${item.item_level}</span>
                </div>
            `).join('');
        }

        this.refs.equipList.classList.add('show');
    },

    async _doEquip(itemUid) {
        if (!this._selectedCardUid) return;

        const result = await apiCall(2008, {
            card_uid: this._selectedCardUid,
            item_uid: itemUid,
        });

        if (result?.success) {
            await this.loadData();
            this._closeDetail();
        }
    },

    async _doUnequip(cardUid) {
        const result = await apiCall(2009, { card_uid: cardUid });

        if (result?.success) {
            await this.loadData();
            this._closeDetail();
        }
    },
};

export default CardsScreen;
