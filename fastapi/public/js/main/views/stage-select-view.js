/**
 * TheSevenRPG — Stage Select View (우측 스테이지 선택 모드)
 * 출정문 클릭 시 표시. 챕터/스테이지 선택 → 전투 진입.
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { showLoading, hideLoading } from '../../utils.js';
import { getChapters, getStagesByChapter } from '../../meta-data.js';
import MainScreen from '../../main.js';

const StageSelectView = {
    el: null,
    _selectedChapter: 1,

    mount(el) {
        this.el = el;

        const chapters = getChapters();

        el.innerHTML = `
            <div class="ssv-screen">
                <div class="ssv-header">
                    <button class="ssv-back-btn" data-action="back">\u2190 마을로</button>
                    <span class="ssv-title">스테이지 선택</span>
                </div>

                <div class="ssv-chapter-bar" id="ssv-chapters">
                    ${chapters.map(ch => `
                        <button class="ssv-chapter-btn ${ch.id === 1 ? 'active' : ''}"
                                data-action="chapter" data-chapter="${ch.id}">
                            ${ch.id}. ${ch.sin}
                        </button>
                    `).join('')}
                </div>

                <div class="ssv-chapter-info" id="ssv-info"></div>

                <div class="ssv-stage-list" id="ssv-list"></div>
            </div>
        `;

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._selectedChapter = 1;
        this._renderChapter();
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
            case 'back':
                MainScreen.switchRightView('town');
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
        this.el.querySelectorAll('.ssv-chapter-btn').forEach(btn => {
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

        // 잠금 처리
        this.el.querySelectorAll('.ssv-chapter-btn').forEach(btn => {
            btn.classList.toggle('locked', parseInt(btn.dataset.chapter) > maxChapter);
        });

        // 챕터 정보
        this.el.querySelector('#ssv-info').innerHTML = `
            <div class="ssv-info-name">${chapter.region || ''}</div>
            <div class="ssv-info-sin">제${chapter.id}장: ${chapter.sin}</div>
            <div class="ssv-info-boss">보스: ${chapter.boss || '???'}</div>
        `;

        // 스테이지 리스트
        const stages = getStagesByChapter(this._selectedChapter);
        this.el.querySelector('#ssv-list').innerHTML = stages.map(stage => {
            const isUnlocked = stage.stageId <= currentStage;
            const isCleared = stage.stageId < currentStage;

            return `
                <div class="ssv-stage-card ${!isUnlocked ? 'locked' : ''} ${isCleared ? 'cleared' : ''}"
                     ${isUnlocked ? `data-action="enter-stage" data-stage-id="${stage.stageId}"` : ''}>
                    <div class="ssv-stage-left">
                        <span class="ssv-stage-name">${stage.stageName}</span>
                        <span class="ssv-stage-type">${stage.monsterType || ''}</span>
                    </div>
                    <div class="ssv-stage-right">
                        ${isCleared
                            ? '<span class="ssv-status cleared">\u2713 클리어</span>'
                            : isUnlocked
                                ? `<button class="ssv-enter-btn" data-action="enter-stage" data-stage-id="${stage.stageId}">입장</button>`
                                : '<span class="ssv-status">\u{1F512} 잠김</span>'
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

            MainScreen.switchRightView('battle', {
                stageId,
                monsters: result.data.monsters || [],
            });
        } finally {
            hideLoading();
        }
    },
};

export default StageSelectView;
