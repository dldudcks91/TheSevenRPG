/**
 * LPC 스프라이트 매니페스트.
 * 캐릭터/몬스터의 레이어 구성과 애니메이션 스펙을 한 곳에서 관리한다.
 *
 * 레이어 template의 `{anim}` 토큰은 애니메이션 이름(idle/walk/slash/hurt)으로 치환된다.
 */

export const LPC_BASE_URL = 'img/lpc/assets';

/** 표준 방향: LPC v2 규약 N=0, W=1, S=2, E=3 */
export const DIR_TO_ROW = { N: 0, W: 1, S: 2, E: 3 };

/**
 * 기본 캐릭터 레이어 (walking.js와 공유). z-order 오름차순으로 합성된다.
 * lpc_download.py가 확보하는 body/head/legs 파츠만 포함한다.
 * cape/hair/eyes/feet 등 추가 파츠는 에셋 확보 후 여기 추가.
 */
export const CHARACTER_LAYERS = [
    { template: 'body/male/{anim}.png', z: 10 },
    { template: 'head/male/{anim}.png', z: 15 },
    { template: 'legs/male/{anim}.png', z: 25 },
];

/**
 * 캐릭터 애니메이션 스펙.
 *  - frames: 프레임 수
 *  - frameRate: fps
 *  - loop: true=idle/walk 반복, false=1회 재생 후 persistent 상태로 복귀
 *  - directional: 4방향 행 지원 여부. false면 방향 무관 single row로 취급
 */
export const CHARACTER_ANIMS = {
    idle:  { frames: 2, frameRate: 3,  loop: true,  directional: true  },
    walk:  { frames: 9, frameRate: 8,  loop: true,  directional: true  },
    slash: { frames: 6, frameRate: 12, loop: false, directional: true  },
    hurt:  { frames: 6, frameRate: 12, loop: false, directional: false },
};

/** 전투 상태 → LPC 애니 매핑. */
export const STATE_TO_ANIM = {
    idle: 'idle',
    walk: 'walk',
    attack: 'slash',
    hurt: 'hurt',
};

/** spawn_type별 표시 크기 배수 (일반=1.0 기준). LpcSprite/StaticSprite 양쪽에 적용. */
export const SPAWN_SIZE_SCALE = {
    '\uC77C\uBC18':      1.00,  // 일반
    '\uC815\uC608':      1.10,  // 정예
    '\uBCF4\uC2A4':      1.30,  // 보스
    '\uCC55\uD130\uBCF4\uC2A4': 1.55,  // 챕터보스
};

/**
 * 몬스터 LPC 매니페스트.
 *   monster_idx(number) → { layers, anims } 형태.
 *   엔트리가 없으면 PNG(StaticSprite) → 컬러박스(RectSprite) 3단 폴백으로 진행.
 *
 * 예시:
 *   1101: {
 *       layers: [{ template: 'monsters/skeleton/{anim}.png', z: 10 }],
 *       anims:  { idle: {...}, walk: {...}, slash: {...}, hurt: {...} },
 *   }
 *
 * LPC 공식 몬스터 에셋은 구조가 불규칙해 현재는 비워둔다. 추후 몬스터별 에셋 확보 시 채운다.
 */
export const MONSTER_MANIFEST = {};
