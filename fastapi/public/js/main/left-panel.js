/**
 * TheSevenRPG — Left Panel Component
 * 5탭 전환: 스탯 / 장비 / 아이템 / 스킬 / 도감
 */
import StatTab from './tabs/stat.js';
import EquipTab from './tabs/equip.js';
import ItemTab from './tabs/item.js';
import SkillTab from './tabs/skill.js';
import CollectionTab from './tabs/collection.js';
import { t } from '../i18n/index.js';

const TAB_MODULES = {
    stat: StatTab,
    equip: EquipTab,
    item: ItemTab,
    skill: SkillTab,
    collection: CollectionTab,
};

const TABS = [
    { key: 'stat',       icon: '\u{1F4CA}', labelKey: 'tab_stat' },
    { key: 'equip',      icon: '\u2694',    labelKey: 'tab_equip' },
    { key: 'item',       icon: '\u{1F392}', labelKey: 'tab_item' },
    { key: 'skill',      icon: '\u26A1',    labelKey: 'tab_skill' },
    { key: 'collection', icon: '\u{1F4D6}', labelKey: 'tab_collection' },
];

const LeftPanel = {
    el: null,
    _activeTab: null,
    _activeModule: null,

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="left-panel">
                <div class="left-panel-tabs" id="lp-tabs">
                    ${TABS.map(tab => `
                        <button class="lp-tab ${tab.key === 'stat' ? 'active' : ''}"
                                data-action="tab" data-tab="${tab.key}"
                                title="${t(tab.labelKey)}">
                            <span class="lp-tab-icon">${tab.icon}</span>
                            <span class="lp-tab-label">${t(tab.labelKey)}</span>
                        </button>
                    `).join('')}
                </div>
                <div class="left-panel-content" id="lp-content"></div>
            </div>
        `;

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        // 기본 탭 마운트
        this._switchTab('stat');
    },

    unmount() {
        if (this._activeModule && this._activeModule.unmount) {
            this._activeModule.unmount();
        }
        this._activeModule = null;
        this._activeTab = null;
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        if (target.dataset.action === 'tab') {
            this._switchTab(target.dataset.tab);
        }
    },

    _switchTab(tabKey) {
        if (tabKey === this._activeTab) return;

        // 현재 탭 언마운트
        if (this._activeModule && this._activeModule.unmount) {
            this._activeModule.unmount();
        }

        this._activeTab = tabKey;

        // 탭 버튼 활성화
        this.el.querySelectorAll('.lp-tab').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabKey);
        });

        // 탭 내용 전환
        const content = this.el.querySelector('#lp-content');
        content.innerHTML = '';

        const module = TAB_MODULES[tabKey];
        if (module) {
            this._activeModule = module;
            module.mount(content);
        } else {
            this._activeModule = null;
            const tab = TABS.find(tab => tab.key === tabKey);
            content.innerHTML = `<div class="lp-tab-placeholder">${t(tab.labelKey)} ${t('tab_preparing')}</div>`;
        }
    },
};

export default LeftPanel;
