/**
 * TheSevenRPG — Chapter Map Data
 * 챕터별 분기 월드맵 노드 & 엣지 정의
 *
 * 노드 타입:
 *   town  — 마을 출발점
 *   hunt  — 사냥터 (클릭 시 스테이지 입장)
 *   boss  — 챕터 보스 (클릭 시 보스전 입장)
 *
 * 좌표: x, y는 맵 컨테이너 기준 % (0~100)
 */

import { t } from './i18n/index.js';

/** 챕터별 맵 데이터 (함수로 감싸서 i18n 적용) */
function buildChapterMaps() {
    return {
        1: {
            name: t('map_ch1_name'),
            sin: 'wrath',
            bgColor: '#1a0808',
            nodes: [
                { id: 'start',     type: 'town', x: 8,  y: 50, name: t('map_town') },
                { id: 'stage_101', type: 'hunt', x: 28, y: 50, name: t('map_ch1_s1'),     stageId: 101 },

                // ── 분기: 두 전장 중 택1 (둘 다 클리어 가능) ──
                { id: 'stage_102', type: 'hunt', x: 50, y: 24, name: t('map_ch1_s2a'),   stageId: 102 },
                { id: 'stage_105', type: 'hunt', x: 50, y: 76, name: t('map_ch1_s2b'),   stageId: 102 },

                { id: 'stage_103', type: 'hunt', x: 72, y: 50, name: t('map_ch1_s3'),     stageId: 103 },
                { id: 'stage_104', type: 'boss', x: 92, y: 50, name: t('map_ch1_boss'),     stageId: 104 },
            ],
        edges: [
            { from: 'start',     to: 'stage_101' },

            // 분기
            { from: 'stage_101', to: 'stage_102' },
            { from: 'stage_101', to: 'stage_105' },

            // 합류
            { from: 'stage_102', to: 'stage_103' },
            { from: 'stage_105', to: 'stage_103' },

            { from: 'stage_103', to: 'stage_104' },
        ],
    },
    };
}

/**
 * 챕터 맵 데이터를 반환한다.
 * @param {number} chapterId
 * @returns {object|null} { name, sin, bgColor, nodes, edges }
 */
export function getChapterMap(chapterId) {
    const maps = buildChapterMaps();
    return maps[chapterId] || null;
}
