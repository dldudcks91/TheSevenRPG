/**
 * TheSevenRPG — Session Manager
 * localStorage 기반 세션 관리
 */
const Session = (() => {
    const KEYS = {
        SESSION_ID: 'session_id',
        USER_NO: 'user_no',
        USER_NAME: 'user_name',
    };

    /** 로그인 성공 시 세션 저장 */
    function save(sessionId, userNo, userName) {
        localStorage.setItem(KEYS.SESSION_ID, sessionId);
        localStorage.setItem(KEYS.USER_NO, String(userNo));
        localStorage.setItem(KEYS.USER_NAME, userName);
    }

    /** 세션 ID 조회 */
    function getSessionId() {
        return localStorage.getItem(KEYS.SESSION_ID);
    }

    /** 유저 번호 조회 */
    function getUserNo() {
        const val = localStorage.getItem(KEYS.USER_NO);
        return val ? parseInt(val, 10) : null;
    }

    /** 유저 이름 조회 */
    function getUserName() {
        return localStorage.getItem(KEYS.USER_NAME);
    }

    /** 로그인 상태 확인 */
    function isLoggedIn() {
        return !!getSessionId();
    }

    /** 세션 삭제 (로그아웃) */
    function clear() {
        localStorage.removeItem(KEYS.SESSION_ID);
        localStorage.removeItem(KEYS.USER_NO);
        localStorage.removeItem(KEYS.USER_NAME);
    }

    return { save, getSessionId, getUserNo, getUserName, isLoggedIn, clear };
})();
