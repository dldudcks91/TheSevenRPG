/**
 * TheSevenRPG — Popup Manager
 * 호버/클릭으로 팝업 표시, 외부 클릭 닫기
 */

let _activePopup = null;
let _pinned = false;

const Popup = {
    /** 팝업 컨테이너 (앱 레벨에 1개) */
    init() {
        if (document.getElementById('popup-container')) return;

        const container = document.createElement('div');
        container.id = 'popup-container';
        container.className = 'popup-container';
        document.body.appendChild(container);

        // 외부 클릭 → 닫기 (다음 틱에서 판정 — show와 같은 이벤트에서 즉시 닫히는 문제 방지)
        document.addEventListener('pointerdown', (e) => {
            if (!_activePopup) return;
            const container = document.getElementById('popup-container');
            if (container && !container.contains(e.target) && !e.target.closest('[data-popup-trigger]')) {
                requestAnimationFrame(() => this.hide());
            }
        });
    },

    /**
     * 팝업 표시
     * @param {string} html - 팝업 내용 HTML
     * @param {HTMLElement} anchorEl - 기준 요소 (위치 계산)
     * @param {object} options - { pinned: boolean, position: 'auto'|'right' }
     */
    show(html, anchorEl, options = {}) {
        this.init();

        const container = document.getElementById('popup-container');
        container.innerHTML = html;
        container.classList.add('show');

        _activePopup = container;
        _pinned = options.pinned || false;

        // 위치 계산
        this._position(container, anchorEl, options.position || 'auto');
    },

    /** 비교 팝업 (좌: 착용중, 우: 미착용) */
    showCompare(leftHtml, rightHtml, anchorEl, options = {}) {
        const html = `
            <div class="popup-compare">
                <div class="popup-card popup-left">${leftHtml}</div>
                <div class="popup-card popup-right">${rightHtml}</div>
            </div>
        `;
        if (!options.position) options.position = 'right';
        this.show(html, anchorEl, options);
    },

    /** 단독 팝업 */
    showSingle(html, anchorEl, options = {}) {
        const wrapped = `<div class="popup-card popup-single">${html}</div>`;
        if (!options.position) options.position = 'right';
        this.show(wrapped, anchorEl, options);
    },

    hide() {
        const container = document.getElementById('popup-container');
        if (container) {
            container.classList.remove('show');
            container.innerHTML = '';
        }
        _activePopup = null;
        _pinned = false;
    },

    isPinned() {
        return _pinned;
    },

    isVisible() {
        return !!_activePopup;
    },

    /** 팝업 위치 계산 */
    _position(container, anchorEl, position = 'auto') {
        if (!anchorEl) return;

        const rect = anchorEl.getBoundingClientRect();
        const popupRect = container.getBoundingClientRect();
        const vw = window.innerWidth;
        const vh = window.innerHeight;

        let top, left;

        if (position === 'right') {
            // 앵커 오른쪽에 표시
            left = rect.right + 8;
            top = rect.top;

            // 오른쪽 공간 부족 → 왼쪽에 표시
            if (left + popupRect.width > vw - 8) {
                left = rect.left - popupRect.width - 8;
            }
        } else {
            // 기본: 앵커 위에 표시
            top = rect.top - popupRect.height - 8;
            left = rect.left + rect.width / 2 - popupRect.width / 2;

            // 위쪽 공간 부족 → 아래에 표시
            if (top < 8) {
                top = rect.bottom + 8;
            }
        }

        // 좌우 화면 밖 보정
        if (left < 8) left = 8;
        if (left + popupRect.width > vw - 8) left = vw - popupRect.width - 8;

        // 상하 화면 밖 보정
        if (top < 8) top = 8;
        if (top + popupRect.height > vh - 8) {
            top = vh - popupRect.height - 8;
        }

        container.style.top = top + 'px';
        container.style.left = left + 'px';
    },
};

export default Popup;
