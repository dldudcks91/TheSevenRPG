/**
 * TheSevenRPG — Skill Tab (스킬 탭)
 * 스킬 슬롯 4개 + 미장착 스킬 아이콘 그리드 + 비교 팝업
 * 장비 탭과 동일한 UI 패턴
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { getMonsterName } from '../../meta-data.js';
import Popup from '../../popup.js';

const SKILL_SLOTS = [
    { key: 1, label: 'S1' },
    { key: 2, label: 'S2' },
    { key: 3, label: 'S3' },
    { key: 4, label: 'S4' },
];

// 스킬 슬롯 해금 레벨
const SLOT_UNLOCK_LEVELS = { 1: 1, 2: 10, 3: 20, 4: 30 };

const SkillTab = {
    el: null,
    _unsubscribers: [],

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="tab-skill">
                <div class="skill-section">
                    <div class="skill-section-title">장착 스킬 슬롯</div>
                    <div class="skill-slots" id="sk-slots">
                        ${SKILL_SLOTS.map(s => {
                            const unlockLv = SLOT_UNLOCK_LEVELS[s.key];
                            return `
                                <div class="sk-slot" data-action="skill-slot-click" data-slot="${s.key}" data-popup-trigger>
                                    <span class="sk-slot-label">${s.label}</span>
                                    <span class="sk-slot-icon"></span>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>

                <div class="skill-section">
                    <div class="skill-section-title">
                        미장착 스킬
                        <span class="skill-count" id="sk-count">0개</span>
                    </div>
                    <div class="skill-grid" id="sk-grid"></div>
                </div>
            </div>
        `;

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._unsubscribers.push(
            Store.subscribe('collections.list', () => this._render()),
        );

        this._loadData();
    },

    unmount() {
        if (this._handleEvent) this.el.removeEventListener('pointerdown', this._handleEvent);
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
        Popup.hide();
    },

    async _loadData() {
        const result = await apiCall(2007, {});
        if (result?.success) {
            Store.set('collections.list', result.data.collections || result.data.cards || []);
        }
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'skill-slot-click':
                this._onSlotClick(parseInt(target.dataset.slot), target);
                break;
            case 'skill-icon-click':
                this._onSkillClick(target.dataset.idx, target);
                break;
            case 'equip-skill':
                this._doEquip(parseInt(target.dataset.idx));
                break;
            case 'unequip-skill':
                this._doUnequip(parseInt(target.dataset.idx));
                break;
        }
    },

    _render() {
        const collections = Store.get('collections.list') || [];
        const userLevel = Store.get('user.level') || 1;

        // 슬롯 렌더
        SKILL_SLOTS.forEach(slot => {
            const slotEl = this.el.querySelector(`[data-slot="${slot.key}"]`);
            if (!slotEl) return;

            const unlockLv = SLOT_UNLOCK_LEVELS[slot.key];
            const unlocked = userLevel >= unlockLv;
            const equipped = collections.find(c => c.skill_slot === slot.key);

            slotEl.className = 'sk-slot';
            slotEl.dataset.action = 'skill-slot-click';

            const iconEl = slotEl.querySelector('.sk-slot-icon');

            if (!unlocked) {
                slotEl.classList.add('locked');
                iconEl.textContent = '\u{1F512}';
                slotEl.title = `Lv.${unlockLv}에 해금`;
            } else if (equipped) {
                slotEl.classList.add('filled');
                iconEl.textContent = '\u26A1';
                slotEl.title = getMonsterName(equipped.monster_idx) + ' 스킬';
            } else {
                iconEl.textContent = '';
                slotEl.title = '빈 슬롯';
            }
        });

        // 미장착 스킬 그리드
        const unequipped = collections.filter(c => !c.skill_slot);
        this.el.querySelector('#sk-count').textContent = `${unequipped.length}개`;

        const grid = this.el.querySelector('#sk-grid');
        if (unequipped.length === 0) {
            grid.innerHTML = '<div class="skill-grid-empty">해금된 스킬이 없습니다</div>';
            return;
        }

        grid.innerHTML = unequipped.map(c => {
            const name = getMonsterName(c.monster_idx);
            const abbr = name.length >= 2 ? name.substring(0, 2) : name;
            return `
                <div class="sk-icon" data-action="skill-icon-click" data-idx="${c.monster_idx}" data-popup-trigger title="${name}">
                    <span class="sk-icon-bolt">\u26A1</span>
                    <span class="sk-icon-abbr">${abbr}</span>
                </div>
            `;
        }).join('');
    },

    _onSlotClick(slotKey, anchorEl) {
        const collections = Store.get('collections.list') || [];
        const equipped = collections.find(c => c.skill_slot === slotKey);
        const userLevel = Store.get('user.level') || 1;
        const unlockLv = SLOT_UNLOCK_LEVELS[slotKey];

        if (userLevel < unlockLv) {
            // 토스트 대신 간단히
            return;
        }

        if (!equipped) return;

        const name = getMonsterName(equipped.monster_idx);
        const html = `
            <div class="popup-header">S${slotKey}: ${name} 스킬</div>
            <div class="popup-name">\u26A1 ${name}</div>
            <div class="popup-info">도감 Lv.${equipped.collection_level}</div>
            <div class="popup-divider"></div>
            <div class="popup-info">카드 ${equipped.card_count}장</div>
            <div class="popup-actions">
                <button class="btn" data-action="unequip-skill" data-idx="${equipped.monster_idx}">해제</button>
            </div>
        `;
        Popup.showSingle(html, anchorEl, { pinned: true });
    },

    _onSkillClick(monsterIdx, anchorEl) {
        const collections = Store.get('collections.list') || [];
        const skill = collections.find(c => c.monster_idx == monsterIdx);
        if (!skill) return;

        // 현재 장착된 스킬 중 첫 번째 슬롯의 스킬과 비교
        const equippedInSlot = collections.find(c => c.skill_slot === 1);

        const name = getMonsterName(skill.monster_idx);

        const rightHtml = `
            <div class="popup-header">미장착 \u25B6</div>
            <div class="popup-name">\u26A1 ${name}</div>
            <div class="popup-info">도감 Lv.${skill.collection_level}</div>
            <div class="popup-divider"></div>
            <div class="popup-info">카드 ${skill.card_count}장</div>
            <div class="popup-actions">
                <button class="btn btn-primary" data-action="equip-skill" data-idx="${skill.monster_idx}">장착</button>
            </div>
        `;

        let leftHtml;
        if (equippedInSlot) {
            const eqName = getMonsterName(equippedInSlot.monster_idx);
            leftHtml = `
                <div class="popup-header">\u25C0 장착중 (S1)</div>
                <div class="popup-name">\u26A1 ${eqName}</div>
                <div class="popup-info">도감 Lv.${equippedInSlot.collection_level}</div>
                <div class="popup-divider"></div>
                <div class="popup-info">카드 ${equippedInSlot.card_count}장</div>
            `;
        } else {
            leftHtml = `
                <div class="popup-header">\u25C0 장착중</div>
                <div class="popup-info">비어있음</div>
            `;
        }

        Popup.showCompare(leftHtml, rightHtml, anchorEl, { pinned: true });
    },

    async _doEquip(monsterIdx) {
        const result = await apiCall(2008, { monster_idx: monsterIdx });
        if (result?.success) {
            Popup.hide();
            await this._loadData();
        }
    },

    async _doUnequip(monsterIdx) {
        const result = await apiCall(2009, { monster_idx: monsterIdx });
        if (result?.success) {
            Popup.hide();
            await this._loadData();
        }
    },
};

export default SkillTab;
