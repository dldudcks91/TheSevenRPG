# models.py
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# ==========================================
# 1. User 테이블 (계정 메타 데이터)
# ==========================================
class User(Base):
    __tablename__ = "users"

    user_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime, default=func.now(), onupdate=func.now())
    status = Column(String(20), default="ACTIVE")

    gold = Column(BigInteger, default=0)
    current_stage = Column(Integer, default=101)
    max_inventory = Column(Integer, default=100)

    # 관계 설정
    stat = relationship("UserStat", back_populates="user", uselist=False, cascade="all, delete-orphan")
    items = relationship("Item", back_populates="user", cascade="all, delete-orphan")
    collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")

# ==========================================
# 2. UserStat 테이블 (인게임 1:1 스탯 데이터)
# ==========================================
class UserStat(Base):
    __tablename__ = "user_stats"

    user_no = Column(Integer, ForeignKey("users.user_no"), primary_key=True)

    # 성장 데이터
    level = Column(Integer, default=1)
    exp = Column(BigInteger, default=0)

    # 순수 스탯 5종
    stat_str = Column(Integer, default=10)
    stat_dex = Column(Integer, default=10)
    stat_vit = Column(Integer, default=10)
    stat_luck = Column(Integer, default=10)
    stat_cost = Column(Integer, default=10)
    stat_points = Column(Integer, default=0)

    # 관계 설정
    user = relationship("User", back_populates="stat")

# ==========================================
# 3. Item 테이블 (장비 아이템)
# ==========================================
class Item(Base):
    __tablename__ = "items"

    item_uid = Column(String(36), primary_key=True)
    user_no = Column(Integer, ForeignKey("users.user_no"), index=True)

    base_item_id = Column(Integer, nullable=False)
    item_level = Column(Integer, default=1)
    rarity = Column(String(20), default="magic")
    item_score = Column(Integer, default=0)
    item_cost = Column(Integer, default=0)
    prefix_id = Column(String(50), nullable=True)
    suffix_id = Column(String(50), nullable=True)
    set_id = Column(String(50), nullable=True)
    dynamic_options = Column(JSON, nullable=True)
    is_equipped = Column(Boolean, default=False, index=True)
    equip_slot = Column(String(20), nullable=True)

    # 관계 설정
    user = relationship("User", back_populates="items")

# ==========================================
# 4. Collection 테이블 (도감 — 카드 수집 + 스킬 해금)
# ==========================================
class Collection(Base):
    __tablename__ = "collections"

    user_no = Column(Integer, ForeignKey("users.user_no"), primary_key=True)
    monster_idx = Column(Integer, primary_key=True)

    card_count = Column(Integer, default=1)
    collection_level = Column(Integer, default=1)
    skill_slot = Column(Integer, nullable=True)

    # 관계 설정
    user = relationship("User", back_populates="collections")
