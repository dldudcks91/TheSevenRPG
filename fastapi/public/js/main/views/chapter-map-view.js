/**
 * TheSevenRPG — Chapter Map View (분기 월드맵)
 * 챕터별 노드 맵 + 캐릭터 이동
 *
 * 구조:
 *   [헤더] 챕터 선택 탭 + 뒤로가기
 *   [맵]   SVG 경로 + 노드(전장/보스) + 캐릭터 스프라이트
 */
import { Store } from '../../store.js';
import { apiCall } from '../../api.js';
import { showLoading, hideLoading, setupEventDelegation, teardown } from '../../utils.js';
import { getChapterMap } from '../../map-data.js';
import { getChapters } from '../../meta-data.js';
import { t } from '../../i18n/index.js';
import MainScreen from '../../main.js';

const ChapterMapView = {
    el: null,
    refs: {},
    _selectedChapter: 1,
    _characterNodeId: null,
    _animating: false,

    mount(el) {
        setupEventDelegation(this, el);

        el.innerHTML = `
            <div class="cmap-screen">
                <div class="cmap-header">
                    <button class="cmap-back-btn" data-action="back">${t('cmap_back')}</button>
                    <div class="cmap-chapter-tabs" id="cmap-tabs"></div>
                </div>
                <div class="cmap-title-bar" id="cmap-title"></div>
                <div class="cmap-container" id="cmap-container">
                    <svg class="cmap-svg" id="cmap-svg"></svg>
                    <div class="cmap-nodes" id="cmap-nodes"></div>
                    <div class="cmap-character" id="cmap-char">
                        <div class="cmap-char-sprite"></div>
                    </div>
                </div>
            </div>
        `;

        this.refs = {
            tabs: el.querySelector('#cmap-tabs'),
            title: el.querySelector('#cmap-title'),
            container: el.querySelector('#cmap-container'),
            svg: el.querySelector('#cmap-svg'),
            nodes: el.querySelector('#cmap-nodes'),
            character: el.querySelector('#cmap-char'),
        };

        this._selectedChapter = 1;
        this._renderTabs();
        this._renderMap();
    },

    unmount() {
        teardown(this);
    },

    // ── 이벤트 ──

    _onEvent(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        switch (target.dataset.action) {
            case 'back':
                MainScreen.switchRightView('town');
                break;
            case 'select-chapter':
                this._selectChapter(parseInt(target.dataset.chapter));
                break;
            case 'node-click':
                this._onNodeClick(target.dataset.nodeId);
                break;
        }
    },

    // ── 챕터 탭 ──

    _renderTabs() {
        const chapters = getChapters();
        const currentStage = Store.get('user.current_stage') || 101;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;

        this.refs.tabs.innerHTML = chapters.map(ch => `
            <button class="cmap-tab ${ch.id === this._selectedChapter ? 'active' : ''} ${ch.id > maxChapter ? 'locked' : ''}"
                    data-action="select-chapter" data-chapter="${ch.id}"
                    ${ch.id > maxChapter ? 'disabled' : ''}>
                ${ch.id}
            </button>
        `).join('');
    },

    _selectChapter(chapterId) {
        const currentStage = Store.get('user.current_stage') || 101;
        const maxChapter = Math.floor((currentStage - 1) / 100) + 1;
        if (chapterId > maxChapter) return;

        this._selectedChapter = chapterId;
        this._renderTabs();
        this._renderMap();
    },

    // ── 맵 렌더링 ──

    _renderMap() {
        const mapData = getChapterMap(this._selectedChapter);
        if (!mapData) {
            this.refs.title.textContent = t('cmap_no_data');
            this.refs.svg.innerHTML = '';
            this.refs.nodes.innerHTML = '';
            return;
        }

        const currentStage = Store.get('user.current_stage') || 101;
        const sinClass = mapData.sin || 'wrath';

        // 타이틀
        this.refs.title.innerHTML = `
            <span class="cmap-title-sin sin-${sinClass}">${t('cmap_chapter', { n: this._selectedChapter })}</span>
            <span class="cmap-title-name">${mapData.name}</span>
        `;

        // 맵 배경
        this.refs.container.style.backgroundColor = mapData.bgColor || '';
        this.refs.container.dataset.sin = sinClass;

        // 노드 상태 계산
        const nodeStates = this._calcNodeStates(mapData, currentStage);

        // SVG 경로
        this._renderEdges(mapData, nodeStates);

        // 노드 렌더링
        this._renderNodes(mapData, nodeStates);

        // 캐릭터 배치
        this._placeCharacter(mapData, nodeStates);
    },

    /** 각 노드의 상태: locked / unlocked / completed */
    _calcNodeStates(mapData, currentStage) {
        const states = {};

        for (const node of mapData.nodes) {
            if (node.type === 'town') {
                states[node.id] = 'completed';
                continue;
            }

            // hunt / boss: stageId 기준
            if (node.stageId < currentStage) {
                states[node.id] = 'completed';
            } else if (node.stageId === currentStage) {
                states[node.id] = 'unlocked';
            } else {
                states[node.id] = 'locked';
            }
        }

        // 선행 노드 기반 해금 검증: 선행 노드 중 하나라도 completed여야 unlocked
        for (const node of mapData.nodes) {
            if (states[node.id] !== 'unlocked') continue;

            const predecessors = mapData.edges
                .filter(e => e.to === node.id)
                .map(e => e.from);

            if (predecessors.length > 0) {
                const anyPredCompleted = predecessors.some(pid => states[pid] === 'completed');
                if (!anyPredCompleted) {
                    states[node.id] = 'locked';
                }
            }
        }

        return states;
    },

    /** SVG 경로를 그린다 */
    _renderEdges(mapData, nodeStates) {
        const nodeMap = {};
        for (const n of mapData.nodes) nodeMap[n.id] = n;

        const lines = mapData.edges.map(edge => {
            const from = nodeMap[edge.from];
            const to = nodeMap[edge.to];
            if (!from || !to) return '';

            const isActive = nodeStates[edge.from] === 'completed';
            const cls = isActive ? 'cmap-edge active' : 'cmap-edge';

            // 곡선: 분기/합류 시 부드러운 커브
            const dx = to.x - from.x;
            const dy = to.y - from.y;
            const needsCurve = Math.abs(dy) > 10;

            if (needsCurve) {
                const cx1 = from.x + dx * 0.4;
                const cy1 = from.y;
                const cx2 = from.x + dx * 0.6;
                const cy2 = to.y;
                return `<path class="${cls}" d="M ${from.x} ${from.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${to.x} ${to.y}" />`;
            }

            return `<line class="${cls}" x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" />`;
        }).join('');

        this.refs.svg.setAttribute('viewBox', '0 0 100 100');
        this.refs.svg.setAttribute('preserveAspectRatio', 'none');
        this.refs.svg.innerHTML = lines;
    },

    /** 노드를 렌더링한다 */
    _renderNodes(mapData, nodeStates) {
        this.refs.nodes.innerHTML = mapData.nodes.map(node => {
            const state = nodeStates[node.id];
            const isClickable = state === 'unlocked' || state === 'completed';
            const typeIcon = this._getNodeIcon(node.type);

            return `
                <div class="cmap-node cmap-node-${node.type} cmap-state-${state}"
                     style="left:${node.x}%;top:${node.y}%"
                     ${isClickable ? `data-action="node-click" data-node-id="${node.id}"` : ''}
                     title="${node.name}">
                    <div class="cmap-node-icon">${typeIcon}</div>
                    <div class="cmap-node-label">${node.name}</div>
                    ${state === 'completed' ? '<div class="cmap-node-check">\u2713</div>' : ''}
                    ${state === 'locked' ? '<div class="cmap-node-lock">\uD83D\uDD12</div>' : ''}
                </div>
            `;
        }).join('');
    },

    _getNodeIcon(type) {
        switch (type) {
            case 'town': return '\uD83C\uDFE0';
            case 'hunt': return '\u2694\uFE0F';
            case 'boss': return '\uD83D\uDC80';
            default:     return '\u25CF';
        }
    },

    /** 캐릭터를 마지막 진행 노드에 배치 */
    _placeCharacter(mapData, nodeStates) {
        let targetNode = null;

        // 첫 번째 unlocked 노드
        for (const node of mapData.nodes) {
            if (nodeStates[node.id] === 'unlocked') {
                targetNode = node;
                break;
            }
        }

        // 없으면 마지막 completed 노드
        if (!targetNode) {
            for (let i = mapData.nodes.length - 1; i >= 0; i--) {
                if (nodeStates[mapData.nodes[i].id] === 'completed') {
                    targetNode = mapData.nodes[i];
                    break;
                }
            }
        }

        if (!targetNode) targetNode = mapData.nodes[0];

        this._characterNodeId = targetNode.id;
        this._moveCharacterTo(targetNode.x, targetNode.y, false);
    },

    /** 캐릭터 스프라이트 이동 */
    _moveCharacterTo(x, y, animate = true) {
        const char = this.refs.character;
        if (animate) {
            char.classList.add('cmap-char-moving');
        } else {
            char.classList.remove('cmap-char-moving');
        }
        char.style.left = `${x}%`;
        char.style.top = `${y}%`;
    },

    // ── 노드 클릭 ──

    _onNodeClick(nodeId) {
        if (this._animating) return;

        const mapData = getChapterMap(this._selectedChapter);
        if (!mapData) return;

        const node = mapData.nodes.find(n => n.id === nodeId);
        if (!node) return;

        // 캐릭터 이동 애니메이션
        if (this._characterNodeId !== nodeId) {
            this._animating = true;
            this._moveCharacterTo(node.x, node.y, true);
            this._characterNodeId = nodeId;

            setTimeout(() => {
                this._animating = false;
                this._enterStage(node.stageId);
            }, 400);
        } else {
            this._enterStage(node.stageId);
        }
    },

    // ── 스테이지 입장 ──

    async _enterStage(stageId) {
        showLoading();
        try {
            const result = await apiCall(3003, { stage_id: stageId });
            if (!result?.success) return;

            Store.set('battle.stage_id', stageId);
            Store.set('battle.monster_pool', result.data.monsters || []);

            MainScreen.switchRightView('battle', {
                stageId,
                monsters: result.data.monsters || [],
            });
        } finally {
            hideLoading();
        }
    },
};

export default ChapterMapView;
