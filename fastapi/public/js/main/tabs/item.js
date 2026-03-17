/**
 * TheSevenRPG — Item Tab (아이템 탭)
 * 포션/광석/낙인/퀘스트재료 — Phase 18 이후 본격 구현
 */

const ItemTab = {
    el: null,

    mount(el) {
        this.el = el;

        const MIN_SLOTS = 20;
        el.innerHTML = `
            <div class="tab-item">
                <div class="item-section">
                    <div class="item-section-title">소지 아이템</div>
                    <div class="item-grid">
                        ${'<div class="item-icon empty"></div>'.repeat(MIN_SLOTS)}
                    </div>
                </div>
            </div>
        `;
    },

    unmount() {},
};

export default ItemTab;
