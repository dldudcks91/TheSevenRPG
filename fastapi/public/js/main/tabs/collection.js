/**
 * TheSevenRPG — Collection Tab (도감 탭)
 * 챕터별 도감 그룹, 카드 수집 현황, 그룹 패시브 (열람 전용)
 */
import { Store } from '../../store.js';
import { getMonsterName, getChapters } from '../../meta-data.js';
import { t } from '../../i18n/index.js';
import Popup from '../../popup.js';

const CollectionTab = {
    el: null,
    _unsubscribers: [],
    _selectedChapter: 1,

    mount(el) {
        this.el = el;

        const chapters = getChapters();

        el.innerHTML = `
            <div class="tab-collection">
                <div class="coll-chapter-bar">
                    ${chapters.map(ch => `
                        <button class="coll-chapter-btn ${ch.id === 1 ? 'active' : ''}"
                                data-action="chapter" data-chapter="${ch.id}">
                            ${ch.id}장
                        </button>
                    `).join('')}
                </div>
                <div class="coll-groups" id="coll-groups"></div>
            </div>
        `;

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._unsubscribers.push(
            Store.subscribe('collections.list', () => this._render()),
        );

        this._selectedChapter = 1;
        this._render();
    },

    unmount() {
        if (this._handleEvent) this.el.removeEventListener('pointerdown', this._handleEvent);
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
        Popup.hide();
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'chapter':
                this._selectChapter(parseInt(target.dataset.chapter));
                break;
            case 'card-click':
                this._onCardClick(parseInt(target.dataset.idx), target);
                break;
        }
    },

    _selectChapter(chapterId) {
        this._selectedChapter = chapterId;
        this.el.querySelectorAll('.coll-chapter-btn').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.chapter) === chapterId);
        });
        this._render();
    },

    _render() {
        const collections = Store.get('collections.list') || [];
        const groupsEl = this.el.querySelector('#coll-groups');

        // 현재 챕터의 몬스터들을 그룹으로 나누기
        // 간단하게: 챕터별로 모든 수집 카드를 표시
        const chapterCollections = collections.filter(c => {
            // monster_idx로 챕터 판별 (간이: 1~100=Ch1, 101~200=Ch2 등)
            // 실제로는 메타데이터에서 매핑해야 하지만, 현재는 전체 표시
            return true;
        });

        if (chapterCollections.length === 0) {
            groupsEl.innerHTML = `
                <div class="coll-empty">
                    ${t('collection_empty')}
                </div>
            `;
            return;
        }

        groupsEl.innerHTML = `
            <div class="coll-group">
                <div class="coll-group-header">
                    <span>${t('collection_status')}</span>
                    <span class="coll-group-count">${chapterCollections.length}종</span>
                </div>
                <div class="coll-card-grid">
                    ${chapterCollections.map(c => {
                        const name = getMonsterName(c.monster_idx);
                        return `
                            <div class="coll-card" data-action="card-click" data-idx="${c.monster_idx}" data-popup-trigger>
                                <span class="coll-card-icon">\u{1F0CF}</span>
                                <span class="coll-card-name">${name}</span>
                                <span class="coll-card-lv">Lv.${c.collection_level}</span>
                                <span class="coll-card-count">${c.card_count}장</span>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    },

    _onCardClick(monsterIdx, anchorEl) {
        const collections = Store.get('collections.list') || [];
        const card = collections.find(c => c.monster_idx === monsterIdx);
        if (!card) return;

        const name = getMonsterName(card.monster_idx);

        const html = `
            <div class="popup-name">${name}</div>
            <div class="popup-divider"></div>
            <div class="popup-info">도감 Lv.${card.collection_level}</div>
            <div class="popup-info">카드: ${card.card_count}장</div>
            <div class="popup-divider"></div>
            <div class="popup-option-row">
                <span>Lv.1</span>
                <span class="popup-option-value ${card.collection_level >= 1 ? 'up' : ''}">${t('collection_skill_unlock')}</span>
            </div>
            <div class="popup-option-row">
                <span>Lv.2</span>
                <span class="popup-option-value ${card.collection_level >= 2 ? 'up' : ''}">${t('collection_prob_up')}</span>
            </div>
            <div class="popup-option-row">
                <span>Lv.3</span>
                <span class="popup-option-value ${card.collection_level >= 3 ? 'up' : ''}">${t('collection_stat_up')}</span>
            </div>
        `;

        Popup.showSingle(html, anchorEl, { pinned: true });
    },
};

export default CollectionTab;
