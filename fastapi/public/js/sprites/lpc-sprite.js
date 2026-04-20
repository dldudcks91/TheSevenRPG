/**
 * LpcSprite — LPC 레이어 합성 기반 Phaser 스프라이트 래퍼.
 *   - 각 애니메이션별 시트를 사전 합성해 Phaser 텍스처로 한 번만 등록
 *   - 프레임 교체는 Phaser 애니메이션으로 수행 (런타임 texture.refresh 0회)
 *
 * StaticSprite와 동일한 외부 시그니처(play, moveTo, fadeOut, setX, x, y, destroy)를 제공한다.
 * 전투(IdleBattleScene)에서는 플레이어·몬스터 동일 인터페이스로 다룬다.
 */
import { LPC_BASE_URL, DIR_TO_ROW, STATE_TO_ANIM } from './lpc-manifest.js';

const FRAME = 64;
const DEFAULT_DISPLAY_SIZE = 220;

const ATTACK_LUNGE_PX = 40;
const ATTACK_DURATION = 100;

function loadImage(src) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error(`LPC load fail: ${src}`));
        img.src = src;
    });
}

/**
 * 레이어를 한 애니의 시트로 합성한다.
 * 반환: HTMLCanvasElement (너비/높이는 최대 레이어 크기). 전체 레이어 실패 시 null.
 */
export async function composeLpcSheet(layers, anim, baseUrl = LPC_BASE_URL) {
    const loaded = [];
    for (const layer of layers) {
        const path = layer.template.replace('{anim}', anim);
        try {
            const img = await loadImage(`${baseUrl}/${path}`);
            loaded.push({ img, z: layer.z });
        } catch (e) {
            console.warn(`[LPC] ${anim} 레이어 실패: ${path}`);
        }
    }
    if (loaded.length === 0) return null;

    loaded.sort((a, b) => a.z - b.z);

    const w = Math.max(...loaded.map(l => l.img.width));
    const h = Math.max(...loaded.map(l => l.img.height));
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    for (const { img } of loaded) ctx.drawImage(img, 0, 0);
    return canvas;
}

export class LpcSprite {
    /**
     * @param {Phaser.Scene} scene
     * @param {number} x
     * @param {number} y
     * @param {object} options
     *   - textureKey: 글로벌 유일 키 (e.g. 'lpc_player'). 여러 인스턴스 충돌 방지.
     *   - layers: [{template, z}]
     *   - anims: { <name>: {frames, frameRate, loop, directional} }
     *   - facing: 'N'|'W'|'S'|'E' (default 'E')
     *   - size: 표시 크기 (default 220)
     *   - baseUrl: LPC 에셋 루트 (default LPC_BASE_URL)
     *   - tint: 초기 틴트 (선택)
     *   - persistent: 초기 지속 상태 (default 'idle')
     */
    constructor(scene, x, y, options) {
        this.scene = scene;
        this._opts = options;
        this._facing = options.facing || 'E';
        this._baseX = x;
        this._baseY = y;
        this._size = options.size || DEFAULT_DISPLAY_SIZE;
        this._tint = options.tint || null;
        this._persistent = options.persistent || 'idle';

        this._anims = {};      // { animName: { texKey, spec, animKeys: {dir: key} } }
        this.sprite = null;
        this._actionTween = null;
        this._walkTween = null;

        this._ready = false;
    }

    async init() {
        const { textureKey, layers, anims, baseUrl } = this._opts;
        const base = baseUrl || LPC_BASE_URL;

        for (const [animName, spec] of Object.entries(anims)) {
            const canvas = await composeLpcSheet(layers, animName, base);
            if (!canvas) continue;

            const texKey = `${textureKey}_${animName}`;
            if (this.scene.textures.exists(texKey)) {
                this.scene.textures.remove(texKey);
            }
            this.scene.textures.addSpriteSheet(texKey, canvas, { frameWidth: FRAME, frameHeight: FRAME });

            const animKeys = {};
            if (spec.directional) {
                for (const [dir, row] of Object.entries(DIR_TO_ROW)) {
                    const animKey = `${texKey}_${dir}`;
                    animKeys[dir] = animKey;
                    if (this.scene.anims.exists(animKey)) this.scene.anims.remove(animKey);
                    this.scene.anims.create({
                        key: animKey,
                        frames: this.scene.anims.generateFrameNumbers(texKey, {
                            start: row * spec.frames,
                            end:   row * spec.frames + spec.frames - 1,
                        }),
                        frameRate: spec.frameRate,
                        repeat: spec.loop ? -1 : 0,
                    });
                }
            } else {
                // 방향 무관: 시트 전체(또는 첫 행)을 하나의 애니로
                const animKey = `${texKey}_omni`;
                animKeys.omni = animKey;
                if (this.scene.anims.exists(animKey)) this.scene.anims.remove(animKey);
                this.scene.anims.create({
                    key: animKey,
                    frames: this.scene.anims.generateFrameNumbers(texKey, { start: 0, end: spec.frames - 1 }),
                    frameRate: spec.frameRate,
                    repeat: spec.loop ? -1 : 0,
                });
            }

            this._anims[animName] = { texKey, spec, animKeys };
        }

        if (Object.keys(this._anims).length === 0) {
            throw new Error(`[LPC] ${this._opts.textureKey}: 어떤 애니도 합성 실패`);
        }

        const initialAnim = STATE_TO_ANIM[this._persistent] || 'idle';
        const initialInfo = this._anims[initialAnim] || this._anims.idle || Object.values(this._anims)[0];

        this.sprite = this.scene.add.sprite(this._baseX, this._baseY, initialInfo.texKey, 0);
        this.sprite.setOrigin(0.5, 1.0);
        this.sprite.setDisplaySize(this._size, this._size);
        if (this._tint) this.sprite.setTint(this._tint);

        this._ready = true;
        this._playPersistent();
    }

    play(state, opts = {}) {
        if (!this._ready) return;

        const animName = STATE_TO_ANIM[state];
        const info = this._anims[animName];

        const isOneShot = state === 'attack' || state === 'hurt';
        if (isOneShot) {
            this._playAttackLunge(state);  // 시각 공격 이동 + hurt는 위치 고정
            if (info) {
                const animKey = this._resolveAnimKey(info);
                this.sprite.off('animationcomplete-' + animKey);
                this.sprite.once('animationcomplete-' + animKey, () => {
                    this._playPersistent();
                    if (opts.onComplete) opts.onComplete();
                });
                this.sprite.anims.play(animKey, false);
            } else if (opts.onComplete) {
                // 애니 없어도 onComplete 호출 보장
                this.scene.time.delayedCall(200, () => {
                    this._playPersistent();
                    opts.onComplete();
                });
            }
            return;
        }

        // 지속 상태 (idle / walk)
        this._persistent = state;
        if (!info) return;
        this._playPersistent();
    }

    _playPersistent() {
        const animName = STATE_TO_ANIM[this._persistent] || 'idle';
        const info = this._anims[animName] || this._anims.idle;
        if (!info || !this.sprite) return;
        const animKey = this._resolveAnimKey(info);
        this.sprite.anims.play(animKey, true);
    }

    _resolveAnimKey(info) {
        if (info.spec.directional) {
            return info.animKeys[this._facing] || info.animKeys.E || info.animKeys.S || Object.values(info.animKeys)[0];
        }
        return info.animKeys.omni;
    }

    _playAttackLunge(state) {
        if (state !== 'attack' || !this.sprite) return;
        if (this._actionTween) { this._actionTween.stop(); this._actionTween = null; }
        const dir = this._facing === 'E' ? 1 : (this._facing === 'W' ? -1 : 0);
        this._actionTween = this.scene.tweens.add({
            targets: this.sprite,
            x: this._baseX + dir * ATTACK_LUNGE_PX,
            duration: ATTACK_DURATION,
            yoyo: true,
            ease: 'Power2',
            onComplete: () => {
                if (this.sprite) this.sprite.x = this._baseX;
                this._actionTween = null;
            },
        });
    }

    setFacing(dir) {
        this._facing = dir;
        if (this._ready) this._playPersistent();
    }

    setX(x) { this._baseX = x; if (this.sprite) this.sprite.x = x; }
    setY(y) { this._baseY = y; if (this.sprite) this.sprite.y = y; }
    get x() { return this.sprite ? this.sprite.x : this._baseX; }
    get y() { return this.sprite ? this.sprite.y : this._baseY; }

    moveTo(x, duration) {
        return new Promise((resolve) => {
            this._baseX = x;
            if (!this.sprite) { resolve(); return; }
            this.scene.tweens.add({
                targets: this.sprite,
                x,
                duration,
                ease: 'Linear',
                onComplete: resolve,
            });
        });
    }

    fadeOut(duration) {
        return new Promise((resolve) => {
            if (!this.sprite) { resolve(); return; }
            this.scene.tweens.add({
                targets: this.sprite,
                alpha: 0,
                y: this.sprite.y + 20,
                duration,
                ease: 'Power2',
                onComplete: resolve,
            });
        });
    }

    setTint(tint) {
        this._tint = tint;
        if (!this.sprite) return;
        if (tint) this.sprite.setTint(tint);
        else this.sprite.clearTint();
    }

    destroy() {
        if (this._actionTween) { this._actionTween.stop(); this._actionTween = null; }
        if (this._walkTween) { this._walkTween.stop(); this._walkTween = null; }
        if (this.sprite) { this.sprite.destroy(); this.sprite = null; }
        // 텍스처/애니는 Phaser Game destroy 시점에 정리. 개별 인스턴스 destroy에서는 유지.
        this._ready = false;
    }
}
