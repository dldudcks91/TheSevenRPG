from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from schemas import ApiRequest  # 네가 만들어둔 스키마 사용
import database  # 네가 만들어둔 모듈
import logging

from services.system import GameDataManager, APIManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RPG_SERVER")

app = FastAPI(title="Hardcore Farming RPG Server")


app.mount("/", StaticFiles(directory="public", html=True), name="public")
@app.on_event("startup")
async def startup_event():
    logger.info("=== RPG Server Starting Up ===")
    
    # 서버 기동 시 CSV 데이터를 메모리에 로드
    GameDataManager.load_all_csv()

    # DB 연결 (너의 기존 코드)
    database.init_db()

    logger.info("=== Server is Ready to Battle ===")



@app.post("/api")
async def api_gateway(request: ApiRequest):
    """모든 클라이언트 요청이 들어오는 유일한 관문 (Gateway)"""
    logger.info(f"[API Call] User: {request.user_no} | Code: {request.api_code}")
    
    api_code = request.api_code
    
    # 1. 요청된 API 코드가 APIManager에 정의되어 있는지 확인
    if api_code not in APIManager.api_map:
        return JSONResponse(status_code=400, content={
            "success": False, 
            "message": f"Unknown API Code: {api_code}"
        })
        
    # 2. 매핑된 클래스와 메서드 호출
    manager_class, manager_method = APIManager.api_map[api_code]
    
    try:
        # User 정보와 Payload Data를 매니저로 전달
        # 모든 매니저 메서드는 async def 로 구현되어야 함
        result = await manager_method(request.user_no, request.data)
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"[API Error] Code {api_code} Failed: {str(e)}")
        return JSONResponse(status_code=500, content={
            "success": False,
            "message": "Internal Server Error during execution."
        })