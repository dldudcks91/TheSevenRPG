/**
 * TheSevenRPG — Login Screen
 * API 1003: 닉네임 입력 → 신규 생성 or 기존 로그인
 */
import { apiCall } from '../api.js';
import { saveSession } from '../session.js';
import { showLoading, hideLoading } from '../utils.js';

const LoginScreen = {
    el: null,
    refs: {},

    mount(el) {
        this.el = el;

        if (!el.dataset.initialized) {
            el.innerHTML = `
                <div class="login-screen">
                    <div class="login-title">THE SEVEN</div>
                    <div class="login-subtitle">7대 죄악의 성에 오신 것을 환영합니다</div>
                    <div class="login-form">
                        <input class="login-input"
                               type="text"
                               placeholder="닉네임을 입력하세요"
                               maxlength="20"
                               autocomplete="off" />
                        <div class="login-error"></div>
                        <button class="login-btn" data-action="login">입장하기</button>
                    </div>
                </div>
            `;
            el.dataset.initialized = 'true';
        }

        this.refs = {
            input: el.querySelector('.login-input'),
            btn: el.querySelector('.login-btn'),
            error: el.querySelector('.login-error'),
        };

        this._handleEvent = this.handleEvent.bind(this);
        el.addEventListener('pointerdown', this._handleEvent);

        this._handleKeydown = this._onKeydown.bind(this);
        this.refs.input.addEventListener('keydown', this._handleKeydown);

        setTimeout(() => this.refs.input.focus(), 100);
    },

    unmount() {
        if (this._handleEvent) {
            this.el.removeEventListener('pointerdown', this._handleEvent);
        }
        if (this._handleKeydown && this.refs.input) {
            this.refs.input.removeEventListener('keydown', this._handleKeydown);
        }
    },

    handleEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        if (target.dataset.action === 'login') {
            this._doLogin();
        }
    },

    _onKeydown(e) {
        if (e.key === 'Enter') this._doLogin();
    },

    async _doLogin() {
        const userName = this.refs.input.value.trim();

        if (!userName) {
            this.refs.error.textContent = '닉네임을 입력해주세요.';
            this.refs.input.focus();
            return;
        }

        if (userName.length < 2) {
            this.refs.error.textContent = '닉네임은 2자 이상이어야 합니다.';
            this.refs.input.focus();
            return;
        }

        this.refs.error.textContent = '';
        this.refs.btn.disabled = true;
        this.refs.btn.textContent = '접속 중...';

        showLoading();
        try {
            const result = await apiCall(1003, { user_name: userName });

            if (result?.success) {
                const { user_no, user_name, session_id } = result.data;
                saveSession(session_id, user_no, user_name);
                window.location.hash = '#town';
            } else if (result) {
                this.refs.error.textContent = result.message || '로그인에 실패했습니다.';
            } else {
                this.refs.error.textContent = '서버에 연결할 수 없습니다.';
            }
        } finally {
            hideLoading();
            this.refs.btn.disabled = false;
            this.refs.btn.textContent = '입장하기';
        }
    },
};

export default LoginScreen;
