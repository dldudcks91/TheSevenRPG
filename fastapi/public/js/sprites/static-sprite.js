/**
 * StaticSprite — 단일 PNG 기반 전투 스프라이트 래퍼.
 * LpcSprite(추후)와 동일한 시그니처를 제공해 idle/walk/attack/hurt 상태를 재생한다.
 *
 * 지속 상태(idle, walk)는 _state로 추적.
 * 일회성 액션(attack, hurt)은 _state를 건드리지 않고 즉시 재생 후 트윈 종료.
 */

const DEFAULT_SIZE = 220;
const WALK_BOUNCE_PX = 6;
const WALK_BOUNCE_DURATION = 220;
const ATTACK_LUNGE_PX = 40;
const ATTACK_DURATION = 100;
const HURT_FLASH_DURATION = 80;

export class StaticSprite {
    constructor(scene, x, y, textureKey, options = {}) {
        this.scene = scene;
        this._facing = options.facing || 'E';
        this._tint = options.tint || null;
        this._size = options.size || DEFAULT_SIZE;

        this._baseX = x;
        this._baseY = y;
        this._state = 'idle';
        this._walkTween = null;
        this._actionTween = null;
        this._hurtTimer = null;

        this.img = scene.add.image(x, y, textureKey);
        this.img.setDisplaySize(this._size, this._size);
        this.img.setOrigin(0.5, 1.0);
        if (this._facing === 'W') this.img.setFlipX(true);
        if (this._tint) this.img.setTint(this._tint);
    }

    play(state, opts = {}) {
        if (state === 'attack') { this._doAttack(opts); return; }
        if (state === 'hurt') { this._doHurt(); return; }

        if (state === this._state) return;
        this._stopContinuous();
        this._state = state;

        if (state === 'walk') this._startWalkBounce();
    }

    _startWalkBounce() {
        this._walkTween = this.scene.tweens.add({
            targets: this.img,
            y: this._baseY - WALK_BOUNCE_PX,
            duration: WALK_BOUNCE_DURATION,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut',
        });
    }

    _doAttack(opts) {
        if (this._actionTween) { this._actionTween.stop(); this._actionTween = null; }
        const dir = this._facing === 'E' ? 1 : -1;
        this._actionTween = this.scene.tweens.add({
            targets: this.img,
            x: this._baseX + dir * ATTACK_LUNGE_PX,
            duration: ATTACK_DURATION,
            yoyo: true,
            ease: 'Power2',
            onComplete: () => {
                this.img.x = this._baseX;
                this._actionTween = null;
                if (opts.onComplete) opts.onComplete();
            },
        });
    }

    _doHurt() {
        if (this._hurtTimer) { this._hurtTimer.remove(false); this._hurtTimer = null; }
        if (!this.img.setTintFill) return;

        this.img.setTintFill(0xffffff);
        this._hurtTimer = this.scene.time.delayedCall(HURT_FLASH_DURATION, () => {
            this.img.clearTint();
            if (this._tint) this.img.setTint(this._tint);
            this._hurtTimer = null;
        });
    }

    _stopContinuous() {
        if (this._walkTween) { this._walkTween.stop(); this._walkTween = null; }
        this.img.y = this._baseY;
    }

    setX(x) { this._baseX = x; this.img.x = x; }
    setY(y) { this._baseY = y; this.img.y = y; }
    get x() { return this.img.x; }
    get y() { return this.img.y; }

    moveTo(x, duration) {
        this._stopContinuous();
        return new Promise((resolve) => {
            this._baseX = x;
            this.scene.tweens.add({
                targets: this.img,
                x,
                duration,
                ease: 'Linear',
                onComplete: resolve,
            });
        });
    }

    fadeOut(duration) {
        this._stopContinuous();
        return new Promise((resolve) => {
            this.scene.tweens.add({
                targets: this.img,
                alpha: 0,
                y: this.img.y + 20,
                duration,
                ease: 'Power2',
                onComplete: resolve,
            });
        });
    }

    destroy() {
        this._stopContinuous();
        if (this._actionTween) { this._actionTween.stop(); this._actionTween = null; }
        if (this._hurtTimer) { this._hurtTimer.remove(false); this._hurtTimer = null; }
        this.img.destroy();
    }
}

/** 텍스처 로드 실패 시 사용하는 Rectangle 폴백. StaticSprite와 동일 시그니처. */
export class RectSprite {
    constructor(scene, x, y, color, options = {}) {
        this.scene = scene;
        this._facing = options.facing || 'E';
        this._baseX = x;
        this._baseY = y;
        this._state = 'idle';
        this._walkTween = null;
        this._actionTween = null;

        const w = options.width || 56;
        const h = options.height || 70;
        this._halfH = h / 2;

        this.img = scene.add.rectangle(x, y - this._halfH, w, h, color);
        this.img.setStrokeStyle(2, 0xffffff);
        this._origColor = color;
    }

    play(state, opts = {}) {
        if (state === 'attack') { this._doAttack(opts); return; }
        if (state === 'hurt') { this._doHurt(); return; }

        if (state === this._state) return;
        this._stopContinuous();
        this._state = state;

        if (state === 'walk') this._startWalkBounce();
    }

    _startWalkBounce() {
        this._walkTween = this.scene.tweens.add({
            targets: this.img,
            y: this._baseY - this._halfH - WALK_BOUNCE_PX,
            duration: WALK_BOUNCE_DURATION,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut',
        });
    }

    _doAttack(opts) {
        if (this._actionTween) { this._actionTween.stop(); this._actionTween = null; }
        const dir = this._facing === 'E' ? 1 : -1;
        this._actionTween = this.scene.tweens.add({
            targets: this.img,
            x: this._baseX + dir * ATTACK_LUNGE_PX,
            duration: ATTACK_DURATION,
            yoyo: true,
            ease: 'Power2',
            onComplete: () => {
                this.img.x = this._baseX;
                this._actionTween = null;
                if (opts.onComplete) opts.onComplete();
            },
        });
    }

    _doHurt() {
        this.img.setFillStyle(0xffffff);
        this.scene.time.delayedCall(HURT_FLASH_DURATION, () => this.img.setFillStyle(this._origColor));
    }

    _stopContinuous() {
        if (this._walkTween) { this._walkTween.stop(); this._walkTween = null; }
        this.img.y = this._baseY - this._halfH;
    }

    setX(x) { this._baseX = x; this.img.x = x; }
    get x() { return this.img.x; }
    get y() { return this.img.y; }

    moveTo(x, duration) {
        this._stopContinuous();
        return new Promise((resolve) => {
            this._baseX = x;
            this.scene.tweens.add({
                targets: this.img,
                x,
                duration,
                ease: 'Linear',
                onComplete: resolve,
            });
        });
    }

    fadeOut(duration) {
        this._stopContinuous();
        return new Promise((resolve) => {
            this.scene.tweens.add({
                targets: this.img,
                alpha: 0,
                duration,
                onComplete: resolve,
            });
        });
    }

    destroy() {
        this._stopContinuous();
        if (this._actionTween) { this._actionTween.stop(); this._actionTween = null; }
        this.img.destroy();
    }
}
