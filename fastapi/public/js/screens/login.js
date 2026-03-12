/**
 * TheSevenRPG — Login Screen
 * API 1003: 닉네임 입력 → 신규 생성 or 기존 로그인
 */
const LoginScreen = (() => {
    let container = null;
    let inputEl = null;
    let btnEl = null;
    let errorEl = null;

    function mount(el) {
        container = el;

        if (!container.innerHTML) {
            container.innerHTML = `
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
                        <button class="login-btn">입장하기</button>
                    </div>
                </div>
            `;
        }

        inputEl = container.querySelector('.login-input');
        btnEl = container.querySelector('.login-btn');
        errorEl = container.querySelector('.login-error');

        btnEl.addEventListener('pointerdown', handleLogin);
        inputEl.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') handleLogin();
        });

        // 포커스
        setTimeout(() => inputEl.focus(), 100);
    }

    async function handleLogin() {
        const userName = inputEl.value.trim();

        if (!userName) {
            errorEl.textContent = '닉네임을 입력해주세요.';
            inputEl.focus();
            return;
        }

        if (userName.length < 2) {
            errorEl.textContent = '닉네임은 2자 이상이어야 합니다.';
            inputEl.focus();
            return;
        }

        errorEl.textContent = '';
        btnEl.disabled = true;
        btnEl.textContent = '접속 중...';

        try {
            const result = await Api.apiCall(1003, { user_name: userName });

            if (result.success) {
                const { user_no, user_name, session_id } = result.data;
                Session.save(session_id, user_no, user_name);
                App.navigate('town');
            } else {
                errorEl.textContent = result.message || '로그인에 실패했습니다.';
            }
        } catch (err) {
            errorEl.textContent = '서버에 연결할 수 없습니다.';
        } finally {
            btnEl.disabled = false;
            btnEl.textContent = '입장하기';
        }
    }

    function unmount() {
        // 이벤트 리스너는 DOM 교체 시 자동 해제
    }

    return { mount, unmount };
})();

// 화면 등록
App.registerScreen('login', LoginScreen);
