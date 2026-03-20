/**
 * TheSevenRPG — Utilities
 * Toast, Loading, DOM 헬퍼, 포맷터
 */

// ── Toast ──

let toastContainer = null;

function initToast() {
    toastContainer = document.getElementById('toast-container');
}

/**
 * 토스트 메시지 표시
 * @param {string} message
 * @param {'success'|'warning'|'error'|'info'} type
 * @param {number} duration - ms (기본 3초)
 */
export function showToast(message, type = 'info', duration = 3000) {
    if (!toastContainer) initToast();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('show'));

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ── Loading ──

let loadingOverlay = null;
let loadingCount = 0;

function initLoading() {
    loadingOverlay = document.getElementById('loading-overlay');
}

export function showLoading() {
    if (!loadingOverlay) initLoading();
    loadingCount++;
    loadingOverlay.classList.add('show');
}

export function hideLoading() {
    if (!loadingOverlay) initLoading();
    loadingCount = Math.max(0, loadingCount - 1);
    if (loadingCount === 0) {
        loadingOverlay.classList.remove('show');
    }
}

// ── DOM 헬퍼 ──

/** XSS 방지용 HTML 이스케이프 */
export function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ── 모듈 라이프사이클 헬퍼 ──

/**
 * 뷰/탭에 이벤트 위임을 설정한다 (mount 시 호출).
 * module._onEvent(e) 메서드가 존재해야 한다.
 * @param {object} module - view/tab 객체
 * @param {HTMLElement} el - mount 대상 엘리먼트
 */
export function setupEventDelegation(module, el) {
    module.el = el;
    module._handleEvent = module._onEvent.bind(module);
    el.addEventListener('pointerdown', module._handleEvent);
}

/**
 * 뷰/탭의 이벤트 리스너 + Store 구독을 일괄 해제한다 (unmount 시 호출).
 * @param {object} module - view/tab 객체
 */
export function teardown(module) {
    if (module._handleEvent && module.el) {
        module.el.removeEventListener('pointerdown', module._handleEvent);
    }
    if (module._unsubscribers) {
        module._unsubscribers.forEach(unsub => unsub());
        module._unsubscribers = [];
    }
}

// ── 아이템 팝업 ──

/**
 * 장비 아이템 팝업 HTML을 생성한다.
 * @param {object} item - 아이템 데이터 (rarity, dynamic_options 등)
 * @param {object} opts
 * @param {string}        opts.name         - 표시 이름 (기본: item.name)
 * @param {string}        opts.metaText     - 래리티/슬롯/레벨 줄 텍스트
 * @param {object|null}   opts.compareOpts  - 비교 대상 dynamic_options (null이면 비교 안 함)
 * @param {boolean}       opts.showAffixes  - prefix/suffix/set 표시 여부
 * @param {string}        opts.cssPrefix    - CSS 클래스 접두사 ('popup' 또는 'ip')
 * @param {function}      opts.optionLabel  - (key) => label 변환 함수
 * @param {string}        opts.prefixLabel  - 접두사 라벨
 * @param {string}        opts.suffixLabel  - 접미사 라벨
 * @param {string}        opts.setLabel     - 세트 라벨
 * @param {function}      opts.sinName      - (sinType) => 죄종 이름 변환 함수
 * @returns {string} HTML 문자열
 */
export function buildItemPopupHtml(item, opts = {}) {
    const {
        name = item.name || 'Equipment',
        metaText = '',
        compareOpts = null,
        showAffixes = false,
        cssPrefix = 'popup',
        optionLabel = (key) => key,
        prefixLabel = 'Prefix',
        suffixLabel = 'Suffix',
        setLabel = 'Set',
        sinName = (v) => v,
    } = opts;

    const rarityClass = item.rarity || 'magic';
    let html = `<div class="${cssPrefix}-name rarity-${rarityClass}" style="color:var(--color-${rarityClass})">${escapeHtml(name)}</div>`;

    if (metaText) {
        html += `<div class="${cssPrefix}-meta">${metaText}</div>`;
    }

    // 옵션
    const itemOpts = item.dynamic_options || {};
    const allKeys = new Set([
        ...Object.keys(itemOpts),
        ...(compareOpts ? Object.keys(compareOpts) : []),
    ]);

    if (allKeys.size > 0) {
        html += `<div class="${cssPrefix}-options">`;
        for (const key of allKeys) {
            const val = itemOpts[key] || 0;
            const label = optionLabel(key);
            let colorClass = '';

            if (compareOpts) {
                const cmpVal = compareOpts[key] || 0;
                if (val > cmpVal) colorClass = 'up';
                else if (val < cmpVal) colorClass = 'down';
            }

            const display = typeof val === 'number'
                ? (val > 0 ? `+${val.toFixed(1)}` : val.toFixed(1))
                : val;
            html += `<div class="${cssPrefix}-opt-row"><span class="${cssPrefix}-opt-name">${label}</span><span class="${cssPrefix}-opt-val ${colorClass}">${display}</span></div>`;
        }
        html += '</div>';
    }

    // 접두사/접미사/세트
    if (showAffixes) {
        if (item.prefix_id) html += `<div class="${cssPrefix}-affix">${prefixLabel}: ${sinName(item.prefix_id)}</div>`;
        if (item.suffix_id) html += `<div class="${cssPrefix}-affix">${suffixLabel}: ${sinName(item.suffix_id)}</div>`;
        if (item.set_id) html += `<div class="${cssPrefix}-set">${setLabel}: ${sinName(item.set_id)}</div>`;
    }

    return html;
}

// ── 포맷터 ──

/** 골드 포맷 (1000 → "1,000 G") */
export function formatGold(gold) {
    return `${gold.toLocaleString()} G`;
}
