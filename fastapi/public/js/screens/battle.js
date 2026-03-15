/**
 * TheSevenRPG — Battle Screen
 * Phaser.js 기반 전투 연출 화면
 * 서버 시뮬레이션 결과(battle_log)를 받아 애니메이션으로 재생한다.
 *
 * 흐름: stage-select → enter_stage(3003) → monster_pool → battle_result(3001) × N
 */
import { apiCall } from '../api.js';
import { Store } from '../store.js';
import { showLoading, hideLoading } from '../utils.js';
import { getMonsterName, getStageName } from '../meta-data.js';

const BattleScreen = {
    el: null,
    refs: {},
    _phaserGame: null,
    _battleScene: null,
    _playTimer: null,

    mount(el) {
        this.el = el;

        // 매 전투마다 초기화
        el.innerHTML = '';
        delete el.dataset.initialized;

        el.innerHTML = `
            <div class="battle-screen">
                <div class="battle-top-bar">
                    <div class="battle-stage-name" id="battle-stage-name"></div>
                    <div class="battle-wave-info" id="battle-wave-info"></div>
                </div>

                <div class="battle-hud">
                    <div class="hud-player">
                        <div class="hud-name">Player</div>
                        <div class="hud-hp-bar">
                            <div class="hud-hp-fill" id="player-hp-fill" style="width:100%"></div>
                        </div>
                        <div class="hud-hp-text" id="player-hp-text"></div>
                    </div>
                    <div class="hud-vs">VS</div>
                    <div class="hud-monster">
                        <div class="hud-name" id="monster-name">Monster</div>
                        <div class="hud-hp-bar monster">
                            <div class="hud-hp-fill monster" id="monster-hp-fill" style="width:100%"></div>
                        </div>
                        <div class="hud-hp-text" id="monster-hp-text"></div>
                    </div>
                </div>

                <div class="battle-arena" id="battle-arena"></div>

                <div class="battle-log-area">
                    <div class="battle-log" id="battle-log"></div>
                </div>

                <div class="battle-result-overlay" id="battle-result-overlay"></div>
            </div>
        `;

        this.refs = {
            stageName: el.querySelector('#battle-stage-name'),
            waveInfo: el.querySelector('#battle-wave-info'),
            playerHpFill: el.querySelector('#player-hp-fill'),
            playerHpText: el.querySelector('#player-hp-text'),
            monsterName: el.querySelector('#monster-name'),
            monsterHpFill: el.querySelector('#monster-hp-fill'),
            monsterHpText: el.querySelector('#monster-hp-text'),
            arena: el.querySelector('#battle-arena'),
            log: el.querySelector('#battle-log'),
            resultOverlay: el.querySelector('#battle-result-overlay'),
        };

        this._handleEvent = this.handleEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._startBattle();
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        if (this._playTimer) {
            clearTimeout(this._playTimer);
            this._playTimer = null;
        }
        this._destroyPhaser();
    },

    /** 탭 비활성 → Phaser 일시정지 */
    onPause() {
        if (this._phaserGame && this._phaserGame.scene) {
            this._phaserGame.scene.pause('BattleScene');
        }
    },

    /** 탭 활성 → Phaser 재개 */
    onResume() {
        if (this._phaserGame && this._phaserGame.scene) {
            this._phaserGame.scene.resume('BattleScene');
        }
    },

    handleEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'battle-again':
                this._startBattle();
                break;
            case 'battle-back':
                window.location.hash = '#stage-select';
                break;
        }
    },

    // ── 전투 시작 ──

    async _startBattle() {
        const stageId = Store.get('battle.stage_id');
        if (!stageId) {
            window.location.hash = '#stage-select';
            return;
        }

        this.refs.stageName.textContent = getStageName(stageId);
        this.refs.resultOverlay.classList.remove('show');
        this.refs.log.innerHTML = '';

        // monster_pool은 enter_stage에서 이미 Store에 저장됨
        const monsterPool = Store.get('battle.monster_pool');
        if (!monsterPool || monsterPool.length === 0) {
            window.location.hash = '#stage-select';
            return;
        }

        // Wave별 순차 전투
        await this._runWaves(monsterPool, stageId);
    },

    async _runWaves(waves, stageId) {
        let totalRewards = { exp_gained: 0, gold_gained: 0, gold: 0, level: 0, exp: 0, leveled_up: false };
        let finalResult = 'win';

        for (let wi = 0; wi < waves.length; wi++) {
            const wave = waves[wi];
            this.refs.waveInfo.textContent = `Wave ${wave.wave || wi + 1} / ${waves.length}`;

            const monsters = wave.monsters || [];
            for (let mi = 0; mi < monsters.length; mi++) {
                const mob = monsters[mi];
                const monsterIdx = mob.monster_idx;
                const spawnType = mob.spawn_type || '\uC77C\uBC18';

                // 몬스터 이름 표시
                this.refs.monsterName.textContent = `${getMonsterName(monsterIdx)} (${spawnType})`;
                this.refs.monsterHpFill.style.width = '100%';
                this.refs.playerHpFill.style.width = '100%';

                // API 호출
                showLoading();
                let data;
                try {
                    const result = await apiCall(3001, {
                        monster_idx: monsterIdx,
                        spawn_type: spawnType,
                    });
                    if (!result?.success) {
                        finalResult = 'lose';
                        break;
                    }
                    data = result.data;
                } finally {
                    hideLoading();
                }

                // 전투 재생
                await this._playBattleLog(data);

                // 보상 누적
                const rw = data.rewards || {};
                totalRewards.exp_gained += rw.exp_gained || 0;
                totalRewards.gold_gained += rw.gold_gained || 0;
                if (rw.gold !== undefined) totalRewards.gold = rw.gold;
                if (rw.level !== undefined) totalRewards.level = rw.level;
                if (rw.exp !== undefined) totalRewards.exp = rw.exp;
                if (rw.leveled_up) totalRewards.leveled_up = true;

                // 패배 또는 시간초과 시 중단
                if (data.result !== 'win') {
                    finalResult = data.result;
                    break;
                }
            }

            if (finalResult !== 'win') break;
        }

        this._showResult(finalResult, totalRewards, stageId);
    },

    // ── 전투 로그 재생 (Promise) ──

    _playBattleLog(data) {
        return new Promise((resolve) => {
            const log = data.battle_log || [];

            // HP 추정 (첫 공격의 target_hp + damage = maxHP)
            const firstPlayerAtk = log.find(e => e.actor === 'player' && e.action === 'attack');
            const firstMonsterAtk = log.find(e => e.actor === 'monster' && e.action === 'attack');

            const playerMaxHp = firstMonsterAtk
                ? firstMonsterAtk.target_hp + firstMonsterAtk.damage
                : 200;
            const monsterMaxHp = firstPlayerAtk
                ? firstPlayerAtk.target_hp + firstPlayerAtk.damage
                : 100;

            this.refs.playerHpText.textContent = `${playerMaxHp} / ${playerMaxHp}`;
            this.refs.monsterHpText.textContent = `${monsterMaxHp} / ${monsterMaxHp}`;
            this.refs.playerHpFill.style.width = '100%';
            this.refs.monsterHpFill.style.width = '100%';

            this._initPhaser();

            let i = 0;
            const delay = 350;

            const playNext = () => {
                if (i >= log.length) {
                    setTimeout(resolve, 400);
                    return;
                }

                const entry = log[i];
                i++;

                if (entry.actor === 'player') {
                    const hp = Math.max(0, entry.target_hp);
                    const pct = monsterMaxHp > 0 ? (hp / monsterMaxHp * 100) : 0;
                    this.refs.monsterHpFill.style.width = pct + '%';
                    this.refs.monsterHpText.textContent = `${hp} / ${monsterMaxHp}`;
                } else {
                    const hp = Math.max(0, entry.target_hp);
                    const pct = playerMaxHp > 0 ? (hp / playerMaxHp * 100) : 0;
                    this.refs.playerHpFill.style.width = pct + '%';
                    this.refs.playerHpText.textContent = `${hp} / ${playerMaxHp}`;
                }

                if (this._battleScene) {
                    this._battleScene.playAction(entry);
                }

                this._appendLog(entry);

                this._playTimer = setTimeout(playNext, delay);
            };

            this._playTimer = setTimeout(playNext, 600);
        });
    },

    _appendLog(entry) {
        const el = document.createElement('div');
        el.className = `log-entry ${entry.actor}`;
        const name = entry.actor === 'player' ? 'Player' : 'Monster';

        if (entry.action === 'miss') {
            el.textContent = `[${entry.turn}] ${name} \u2192 MISS`;
            el.classList.add('miss');
        } else {
            el.textContent = `[${entry.turn}] ${name} \u2192 ${entry.damage}${entry.crit ? ' CRIT!' : ''}`;
            if (entry.crit) el.classList.add('crit');
        }

        this.refs.log.appendChild(el);
        this.refs.log.scrollTop = this.refs.log.scrollHeight;
    },

    // ── 결과 표시 ──

    async _showResult(battleResult, rewards, stageId) {
        const isVictory = battleResult === 'win';

        if (isVictory) {
            const clearResult = await apiCall(3004, { stage_id: stageId });
            if (clearResult?.success) {
                Store.set('user.current_stage', clearResult.data.current_stage);
            }
        }

        if (rewards.gold) Store.set('user.gold', rewards.gold);
        if (rewards.exp) Store.set('user.exp', rewards.exp);
        if (rewards.level) Store.set('user.level', rewards.level);

        this.refs.resultOverlay.innerHTML = `
            <div class="battle-result-box ${isVictory ? 'victory' : 'defeat'}">
                <div class="battle-result-title">${isVictory ? '\u2694\uFE0F \uC2B9\uB9AC!' : '\u{1F480} \uD328\uBC30...'}</div>
                ${isVictory ? `
                    <div class="battle-result-rewards">
                        ${rewards.exp_gained ? `<div class="reward-row">EXP <span>+${rewards.exp_gained}</span></div>` : ''}
                        ${rewards.gold_gained ? `<div class="reward-row">Gold <span>+${rewards.gold_gained}</span></div>` : ''}
                        ${rewards.leveled_up ? '<div class="reward-row level-up">LEVEL UP!</div>' : ''}
                    </div>
                ` : ''}
                <div class="battle-result-actions">
                    <button class="btn btn-primary" data-action="battle-again">\uC7AC\uB3C4\uC804</button>
                    <button class="btn" data-action="battle-back">\uB3CC\uC544\uAC00\uAE30</button>
                </div>
            </div>
        `;

        this.refs.resultOverlay.classList.add('show');
    },

    // ── Phaser.js ──

    _initPhaser() {
        this._destroyPhaser();

        const arenaEl = this.refs.arena;
        const width = arenaEl.clientWidth || 360;
        const height = arenaEl.clientHeight || 200;

        const scene = new BattleScene(width, height);
        this._battleScene = scene;

        this._phaserGame = new Phaser.Game({
            type: Phaser.AUTO,
            width,
            height,
            parent: arenaEl,
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

// ── Phaser Scene ──

class BattleScene extends Phaser.Scene {
    constructor(w, h) {
        super({ key: 'BattleScene' });
        this._w = w;
        this._h = h;
        this.playerSprite = null;
        this.monsterSprite = null;
    }

    create() {
        const cx = this._w / 2;
        const cy = this._h / 2;

        this.playerSprite = this.add.rectangle(cx - 80, cy, 40, 50, 0x42a5f5);
        this.playerSprite.setStrokeStyle(2, 0x90caf9);
        this.add.text(cx - 80, cy + 35, 'Player', {
            fontSize: '11px', color: '#90caf9', fontFamily: 'sans-serif',
        }).setOrigin(0.5);

        this.monsterSprite = this.add.rectangle(cx + 80, cy, 45, 55, 0xe53935);
        this.monsterSprite.setStrokeStyle(2, 0xef9a9a);
        this.add.text(cx + 80, cy + 38, 'Monster', {
            fontSize: '11px', color: '#ef9a9a', fontFamily: 'sans-serif',
        }).setOrigin(0.5);
    }

    playAction(entry) {
        if (!this.playerSprite || !this.monsterSprite) return;

        const cx = this._w / 2;

        if (entry.actor === 'player') {
            this.tweens.add({
                targets: this.playerSprite,
                x: cx + 30, duration: 100, yoyo: true, ease: 'Power2',
            });
            if (entry.action === 'attack') {
                this._showDamage(cx + 80, this._h / 2 - 35, entry.damage, entry.crit);
                this._flashSprite(this.monsterSprite);
            } else {
                this._showMiss(cx + 80, this._h / 2 - 35);
            }
        } else {
            this.tweens.add({
                targets: this.monsterSprite,
                x: cx - 30, duration: 100, yoyo: true, ease: 'Power2',
            });
            if (entry.action === 'attack') {
                this._showDamage(cx - 80, this._h / 2 - 35, entry.damage, entry.crit);
                this._flashSprite(this.playerSprite);
            } else {
                this._showMiss(cx - 80, this._h / 2 - 35);
            }
        }
    }

    _showDamage(x, y, damage, isCrit) {
        const text = this.add.text(x, y, `${isCrit ? '\u2757' : ''}${damage}`, {
            fontSize: isCrit ? '18px' : '14px',
            color: isCrit ? '#ffeb3b' : '#ffffff',
            fontFamily: 'sans-serif',
            fontStyle: isCrit ? 'bold' : 'normal',
            stroke: '#000', strokeThickness: 2,
        }).setOrigin(0.5);

        this.tweens.add({
            targets: text, y: y - 30, alpha: 0, duration: 600,
            ease: 'Power2', onComplete: () => text.destroy(),
        });
    }

    _showMiss(x, y) {
        const text = this.add.text(x, y, 'MISS', {
            fontSize: '13px', color: '#999999', fontFamily: 'sans-serif',
            stroke: '#000', strokeThickness: 2,
        }).setOrigin(0.5);

        this.tweens.add({
            targets: text, y: y - 25, alpha: 0, duration: 500,
            onComplete: () => text.destroy(),
        });
    }

    _flashSprite(sprite) {
        const originalFillColor = sprite.fillColor;
        sprite.setFillStyle(0xffffff);
        this.time.delayedCall(80, () => sprite.setFillStyle(originalFillColor));
    }
}

export default BattleScreen;
