/**
 * TheSevenRPG — Central Store (pub/sub)
 * 중앙 상태 관리: API 응답 → Store → UI 갱신
 */
const Store = {
    _state: {},
    _listeners: {},  // key → Set<callback>
    _batchDepth: 0,
    _pendingNotifications: [],  // 배치 중 지연된 알림

    /** 값 읽기 (dot notation) */
    get(key) {
        return key.split('.').reduce((obj, k) => obj?.[k], this._state);
    },

    /** 값 쓰기 + 구독자 알림 */
    set(key, value) {
        const keys = key.split('.');
        let target = this._state;
        for (let i = 0; i < keys.length - 1; i++) {
            if (!target[keys[i]]) target[keys[i]] = {};
            target = target[keys[i]];
        }
        target[keys[keys.length - 1]] = value;

        if (this._batchDepth > 0) {
            // 배치 중: 알림 지연, 같은 키는 마지막 값만 유지
            const existing = this._pendingNotifications.find(n => n.key === key);
            if (existing) {
                existing.value = value;
            } else {
                this._pendingNotifications.push({ key, value });
            }
        } else {
            this._notify(key, value);
        }
    },

    /** 구독 — 해제 함수 반환 */
    subscribe(key, callback) {
        if (!this._listeners[key]) this._listeners[key] = new Set();
        this._listeners[key].add(callback);

        return () => this._listeners[key].delete(callback);
    },

    /** 구독자 알림 */
    _notify(key, value) {
        const listeners = this._listeners[key];
        if (listeners) {
            listeners.forEach(cb => cb(value));
        }
    },

    /**
     * 배치 업데이트: 블록 내 set() 호출은 알림을 지연시키고,
     * 블록 종료 시 변경된 키만 1회씩 알림.
     * 같은 콜백이 여러 키를 구독해도 중복 호출 방지.
     * @param {Function} fn - 배치 블록
     */
    batch(fn) {
        this._batchDepth++;
        try {
            fn();
        } finally {
            this._batchDepth--;
            if (this._batchDepth === 0) {
                this._flushBatch();
            }
        }
    },

    /** 지연된 알림을 일괄 발행 (콜백 중복 제거) */
    _flushBatch() {
        const pending = this._pendingNotifications;
        this._pendingNotifications = [];

        // 콜백 중복 실행 방지: 이미 호출된 콜백을 추적
        const calledCallbacks = new Set();

        for (const { key, value } of pending) {
            const listeners = this._listeners[key];
            if (!listeners) continue;
            for (const cb of listeners) {
                if (!calledCallbacks.has(cb)) {
                    calledCallbacks.add(cb);
                    cb(value);
                }
            }
        }
    },

    /** 여러 값 일괄 업데이트 (배치로 감싸서 알림 최소화) */
    merge(obj, prefix = '') {
        this.batch(() => {
            this._mergeInner(obj, prefix);
        });
    },

    /** @private merge 내부 재귀 */
    _mergeInner(obj, prefix) {
        for (const [k, v] of Object.entries(obj)) {
            const fullKey = prefix ? `${prefix}.${k}` : k;
            if (v !== null && typeof v === 'object' && !Array.isArray(v)) {
                this._mergeInner(v, fullKey);
            } else {
                this.set(fullKey, v);
            }
        }
    },
};

export { Store };
