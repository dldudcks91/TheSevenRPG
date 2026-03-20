/**
 * TheSevenRPG — Tutorial Battle Scene
 * 프롤로그 직후 간이 전투 화면.
 * 3단계: 인트로 → 전투 재생 → 승리(드롭+장착) → Ch1 진입
 */
import { apiCall } from '../api.js';
import { SceneManager } from '../scene-manager.js';
import { t } from '../i18n/index.js';
import story from '../i18n/story-ko.js';

/** 턴 재생 간격 (ms) */
const TURN_DELAY = 800;

const TutorialBattleScene = {
    el: null,
    refs: {},
    _phase: 'intro', // intro | battle | victory | chapter
    _introIdx: 0,
    _turnIdx: 0,
    _turnTimer: null,
    _battleData: null,

    // ── mount ──
    mount(el) {
        this.el = el;
        this._phase = 'intro';
        this._introIdx = 0;
        this._turnIdx = 0;
        this._battleData = null;

        el.innerHTML = `
            <div class="tutorial-battle-screen" data-action="advance">
                <div id="tut-content"></div>
                <div class="tutorial-footer">
                    <span class="tutorial-hint" id="tut-hint">${t('prologue_click')}</span>
                </div>
            </div>
        `;

        this.refs = {
            content: el.querySelector('#tut-content'),
            hint: el.querySelector('#tut-hint'),
        };

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._handleKeydown = this._onKeydown.bind(this);
        document.addEventListener('keydown', this._handleKeydown);

        this._showIntro();
    },

    unmount() {
        if (this._handleEvent) this.el.removeEventListener('pointerdown', this._handleEvent);
        if (this._handleKeydown) document.removeEventListener('keydown', this._handleKeydown);
        if (this._turnTimer) clearTimeout(this._turnTimer);
        this.refs = {};
    },

    // ── 이벤트 ──
    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'advance':
                this._advance();
                break;
            case 'equip':
                e.stopPropagation();
                this._doEquip();
                break;
        }
    },

    _onKeydown(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            this._advance();
        }
    },

    _advance() {
        switch (this._phase) {
            case 'intro':
                this._advanceIntro();
                break;
            case 'battle':
                // 전투 중 클릭 → 빠르게 재생 (남은 턴 즉시)
                this._skipBattle();
                break;
            case 'victory':
                // 승리 화면은 장착 버튼으로만 진행
                break;
            case 'chapter':
                SceneManager.replace('main');
                break;
        }
    },

    // ══════════════════════════════════════
    // Phase 1: 인트로 내레이션
    // ══════════════════════════════════════
    _showIntro() {
        this._phase = 'intro';
        this._introIdx = 0;
        this.refs.content.className = 'tutorial-intro';
        this.refs.content.innerHTML = '';
        this.refs.hint.textContent = t('prologue_click');
        this._appendIntroLine();
    },

    _advanceIntro() {
        const introLines = story.tutorial_intro;
        if (this._introIdx < introLines.length) {
            this._appendIntroLine();
        } else {
            this._startBattle();
        }
    },

    _appendIntroLine() {
        const introLines = story.tutorial_intro;
        const accentKeywords = story.tutorial_accent_keywords;
        const line = introLines[this._introIdx];
        this._introIdx++;

        if (!line) {
            const br = document.createElement('div');
            br.style.height = '12px';
            this.refs.content.appendChild(br);
            // 빈 줄 후 자동으로 다음
            if (this._introIdx < introLines.length) {
                this._appendIntroLine();
            }
            return;
        }

        const lineEl = document.createElement('div');
        lineEl.className = 'tutorial-intro-line';
        if (accentKeywords.some(kw => line.includes(kw))) {
            lineEl.classList.add('accent');
        }
        lineEl.style.animationDelay = '0s';
        lineEl.textContent = line;
        this.refs.content.appendChild(lineEl);
    },

    // ══════════════════════════════════════
    // Phase 2: 전투 재생
    // ══════════════════════════════════════
    async _startBattle() {
        this._phase = 'battle';
        this.refs.hint.textContent = story.tutorial_guide_battle;

        // 서버 API 호출
        const result = await apiCall(1010);
        if (!result?.success) {
            // 이미 튜토리얼 완료 등 → 바로 메인으로
            SceneManager.replace('main');
            return;
        }

        this._battleData = result.data;
        const log = result.data.battle_log;
        const playerName = story.tutorial_player_name;

        // 전투 UI 렌더링
        this.refs.content.className = 'tutorial-battle-area';
        this.refs.content.innerHTML = `
            <div class="tutorial-combatant">
                <div class="tutorial-combatant-header">
                    <span class="tutorial-combatant-name">${log.monster_name}</span>
                    <span class="tutorial-combatant-hp-text" id="tut-m-hp-text">${log.monster_max_hp} / ${log.monster_max_hp}</span>
                </div>
                <div class="tutorial-hp-track">
                    <div class="tutorial-hp-fill monster" id="tut-m-hp" style="width:100%"></div>
                </div>
            </div>
            <div class="tutorial-vs">VS</div>
            <div class="tutorial-combatant">
                <div class="tutorial-combatant-header">
                    <span class="tutorial-combatant-name">${playerName}</span>
                    <span class="tutorial-combatant-hp-text" id="tut-p-hp-text">${log.player_max_hp} / ${log.player_max_hp}</span>
                </div>
                <div class="tutorial-hp-track">
                    <div class="tutorial-hp-fill" id="tut-p-hp" style="width:100%"></div>
                </div>
            </div>
            <div class="tutorial-battle-log" id="tut-log"></div>
        `;

        this._turnIdx = 0;
        this._playNextTurn();
    },

    _playNextTurn() {
        const turns = this._battleData.battle_log.turns;
        if (this._turnIdx >= turns.length) {
            // 전투 종료 → 승리 화면
            setTimeout(() => this._showVictory(), 600);
            return;
        }

        const turn = turns[this._turnIdx];
        this._turnIdx++;

        this._applyTurn(turn);
        this._turnTimer = setTimeout(() => this._playNextTurn(), TURN_DELAY);
    },

    _applyTurn(turn) {
        const log = this._battleData.battle_log;
        const isPlayer = turn.attacker === 'player';
        const playerName = story.tutorial_player_name;

        // HP 바 업데이트
        if (isPlayer) {
            const pct = Math.max(0, (turn.target_hp / log.monster_max_hp) * 100);
            const hpFill = this.el.querySelector('#tut-m-hp');
            const hpText = this.el.querySelector('#tut-m-hp-text');
            if (hpFill) hpFill.style.width = `${pct}%`;
            if (hpText) hpText.textContent = `${Math.max(0, turn.target_hp)} / ${log.monster_max_hp}`;
        } else {
            const pct = Math.max(0, (turn.target_hp / log.player_max_hp) * 100);
            const hpFill = this.el.querySelector('#tut-p-hp');
            const hpText = this.el.querySelector('#tut-p-hp-text');
            if (hpFill) hpFill.style.width = `${pct}%`;
            if (hpText) hpText.textContent = `${Math.max(0, turn.target_hp)} / ${log.player_max_hp}`;
        }

        // 로그 추가
        const logEl = this.el.querySelector('#tut-log');
        if (logEl) {
            const entry = document.createElement('div');
            entry.className = `tutorial-log-entry ${isPlayer ? 'player-hit' : 'monster-hit'}`;
            const attackerName = isPlayer ? playerName : log.monster_name;
            const targetName = isPlayer ? log.monster_name : playerName;
            entry.textContent = t('tutorial_attack_log', { attacker: attackerName, target: targetName, damage: turn.damage });
            logEl.appendChild(entry);
            logEl.scrollTop = logEl.scrollHeight;
        }
    },

    _skipBattle() {
        // 남은 턴 모두 즉시 적용
        if (this._turnTimer) clearTimeout(this._turnTimer);

        const turns = this._battleData.battle_log.turns;
        while (this._turnIdx < turns.length) {
            this._applyTurn(turns[this._turnIdx]);
            this._turnIdx++;
        }

        setTimeout(() => this._showVictory(), 400);
    },

    // ══════════════════════════════════════
    // Phase 3: 승리 + 드롭 + 장착
    // ══════════════════════════════════════
    _showVictory() {
        this._phase = 'victory';
        const data = this._battleData;
        const drop = data.drop_item;
        const opts = drop.dynamic_options || {};

        // 스탯 텍스트 생성
        const statLines = [];
        if (opts.base_defense) statLines.push(`${story.tutorial_defense} +${opts.base_defense}`);
        if (opts.base_magic_defense) statLines.push(`${story.tutorial_magic_defense} +${opts.base_magic_defense}`);

        this.refs.content.className = 'tutorial-victory';
        this.refs.content.innerHTML = `
            <div class="tutorial-victory-title">${story.tutorial_victory}</div>
            <div class="tutorial-rewards">
                <div class="tutorial-reward-row">
                    <span>${story.tutorial_exp}</span>
                    <span class="tutorial-reward-value">+${data.exp_gained} EXP</span>
                </div>
                <div class="tutorial-reward-row">
                    <span>${story.tutorial_gold}</span>
                    <span class="tutorial-reward-value">+${data.gold_gained} G</span>
                </div>
            </div>
            <div class="tutorial-drop-card">
                <div class="tutorial-drop-label">${story.tutorial_drop_label}</div>
                <div class="tutorial-drop-name">${drop.item_name}</div>
                <div class="tutorial-drop-stats">${statLines.join('<br>')}</div>
            </div>
            <div class="tutorial-guide">${story.tutorial_guide_drop}</div>
            <button class="tutorial-equip-btn" data-action="equip">${story.tutorial_equip_btn}</button>
        `;

        this.refs.hint.textContent = '';
    },

    async _doEquip() {
        const drop = this._battleData.drop_item;

        const result = await apiCall(2001, {
            item_uid: drop.item_uid,
            equip_slot: 'armor',
        });

        if (result?.success) {
            this._showChapterEnter();
        } else {
            // 장착 실패해도 진행 허용
            this._showChapterEnter();
        }
    },

    // ══════════════════════════════════════
    // Phase 4: 챕터 진입
    // ══════════════════════════════════════
    _showChapterEnter() {
        this._phase = 'chapter';

        this.refs.content.className = 'tutorial-victory';
        this.refs.content.innerHTML = `
            <div class="tutorial-chapter-enter">${story.tutorial_chapter_enter}</div>
        `;

        this.refs.hint.textContent = story.tutorial_guide_chapter;
    },
};

export default TutorialBattleScene;
