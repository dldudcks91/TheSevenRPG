from pydantic import BaseModel
from typing import Dict, Any

class ApiRequest(BaseModel):
    user_no: int            # 유저 고유 번호
    api_code: int           # 요청할 API 코드 (예: 3001)
    data: Dict[str, Any] = {} # 상세 데이터
