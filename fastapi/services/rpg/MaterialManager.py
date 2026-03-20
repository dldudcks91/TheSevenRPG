import logging
from database import SessionLocal
from models import Material, BattleSession
from services.system.ErrorCode import ErrorCode, error_response

logger = logging.getLogger("RPG_SERVER")

# ── 포션 설정 (CSV 미확정 → 폴백 상수) ──
POTION_CONFIG = {
    1: {"name": "하급 포션", "heal": 50},
    2: {"name": "중급 포션", "heal": 150},
    3: {"name": "상급 포션", "heal": 400},
}

MAX_POTION_PER_RUN = 3  # 스테이지 런 당 최대 포션 사용 횟수

# 웨이브별 몬스터 수 (웨이브 1~3: 4마리, 웨이브 4: 1마리 보스)
WAVE_MONSTER_COUNT = {1: 4, 2: 4, 3: 4, 4: 1}


class MaterialManager:
    """재료 아이템 관리 (API 2011, 2015)"""

    @classmethod
    async def get_materials(cls, user_no: int, data: dict):
        """API 2015: 재료 인벤토리 조회"""
        # ── [3] DB 세션 ──
        db = SessionLocal()
        try:
            materials = db.query(Material).filter(
                Material.user_no == user_no,
                Material.amount > 0,
            ).all()

            mat_list = [
                {
                    "material_type": m.material_type,
                    "material_id": m.material_id,
                    "amount": m.amount,
                }
                for m in materials
            ]

        except Exception as e:
            logger.error(f"[MaterialManager] get_materials 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "재료 조회 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"재료 {len(mat_list)}종 조회",
            "data": {"materials": mat_list},
        }

    @classmethod
    async def use_potion(cls, user_no: int, data: dict):
        """API 2011: 포션 사용 — 웨이브 클리어 후 HP 회복 (전투 중 불가)"""
        # ── [1] 입력 추출 ──
        potion_id = data.get("potion_id")
        if potion_id is None:
            return error_response(ErrorCode.INVALID_REQUEST, "potion_id가 필요합니다.")
        potion_id = int(potion_id)

        # ── [2] 메타데이터 검증 ──
        potion_info = POTION_CONFIG.get(potion_id)
        if not potion_info:
            return error_response(ErrorCode.INVALID_REQUEST, f"존재하지 않는 포션: {potion_id}")

        # ── [3] DB 세션 + 상태 검증 ──
        db = SessionLocal()
        try:
            # BattleSession 존재 여부
            session = db.query(BattleSession).filter(
                BattleSession.user_no == user_no
            ).with_for_update().first()
            if not session:
                return error_response(ErrorCode.POTION_NOT_USABLE, "진행 중인 전투 세션이 없습니다.")

            # 웨이브 클리어 상태 검증 (현재 웨이브의 모든 몬스터 처치 확인)
            if not cls._is_wave_cleared(session):
                return error_response(ErrorCode.POTION_NOT_USABLE, "웨이브 클리어 후에만 포션을 사용할 수 있습니다.")

            # HP가 이미 최대인 경우
            if session.current_hp >= session.max_hp:
                return error_response(ErrorCode.POTION_NOT_USABLE, "HP가 이미 최대입니다.")

            # 포션 사용 횟수 제한
            potion_used = session.potion_used or 0
            if potion_used >= MAX_POTION_PER_RUN:
                return error_response(ErrorCode.POTION_LIMIT, f"이번 런에서 포션을 더 이상 사용할 수 없습니다. ({potion_used}/{MAX_POTION_PER_RUN})")

            # 포션 보유량 확인
            material = db.query(Material).filter(
                Material.user_no == user_no,
                Material.material_type == "potion",
                Material.material_id == potion_id,
            ).with_for_update().first()
            if not material or material.amount <= 0:
                return error_response(ErrorCode.MATERIAL_NOT_FOUND, "포션이 부족합니다.")

            # ── [4] 비즈니스 로직 ──
            heal_amount = potion_info["heal"]
            old_hp = session.current_hp
            session.current_hp = min(session.current_hp + heal_amount, session.max_hp)
            actual_heal = session.current_hp - old_hp
            session.potion_used = potion_used + 1

            material.amount -= 1
            remaining = material.amount
            if material.amount <= 0:
                db.delete(material)
                remaining = 0

            result_hp = session.current_hp
            max_hp = session.max_hp
            new_potion_used = session.potion_used

            # ── [5] 커밋 ──
            db.commit()
            logger.info(f"[MaterialManager] use_potion (user_no={user_no}, potion_id={potion_id}, heal={actual_heal}, hp={result_hp}/{max_hp}, used={new_potion_used})")

        except Exception as e:
            db.rollback()
            logger.error(f"[MaterialManager] use_potion 실패: {e}", exc_info=True)
            return error_response(ErrorCode.DB_ERROR, "포션 사용 중 오류가 발생했습니다.")
        finally:
            db.close()

        # ── [6] 응답 반환 ──
        return {
            "success": True,
            "message": f"{potion_info['name']}을 사용하여 HP를 {actual_heal} 회복했습니다.",
            "data": {
                "current_hp": result_hp,
                "max_hp": max_hp,
                "healed": actual_heal,
                "potion_used": new_potion_used,
                "potion_remaining": remaining,
            },
        }

    # ── 헬퍼 ──

    @classmethod
    def _is_wave_cleared(cls, session: BattleSession) -> bool:
        """현재 웨이브의 모든 몬스터가 처치되었는지 확인"""
        wave_kills = session.wave_kills or {}
        current_wave = session.current_wave
        current_wave_key = str(current_wave)

        # 웨이브4(보스) 클리어 후에는 clear_stage를 호출해야 하므로 포션 사용 불가
        if current_wave > 4:
            return False

        # 현재 웨이브의 킬 기록
        kills = wave_kills.get(current_wave_key, [])
        expected_count = WAVE_MONSTER_COUNT.get(current_wave, 4)

        return len(kills) >= expected_count
