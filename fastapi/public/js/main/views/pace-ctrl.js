/**
 * PaceCtrl — 전투 재생 속도/일시정지 래퍼.
 * Iter 1: setTimeout/Phaser tween passthrough (속도 1x, 일시정지 미지원).
 * Iter 4에서 setSpeed/pause/resume 내부 구현을 확장해도 호출부는 불변.
 */
export class PaceCtrl {
    constructor() {
        this._speed = 1;
        this._paused = false;
        this._timers = new Set();
    }

    /** 속도·일시정지 반영된 setTimeout. fn은 0 또는 양수 ms 후 실행. */
    after(ms, fn) {
        const adjusted = Math.max(0, Math.round(ms / this._speed));
        const handle = setTimeout(() => {
            this._timers.delete(handle);
            fn();
        }, adjusted);
        this._timers.add(handle);
        return handle;
    }

    /** Promise 버전의 wait. */
    wait(ms) {
        return new Promise((resolve) => this.after(ms, resolve));
    }

    /** 지정 시간(속도 반영)으로 Phaser tween 생성. */
    tween(scene, opts) {
        const cloned = { ...opts };
        if (typeof cloned.duration === 'number') {
            cloned.duration = Math.max(0, Math.round(cloned.duration / this._speed));
        }
        return scene.tweens.add(cloned);
    }

    setSpeed(n) { this._speed = Math.max(0.25, Math.min(4, n)); }
    getSpeed() { return this._speed; }

    pause() { this._paused = true; }
    resume() { this._paused = false; }
    isPaused() { return this._paused; }

    clearAll() {
        for (const h of this._timers) clearTimeout(h);
        this._timers.clear();
    }
}
