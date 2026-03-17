/**
 * TheSevenRPG — Battle View (우측 전투 모드)
 * 서버 battle_log를 Phaser 애니메이션으로 재생
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { showLoading, hideLoading } from '../../utils.js';
import { getMonsterName, getStageName } from '../../meta-data.js';
import MainScreen from '../../main.js';

/** stage_id → 배경 이미지 경로 */
function getStageBgUrl(stageId) {
    return `/assets/backgrounds/background_stage_${stageId}.png`;
}

const BattleView = {
    el: null,
    refs: {},
    _phaserGame: null,
    _battleScene: null,
    _playTimer: null,

    mount(el, data) {
        this.el = el;

        el.innerHTML = `
            <div class="bv-screen">
                <div class="bv-top-bar">
                    <div class="bv-stage-name" id="bv-stage-name"></div>
                    <div class="bv-wave-info" id="bv-wave-info"></div>
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

                <div class="bv-arena" id="bv-arena"></div>

                <div class="bv-log-area">
                    <div class="bv-log" id="bv-log"></div>
                </div>

                <div class="bv-result-overlay" id="bv-result"></div>
            </div>
        `;

        this.refs = {
            stageName: el.querySelector('#bv-stage-name'),
            waveInfo: el.querySelector('#bv-wave-info'),
            playerHp: el.querySelector('#bv-player-hp'),
            playerHpText: el.querySelector('#bv-player-hp-text'),
            monsterName: el.querySelector('#bv-monster-name'),
            monsterHp: el.querySelector('#bv-monster-hp'),
            monsterHpText: el.querySelector('#bv-monster-hp-text'),
            arena: el.querySelector('#bv-arena'),
            log: el.querySelector('#bv-log'),
            result: el.querySelector('#bv-result'),
        };

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._startBattle();
    },

    unmount() {
        if (this._handleEvent && this.el) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        if (this._playTimer) {
            clearTimeout(this._playTimer);
            this._playTimer = null;
        }
        this._destroyPhaser();
    },

    onVisibilityChange(hidden) {
        if (this._phaserGame && this._phaserGame.scene) {
            if (hidden) this._phaserGame.scene.pause('BattleScene');
            else this._phaserGame.scene.resume('BattleScene');
        }
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'battle-again':
                this._startBattle();
                break;
            case 'battle-back':
                MainScreen.switchRightView('town');
                break;
        }
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
        this.refs.log.innerHTML = '';

        // 스테이지 배경 적용
        this.refs.arena.style.backgroundImage = `url('${getStageBgUrl(stageId)}')`;
        this.refs.arena.style.backgroundSize = 'cover';
        this.refs.arena.style.backgroundPosition = 'center';

        const monsterPool = Store.get('battle.monster_pool');
        if (!monsterPool || monsterPool.length === 0) {
            MainScreen.switchRightView('town');
            return;
        }

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

                this.refs.monsterName.textContent = `${getMonsterName(monsterIdx)} (${spawnType})`;
                this.refs.monsterHp.style.width = '100%';
                this.refs.playerHp.style.width = '100%';

                showLoading();
                let data;
                try {
                    const result = await apiCall(3001, { monster_idx: monsterIdx, spawn_type: spawnType });
                    if (!result?.success) { finalResult = 'lose'; break; }
                    data = result.data;
                } finally {
                    hideLoading();
                }

                await this._playBattleLog(data, monsterIdx);

                const rw = data.rewards || {};
                totalRewards.exp_gained += rw.exp_gained || 0;
                totalRewards.gold_gained += rw.gold_gained || 0;
                if (rw.gold !== undefined) totalRewards.gold = rw.gold;
                if (rw.level !== undefined) totalRewards.level = rw.level;
                if (rw.exp !== undefined) totalRewards.exp = rw.exp;
                if (rw.leveled_up) totalRewards.leveled_up = true;

                if (data.result !== 'win') { finalResult = data.result; break; }
            }
            if (finalResult !== 'win') break;
        }

        this._showResult(finalResult, totalRewards, stageId);
    },

    // ── battle_log 재생 ──

    _playBattleLog(data, monsterIdx) {
        return new Promise((resolve) => {
            const log = data.battle_log || [];

            const firstPlayerAtk = log.find(e => e.actor === 'player' && e.action === 'attack');
            const firstMonsterAtk = log.find(e => e.actor === 'monster' && e.action === 'attack');

            const playerMaxHp = firstMonsterAtk ? firstMonsterAtk.target_hp + firstMonsterAtk.damage : 200;
            const monsterMaxHp = firstPlayerAtk ? firstPlayerAtk.target_hp + firstPlayerAtk.damage : 100;

            this.refs.playerHpText.textContent = `${playerMaxHp} / ${playerMaxHp}`;
            this.refs.monsterHpText.textContent = `${monsterMaxHp} / ${monsterMaxHp}`;
            this.refs.playerHp.style.width = '100%';
            this.refs.monsterHp.style.width = '100%';

            this._initPhaser(monsterIdx);

            let i = 0;
            const delay = 350;

            const playNext = () => {
                if (i >= log.length) { setTimeout(resolve, 400); return; }

                const entry = log[i];
                i++;

                if (entry.actor === 'player') {
                    const hp = Math.max(0, entry.target_hp);
                    this.refs.monsterHp.style.width = (monsterMaxHp > 0 ? hp / monsterMaxHp * 100 : 0) + '%';
                    this.refs.monsterHpText.textContent = `${hp} / ${monsterMaxHp}`;
                } else {
                    const hp = Math.max(0, entry.target_hp);
                    this.refs.playerHp.style.width = (playerMaxHp > 0 ? hp / playerMaxHp * 100 : 0) + '%';
                    this.refs.playerHpText.textContent = `${hp} / ${playerMaxHp}`;
                }

                if (this._battleScene) this._battleScene.playAction(entry);
                this._appendLog(entry);

                this._playTimer = setTimeout(playNext, delay);
            };

            this._playTimer = setTimeout(playNext, 600);
        });
    },

    _appendLog(entry) {
        const el = document.createElement('div');
        el.className = `bv-log-entry ${entry.actor}`;
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

    // ── 결과 ──

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

        this.refs.result.innerHTML = `
            <div class="bv-result-box ${isVictory ? 'victory' : 'defeat'}">
                <div class="bv-result-title">${isVictory ? '\u2694\uFE0F 승리!' : '\u{1F480} 패배...'}</div>
                ${isVictory ? `
                    <div class="bv-result-rewards">
                        ${rewards.exp_gained ? `<div class="bv-reward-row">EXP <span>+${rewards.exp_gained}</span></div>` : ''}
                        ${rewards.gold_gained ? `<div class="bv-reward-row">Gold <span>+${rewards.gold_gained}</span></div>` : ''}
                        ${rewards.leveled_up ? '<div class="bv-reward-row level-up">LEVEL UP!</div>' : ''}
                    </div>
                ` : ''}
                <div class="bv-result-actions">
                    <button class="btn btn-primary" data-action="battle-again">재도전</button>
                    <button class="btn" data-action="battle-back">마을로</button>
                </div>
            </div>
        `;
        this.refs.result.classList.add('show');
    },

    // ── Phaser ──

    _initPhaser(monsterIdx) {
        this._destroyPhaser();

        const arenaEl = this.refs.arena;
        const width = arenaEl.clientWidth || 600;
        const height = arenaEl.clientHeight || 300;

        const scene = new BattlePhaserScene(width, height, monsterIdx || 0);
        this._battleScene = scene;

        this._phaserGame = new Phaser.Game({
            type: Phaser.AUTO,
            width, height,
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

class BattlePhaserScene extends Phaser.Scene {
    constructor(w, h, monsterIdx) {
        super({ key: 'BattleScene' });
        this._w = w;
        this._h = h;
        this._monsterIdx = monsterIdx;
        this.playerSprite = null;
        this.monsterSprite = null;
    }

    preload() {
        // 로드 실패 시 무시 (create에서 폴백 처리)
        this.load.on('loaderror', () => {});
        this.load.image('player', '/assets/sprites/character.png');
        this.load.image('monster', `/assets/sprites/monster_${this._monsterIdx}.png`);
    }

    create() {
        const cx = this._w / 2;
        const cy = this._h / 2 + 20;

        const bottom = this._h - 10;

        // 캐릭터 (좌측) — 이미지 있으면 스프라이트, 없으면 사각형
        if (this.textures.exists('player')) {
            this.playerSprite = this.add.image(cx - 180, bottom, 'player');
            this.playerSprite.setDisplaySize(240, 240);
            this.playerSprite.setOrigin(0.5, 1.0);
        } else {
            this.playerSprite = this.add.rectangle(cx - 180, bottom - 32, 50, 64, 0x42a5f5);
            this.playerSprite.setStrokeStyle(2, 0x90caf9);
            this.add.text(cx - 120, bottom, 'Player', {
                fontSize: '12px', color: '#90caf9', fontFamily: 'sans-serif',
            }).setOrigin(0.5);
        }

        // 몬스터 (우측) — 이미지 있으면 스프라이트, 없으면 사각형
        if (this.textures.exists('monster')) {
            this.monsterSprite = this.add.image(cx + 180, bottom, 'monster');
            this.monsterSprite.setDisplaySize(240, 240);
            this.monsterSprite.setOrigin(0.5, 1.0);
        } else {
            this.monsterSprite = this.add.rectangle(cx + 180, bottom - 35, 56, 70, 0xe53935);
            this.monsterSprite.setStrokeStyle(2, 0xef9a9a);
            this.add.text(cx + 180, bottom, 'Monster', {
                fontSize: '12px', color: '#ef9a9a', fontFamily: 'sans-serif',
            }).setOrigin(0.5);
        }
    }

    playAction(entry) {
        if (!this.playerSprite || !this.monsterSprite) return;
        const cx = this._w / 2;

        const dmgY = this._h - 120;

        if (entry.actor === 'player') {
            this.tweens.add({ targets: this.playerSprite, x: cx + 60, duration: 100, yoyo: true, ease: 'Power2' });
            if (entry.action === 'attack') {
                this._showDamage(cx + 180, dmgY, entry.damage, entry.crit);
                this._flashSprite(this.monsterSprite);
            } else {
                this._showMiss(cx + 180, dmgY);
            }
        } else {
            this.tweens.add({ targets: this.monsterSprite, x: cx - 60, duration: 100, yoyo: true, ease: 'Power2' });
            if (entry.action === 'attack') {
                this._showDamage(cx - 180, dmgY, entry.damage, entry.crit);
                this._flashSprite(this.playerSprite);
            } else {
                this._showMiss(cx - 180, dmgY);
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
        this.tweens.add({ targets: text, y: y - 30, alpha: 0, duration: 600, ease: 'Power2', onComplete: () => text.destroy() });
    }

    _showMiss(x, y) {
        const text = this.add.text(x, y, 'MISS', {
            fontSize: '13px', color: '#999999', fontFamily: 'sans-serif', stroke: '#000', strokeThickness: 2,
        }).setOrigin(0.5);
        this.tweens.add({ targets: text, y: y - 25, alpha: 0, duration: 500, onComplete: () => text.destroy() });
    }

    _flashSprite(sprite) {
        if (sprite.setTintFill) {
            sprite.setTintFill(0xffffff);
            this.time.delayedCall(80, () => sprite.clearTint());
        } else if (sprite.setFillStyle) {
            const orig = sprite.fillColor;
            sprite.setFillStyle(0xffffff);
            this.time.delayedCall(80, () => sprite.setFillStyle(orig));
        }
    }
}

export default BattleView;
