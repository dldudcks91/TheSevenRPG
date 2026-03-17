/**
 * TheSevenRPG — Town View (우측 마을 모드)
 * 배경 이미지 위에 NPC 핫스팟 배치
 * 출정문 클릭 → 스테이지 선택 팝업 (오버레이)
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { showLoading, hideLoading } from '../../utils.js';
import { getChapters, getStagesByChapter } from '../../meta-data.js';
import MainScreen from '../../main.js';

const NPC_LIST = [
    // 성문: 상단 중앙 철창문
    { key: 'gate',  label: '출정문', unlockChapter: 0, left: 35, top: 8,  right: 65, bottom: 42, view: 'stage-select' },
    // 대장간: 좌측 하단 화로+모루
    { key: 'forge', label: '대장간', unlockChapter: 1, left: 3,  top: 50, right: 25, bottom: 95, view: 'forge' },
    // 상인: 중앙 하단 가판대+천막
    { key: 'shop',  label: '상인',   unlockChapter: 3, left: 36, top: 58, right: 64, bottom: 96, view: 'shop' },
    // 게시판: 우측 하단 벽면 프레임
    { key: 'quest', label: '게시판', unlockChapter: 2, left: 79, top: 57, right: 97, bottom: 95, view: 'quest' },
];

const TownView = {
    el: null,
    _selectedChapter: 1,

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="town-view">
                <div class="tv-bg">
                    ${NPC_LIST.map(npc => `
                        <div class="tv-hotspot" data-action="npc-click" data-npc="${npc.key}" data-view="${npc.view}"
                             data-unlock="${npc.unlockChapter}"
                             style="left:${npc.left}%;top:${npc.top}%;width:${npc.right - npc.left}%;height:${npc.bottom - npc.top}%">
                            <span class="tv-hotspot-label">${npc.label}</span>
                        </div>
                    `).join('')}
                </div>

                <!-- 스테이지 선택 팝업 오버레이 -->
                <div class="tv-stage-overlay" id="tv-stage-overlay">
                    <div class="tv-stage-popup">
                        <div class="tv-stage-popup-header">
                            <span class="tv-stage-popup-title">스테이지 선택</span>
                            <button class="tv-stage-popup-close" data-action="close-stage">\u2715</button>
                        </div>
                        <div class="tv-stage-popup-chapters" id="tv-popup-chapters"></div>
                        <div class="tv-stage-popup-info" id="tv-popup-info"></div>
                        <div class="tv-stage-popup-list" id="tv-popup-list"></div>
                    </div>
                </div>
            </div>
        `;

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._updateUnlockState();
    },

    unmount() {
        if (this._handleEvent && this.el) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'npc-click':
                this._onNpcClick(target);
                break;
            case 'close-stage':
                this._closeStagePopup();
                break;
            case 'chapter':
                this._selectChapter(parseInt(target.dataset.chapter));
                break;
            case 'enter-stage':
                this._enterStage(parseInt(target.dataset.stageId));
                break;
        }
    },

    _onNpcClick(target) {
        const unlockChapter = parseInt(target.dataset.unlock);
        const currentStage = Store.get('user.current_stage') || 101;
        const clearedChapter = Math.floor((currentStage - 1) / 100);

        if (unlockChapter > 0 && clearedChapter < unlockChapter) {
            return;
        }

        const viewMode = target.dataset.view;

        if (viewMode === 'stage-select') {
            this._openStagePopup();
        } else {
            // NPC 시설 (Phase 19~20, 현재 미구현)
            MainScreen.switchRightView(viewMode);
        }
    },

    _updateUnlockState() {
        const currentStage = Store.get('user.current_stage') || 101;
        const clearedChapter = Math.floor((currentStage - 1) / 100);

        this.el.querySelectorAll('.tv-hotspot').forEach(npcEl => {
            const unlockChapter = parseInt(npcEl.dataset.unlock);
            if (unlockChapter > 0 && clearedChapter < unlockChapter) {
                npcEl.classList.add('locked');
            } else {
                npcEl.classList.remove('locked');
            }
        });
    },

    // ── 스테이지 선택 팝업 ──

    _openStagePopup() {
        const overlay = this.el.querySelector('#tv-stage-overlay');
        overlay.classList.add('show');

        this._selectedChapter = 1;
        this._renderChapters();
        this._renderStages();
    },

    _closeStagePopup() {
        const overlay = this.el.querySelector('#tv-stage-overlay');
        overlay.classList.remove('show');
    },

    _renderChapters() {
        const chapters = getChapters();
        const currentStage = Store.get('user.current_stage') || 101;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;

        this.el.querySelector('#tv-popup-chapters').innerHTML = chapters.map(ch => `
            <button class="tv-popup-ch-btn ${ch.id === this._selectedChapter ? 'active' : ''} ${ch.id > maxChapter ? 'locked' : ''}"
                    data-action="chapter" data-chapter="${ch.id}">
                ${ch.id}. ${ch.sin}
            </button>
        `).join('');
    },

    _selectChapter(chapterId) {
        const currentStage = Store.get('user.current_stage') || 101;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;
        if (chapterId > maxChapter) return;

        this._selectedChapter = chapterId;
        this._renderChapters();
        this._renderStages();
    },

    _renderStages() {
        const chapters = getChapters();
        const chapter = chapters.find(c => c.id === this._selectedChapter);
        if (!chapter) return;

        const currentStage = Store.get('user.current_stage') || 101;

        // 챕터 정보
        this.el.querySelector('#tv-popup-info').innerHTML = `
            <div class="tv-popup-info-name">${chapter.region || ''}</div>
            <div class="tv-popup-info-sin">제${chapter.id}장: ${chapter.sin}</div>
            <div class="tv-popup-info-boss">보스: ${chapter.boss || '???'}</div>
        `;

        // 스테이지 리스트
        const stages = getStagesByChapter(this._selectedChapter);
        this.el.querySelector('#tv-popup-list').innerHTML = stages.map(stage => {
            const isUnlocked = stage.stageId <= currentStage;
            const isCleared = stage.stageId < currentStage;

            return `
                <div class="tv-popup-stage ${!isUnlocked ? 'locked' : ''} ${isCleared ? 'cleared' : ''}"
                     ${isUnlocked ? `data-action="enter-stage" data-stage-id="${stage.stageId}"` : ''}>
                    <div class="tv-popup-stage-left">
                        <span class="tv-popup-stage-name">${stage.stageName}</span>
                        <span class="tv-popup-stage-type">${stage.monsterType || ''}</span>
                    </div>
                    <div class="tv-popup-stage-right">
                        ${isCleared
                            ? '<span class="tv-popup-status cleared">\u2713 클리어</span>'
                            : isUnlocked
                                ? `<button class="tv-popup-enter" data-action="enter-stage" data-stage-id="${stage.stageId}">입장</button>`
                                : '<span class="tv-popup-status">\u{1F512} 잠김</span>'
                        }
                    </div>
                </div>
            `;
        }).join('');
    },

    async _enterStage(stageId) {
        showLoading();
        try {
            const result = await apiCall(3003, { stage_id: stageId });
            if (!result?.success) return;

            Store.set('battle.stage_id', stageId);
            Store.set('battle.monster_pool', result.data.monsters || []);

            this._closeStagePopup();
            MainScreen.switchRightView('battle', {
                stageId,
                monsters: result.data.monsters || [],
            });
        } finally {
            hideLoading();
        }
    },
};

export default TownView;
