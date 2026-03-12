/**
 * TheSevenRPG — API Communication Layer
 * POST /api 단일 게이트웨이, Bearer 세션 인증, 재시도 로직
 */
const Api = (() => {
    const MAX_RETRIES = 3;
    const BASE_DELAY = 1000; // 1초, 지수 백오프

    /**
     * 서버 API 호출
     * @param {number} apiCode - API 코드 (1002, 1003, 2001, ...)
     * @param {object} data - 요청 데이터
     * @returns {Promise<object>} 서버 응답
     */
    async function apiCall(apiCode, data = {}) {
        const headers = { 'Content-Type': 'application/json' };

        const sessionId = Session.getSessionId();
        if (sessionId) {
            headers['Authorization'] = `Bearer ${sessionId}`;
        }

        const body = JSON.stringify({
            api_code: apiCode,
            data: data
        });

        let lastError = null;

        for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
            try {
                const response = await fetch('/api', {
                    method: 'POST',
                    headers,
                    body
                });

                const result = await response.json();

                // 서버가 정상 응답했으면 재시도 불필요
                if (response.ok) {
                    if (result.success === false) {
                        handleApiError(result);
                    }
                    return result;
                }

                // HTTP 에러 (4xx, 5xx)
                handleApiError(result);
                return result;

            } catch (err) {
                lastError = err;
                // 네트워크 에러만 재시도 (fetch 자체 실패)
                if (attempt < MAX_RETRIES - 1) {
                    const delay = BASE_DELAY * Math.pow(2, attempt);
                    await sleep(delay);
                }
            }
        }

        // 모든 재시도 실패
        Toast.show('서버에 연결할 수 없습니다. 네트워크를 확인해주세요.', 'error');
        throw lastError;
    }

    /** API 에러 처리 */
    function handleApiError(result) {
        const errorCode = result.error_code || '';
        const message = result.message || '알 수 없는 오류';

        // E1002: 세션 만료 → 로그인 화면으로
        if (errorCode === 'E1002') {
            Session.clear();
            Toast.show('세션이 만료되었습니다. 다시 로그인해주세요.', 'warning');
            App.navigate('login');
            return;
        }

        // 그 외 에러 → 토스트
        if (result.success === false) {
            Toast.show(message, 'error');
        }
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    return { apiCall };
})();
