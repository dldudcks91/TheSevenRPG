# models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# ==========================================
# 1. User 테이블 (계정 메타 데이터)
# ==========================================
class User(Base):
    __tablename__ = "users"

    user_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(50), unique=True, index=True, nullable=False) # 로그인 아이디
    created_at = Column(DateTime, default=func.now())          # 캐릭터 생성일
    last_login = Column(DateTime, default=func.now(), onupdate=func.now()) # 마지막 접속
    status = Column(String(20), default="ACTIVE")              # 계정 상태 (BANNED 등)

    # 관계 설정 (1:1 및 1:N)
    stat = relationship("UserStat", back_populates="user", uselist=False, cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="user", cascade="all, delete-orphan")

# ==========================================
# 2. UserStat 테이블 (인게임 1:1 스탯 데이터)
# ==========================================
class UserStat(Base):
    __tablename__ = "user_stats"

    # User 테이블의 PK를 그대로 PK이자 FK로 사용 (완벽한 1:1 구조)
    user_no = Column(Integer, ForeignKey("users.user_no"), primary_key=True)
    
    # 성장 데이터
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    gold = Column(Integer, default=0)
    
    # 순수 스탯 데이터 (여기엔 파생 스탯인 공격력, 방어력 안 넣은 거 기억하지?)
    stat_str = Column(Integer, default=10)
    stat_dex = Column(Integer, default=10)
    stat_vit = Column(Integer, default=10)
    stat_points = Column(Integer, default=0) # 레벨업 시 찍을 수 있는 잔여 포인트

    # 관계 설정
    user = relationship("User", back_populates="stat")

# ==========================================
# 3. Inventory 테이블 (장비, 재료 통합 가방)
# ==========================================
class Inventory(Base):
    __tablename__ = "inventories"

    item_uid = Column(Integer, primary_key=True, autoincrement=True) # 아이템 고유 번호
    user_no = Column(Integer, ForeignKey("users.user_no"), index=True)
    
    # 아이템 기본 정보
    item_type = Column(String(20), nullable=False)     # "WEAPON", "ARMOR", "MATERIAL", "CARD" 등
    item_base_id = Column(String(50), nullable=False)  # meta_data의 ID (예: "dagger_001")
    amount = Column(Integer, default=1)                # 장비는 1, 재료/소모품은 99 등 누적
    
    # 장비 전용 특수 데이터 (재료일 경우 NULL)
    item_score = Column(Float, nullable=True)     # 아이템 퀄리티 점수 (아까 만든 스코어 공식)
    prefix_id = Column(String(50), nullable=True) # 7죄종 옵션 ID (예: "SLOTH_01")
    is_equipped = Column(Boolean, default=False)  # 현재 장착 중인가?

    # 관계 설정
    user = relationship("User", back_populates="inventory")