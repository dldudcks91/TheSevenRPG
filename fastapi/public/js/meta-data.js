/**
 * TheSevenRPG — Meta Data Manager
 * API 1002로 서버 메타데이터를 로드하고 룩업 함수를 제공한다.
 */
import { apiCall } from './api.js';

let _loaded = false;
let _configs = {};

// ── 장비 베이스 인덱스 (item_idx → row) ──
let _equipBaseMap = {};

// ── 초기 로드 ──

/**
 * 서버에서 메타데이터를 로드한다. 앱 초기화 시 1회 호출.
 * @returns {Promise<boolean>} 성공 여부
 */
export async function loadMetaData() {
    if (_loaded) return true;

    const result = await apiCall(1002, {});
    if (!result?.success) {
        console.error('[MetaData] 메타데이터 로드 실패');
        return false;
    }

    _configs = result.data;

    // 장비 베이스 인덱스 생성
    (_configs.equip_bases || []).forEach(row => {
        _equipBaseMap[String(row.item_idx)] = row;
    });

    _loaded = true;
    console.log('[MetaData] 메타데이터 로드 완료');
    return true;
}

/** 로드 여부 확인 */
export function isMetaLoaded() {
    return _loaded;
}

// ── 장비 룩업 ──

/**
 * base_item_id로 장비 이름을 반환한다.
 * @param {number|string} baseItemId
 * @returns {string} 장비 이름 또는 fallback
 */
export function getEquipName(baseItemId) {
    const row = _equipBaseMap[String(baseItemId)];
    return row ? row.item_base : `장비 #${baseItemId}`;
}

/**
 * base_item_id로 장비 베이스 정보를 반환한다.
 * @param {number|string} baseItemId
 * @returns {object|null}
 */
export function getEquipBase(baseItemId) {
    return _equipBaseMap[String(baseItemId)] || null;
}

/**
 * base_item_id로 장착 슬롯을 결정한다.
 * @param {number|string} baseItemId
 * @returns {string} weapon/armor/helmet/gloves/boots
 */
export function getEquipSlot(baseItemId) {
    const row = _equipBaseMap[String(baseItemId)];
    if (row) return row.main_group === 'weapon' ? 'weapon' : row.main_group;

    // fallback: ID 범위 기반
    const id = Number(baseItemId);
    if (id >= 100000 && id < 200000) return 'weapon';
    if (id >= 200000 && id < 300000) return 'armor';
    if (id >= 300000 && id < 400000) return 'helmet';
    if (id >= 400000 && id < 500000) return 'gloves';
    if (id >= 500000 && id < 600000) return 'boots';
    return 'armor';
}

// ── 몬스터 룩업 ──

/**
 * monster_idx로 몬스터 이름을 반환한다.
 * @param {number|string} monsterIdx
 * @returns {string}
 */
export function getMonsterName(monsterIdx) {
    const monster = (_configs.monsters || {})[String(monsterIdx)];
    return monster ? monster.name : `몬스터 #${monsterIdx}`;
}

/**
 * monster_idx로 몬스터 정보를 반환한다.
 * @param {number|string} monsterIdx
 * @returns {object|null}
 */
export function getMonsterInfo(monsterIdx) {
    return (_configs.monsters || {})[String(monsterIdx)] || null;
}

// ── 챕터/스테이지 룩업 ──

// 죄악 → CSS 컬러 키 매핑
const SIN_COLOR_MAP = {
    'Wrath': 'wrath', 'Sloth': 'sloth', 'Greed': 'greed',
    'Envy': 'envy', 'Gluttony': 'gluttony', 'Lust': 'lust', 'Pride': 'pride',
};

/**
 * 모든 챕터 목록을 반환한다.
 * @returns {Array<{id, sin, region, color, boss, bossDesc}>}
 */
export function getChapters() {
    const chapters = _configs.chapters || {};
    const result = Object.entries(chapters)
        .map(([id, ch]) => ({
            id: Number(id),
            sin: ch.sin_kr,
            region: ch.region_kr,
            color: SIN_COLOR_MAP[ch.sin_en] || 'wrath',
            boss: ch.boss_name,
            bossDesc: ch.boss_desc,
        }))
        .sort((a, b) => a.id - b.id);

    // 더미: chapters가 비어있으면 기본값
    if (result.length === 0) {
        return [
            { id: 1, sin: '분노', region: '불타는 전장', boss: '아바돈' },
            { id: 2, sin: '시기', region: '뒤틀린 숲', boss: '사마엘' },
            { id: 3, sin: '탐욕', region: '황금의 사막', boss: '다곤' },
        ];
    }
    return result;
}

/**
 * 특정 챕터의 스테이지 목록을 반환한다.
 * @param {number} chapterId
 * @returns {Array<{stageId, stageNum, stageName}>}
 */
export function getStagesByChapter(chapterId) {
    const stages = _configs.stages || {};
    const result = Object.entries(stages)
        .filter(([, s]) => s.chapter === chapterId)
        .map(([id, s]) => ({
            stageId: Number(id),
            stageNum: s.stage_num,
            stageName: s.stage_name,
        }))
        .sort((a, b) => a.stageId - b.stageId);

    // 더미: stages가 비어있으면 기본값
    if (result.length === 0) {
        const dummyStages = {
            1: [
                { stageId: 101, stageNum: 1, stageName: '파멸의 진영' },
                { stageId: 102, stageNum: 2, stageName: '흑심의 동굴' },
                { stageId: 103, stageNum: 3, stageName: '아바돈의 궁전' },
            ],
            2: [
                { stageId: 201, stageNum: 1, stageName: '시기의 숲' },
                { stageId: 202, stageNum: 2, stageName: '증오의 늪지' },
                { stageId: 203, stageNum: 3, stageName: '사마엘의 서식지' },
            ],
            3: [
                { stageId: 301, stageNum: 1, stageName: '황금의 사막' },
                { stageId: 302, stageNum: 2, stageName: '탐욕의 탑' },
                { stageId: 303, stageNum: 3, stageName: '다곤의 무덤' },
            ],
        };
        return dummyStages[chapterId] || [];
    }
    return result;
}

// ── 세트 보너스 룩업 ──

/**
 * set_id + breakpoint로 세트 효과를 반환한다.
 * @param {string} setId - 죄종 key (wrath, envy, ...)
 * @param {number} breakpoint - 2, 4, 6
 * @returns {object|null} { effect_name, effect_desc, status, ... }
 */
export function getSetBonus(setId, breakpoint) {
    const setBonus = (_configs.set_bonus || {})[setId];
    if (!setBonus) return null;
    return setBonus[String(breakpoint)] || null;
}

/**
 * stage_id로 스테이지 이름을 반환한다.
 * @param {number|string} stageId
 * @returns {string}
 */
export function getStageName(stageId) {
    const stage = (_configs.stages || {})[String(stageId)];
    return stage ? stage.stage_name : `스테이지 ${stageId}`;
}
