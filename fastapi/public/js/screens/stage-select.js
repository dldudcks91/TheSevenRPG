/**
 * TheSevenRPG — Stage Select Screen
 * 챕터/스테이지 선택 → 전투 화면 진입
 * API: 3003(입장), 3004(클리어)
 */
import { apiCall } from '../api.js';
import { Store } from '../store.js';
import { showLoading, hideLoading } from '../utils.js';
import { getChapters, getStagesByChapter } from '../meta-data.js';

const StageSelectScreen = {
    el: null,
    refs: {},
    _unsubscribers: [],
    _selectedChapter: 1,

    mount(el) {
        this.el = el;

        const chapters = getChapters();

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="stage-screen">
                    <div class="stage-header">
                        <button class="stage-back-btn" data-action="back">\u2190</button>
                        <span class="stage-header-title">스테이지</span>
                        <span class="stage-header-right"></span>
                    </div>

                    <div class="chapter-selector" id="chapter-selector">
                        ${chapters.map(ch => `
                            <button class="chapter-btn ${ch.id === 1 ? 'active' : ''}"
                                    data-action="chapter" data-chapter="${ch.id}">
                                ${ch.id}. ${ch.sin}
                            </button>
                        `).join('')}
                    </div>

                    <div class="chapter-info" id="chapter-info"></div>

                    <div class="stage-list" id="stage-list"></div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        this.refs = {
            chapterSelector: el.querySelector('#chapter-selector'),
            chapterInfo: el.querySelector('#chapter-info'),
            stageList: el.querySelector('#stage-list'),
        };

        this._handleEvent = this.handleEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._selectedChapter = 1;
        this._renderChapter();
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
    },

    handleEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;

        switch (action) {
            case 'back':
                window.location.hash = '#town';
                break;
            case 'chapter':
                this._selectChapter(parseInt(target.dataset.chapter));
                break;
            case 'enter-stage':
                this._enterStage(parseInt(target.dataset.stageId));
                break;
        }
    },

    _selectChapter(chapterId) {
        const currentStage = Store.get('user.current_stage') || 101;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;

        if (chapterId > maxChapter) return;

        this._selectedChapter = chapterId;

        this.refs.chapterSelector.querySelectorAll('.chapter-btn').forEach(btn => {
            const ch = parseInt(btn.dataset.chapter);
            btn.classList.toggle('active', ch === chapterId);
            btn.classList.toggle('locked', ch > maxChapter);
        });

        this._renderChapter();
    },

    _renderChapter() {
        const chapters = getChapters();
        const chapter = chapters.find(c => c.id === this._selectedChapter);
        if (!chapter) return;

        const currentStage = Store.get('user.current_stage') || 101;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;

        // 챕터 버튼 잠금
        this.refs.chapterSelector.querySelectorAll('.chapter-btn').forEach(btn => {
            const ch = parseInt(btn.dataset.chapter);
            btn.classList.toggle('locked', ch > maxChapter);
        });

        // 챕터 정보
        this.refs.chapterInfo.innerHTML = `
            <div class="chapter-name" style="color: var(--color-${chapter.color})">${chapter.region}</div>
            <div class="chapter-sin">제${chapter.id}장: ${chapter.sin}</div>
            <div class="chapter-boss">보스: ${chapter.boss}</div>
        `;

        // 스테이지 리스트 (메타데이터 기반)
        const stages = getStagesByChapter(this._selectedChapter);
        this.refs.stageList.innerHTML = stages.map(stage => {
            const isUnlocked = stage.stageId <= currentStage;
            const isCleared = stage.stageId < currentStage;

            return `
                <div class="stage-card ${!isUnlocked ? 'locked' : ''} ${isCleared ? 'cleared' : ''}"
                     ${isUnlocked ? `data-action="enter-stage" data-stage-id="${stage.stageId}"` : ''}>
                    <div class="stage-card-left">
                        <span class="stage-card-name">${stage.stageName}</span>
                        <span class="stage-card-type">${stage.monsterType}</span>
                    </div>
                    <div class="stage-card-right">
                        ${isCleared
                            ? '<span class="stage-card-status cleared">\u2713 클리어</span>'
                            : isUnlocked
                                ? `<button class="stage-enter-btn" data-action="enter-stage" data-stage-id="${stage.stageId}">입장</button>`
                                : '<span class="stage-card-status">\u{1F512} 잠김</span>'
                        }
                    </div>
                </div>
            `;
        }).join('');
    },

    async _enterStage(stageId) {
        showLoading();
        try {
            // 1. 스테이지 입장 → monster_pool 수신
            const enterResult = await apiCall(3003, { stage_id: stageId });
            if (!enterResult?.success) return;

            // 2. 전투 데이터를 Store에 저장 후 전투 화면으로 전환
            Store.set('battle.stage_id', stageId);
            Store.set('battle.monster_pool', enterResult.data.monsters || []);
            window.location.hash = '#battle';
        } finally {
            hideLoading();
        }
    },
};

export default StageSelectScreen;
