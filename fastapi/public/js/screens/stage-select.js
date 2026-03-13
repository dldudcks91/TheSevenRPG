/**
 * TheSevenRPG — Stage Select Screen
 * 챕터/스테이지 선택 → 전투 → 결과 표시
 * API: 3001(전투결과), 3003(입장), 3004(클리어)
 */
import { apiCall } from '../api.js';
import { Store } from '../store.js';
import { showLoading, hideLoading, escapeHtml } from '../utils.js';

// 챕터 데이터 (메타데이터 — 추후 서버에서 받을 수 있음)
const CHAPTERS = [
    { id: 1, sin: '분노', region: '불타는 전장', color: 'wrath', boss: '전장의 군주' },
    { id: 2, sin: '나태', region: '망각의 늪', color: 'sloth', boss: '늪의 지배자' },
    { id: 3, sin: '탐욕', region: '황금의 폐허', color: 'greed', boss: '황금 수호자' },
    { id: 4, sin: '시기', region: '저주받은 숲', color: 'envy', boss: '숲의 거울' },
    { id: 5, sin: '폭식', region: '심연의 동굴', color: 'gluttony', boss: '심연의 입' },
    { id: 6, sin: '색욕', region: '타락한 궁전', color: 'lust', boss: '궁전의 여왕' },
    { id: 7, sin: '오만', region: '신의 폐허', color: 'pride', boss: '타락한 신' },
];

// 챕터별 스테이지 (stage_id = chapter_id * 100 + stage_num)
const STAGES_PER_CHAPTER = [
    { num: 1, suffix: '1구역' },
    { num: 2, suffix: '2구역' },
    { num: 3, suffix: '3구역' },
];

const StageSelectScreen = {
    el: null,
    refs: {},
    _unsubscribers: [],
    _selectedChapter: 1,

    mount(el) {
        this.el = el;

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="stage-screen">
                    <div class="stage-header">
                        <button class="stage-back-btn" data-action="back">\u2190</button>
                        <span class="stage-header-title">스테이지</span>
                        <span class="stage-header-right"></span>
                    </div>

                    <div class="chapter-selector" id="chapter-selector">
                        ${CHAPTERS.map(ch => `
                            <button class="chapter-btn ${ch.id === 1 ? 'active' : ''}"
                                    data-action="chapter" data-chapter="${ch.id}">
                                ${ch.id}. ${ch.sin}
                            </button>
                        `).join('')}
                    </div>

                    <div class="chapter-info" id="chapter-info"></div>

                    <div class="stage-list" id="stage-list"></div>

                    <!-- 전투 결과 오버레이 -->
                    <div class="battle-result-overlay" id="battle-result"></div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        this.refs = {
            chapterSelector: el.querySelector('#chapter-selector'),
            chapterInfo: el.querySelector('#chapter-info'),
            stageList: el.querySelector('#stage-list'),
            battleResult: el.querySelector('#battle-result'),
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
            case 'battle-again':
                this._enterStage(parseInt(target.dataset.stageId));
                break;
            case 'battle-close':
                this.refs.battleResult.classList.remove('show');
                break;
        }
    },

    _selectChapter(chapterId) {
        const currentStage = Store.get('user.current_stage') || 1;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;

        // 해금 안 된 챕터 클릭 차단
        if (chapterId > maxChapter) return;

        this._selectedChapter = chapterId;

        // 챕터 버튼 활성화
        this.refs.chapterSelector.querySelectorAll('.chapter-btn').forEach(btn => {
            const ch = parseInt(btn.dataset.chapter);
            btn.classList.toggle('active', ch === chapterId);
            btn.classList.toggle('locked', ch > maxChapter);
        });

        this._renderChapter();
    },

    _renderChapter() {
        const chapter = CHAPTERS.find(c => c.id === this._selectedChapter);
        if (!chapter) return;

        const currentStage = Store.get('user.current_stage') || 1;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;

        // 챕터 버튼 잠금 상태 업데이트
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

        // 스테이지 리스트
        this.refs.stageList.innerHTML = STAGES_PER_CHAPTER.map(stage => {
            const stageId = chapter.id * 100 + stage.num;
            const isUnlocked = stageId <= currentStage;
            const isCleared = stageId < currentStage;

            return `
                <div class="stage-card ${!isUnlocked ? 'locked' : ''} ${isCleared ? 'cleared' : ''}"
                     ${isUnlocked ? `data-action="enter-stage" data-stage-id="${stageId}"` : ''}>
                    <div class="stage-card-left">
                        <span class="stage-card-name">${chapter.region} ${stage.suffix}</span>
                        <span class="stage-card-type">스테이지 ${stageId}</span>
                    </div>
                    <div class="stage-card-right">
                        ${isCleared
                            ? '<span class="stage-card-status cleared">\u2713 클리어</span>'
                            : isUnlocked
                                ? `<button class="stage-enter-btn" data-action="enter-stage" data-stage-id="${stageId}">입장</button>`
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
            // 1. 스테이지 입장
            const enterResult = await apiCall(3003, { stage_id: stageId });
            if (!enterResult?.success) return;

            // 2. 전투 실행
            const battleResult = await apiCall(3001, { stage_id: stageId });
            if (!battleResult?.success) return;

            // 3. 전투 결과 표시
            this._showBattleResult(battleResult.data, stageId);

            // 4. 승리 시 스테이지 클리어
            if (battleResult.data.result === 'victory') {
                const clearResult = await apiCall(3004, { stage_id: stageId });
                if (clearResult?.success) {
                    Store.set('user.current_stage', clearResult.data.current_stage);
                    // 스테이지 리스트 갱신
                    this._renderChapter();
                }
            }
        } finally {
            hideLoading();
        }
    },

    _showBattleResult(data, stageId) {
        const isVictory = data.result === 'victory';

        this.refs.battleResult.innerHTML = `
            <div class="battle-result-title ${isVictory ? 'victory' : 'defeat'}">
                ${isVictory ? '\u2694 \uC2B9\uB9AC!' : '\u{1F480} \uD328\uBC30...'}
            </div>
            <div class="battle-result-rewards">
                ${data.exp_gained ? `<div>EXP +${data.exp_gained}</div>` : ''}
                ${data.gold_gained ? `<div>Gold +${data.gold_gained}</div>` : ''}
                ${data.drops?.length ? `<div>드롭 아이템 ${data.drops.length}개</div>` : ''}
            </div>
            <div class="battle-result-actions">
                <button class="btn btn-primary" data-action="battle-again" data-stage-id="${stageId}">재도전</button>
                <button class="btn" data-action="battle-close">확인</button>
            </div>
        `;

        this.refs.battleResult.classList.add('show');

        // 골드/경험치 Store 갱신
        if (data.total_gold !== undefined) Store.set('user.gold', data.total_gold);
        if (data.total_exp !== undefined) Store.set('user.exp', data.total_exp);
        if (data.level !== undefined) Store.set('user.level', data.level);
    },
};

export default StageSelectScreen;
