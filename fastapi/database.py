

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


host = 'localhost'
user = 'root'
password = 'an98'
db='TheSevenRPG'
charset='utf8'
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:3306/{db}?charset-{charset}"

engine = create_engine(DATABASE_URL)
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    """서버 시작 시 테이블이 없으면 자동으로 생성해주는 함수"""
    import models  # 모델을 임포트해야 Base.metadata가 테이블을 인식함
    Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 테이블 생성 완료!")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()