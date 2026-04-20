/**
 * TheSevenRPG — Battle View (우측 전투 모드, idle 횡스크롤)
 * 서버 battle_log를 IdleBattleScene에 위임하여 "오른쪽 스폰 → 조우 → 평타 교환 → 사망" 흐름으로 재생.
 * 전투 공식/결과/드롭은 서버 결과 그대로 사용.
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { showLoading, hideLoading, escapeHtml, setupEventDelegation, teardown, buildItemPopupHtml } from '../../utils.js';
import { getMonsterName, getStageName } from '../../meta-data.js';
import { t, sinName, rarityName, slotName } from '../../i18n/index.js';
import MainScreen from '../../main.js';
import Popup from '../../popup.js';
import { IdleBattleScene } from './idle-battle-scene.js';
import { PaceCtrl } from './pace-ctrl.js';

/** stage_id → 배경 이미지 경로 */
function getStageBgUrl(stageId) {
    return `/assets/backgrounds/background_stage_${stageId}.png`;
}

const BattleView = {
    el: null,
    refs: {},
    _phaserGame: null,
    _battleScene: null,
    _pace: null,
    _playerMaxHp: 0,
    _monsterMaxHp: 0,

    mount(el, data) {
        setupEventDelegation(this, el);
        this._pace = new PaceCtrl();

        el.innerHTML = `
            <div class="bv-screen">
                <div class="bv-top-bar">
                    <div class="bv-stage-name" id="bv-stage-name"></div>
                    <div class="bv-wave-indicator" id="bv-wave-indicator"></div>
                </div>

                <div class="bv-hud">
                    <div class="bv-hud-player">
                        <div class="bv-hud-name player">Player</div>
                        <div class="bv-hp-bar"><div class="bv-hp-fill" id="bv-player-hp" style="width:100%"></div></div>
                        <div class="bv-hp-text" id="bv-player-hp-text"></div>
                    </div>
                    <div class="bv-vs">VS</div>
                    <div class="bv-hud-monster">
                        <div class="bv-hud-name monster" id="bv-monster-name">Monster</div>
                        <div class="bv-hp-bar monster"><div class="bv-hp-fill monster" id="bv-monster-hp" style="width:100%"></div></div>
                        <div class="bv-hp-text" id="bv-monster-hp-text"></div>
                    </div>
                </div>

                <div class="bv-stage" id="bv-stage">
                    <div class="bv-stage-bg" id="bv-stage-bg"></div>
                    <div class="bv-stage-phaser" id="bv-stage-phaser"></div>
                    <div class="bv-floating-log" id="bv-floating-log"></div>
                    <div class="bv-wave-banner" id="bv-wave-banner"></div>
                </div>

                <div class="bv-result-overlay" id="bv-result"></div>
            </div>
        `;

        this.refs = {
            stageName: el.querySelector('#bv-stage-name'),
            waveIndicator: el.querySelector('#bv-wave-indicator'),
            playerHp: el.querySelector('#bv-player-hp'),
            playerHpText: el.querySelector('#bv-player-hp-text'),
            monsterName: el.querySelector('#bv-monster-name'),
            monsterHp: el.querySelector('#bv-monster-hp'),
            monsterHpText: el.querySelector('#bv-monster-hp-text'),
            stage: el.querySelector('#bv-stage'),
            stageBg: el.querySelector('#bv-stage-bg'),
            phaserHost: el.querySelector('#bv-stage-phaser'),
            floatingLog: el.querySelector('#bv-floating-log'),
            waveBanner: el.querySelector('#bv-wave-banner'),
            result: el.querySelector('#bv-result'),
        };

        this._initPhaser();
        this._startBattle();
    },

    unmount() {
        teardown(this);
        if (this._pace) { this._pace.clearAll(); this._pace = null; }
        this._destroyPhaser();
    },

    onVisibilityChange(hidden) {
        if (this._phaserGame && this._phaserGame.scene) {
            if (hidden) this._phaserGame.scene.pause('IdleBattleScene');
            else this._phaserGame.scene.resume('IdleBattleScene');
        }
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'battle-again':
                Popup.hide();
                this._startBattle();
                break;
            case 'battle-back':
                Popup.hide();
                MainScreen.switchRightView('town');
                break;
            case 'show-drop-detail':
                this._showDropPopup(target);
                break;
        }
    },

    // ── 웨이브 인디케이터 ──

    _createWaveIndicator(waveCount) {
        let html = '';
        for (let i = 0; i < waveCount; i++) {
            html += `<div class="bv-wave-dot ${i === 0 ? 'active' : ''}"></div>`;
            if (i < waveCount - 1) {
                html += `<div class="bv-wave-line"></div>`;
            }
        }
        this.refs.waveIndicator.innerHTML = html;
    },

    _updateWaveIndicator(currentWaveIndex) {
        const dots = this.refs.waveIndicator.querySelectorAll('.bv-wave-dot');
        dots.forEach((dot, idx) => {
            dot.classList.toggle('active', idx === currentWaveIndex);
        });
    },

    // ── 전투 시작 ──

    async _startBattle() {
        const stageId = Store.get('battle.stage_id');
        if (!stageId) {
            MainScreen.switchRightView('town');
            return;
        }

        this.refs.stageName.textContent = getStageName(stageId);
        this.refs.result.classList.remove('show');
        this.refs.floatingLog.innerHTML = '';
        this.refs.waveBanner.classList.remove('show');

        this.refs.stageBg.style.backgroundImage = `url('${getStageBgUrl(stageId)}')`;
        this._setBgScroll(false);

        if (this._battleScene) await this._battleScene.resetForNewBattle();

        showLoading();
        try {
            const enterResult = await apiCall(3003, { stage_id: stageId });
            if (!enterResult?.success) {
                MainScreen.switchRightView('town');
                return;
            }
            Store.set('battle.monster_pool', enterResult.data.monsters);
        } finally {
            hideLoading();
        }

        const monsterPool = Store.get('battle.monster_pool');
        if (!monsterPool || monsterPool.length === 0) {
            MainScreen.switchRightView('town');
            return;
        }

        this._createWaveIndicator(monsterPool.length);
        await this._runWaves(monsterPool, stageId);
    },

    async _runWaves(waves, stageId) {
        let totalRewards = { exp_gained: 0, gold_gained: 0, gold: 0, level: 0, exp: 0, leveled_up: false, drops: [] };
        let finalResult = 'win';

        for (let wi = 0; wi < waves.length; wi++) {
            const wave = waves[wi];
            this._updateWaveIndicator(wi);
            this._showWaveBanner(wi + 1, waves.length, wave.is_boss);

            const monsters = wave.monsters || [];
            for (let mi = 0; mi < monsters.length; mi++) {
                const mob = monsters[mi];
                const monsterIdx = mob.monster_idx;
                const spawnType = mob.spawn_type || '\uC77C\uBC18';

                this.refs.monsterName.textContent = `${getMonsterName(monsterIdx)} (${spawnType})`;
                this.refs.monsterHp.style.width = '100%';

                showLoading();
                let data;
                try {
                    const result = await apiCall(3001, { monster_idx: monsterIdx, spawn_type: spawnType });
                    if (!result?.success) { finalResult = 'lose'; break; }
                    data = result.data;
                } finally {
                    hideLoading();
                }

                this._initHpBars(data);
                await this._playMob(data, monsterIdx, spawnType);

                const rw = data.rewards || {};
                totalRewards.exp_gained += rw.exp_gained || 0;
                totalRewards.gold_gained += rw.gold_gained || 0;
                if (rw.gold !== undefined) totalRewards.gold = rw.gold;
                if (rw.level !== undefined) totalRewards.level = rw.level;
                if (rw.exp !== undefined) totalRewards.exp = rw.exp;
                if (rw.leveled_up) totalRewards.leveled_up = true;

                const drops = data.drops || [];
                totalRewards.drops.push(...drops);

                if (data.result !== 'win') { finalResult = data.result; break; }
            }
            if (finalResult !== 'win') break;
        }

        this._showResult(finalResult, totalRewards, stageId);
    },

    // ── 몬스터 1기 재생 (Scene에 위임) ──

    _initHpBars(data) {
        const log = data.battle_log || [];
        const firstPlayerAtk = log.find(e => e.actor === 'player' && e.action === 'attack');
        const firstMonsterAtk = log.find(e => e.actor === 'monster' && e.action === 'attack');

        this._playerMaxHp = firstMonsterAtk ? firstMonsterAtk.target_hp + firstMonsterAtk.damage : (this._playerMaxHp || 200);
        this._monsterMaxHp = firstPlayerAtk ? firstPlayerAtk.target_hp + firstPlayerAtk.damage : 100;

        this.refs.playerHpText.textContent = `${this._playerMaxHp} / ${this._playerMaxHp}`;
        this.refs.monsterHpText.textContent = `${this._monsterMaxHp} / ${this._monsterMaxHp}`;
        this.refs.playerHp.style.width = '100%';
        this.refs.monsterHp.style.width = '100%';
    },

    _playMob(data, monsterIdx, spawnType) {
        if (!this._battleScene) return Promise.resolve();
        return this._battleScene.playMob(data, monsterIdx, spawnType);
    },

    _onPhase(phase) {
        // APPROACH 구간에서만 배경을 왼쪽으로 스크롤
        this._setBgScroll(phase === 'approach');
    },

    _onBattleEntry(entry) {
        if (entry.actor === 'player') {
            const hp = Math.max(0, entry.target_hp);
            const pct = this._monsterMaxHp > 0 ? (hp / this._monsterMaxHp) * 100 : 0;
            this.refs.monsterHp.style.width = pct + '%';
            this.refs.monsterHpText.textContent = `${hp} / ${this._monsterMaxHp}`;
        } else {
            const hp = Math.max(0, entry.target_hp);
            const pct = this._playerMaxHp > 0 ? (hp / this._playerMaxHp) * 100 : 0;
            this.refs.playerHp.style.width = pct + '%';
            this.refs.playerHpText.textContent = `${hp} / ${this._playerMaxHp}`;
        }
        this._appendLog(entry);
    },

    _setBgScroll(on) {
        if (!this.refs.stageBg) return;
        this.refs.stageBg.classList.toggle('scrolling', !!on);
    },

    _appendLog(entry) {
        const el = document.createElement('div');
        el.className = `bv-floating-entry ${entry.actor}`;
        const name = entry.actor === 'player' ? 'Player' : 'Monster';

        if (entry.action === 'miss') {
            el.textContent = `${name} \u2192 MISS`;
            el.classList.add('miss');
        } else {
            el.textContent = `${name} \u2192 ${entry.damage}${entry.crit ? ' CRIT!' : ''}`;
            if (entry.crit) el.classList.add('crit');
        }

        this.refs.floatingLog.appendChild(el);

        // 최근 3줄만 유지
        while (this.refs.floatingLog.children.length > 3) {
            this.refs.floatingLog.removeChild(this.refs.floatingLog.firstChild);
        }

        // 생성 직후 show, 1.2s 후 fade out, 1.8s 후 제거
        requestAnimationFrame(() => el.classList.add('show'));
        setTimeout(() => el.classList.add('fade'), 1200);
        setTimeout(() => { if (el.parentNode) el.parentNode.removeChild(el); }, 1800);
    },

    _showWaveBanner(waveNum, total, isBoss) {
        const banner = this.refs.waveBanner;
        if (!banner) return;
        const label = isBoss ? `BOSS WAVE` : `WAVE ${waveNum} / ${total}`;
        banner.textContent = label;
        banner.classList.toggle('boss', !!isBoss);
        banner.classList.remove('show');
        // 재적용(클래스 재지정) 위해 reflow
        void banner.offsetWidth;
        banner.classList.add('show');
    },

    // ── 결과 ──

    async _showResult(battleResult, rewards, stageId) {
        const isVictory = battleResult === 'win';

        if (isVictory) {
            const clearResult = await apiCall(3004, { stage_id: stageId });
            if (clearResult?.success) {
                Store.set('user.current_stage', clearResult.data.current_stage);
            }
        }

        Store.batch(() => {
            if (rewards.gold) Store.set('user.gold', rewards.gold);
            if (rewards.exp) Store.set('user.exp', rewards.exp);
            if (rewards.level) Store.set('user.level', rewards.level);
        });

        const dropsHtml = this._formatDrops(rewards.drops || []);

        this.refs.result.innerHTML = `
            <div class="bv-result-box ${isVictory ? 'victory' : 'defeat'}">
                <div class="bv-result-title">${isVictory ? '\u2694\uFE0F ' + t('battle_victory') : '\uD83D\uDC80 ' + t('battle_defeat')}</div>
                ${isVictory ? `
                    <div class="bv-result-rewards">
                        ${rewards.exp_gained ? `<div class="bv-reward-row">EXP <span>+${rewards.exp_gained}</span></div>` : ''}
                        ${rewards.gold_gained ? `<div class="bv-reward-row">Gold <span>+${rewards.gold_gained}</span></div>` : ''}
                        ${rewards.leveled_up ? `<div class="bv-reward-row level-up">${t('battle_level_up')}</div>` : ''}
                        ${dropsHtml ? `<div class="bv-drops-section">${dropsHtml}</div>` : ''}
                    </div>
                ` : ''}
                <div class="bv-result-actions">
                    <button class="btn btn-primary" data-action="battle-again">${t('battle_retry')}</button>
                    <button class="btn" data-action="battle-back">${t('battle_back')}</button>
                </div>
            </div>
        `;
        this.refs.result.classList.add('show');
    },

    _lastDrops: [],

    _formatDrops(drops) {
        if (!drops || drops.length === 0) return '';
        this._lastDrops = drops;

        let totalGold = 0;
        const equipDrops = [];
        const cardDrops = [];
        const matDrops = [];
        const stigmaDrops = [];

        drops.forEach((d, idx) => {
            if (d.type === 'gold') totalGold += (d.amount || 0);
            else if (d.type === 'equipment') equipDrops.push({ ...d, _idx: idx });
            else if (d.type === 'card') cardDrops.push(d);
            else if (d.type === 'material') matDrops.push(d);
            else if (d.type === 'stigma') stigmaDrops.push(d);
        });

        let html = '<div class="bv-drops-list">';
        if (totalGold > 0) {
            html += `<div class="bv-drop-row bv-drop-gold">\uD83D\uDCB0 Gold +${totalGold.toLocaleString()}</div>`;
        }
        if (equipDrops.length > 0) {
            html += `<div class="bv-drop-category">${t('drop_equipment')}</div>`;
            equipDrops.forEach(drop => {
                const eq = drop.data || {};
                const rc = { magic: 'var(--color-magic)', rare: 'var(--color-rare)', unique: 'var(--color-unique)', craft: 'var(--color-craft)' };
                const color = rc[eq.rarity] || 'var(--text-secondary)';
                html += `<div class="bv-drop-item bv-drop-equip" data-action="show-drop-detail" data-drop-idx="${drop._idx}" style="color:${color}" data-popup-trigger>
                    <span class="bv-drop-icon">\u2694</span>
                    <span class="bv-drop-name">${escapeHtml(eq.name || t('drop_equipment'))}</span>
                    <span class="bv-drop-tag">iLv ${eq.item_level || '?'}</span>
                </div>`;
            });
        }
        if (cardDrops.length > 0) {
            html += `<div class="bv-drop-category">${t('drop_card')}</div>`;
            cardDrops.forEach(drop => {
                html += `<div class="bv-drop-item bv-drop-card">\uD83C\uDCCF ${getMonsterName(drop.monster_idx)} ${t('drop_card')}</div>`;
            });
        }
        if (matDrops.length > 0) {
            const matNames = { ore: t('mat_ore'), potion: t('mat_potion'), quest_material: t('mat_quest') };
            html += `<div class="bv-drop-category">${t('drop_material')}</div>`;
            matDrops.forEach(drop => {
                const name = matNames[drop.material_type] || drop.material_type;
                html += `<div class="bv-drop-item bv-drop-mat">\uD83E\uDEA8 ${name} Lv${drop.material_id} \u00D7${drop.amount}</div>`;
            });
        }
        if (stigmaDrops.length > 0) {
            html += `<div class="bv-drop-category">${t('drop_stigma')}</div>`;
            stigmaDrops.forEach(drop => {
                html += `<div class="bv-drop-item bv-drop-stigma">\uD83D\uDD25 ${sinName(drop.sin_type)}${t('drop_stigma_of')}</div>`;
            });
        }
        html += '</div>';
        return html;
    },

    _showDropPopup(target) {
        const idx = parseInt(target.dataset.dropIdx);
        const drop = this._lastDrops[idx];
        if (!drop || drop.type !== 'equipment') return;

        const eq = drop.data || {};
        const html = `<div class="item-popup rarity-${eq.rarity || 'magic'}">` + buildItemPopupHtml(eq, {
            name: eq.name || t('drop_equipment'),
            metaText: `${rarityName(eq.rarity)} ${slotName(eq.equip_slot)} &nbsp;|&nbsp; iLv ${eq.item_level || 0} &nbsp;|&nbsp; Cost ${eq.item_cost || 0}`,
            showAffixes: true,
            cssPrefix: 'ip',
            optionLabel: (key) => { const k = `opt_${key}`; return t(k) !== k ? t(k) : key; },
            prefixLabel: t('prefix_label'),
            suffixLabel: t('suffix_label'),
            setLabel: t('set_label'),
            sinName,
        }) + '</div>';
        Popup.showSingle(html, target, { pinned: true });
    },

    // ── Phaser 초기화 ──

    _initPhaser() {
        if (this._phaserGame) return;

        const host = this.refs.phaserHost;
        const width = host.clientWidth || 600;
        const height = host.clientHeight || 300;

        const scene = new IdleBattleScene(width, height, {
            onPhase: (p) => this._onPhase(p),
            onBattleEntry: (e) => this._onBattleEntry(e),
        });
        this._battleScene = scene;

        this._phaserGame = new Phaser.Game({
            type: Phaser.AUTO,
            width, height,
            parent: host,
            transparent: true,
            scene: scene,
            physics: { default: 'none' },
        });
    },

    _destroyPhaser() {
        if (this._phaserGame) {
            this._phaserGame.destroy(true);
            this._phaserGame = null;
            this._battleScene = null;
        }
    },
};

export default BattleView;
