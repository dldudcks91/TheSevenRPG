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

# 이 스크립트가 위치한 폴더 = meta_data 폴더
SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
# ---------------------------------------------------------


def sync_from_gs():
    """구글 시트 전체를 meta_data 폴더로 다운로드해서 덮어쓴다."""
    os.makedirs(SAVE_DIR, exist_ok=True)

    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
    print(f"구글 시트에서 데이터를 다운로드합니다...\n  URL: {url}\n")

    try:
        all_sheets = pd.read_excel(url, sheet_name=None, engine='openpyxl')
    except Exception as e:
        print(f"다운로드 실패: {e}")
        print("  구글 시트 공유 설정이 '링크가 있는 모든 사용자 - 뷰어'로 되어있는지 확인해라.")
        sys.exit(1)

    success_count = 0
    skip_count = 0

    for sheet_name, df in all_sheets.items():
        # 언더바로 시작하는 탭은 무시 (작업중/메모 등)
        if sheet_name.startswith('_'):
            print(f"  skip [{sheet_name}] (언더바 탭)")
            skip_count += 1
            continue

        # 완전히 빈 행 제거
        df = df.dropna(how='all')

        save_path = os.path.join(SAVE_DIR, f"{sheet_name}.csv")
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        print(f"  [{sheet_name}] -> {save_path}")
        success_count += 1

    print(f"\n완료: {success_count}개 저장 / {skip_count}개 스킵")


if __name__ == "__main__":
    sync_from_gs()


# =============================================================
# 필요한 패키지 설치 명령어
# pip install pandas openpyxl
# =============================================================
