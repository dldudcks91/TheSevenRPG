/**
 * TheSevenRPG — Item Tab (아이템 탭)
 * 포션/광석/낙인/퀘스트재료 — Phase 18 이후 본격 구현
 */

const ItemTab = {
    el: null,

    mount(el) {
        this.el = el;

        el.innerHTML = `
            <div class="tab-item">
                <div class="item-placeholder">
                    <span class="item-placeholder-icon">\u{1F392}</span>
                    <span class="item-placeholder-text">아이템 탭</span>
                    <span class="item-placeholder-sub">준비 중</span>
                </div>
            </div>
        `;
    },

    unmount() {},
};

export default ItemTab;
