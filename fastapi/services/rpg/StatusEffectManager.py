"""
상태이상 시스템 (Phase 16)

7종 상태이상:
- burn(화상 4s): 체력회복 감소
- poison(중독 4s): 매초 고정 데미지
- stun(스턴 1s): 공격 불가
- freeze(빙결 3s): 공격속도 감소
- corrode(침식 영구): 피격마다 방어력 영구 감소 (스택)
- charm(매혹 4s): 명중률 대폭 감소
- judge(심판 2s): 카드 스킬 발동 확률 0%

중첩 규칙: 갱신(타이머 리셋), 침식만 스택형
다른 종류 동시 적용 가능
"""


# 상태이상 기본 설정
STATUS_EFFECTS = {
    "burn": {"duration": 4.0, "stackable": False},
    "poison": {"duration": 4.0, "stackable": False},
    "stun": {"duration": 1.0, "stackable": False},
    "freeze": {"duration": 3.0, "stackable": False},
    "corrode": {"duration": 999.0, "stackable": True},  # 영구
    "charm": {"duration": 4.0, "stackable": False},
    "judge": {"duration": 2.0, "stackable": False},
}

# 상태이상 수치 (밸런싱 미확정 → 임시값)
POISON_DMG_PER_SEC = 5          # 초당 고정 데미지 (밸런스 조정 필요)
FREEZE_ASPD_REDUCTION = 0.50    # 공속 50% 감소
CHARM_ACC_REDUCTION = 0.50      # 명중률 50% 감소
CORRODE_DEF_REDUCTION = 0.02    # 피격당 방어력 2% 영구 감소
BURN_HEAL_REDUCTION = 0.50      # 회복량 50% 감소


class CombatUnit:
    """전투 유닛 — 플레이어 또는 몬스터의 전투 상태를 관리"""

    def __init__(self, hp, max_hp, atk, atk_speed, defense, magic_def,
                 acc, eva, crit_chance, crit_dmg, level, size=2, fhr=0.0):
        self.hp = hp
        self.max_hp = max_hp
        self.atk = atk
        self.base_atk = atk
        self.atk_speed = atk_speed
        self.base_atk_speed = atk_speed
        self.defense = defense
        self.base_defense = defense
        self.magic_def = magic_def
        self.acc = acc
        self.base_acc = acc
        self.eva = eva
        self.crit_chance = crit_chance
        self.crit_dmg = crit_dmg
        self.level = level
        self.size = size        # 1=소형, 2=중형, 3=대형
        self.fhr = fhr          # 타격회복속도 (0~1)

        # 상태이상 타이머 {effect_name: remaining_seconds}
        self.status_effects = {}
        # 침식 스택
        self.corrode_stacks = 0
        # 경직 타이머
        self.stagger_timer = 0.0

    def apply_status(self, effect_name: str):
        """상태이상 적용 (갱신 or 스택)"""
        cfg = STATUS_EFFECTS.get(effect_name)
        if not cfg:
            return
        if effect_name == "corrode":
            # 침식은 스택형
            self.corrode_stacks += 1
            self.defense = self.base_defense * max(0, 1 - self.corrode_stacks * CORRODE_DEF_REDUCTION)
        else:
            # 갱신형: 타이머 리셋
            self.status_effects[effect_name] = cfg["duration"]

    def has_status(self, effect_name: str) -> bool:
        if effect_name == "corrode":
            return self.corrode_stacks > 0
        return self.status_effects.get(effect_name, 0) > 0

    def tick_status(self, dt: float) -> dict:
        """dt초 경과. 상태이상 효과 처리. 반환: 이벤트 dict"""
        events = {}
        expired = []

        for name, remaining in self.status_effects.items():
            self.status_effects[name] = remaining - dt
            if self.status_effects[name] <= 0:
                expired.append(name)

        for name in expired:
            del self.status_effects[name]
            events[f"{name}_expired"] = True
            # 빙결 해제 시 공속 복구
            if name == "freeze":
                self.atk_speed = self.base_atk_speed
            # 매혹 해제 시 명중 복구
            if name == "charm":
                self.acc = self.base_acc

        # 빙결 효과: 공속 감소 (지속 중)
        if self.has_status("freeze"):
            self.atk_speed = self.base_atk_speed * (1 - FREEZE_ASPD_REDUCTION)

        # 매혹 효과: 명중 감소 (지속 중)
        if self.has_status("charm"):
            self.acc = self.base_acc * (1 - CHARM_ACC_REDUCTION)

        return events

    def tick_stagger(self, dt: float) -> bool:
        """경직 타이머 갱신. 경직 중이면 True 반환"""
        if self.stagger_timer > 0:
            self.stagger_timer -= dt
            if self.stagger_timer <= 0:
                self.stagger_timer = 0
            return True
        return False

    def apply_stagger(self, damage: float, base_stagger_time: float = 0.5):
        """경직 판정: 단타 피해 > 최대HP÷10"""
        if damage > self.max_hp / 10:
            actual = base_stagger_time * (1 - self.fhr)
            self.stagger_timer = max(0.1, actual)


def get_size_correction(attacker_size: int, defender_size: int) -> float:
    """사이즈 보정 배율"""
    if attacker_size == 3 and defender_size == 3:
        return 1.10
    elif attacker_size == 3 and defender_size == 1:
        return 0.90
    elif attacker_size == 1 and defender_size == 3:
        return 0.90
    return 1.0
