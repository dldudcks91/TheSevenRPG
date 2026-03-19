/**
 * TheSevenRPG — i18n (다국어 지원)
 * t('key') → 현재 언어에 맞는 문자열 반환
 * t('key', { n: 5 }) → 템플릿 치환 ({n} → 5)
 */
import ko from './ko.js';
import en from './en.js';

const LANGS = { ko, en };
const VALID_LANGS = Object.keys(LANGS);

let _currentLang = localStorage.getItem('lang') || 'ko';
let _listeners = new Set();

/**
 * 번역 문자열 반환
 * @param {string} key
 * @param {object} params - 치환 파라미터 (optional)
 * @returns {string}
 */
export function t(key, params) {
    const dict = LANGS[_currentLang] || LANGS.ko;
    let text = dict[key] ?? LANGS.ko[key] ?? key;

    if (params) {
        for (const [k, v] of Object.entries(params)) {
            text = text.replace(`{${k}}`, v);
        }
    }
    return text;
}

/** 현재 언어 반환 */
export function getLang() {
    return _currentLang;
}

/** 언어 변경 */
export function setLang(lang) {
    if (!VALID_LANGS.includes(lang)) return;
    _currentLang = lang;
    localStorage.setItem('lang', lang);
    _listeners.forEach(cb => cb(lang));
}

/** 언어 변경 시 콜백 등록 (해제 함수 반환) */
export function onLangChange(callback) {
    _listeners.add(callback);
    return () => _listeners.delete(callback);
}

/** 죄종 키 → 현재 언어 이름 */
export function sinName(sinKey) {
    return t(`sin_${sinKey}`);
}

/** 등급 키 → 현재 언어 이름 */
export function rarityName(rarityKey) {
    return t(`rarity_${rarityKey}`);
}

/** 슬롯 키 → 현재 언어 이름 */
export function slotName(slotKey) {
    return t(`slot_${slotKey}`);
}
