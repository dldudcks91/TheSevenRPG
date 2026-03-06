import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import os
import sys

# Windows 콘솔 한글/이모지 출력 깨짐 방지
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------
# ⚙️ 세팅 구역
# ---------------------------------------------------------
# 구글 시트 ID
SHEET_ID = '1FRV4LHL6dL_5Hz0x1I_lTFg-aL0w5XY73DjYBuFBsl0'

# 서비스 계정 키 파일 (이 스크립트와 같은 폴더에 놓아라)
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'credentials.json')

# 이 스크립트가 위치한 폴더 = meta_data 폴더
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# 업로드 제외 파일
EXCLUDE_FILES = {'sync_data.py', 'sync_data_from_gs.py', 'sync_data_to_gs.py'}

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
# ---------------------------------------------------------


def check_credentials():
    """credentials.json 파일이 없으면 발급 방법을 안내하고 종료한다."""
    if not os.path.exists(CREDENTIALS_FILE):
        print("credentials.json 파일이 없습니다.")
        print()
        print("=" * 60)
        print("  서비스 계정 키 발급 방법 (최초 1회만)")
        print("=" * 60)
        print("  1. https://console.cloud.google.com 접속")
        print("  2. API 및 서비스 -> 라이브러리 -> 'Google Sheets API' 활성화")
        print("  3. API 및 서비스 -> 라이브러리 -> 'Google Drive API' 활성화")
        print("  4. API 및 서비스 -> 사용자 인증 정보")
        print("     -> '사용자 인증 정보 만들기' -> '서비스 계정'")
        print("  5. 서비스 계정 생성 후 -> '키' 탭 -> 'JSON' 키 추가 -> 다운로드")
        print(f"  6. 다운로드한 파일을 '{CREDENTIALS_FILE}' 으로 저장")
        print()
        print("  마지막으로 구글 시트를 서비스 계정 이메일과 공유해야 한다.")
        print("  (credentials.json 안의 'client_email' 값을 시트 편집자로 추가)")
        print("=" * 60)
        sys.exit(1)


def upload_csv_to_sheet(worksheet, csv_path):
    """CSV 파일을 읽어서 워크시트에 덮어쓴다. (구조화된 데이터 기준)"""
    df = pd.read_csv(csv_path, encoding='utf-8-sig', dtype=str)
    df = df.fillna('')

    # 헤더 + 데이터 행을 리스트로 변환
    rows = [df.columns.tolist()] + df.values.tolist()

    worksheet.clear()
    worksheet.update(rows, value_input_option='RAW')


def sync_to_gs():
    """meta_data 폴더의 모든 CSV를 구글 시트로 업로드한다."""
    check_credentials()

    print("서비스 계정으로 구글 시트에 접속합니다...\n")
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)

    try:
        spreadsheet = gc.open_by_key(SHEET_ID)
    except gspread.SpreadsheetNotFound:
        print(f"시트 ID '{SHEET_ID}'를 찾을 수 없습니다.")
        print("  SHEET_ID가 맞는지, 서비스 계정 이메일이 시트 편집자로 공유되어 있는지 확인해라.")
        sys.exit(1)

    print(f"'{spreadsheet.title}' 시트에 연결 완료!\n")

    csv_files = sorted([
        f for f in os.listdir(DATA_DIR)
        if f.endswith('.csv') and f not in EXCLUDE_FILES
    ])

    if not csv_files:
        print("업로드할 CSV 파일이 없습니다.")
        return

    success_count = 0
    fail_count = 0

    for csv_file in csv_files:
        sheet_name = csv_file.replace('.csv', '')

        # 언더바로 시작하는 탭은 스킵
        if sheet_name.startswith('_'):
            print(f"  skip [{sheet_name}] (언더바 탭)")
            continue

        csv_path = os.path.join(DATA_DIR, csv_file)

        try:
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=50)
                print(f"  [{sheet_name}] 탭 신규 생성")

            upload_csv_to_sheet(worksheet, csv_path)
            print(f"  [{sheet_name}] -> 업로드 완료")
            success_count += 1

        except Exception as e:
            print(f"  [{sheet_name}] 업로드 실패: {e}")
            fail_count += 1

    print(f"\n완료: {success_count}개 업로드 / {fail_count}개 실패")


if __name__ == "__main__":
    sync_to_gs()


# =============================================================
# 필요한 패키지 설치 명령어
# pip install gspread google-auth pandas openpyxl
# =============================================================
