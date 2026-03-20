/**
 * TheSevenRPG — Battle View (우측 전투 모드)
 * 서버 battle_log를 Phaser 애니메이션으로 재생
 *
 * Phaser 최적화:
 *   Game 인스턴스는 mount 시 1회 생성, unmount 시 파괴.
 *   몬스터 교체 시 swapMonster()로 스프라이트만 교체.
 */
import { apiCall } from '../../api.js';
import { Store } from '../../store.js';
import { showLoading, hideLoading, escapeHtml, setupEventDelegation, teardown, buildItemPopupHtml } from '../../utils.js';
import { getMonsterName, getStageName } from '../../meta-data.js';
import { t, sinName, rarityName, slotName } from '../../i18n/index.js';
import MainScreen from '../../main.js';
import Popup from '../../popup.js';

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
        setupEventDelegation(this, el);

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

                <div class="bv-arena" id="bv-arena"></div>

                <div class="bv-log-area">
                    <div class="bv-log" id="bv-log"></div>
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
            arena: el.querySelector('#bv-arena'),
            log: el.querySelector('#bv-log'),
            result: el.querySelector('#bv-result'),
        };

        this._initPhaser();
        this._startBattle();
    },

    unmount() {
        teardown(this);
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
        this.refs.log.innerHTML = '';

        this.refs.arena.style.backgroundImage = `url('${getStageBgUrl(stageId)}')`;
        this.refs.arena.style.backgroundSize = 'cover';
        this.refs.arena.style.backgroundPosition = 'center';

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

                await this._playBattleLog(data, monsterIdx, spawnType);

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

    // ── battle_log 재생 ──

    _playBattleLog(data, monsterIdx, spawnType) {
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

            // 스프라이트 교체 (Phaser 재생성 없음)
            if (this._battleScene) {
                this._battleScene.swapMonster(monsterIdx, spawnType);
            }

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

    // ── Phaser (1회 생성, 스프라이트만 교체) ──

    _initPhaser() {
        if (this._phaserGame) return;

        const arenaEl = this.refs.arena;
        const width = arenaEl.clientWidth || 600;
        const height = arenaEl.clientHeight || 300;

        const scene = new BattlePhaserScene(width, height);
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

const SPAWN_TINT = {
    '\uC815\uC608':     0x4488ff,
    '\uBCF4\uC2A4':     0xff4444,
    '\uCC55\uD130\uBCF4\uC2A4': 0xffaa00,
};

class BattlePhaserScene extends Phaser.Scene {
    constructor(w, h) {
        super({ key: 'BattleScene' });
        this._w = w;
        this._h = h;
        this._spawnType = '\uC77C\uBC18';
        this.playerSprite = null;
        this.monsterSprite = null;
        this._monsterLabel = null;
    }

    preload() {
        this.load.on('loaderror', () => {});
        this.load.image('player', '/assets/sprites/character.png');
    }

    create() {
        this._createPlayerSprite();
    }

    /** 몬스터 스프라이트를 교체한다 (Phaser Game 재생성 없음) */
    swapMonster(monsterIdx, spawnType) {
        this._spawnType = spawnType || '\uC77C\uBC18';

        if (this.monsterSprite) { this.monsterSprite.destroy(); this.monsterSprite = null; }
        if (this._monsterLabel) { this._monsterLabel.destroy(); this._monsterLabel = null; }

        const textureKey = `monster_${monsterIdx}`;

        if (this.textures.exists(textureKey)) {
            this._createMonsterSprite(textureKey);
        } else {
            this.load.image(textureKey, `/assets/sprites/monster_${monsterIdx}.png`);
            this.load.once('complete', () => this._createMonsterSprite(textureKey));
            this.load.once('loaderror', () => this._createMonsterFallback());
            this.load.start();
        }
    }

    _createPlayerSprite() {
        const cx = this._w / 2;
        const bottom = this._h - 10;

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
    }

    _createMonsterSprite(textureKey) {
        const cx = this._w / 2;
        const bottom = this._h - 10;
        const tint = SPAWN_TINT[this._spawnType];

        this.monsterSprite = this.add.image(cx + 180, bottom, textureKey);
        this.monsterSprite.setDisplaySize(240, 240);
        this.monsterSprite.setOrigin(0.5, 1.0);
        if (tint) this.monsterSprite.setTint(tint);
    }

    _createMonsterFallback() {
        const cx = this._w / 2;
        const bottom = this._h - 10;
        const tint = SPAWN_TINT[this._spawnType];
        const rectColor = tint || 0xe53935;

        this.monsterSprite = this.add.rectangle(cx + 180, bottom - 35, 56, 70, rectColor);
        this.monsterSprite.setStrokeStyle(2, tint ? 0xffffff : 0xef9a9a);
        this._monsterLabel = this.add.text(cx + 180, bottom, 'Monster', {
            fontSize: '12px', color: tint ? '#ffffff' : '#ef9a9a', fontFamily: 'sans-serif',
        }).setOrigin(0.5);
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
            const origTint = sprite.tintTopLeft;
            const hadTint = origTint !== 0xffffff;
            sprite.setTintFill(0xffffff);
            this.time.delayedCall(80, () => {
                sprite.clearTint();
                if (hadTint) sprite.setTint(origTint);
            });
        } else if (sprite.setFillStyle) {
            const orig = sprite.fillColor;
            sprite.setFillStyle(0xffffff);
            this.time.delayedCall(80, () => sprite.setFillStyle(orig));
        }
    }
}

export default BattleView;
