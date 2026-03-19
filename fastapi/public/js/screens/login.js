/**
 * TheSevenRPG — Login Screen
 * API 1003: 회원가입 (user_name + password)
 * API 1007: 로그인 (user_name + password)
 */
import { apiCall } from '../api.js';
import { saveSession } from '../session.js';
import { showLoading, hideLoading } from '../utils.js';
import { SceneManager } from '../scene-manager.js';
import { t } from '../i18n/index.js';

const LoginScreen = {
    el: null,
    refs: {},

    mount(el) {
        this.el = el;

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="login-screen">
                    <div class="login-title">THE SEVEN</div>
                    <div class="login-subtitle">${t('login_title')}</div>
                    <div class="login-form">
                        <input class="login-input"
                               id="login-name"
                               type="text"
                               placeholder="${t('login_nickname_ph')}"
                               maxlength="20"
                               autocomplete="off" />
                        <input class="login-input"
                               id="login-pw"
                               type="password"
                               placeholder="${t('login_password_ph')}"
                               maxlength="30"
                               autocomplete="off" />
                        <div class="login-error" id="login-error"></div>
                        <div class="login-buttons">
                            <button class="login-btn" data-action="login">${t('login_btn')}</button>
                            <button class="login-btn login-btn-sub" data-action="signup">${t('signup_btn')}</button>
                        </div>
                    </div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        this.refs = {
            name: el.querySelector('#login-name'),
            pw: el.querySelector('#login-pw'),
            error: el.querySelector('#login-error'),
        };

        this._handleEvent = this._onEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._handleKeydown = this._onKeydown.bind(this);
        el.addEventListener('keydown', this._handleKeydown);

        setTimeout(() => this.refs.name.focus(), 100);
    },

    unmount() {
        if (this._handleEvent) this.el.removeEventListener('pointerdown', this._handleEvent);
        if (this._handleKeydown) this.el.removeEventListener('keydown', this._handleKeydown);
    },

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'login':
                this._doAuth(1007);
                break;
            case 'signup':
                this._doAuth(1003);
                break;
        }
    },

    _onKeydown(e) {
        if (e.key === 'Enter') this._doAuth(1007);
    },

    async _doAuth(apiCode) {
        const userName = this.refs.name.value.trim();
        const password = this.refs.pw.value;

        // 검증
        if (!userName) {
            this.refs.error.textContent = t('login_err_name_empty');
            this.refs.name.focus();
            return;
        }
        if (userName.length < 2) {
            this.refs.error.textContent = t('login_err_name_short');
            this.refs.name.focus();
            return;
        }
        if (!password) {
            this.refs.error.textContent = t('login_err_pw_empty');
            this.refs.pw.focus();
            return;
        }
        if (password.length < 4) {
            this.refs.error.textContent = t('login_err_pw_short');
            this.refs.pw.focus();
            return;
        }

        this.refs.error.textContent = '';

        showLoading();
        try {
            const result = await apiCall(apiCode, {
                user_name: userName,
                password: password,
            });

            if (result?.success) {
                const { user_no, user_name, session_id } = result.data;
                saveSession(session_id, user_no, user_name);

                // 회원가입(1003) → 프롤로그, 로그인(1007) → 바로 메인
                if (apiCode === 1003) {
                    SceneManager.replace('prologue');
                } else {
                    SceneManager.replace('main');
                }
            } else if (result) {
                this.refs.error.textContent = result.message || t('error_request');
            } else {
                this.refs.error.textContent = t('login_err_server');
            }
        } finally {
            hideLoading();
        }
    },
};

export default LoginScreen;
