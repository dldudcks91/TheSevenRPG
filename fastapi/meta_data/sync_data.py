import pandas as pd
import os

# ---------------------------------------------------------
# ⚙️ 세팅 구역 
# ---------------------------------------------------------
# 1. 구글 시트 ID 
# URL이 https://docs.google.com/spreadsheets/d/1aBcD...eF/edit 이라면
# 저 중간에 있는 '1aBcD...eF' 부분이 ID다.
SHEET_ID = '1FRV4LHL6dL_5Hz0x1I_lTFg-aL0w5XY73DjYBuFBsl0'

SHEET_NAMES = [
    'equipment_prefix',
    'equipment_base'
    'monster_info', 
    'monster_drop_config', 
    'monster_drop_equipment'

]

# [핵심] 이 스크립트 파일이 위치한 현재 폴더 경로를 자동으로 잡아낸다!
SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
# ---------------------------------------------------------

def download_google_sheets_to_csv():
    # 이미 meta_data 폴더 안이므로 폴더 생성(os.makedirs)은 굳이 안 해도 되지만, 
    # 안전장치로 둬도 무방하다.
    os.makedirs(SAVE_DIR, exist_ok=True)
    print("🌐 온라인 구글 스프레드시트에서 기획 데이터를 긁어옵니다...\n")
    
    for sheet_name in SHEET_NAMES:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        
        try:
            df = pd.read_csv(url)
            
            # 경로 조합 (예: C:/.../RPG_SERVER/meta_data/monster_info.csv)
            save_path = os.path.join(SAVE_DIR, f"{sheet_name}.csv")
            
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
            print(f"✅ [{sheet_name}] 탭 ➔ {save_path} 저장 완료!")
            
        except Exception as e:
            print(f"❌ [{sheet_name}] 탭 다운로드 실패: {e}")


def download_all_sheets_to_csv():
    os.makedirs(SAVE_DIR, exist_ok=True)
    print("🌐 온라인 구글 스프레드시트를 통째로 다운로드 중입니다...\n")
    
    # 마법의 URL: 구글 시트 전체를 엑셀(.xlsx) 형태로 한 번에 다운로드!
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
    
    try:
        # sheet_name=None 을 주면 파이썬이 엑셀 안의 모든 탭을 다 읽어서 딕셔너리로 만들어준다!
        all_sheets = pd.read_excel(url, sheet_name=None, engine='openpyxl')
        
        for sheet_name, df in all_sheets.items():
            # [꿀팁] 만약 기획서에 '작업중', '메모장' 같은 탭이 있다면 
            # 탭 이름 앞에 언더바(_)를 붙여라. (예: _메모장)
            # 파이썬이 언더바가 붙은 탭은 무시하고 안 뽑게 만들어뒀다.
            if sheet_name.startswith('_'):
                print(f"⏭️ [{sheet_name}] 탭은 무시되었습니다. (언더바 포함)")
                continue
                
            save_path = os.path.join(SAVE_DIR, f"{sheet_name}.csv")
            
            # 빈 값이 있는 행이나 열이 있으면 깔끔하게 정리 (NaN 방지)
            df = df.dropna(how='all') 
            
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
            print(f"✅ [{sheet_name}] ➔ {save_path} (추출 완료!)")
            
        print("\n🎉 모든 기획 데이터 동기화가 완벽하게 끝났습니다!")
        
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        print("   👉 팁: 구글 시트 공유 설정이 '링크가 있는 모든 사용자'로 되어있는지 확인해라.")

if __name__ == "__main__":
    download_all_sheets_to_csv()

