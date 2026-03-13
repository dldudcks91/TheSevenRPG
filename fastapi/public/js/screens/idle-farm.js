/**
 * TheSevenRPG — Idle Farm Screen
 * 방치 파밍 ON/OFF, 보상 수령
 * API: 3005(toggle_idle), 3006(collect_idle)
 */
import { apiCall } from '../api.js';
import { Store } from '../store.js';
import { showLoading, hideLoading, formatGold } from '../utils.js';

const IdleFarmScreen = {
    el: null,
    refs: {},
    _unsubscribers: [],
    _timerInterval: null,
    _elapsed: 0,
    _selectedStage: 101,

    mount(el) {
        this.el = el;

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="idle-screen">
                    <div class="idle-header">
                        <button class="idle-back-btn" data-action="back">\u2190</button>
                        <span class="idle-header-title">방치 파밍</span>
                        <span class="idle-header-right"></span>
                    </div>

                    <div class="idle-content">
                        <!-- 타이머 -->
                        <div class="idle-timer-display">
                            <div class="idle-timer-value" id="idle-timer">00:00:00</div>
                            <div class="idle-timer-label">경과 시간</div>
                        </div>

                        <!-- 상태 -->
                        <div class="idle-status-box">
                            <div class="idle-status-text" id="idle-status">방치 파밍 비활성</div>
                            <div class="idle-stage-info" id="idle-stage-info"></div>
                        </div>

                        <!-- 스테이지 선택 (비활성 시만) -->
                        <div class="idle-stage-select" id="idle-stage-select">
                            <div class="idle-stage-label">파밍 스테이지</div>
                            <div class="idle-stage-selector">
                                <button class="idle-stage-nav" data-action="stage-prev">\u25C0</button>
                                <span class="idle-stage-current" id="idle-stage-value">101</span>
                                <button class="idle-stage-nav" data-action="stage-next">\u25B6</button>
                            </div>
                        </div>

                        <!-- 액션 버튼 -->
                        <div class="idle-actions">
                            <button class="idle-toggle-btn start" id="idle-toggle" data-action="toggle">파밍 시작</button>
                            <button class="idle-collect-btn" id="idle-collect" data-action="collect" style="display:none">보상 수령</button>
                        </div>

                        <!-- 보상 결과 -->
                        <div class="idle-reward-box" id="idle-reward">
                            <div class="idle-reward-title">보상 수령 완료</div>
                            <div class="idle-reward-detail" id="idle-reward-detail"></div>
                        </div>
                    </div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        this.refs = {
            timer: el.querySelector('#idle-timer'),
            status: el.querySelector('#idle-status'),
            stageInfo: el.querySelector('#idle-stage-info'),
            stageSelect: el.querySelector('#idle-stage-select'),
            stageValue: el.querySelector('#idle-stage-value'),
            toggleBtn: el.querySelector('#idle-toggle'),
            collectBtn: el.querySelector('#idle-collect'),
            rewardBox: el.querySelector('#idle-reward'),
            rewardDetail: el.querySelector('#idle-reward-detail'),
        };

        this._handleEvent = this.handleEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        // 현재 상태 반영
        this._syncState();
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        this._unsubscribers.forEach(unsub => unsub());
        this._unsubscribers = [];
        this._clearTimer();
    },

    handleEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'back':
                window.location.hash = '#town';
                break;
            case 'toggle':
                this._doToggle();
                break;
            case 'collect':
                this._doCollect();
                break;
            case 'stage-prev':
                this._changeStage(-1);
                break;
            case 'stage-next':
                this._changeStage(1);
                break;
        }
    },

    _syncState() {
        const isActive = Store.get('idle.active');
        const stageId = Store.get('idle.stage_id');
        const elapsed = Store.get('idle.elapsed_seconds') || 0;

        // 선택 스테이지 초기값
        const currentStage = Store.get('user.current_stage') || 101;
        this._selectedStage = stageId || currentStage;
        this.refs.stageValue.textContent = this._selectedStage;

        if (isActive) {
            this._setActiveUI(stageId, elapsed);
        } else {
            this._setInactiveUI();
        }
    },

    _setActiveUI(stageId, elapsed) {
        this.refs.status.textContent = '방치 파밍 진행 중';
        this.refs.status.classList.add('active');
        this.refs.stageInfo.textContent = `스테이지 ${stageId}`;
        this.refs.stageSelect.style.display = 'none';
        this.refs.toggleBtn.textContent = '파밍 중지';
        this.refs.toggleBtn.className = 'idle-toggle-btn stop';
        this.refs.collectBtn.style.display = 'block';
        this.refs.rewardBox.classList.remove('show');

        this._elapsed = elapsed;
        this._startTimer();
    },

    _setInactiveUI() {
        this.refs.status.textContent = '방치 파밍 비활성';
        this.refs.status.classList.remove('active');
        this.refs.stageInfo.textContent = '';
        this.refs.stageSelect.style.display = 'block';
        this.refs.toggleBtn.textContent = '파밍 시작';
        this.refs.toggleBtn.className = 'idle-toggle-btn start';
        this.refs.collectBtn.style.display = 'none';
        this.refs.timer.textContent = '00:00:00';

        this._clearTimer();
    },

    _startTimer() {
        this._clearTimer();
        this._updateTimerDisplay();
        this._timerInterval = setInterval(() => {
            this._elapsed++;
            this._updateTimerDisplay();
        }, 1000);
    },

    _clearTimer() {
        if (this._timerInterval) {
            clearInterval(this._timerInterval);
            this._timerInterval = null;
        }
    },

    _updateTimerDisplay() {
        const h = Math.floor(this._elapsed / 3600);
        const m = Math.floor((this._elapsed % 3600) / 60);
        const s = this._elapsed % 60;
        this.refs.timer.textContent =
            `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    },

    _changeStage(delta) {
        const currentStage = Store.get('user.current_stage') || 101;
        let next = this._selectedStage + delta;

        // 범위 제한: 101 ~ currentStage
        if (next < 101) next = 101;
        if (next > currentStage) next = currentStage;

        this._selectedStage = next;
        this.refs.stageValue.textContent = next;
    },

    async _doToggle() {
        const isActive = Store.get('idle.active');

        showLoading();
        try {
            const data = isActive
                ? {}
                : { stage_id: this._selectedStage };

            const result = await apiCall(3005, data);
            if (result?.success) {
                const newActive = result.data.idle_active;
                Store.set('idle.active', newActive);

                if (newActive) {
                    Store.set('idle.stage_id', result.data.stage_id);
                    Store.set('idle.elapsed_seconds', 0);
                    this._setActiveUI(result.data.stage_id, 0);
                } else {
                    this._setInactiveUI();
                }
            }
        } finally {
            hideLoading();
        }
    },

    async _doCollect() {
        showLoading();
        try {
            const result = await apiCall(3006, {});
            if (result?.success) {
                const d = result.data;
                Store.set('user.gold', d.total_gold);

                this.refs.rewardDetail.innerHTML = [
                    `경과 시간: ${d.elapsed_minutes}분`,
                    `처치 몬스터: ${d.kill_count}마리`,
                    `획득 골드: ${formatGold(d.gold_reward)}`,
                ].join('<br>');

                this.refs.rewardBox.classList.add('show');
            }
        } finally {
            hideLoading();
        }
    },
};

export default IdleFarmScreen;
