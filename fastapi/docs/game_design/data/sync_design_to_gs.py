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
# 1. 구글 시트 ID (sync_design_from_gs.py와 동일)
SHEET_ID = '121vKiAiPh1h0JkTZnO6vJI_cDibMPxtd4CeXz1shFZU'

# 2. 서비스 계정 키 파일 경로
# 구글 클라우드 콘솔에서 서비스 계정 키를 발급받아 이 폴더에 넣어라.
# 발급 방법은 스크립트 하단 주석 참고.
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'credentials.json')

# 3. 업로드할 CSV가 있는 폴더 (이 스크립트가 위치한 폴더)
DESIGN_DIR = os.path.dirname(os.path.abspath(__file__))

# 4. 업로드 제외할 파일 목록 (이 스크립트 자체 등)
EXCLUDE_FILES = {'sync_design_from_gs.py', 'sync_design_to_gs.py'}

# 5. 구글 시트에서 언더바(_)로 시작하는 탭은 덮어쓰지 않는다
#    (from_gs.py와 동일한 규칙)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]
# ---------------------------------------------------------


def check_credentials():
    """credentials.json 파일이 없으면 발급 방법을 안내하고 종료한다."""
    if not os.path.exists(CREDENTIALS_FILE):
        print("❌ credentials.json 파일이 없습니다.")
        print()
        print("=" * 60)
        print("  📋 서비스 계정 키 발급 방법 (최초 1회만)")
        print("=" * 60)
        print("  1. https://console.cloud.google.com 접속")
        print("  2. 프로젝트 선택 (또는 새 프로젝트 생성)")
        print("  3. API 및 서비스 → 라이브러리 → 'Google Sheets API' 활성화")
        print("  4. API 및 서비스 → 라이브러리 → 'Google Drive API' 활성화")
        print("  5. API 및 서비스 → 사용자 인증 정보")
        print("     → '사용자 인증 정보 만들기' → '서비스 계정'")
        print("  6. 서비스 계정 생성 후 → '키' 탭 → 'JSON' 키 추가 → 다운로드")
        print(f"  7. 다운로드한 파일을 '{CREDENTIALS_FILE}' 으로 저장")
        print()
        print("  ⚠️  마지막으로 구글 시트를 서비스 계정 이메일과 공유해야 한다.")
        print("     (credentials.json 안의 'client_email' 값을 시트 편집자로 추가)")
        print("=" * 60)
        sys.exit(1)


def upload_csv_to_sheet(worksheet, csv_path):
    """CSV 파일 하나를 읽어서 해당 워크시트에 업로드한다.
    기획 문서는 행마다 컬럼 수가 다를 수 있으므로 csv.reader로 직접 읽어 처리한다.
    """
    import csv

    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return

    # 모든 행 중 최대 컬럼 수 기준으로 맞춰 패딩
    max_cols = max(len(row) for row in rows)
    padded = [row + [''] * (max_cols - len(row)) for row in rows]

    worksheet.clear()
    worksheet.update(padded, value_input_option='RAW')


def sync_all_csvs_to_gs():
    check_credentials()

    print("🔑 서비스 계정으로 구글 시트에 접속합니다...\n")

    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    gc = gspread.authorize(creds)

    try:
        spreadsheet = gc.open_by_key(SHEET_ID)
    except gspread.SpreadsheetNotFound:
        print(f"❌ 시트 ID '{SHEET_ID}'를 찾을 수 없습니다.")
        print("   👉 SHEET_ID가 맞는지, 서비스 계정 이메일이 시트 편집자로 공유되어 있는지 확인해라.")
        sys.exit(1)

    print(f"✅ '{spreadsheet.title}' 시트에 연결 완료!\n")
    print("📤 CSV 파일들을 구글 시트로 업로드합니다...\n")

    # 현재 폴더의 모든 CSV 파일 탐색
    csv_files = sorted([
        f for f in os.listdir(DESIGN_DIR)
        if f.endswith('.csv') and f not in EXCLUDE_FILES
    ])

    if not csv_files:
        print("⚠️  업로드할 CSV 파일이 없습니다.")
        return

    success_count = 0
    fail_count = 0

    for csv_file in csv_files:
        sheet_name = csv_file.replace('.csv', '')

        # 언더바로 시작하는 탭은 스킵 (from_gs.py와 동일 규칙)
        if sheet_name.startswith('_'):
            print(f"⏭️  [{sheet_name}] 탭은 무시되었습니다. (언더바 포함)")
            continue

        csv_path = os.path.join(DESIGN_DIR, csv_file)

        try:
            # 해당 탭이 없으면 새로 생성
            try:
                worksheet = spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=500, cols=30)
                print(f"   ➕ [{sheet_name}] 탭이 없어서 새로 생성했습니다.")

            upload_csv_to_sheet(worksheet, csv_path)
            print(f"✅ [{sheet_name}] ➔ 구글 시트 업로드 완료!")
            success_count += 1

        except Exception as e:
            print(f"❌ [{sheet_name}] 업로드 실패: {e}")
            fail_count += 1

    print()
    print(f"🎉 완료! 성공: {success_count}개 / 실패: {fail_count}개")
    if fail_count > 0:
        print("   실패한 항목은 위 오류 메시지를 확인해라.")


if __name__ == "__main__":
    sync_all_csvs_to_gs()


# =============================================================
# 필요한 패키지 설치 명령어
# pip install gspread google-auth pandas openpyxl
# =============================================================
