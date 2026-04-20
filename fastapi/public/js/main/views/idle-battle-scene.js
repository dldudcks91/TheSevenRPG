/**
 * IdleBattleScene — 횡스크롤 idle 오토배틀 Phaser Scene.
 * 서버 battle_log를 받아 4페이즈 FSM(SPAWN → APPROACH → EXCHANGE → DEATH)으로 재해석 재생한다.
 * 전투 공식·결과는 서버 결과 그대로 사용하며, 이동/조우는 순전히 시각 좌표.
 *
 * 플레이어는 LpcSprite 우선 시도, 로드 실패 시 PNG StaticSprite로 폴백.
 * 몬스터는 Iter 3 전까지는 PNG 전용(StaticSprite).
 */
import { StaticSprite, RectSprite } from '../../sprites/static-sprite.js';
import { LpcSprite } from '../../sprites/lpc-sprite.js';
import { CHARACTER_LAYERS, CHARACTER_ANIMS, MONSTER_MANIFEST, SPAWN_SIZE_SCALE } from '../../sprites/lpc-manifest.js';

const PLAYER_X_RATIO = 0.22;
const ENCOUNTER_X_RATIO = 0.58;
const SPAWN_X_OFFSET = 60;

const APPROACH_DURATION = 800;
const TURN_DELAY_MS = 350;
const PRE_EXCHANGE_DELAY = 200;
const POST_EXCHANGE_DELAY = 300;
const DEATH_FADE_MS = 400;
const POST_DEATH_DELAY = 250;

const SPRITE_SIZE = 220;

const SPAWN_TINT = {
    '\uC815\uC608':     0x4488ff,  // 정예
    '\uBCF4\uC2A4':     0xff4444,  // 보스
    '\uCC55\uD130\uBCF4\uC2A4': 0xffaa00,  // 챕터보스
};

export class IdleBattleScene extends Phaser.Scene {
    constructor(width, height, callbacks = {}) {
        super({ key: 'IdleBattleScene' });
        this._w = width;
        this._h = height;
        this._callbacks = callbacks;
        this.player = null;
        this.monster = null;
        this._ready = false;
        this._readyWaiters = [];
    }

    preload() {
        this.load.on('loaderror', () => {});
        this.load.image('player', '/assets/sprites/character.png');
    }

    create() {
        this._createPlayer().then(() => this._setReady());
    }

    _setReady() {
        this._ready = true;
        this._callbacks.onReady?.();
        const waiters = this._readyWaiters;
        this._readyWaiters = [];
        for (const r of waiters) r();
    }

    _waitReady() {
        if (this._ready) return Promise.resolve();
        return new Promise((r) => this._readyWaiters.push(r));
    }

    async _createPlayer() {
        const x = Math.round(this._w * PLAYER_X_RATIO);
        const y = this._h - 10;

        // 1순위: LpcSprite (레이어 합성 성공 시)
        try {
            const lpc = new LpcSprite(this, x, y, {
                textureKey: 'lpc_player',
                layers: CHARACTER_LAYERS,
                anims: CHARACTER_ANIMS,
                facing: 'E',
                size: SPRITE_SIZE,
                persistent: 'idle',
            });
            await lpc.init();
            this.player = lpc;
            return;
        } catch (e) {
            console.warn('[IdleBattle] LPC 플레이어 실패, PNG 폴백:', e.message);
        }

        // 2순위: PNG StaticSprite
        if (this.textures.exists('player')) {
            this.player = new StaticSprite(this, x, y, 'player', { facing: 'E', size: SPRITE_SIZE });
        } else {
            this.player = new RectSprite(this, x, y, 0x42a5f5, { facing: 'E', width: 50, height: 64 });
        }
        this.player.play('idle');
    }

    async _spawnMonster(monsterIdx, spawnType) {
        const spawnX = this._w + SPAWN_X_OFFSET;
        const y = this._h - 10;
        const tint = SPAWN_TINT[spawnType] || null;
        const sizeScale = SPAWN_SIZE_SCALE[spawnType] || 1.0;
        const size = Math.round(SPRITE_SIZE * sizeScale);

        // 1순위: 몬스터 LPC 매니페스트
        const manifest = MONSTER_MANIFEST[monsterIdx];
        if (manifest) {
            try {
                const lpc = new LpcSprite(this, spawnX, y, {
                    textureKey: `lpc_monster_${monsterIdx}`,
                    layers: manifest.layers,
                    anims: manifest.anims,
                    facing: 'W',
                    size,
                    tint,
                    persistent: 'walk',
                });
                await lpc.init();
                this.monster = lpc;
                return;
            } catch (e) {
                console.warn(`[IdleBattle] 몬스터 LPC 실패(idx=${monsterIdx}), PNG 폴백:`, e.message);
            }
        }

        // 2순위: 기존 monster_{idx}.png
        const textureKey = `monster_${monsterIdx}`;
        if (this.textures.exists(textureKey)) {
            this.monster = new StaticSprite(this, spawnX, y, textureKey, { facing: 'W', size, tint });
            return;
        }

        // 로드 시도 → 실패 시 컬러박스 (3순위)
        await new Promise((resolve) => {
            const onDone = () => {
                if (this.textures.exists(textureKey)) {
                    this.monster = new StaticSprite(this, spawnX, y, textureKey, { facing: 'W', size, tint });
                } else {
                    const color = tint || 0xe53935;
                    const boxSize = Math.round(70 * sizeScale);
                    this.monster = new RectSprite(this, spawnX, y, color, {
                        facing: 'W', width: Math.round(56 * sizeScale), height: boxSize,
                    });
                }
                resolve();
            };
            this.load.image(textureKey, `/assets/sprites/monster_${monsterIdx}.png`);
            this.load.once('complete', onDone);
            this.load.once('loaderror', onDone);
            this.load.start();
        });
    }

    /**
     * 몬스터 1기 라이프사이클 재생.
     * @param {object} data — 서버 3001 응답 (battle_log, result)
     * @param {number} monsterIdx
     * @param {string} spawnType
     */
    async playMob(data, monsterIdx, spawnType) {
        await this._waitReady();

        if (this.monster) { this.monster.destroy(); this.monster = null; }

        // SPAWN
        this._callbacks.onPhase?.('spawn');
        await this._spawnMonster(monsterIdx, spawnType);

        // APPROACH
        this._callbacks.onPhase?.('approach');
        this.monster.play('walk');
        this.player.play('walk');

        const encounterX = Math.round(this._w * ENCOUNTER_X_RATIO);
        await this.monster.moveTo(encounterX, APPROACH_DURATION);

        this.monster.play('idle');
        this.player.play('idle');

        // EXCHANGE
        this._callbacks.onPhase?.('exchange');
        await this._wait(PRE_EXCHANGE_DELAY);

        const log = data.battle_log || [];
        for (let i = 0; i < log.length; i++) {
            const entry = log[i];
            this._playEntry(entry);
            this._callbacks.onBattleEntry?.(entry);
            await this._wait(TURN_DELAY_MS);
        }
        await this._wait(POST_EXCHANGE_DELAY);

        // DEATH
        this._callbacks.onPhase?.('death');
        if (data.result === 'win') {
            await this.monster.fadeOut(DEATH_FADE_MS);
        } else {
            await this.player.fadeOut(DEATH_FADE_MS);
        }
        await this._wait(POST_DEATH_DELAY);
    }

    _playEntry(entry) {
        const dmgY = Math.round(this._h * 0.35);
        const isPlayerAct = entry.actor === 'player';
        const attacker = isPlayerAct ? this.player : this.monster;
        const defender = isPlayerAct ? this.monster : this.player;
        if (!attacker || !defender) return;

        attacker.play('attack');

        if (entry.action === 'attack') {
            this._showDamage(defender.x, dmgY, entry.damage, entry.crit);
            defender.play('hurt');
        } else {
            this._showMiss(defender.x, dmgY);
        }
    }

    _showDamage(x, y, damage, isCrit) {
        const text = this.add.text(x, y, `${isCrit ? '!' : ''}${damage}`, {
            fontSize: isCrit ? '20px' : '15px',
            color: isCrit ? '#ffeb3b' : '#ffffff',
            fontFamily: 'sans-serif',
            fontStyle: isCrit ? 'bold' : 'normal',
            stroke: '#000', strokeThickness: 3,
        }).setOrigin(0.5);
        this.tweens.add({
            targets: text,
            y: y - 34,
            alpha: 0,
            duration: 600,
            ease: 'Power2',
            onComplete: () => text.destroy(),
        });
    }

    _showMiss(x, y) {
        const text = this.add.text(x, y, 'MISS', {
            fontSize: '13px', color: '#cccccc', fontFamily: 'sans-serif',
            stroke: '#000', strokeThickness: 2,
        }).setOrigin(0.5);
        this.tweens.add({
            targets: text,
            y: y - 25,
            alpha: 0,
            duration: 500,
            onComplete: () => text.destroy(),
        });
    }

    /** 전투 재시작 시 호출 — 몬스터/플레이어를 파괴하고 플레이어를 다시 만든다. */
    async resetForNewBattle() {
        if (this.monster) { this.monster.destroy(); this.monster = null; }
        if (this.player) { this.player.destroy(); this.player = null; }
        this._ready = false;
        await this._createPlayer();
        this._setReady();
    }

    _wait(ms) {
        return new Promise((resolve) => this.time.delayedCall(ms, resolve));
    }
}
