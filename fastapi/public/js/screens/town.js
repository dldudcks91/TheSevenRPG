/**
 * TheSevenRPG — Town Hub Screen (죄악의 성)
 * API 1004: 유저 정보 로드, 방치 파밍 상태 표시
 */
const TownScreen = (() => {
    let container = null;
    let idleTimerInterval = null;
    let userInfo = null;

    function mount(el) {
        container = el;
        container.innerHTML = `
            <div class="town-screen">
                <button class="town-logout" id="town-logout">로그아웃</button>

                <!-- 상단: 캐릭터 정보 -->
                <div class="town-header">
                    <div class="town-header-row">
                        <div>
                            <span class="char-name" id="char-name">-</span>
                            <span class="char-level" id="char-level">Lv.1</span>
                        </div>
                        <div class="char-gold" id="char-gold">0 G</div>
                    </div>
                    <div class="town-exp-bar">
                        <div class="fill" id="exp-fill" style="width: 0%"></div>
                    </div>
                    <div class="town-stats" id="stat-chips"></div>
                </div>

                <!-- 중앙: 메뉴 -->
                <div class="town-menu">
                    <div class="town-title">죄악의 성</div>
                    <div class="town-menu-grid">
                        <button class="town-menu-btn" data-screen="stage-select">
                            <span class="menu-icon">&#9876;</span>
                            <span class="menu-label">스테이지</span>
                        </button>
                        <button class="town-menu-btn" data-screen="inventory">
                            <span class="menu-icon">&#128188;</span>
                            <span class="menu-label">인벤토리</span>
                        </button>
                        <button class="town-menu-btn" data-screen="idle-farm">
                            <span class="menu-icon">&#9202;</span>
                            <span class="menu-label">방치 파밍</span>
                        </button>
                        <button class="town-menu-btn" data-screen="cards">
                            <span class="menu-icon">&#127183;</span>
                            <span class="menu-label">카드 도감</span>
                        </button>
                    </div>
                </div>

                <!-- 하단: 방치 파밍 상태 -->
                <div class="town-idle-bar" id="idle-bar">
                    <span class="idle-status" id="idle-status">방치 파밍: 비활성</span>
                    <span class="idle-timer" id="idle-timer"></span>
                </div>
            </div>
        `;

        // 메뉴 버튼 이벤트
        container.querySelectorAll('.town-menu-btn').forEach(btn => {
            btn.addEventListener('pointerdown', () => {
                const screen = btn.dataset.screen;
                if (screen) App.navigate(screen);
            });
        });

        // 로그아웃
        container.querySelector('#town-logout').addEventListener('pointerdown', () => {
            Session.clear();
            App.navigate('login');
        });

        // 유저 정보 로드
        loadUserInfo();
    }

    async function loadUserInfo() {
        Loading.show();
        try {
            const result = await Api.apiCall(1004, {});
            if (result.success) {
                userInfo = result.data;
                renderUserInfo();
            }
        } catch (err) {
            // 네트워크 에러는 api.js에서 처리
        } finally {
            Loading.hide();
        }
    }

    function renderUserInfo() {
        if (!userInfo || !container) return;

        const d = userInfo;

        // 이름, 레벨, 골드
        container.querySelector('#char-name').textContent = d.user_name;
        container.querySelector('#char-level').textContent = `Lv.${d.level}`;
        container.querySelector('#char-gold').textContent = `${d.gold.toLocaleString()} G`;

        // EXP 바 (임시: 레벨당 필요 경험치 미확정이므로 % 표시 보류)
        const expPercent = d.exp > 0 ? Math.min(100, (d.exp % 1000) / 10) : 0;
        container.querySelector('#exp-fill').style.width = expPercent + '%';

        // 스탯 칩
        const stats = d.stats;
        const chipContainer = container.querySelector('#stat-chips');
        chipContainer.innerHTML = [
            { label: 'STR', value: stats.str },
            { label: 'DEX', value: stats.dex },
            { label: 'VIT', value: stats.vit },
            { label: 'LUK', value: stats.luck },
            { label: 'COST', value: stats.cost },
        ].map(s =>
            `<div class="stat-chip"><span>${s.label}</span> <span class="stat-value">${s.value}</span></div>`
        ).join('');

        if (d.stat_points > 0) {
            chipContainer.innerHTML += `<div class="stat-chip" style="color:var(--color-warning);"><span>SP</span> <span class="stat-value">${d.stat_points}</span></div>`;
        }

        // 방치 파밍 상태
        renderIdleStatus(d.idle_farm);
    }

    function renderIdleStatus(idle) {
        const statusEl = container.querySelector('#idle-status');
        const timerEl = container.querySelector('#idle-timer');
        const bar = container.querySelector('#idle-bar');

        // 기존 타이머 정리
        if (idleTimerInterval) {
            clearInterval(idleTimerInterval);
            idleTimerInterval = null;
        }

        if (!idle || !idle.active) {
            statusEl.textContent = '방치 파밍: 비활성';
            statusEl.classList.remove('active');
            timerEl.textContent = '';
            return;
        }

        statusEl.textContent = `방치 파밍 중 (스테이지 ${idle.stage_id})`;
        statusEl.classList.add('active');

        // 클라이언트 타이머 (표시용, 실제 계산은 서버)
        let elapsed = idle.elapsed_seconds;

        function updateTimer() {
            const h = Math.floor(elapsed / 3600);
            const m = Math.floor((elapsed % 3600) / 60);
            const s = elapsed % 60;
            timerEl.textContent = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
            elapsed++;
        }

        updateTimer();
        idleTimerInterval = setInterval(updateTimer, 1000);
    }

    function unmount() {
        if (idleTimerInterval) {
            clearInterval(idleTimerInterval);
            idleTimerInterval = null;
        }
    }

    return { mount, unmount };
})();

// 화면 등록
App.registerScreen('town', TownScreen);
