/**
 * TheSevenRPG — SceneManager
 * Unity-style stack-based scene management
 *
 * Lifecycle:
 *   mount(el, data)  — scene enters (Unity: Awake + Start)
 *   unmount()        — scene exits (Unity: OnDestroy)
 *   onPause()        — scene paused, another pushed on top (optional)
 *   onResume(data)   — scene resumed after top popped (optional)
 */

const SceneManager = {
    /** @type {Object<string, object>} name -> module */
    _scenes: {},

    /** @type {Array<{name: string, module: object, el: HTMLElement}>} */
    _stack: [],

    /** @type {HTMLElement} */
    _container: null,

    /**
     * Initialize
     * @param {HTMLElement} container - root container (#app)
     */
    init(container) {
        this._container = container;
        this._scenes = {};
        this._stack = [];
    },

    /**
     * Register a scene module
     * @param {string} name
     * @param {object} module - must implement mount(el, data) / unmount()
     */
    register(name, module) {
        this._scenes[name] = module;
    },

    /**
     * Push — new scene on top, current scene paused (hidden)
     * @param {string} name
     * @param {object} [data]
     */
    async push(name, data) {
        const module = this._scenes[name];
        if (!module) {
            console.error(`[SceneManager] Scene not found: ${name}`);
            return;
        }

        // pause current
        const current = this._peek();
        if (current) {
            if (current.module.onPause) current.module.onPause();
            current.el.classList.remove('scene-active');
            current.el.classList.add('scene-hidden');
        }

        // create & mount new
        const el = this._createElement(name);
        this._stack.push({ name, module, el });
        await module.mount(el, data);

        console.log(`[SceneManager] push -> ${name} (depth: ${this._stack.length})`);
    },

    /**
     * Pop — remove current, resume previous
     * @param {object} [data] - passed to previous scene's onResume
     */
    async pop(data) {
        if (this._stack.length <= 1) {
            console.warn('[SceneManager] Cannot pop last scene');
            return;
        }

        const popped = this._stack.pop();
        if (popped.module.unmount) popped.module.unmount();
        popped.el.remove();

        // resume previous
        const current = this._peek();
        if (current) {
            current.el.classList.remove('scene-hidden');
            current.el.classList.add('scene-active');
            if (current.module.onResume) current.module.onResume(data);
        }

        console.log(`[SceneManager] pop <- ${popped.name} (depth: ${this._stack.length})`);
    },

    /**
     * Replace — swap current scene, no stack growth
     * @param {string} name
     * @param {object} [data]
     */
    async replace(name, data) {
        const module = this._scenes[name];
        if (!module) {
            console.error(`[SceneManager] Scene not found: ${name}`);
            return;
        }

        // remove current
        const current = this._peek();
        if (current) {
            if (current.module.unmount) current.module.unmount();
            current.el.remove();
            this._stack.pop();
        }

        // create & mount new
        const el = this._createElement(name);
        this._stack.push({ name, module, el });
        await module.mount(el, data);

        console.log(`[SceneManager] replace -> ${name} (depth: ${this._stack.length})`);
    },

    /**
     * Clear entire stack and push a fresh scene
     * Useful for hard resets (e.g. session expired -> login)
     * @param {string} name
     * @param {object} [data]
     */
    async resetTo(name, data) {
        // unmount all scenes in reverse order
        while (this._stack.length > 0) {
            const entry = this._stack.pop();
            if (entry.module.unmount) entry.module.unmount();
            entry.el.remove();
        }

        await this.push(name, data);
    },

    /**
     * Get current scene name
     * @returns {string|null}
     */
    current() {
        const top = this._peek();
        return top ? top.name : null;
    },

    /**
     * Get stack depth
     * @returns {number}
     */
    depth() {
        return this._stack.length;
    },

    /** @private */
    _peek() {
        return this._stack.length > 0
            ? this._stack[this._stack.length - 1]
            : null;
    },

    /** @private */
    _createElement(name) {
        const el = document.createElement('div');
        el.className = 'scene scene-active';
        el.dataset.scene = name;
        this._container.appendChild(el);
        return el;
    },
};

export { SceneManager };
