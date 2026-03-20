"""
LPC Spritesheet 에셋 다운로드 스크립트 (v2 - 애니메이션별 개별 파일 포맷)

Universal LPC Spritesheet Character Generator에서
기본 캐릭터 + 무기 에셋을 다운로드한다.

LPC v2 포맷:
    - 애니메이션별 개별 PNG 파일 (idle.png, walk.png, slash.png 등)
    - 각 파일: (프레임수 × 64)px wide × (4방향 × 64)px tall
    - 방향 순서: N(↑), W(←), S(↓), E(→)

사용법:
    python lpc_download.py                # 기본 에셋 다운로드
    python lpc_download.py --list         # 다운로드할 파일 목록 표시
"""

import argparse
import urllib.request
from pathlib import Path

BASE_URL = "https://raw.githubusercontent.com/liberatedpixelcup/Universal-LPC-Spritesheet-Character-Generator/master"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "img" / "lpc" / "assets"

# 표준 애니메이션 세트
STANDARD_ANIMS = ["idle", "walk", "run", "slash", "thrust", "spellcast", "shoot", "hurt"]

# 캐릭터 바디 파츠 (애니메이션별 개별 파일)
# {로컬_폴더: GitHub_폴더}
BODY_PARTS = {
    "body/male":    "spritesheets/body/bodies/male",
    "body/female":  "spritesheets/body/bodies/female",
    "head/male":    "spritesheets/head/heads/human/male",
    "head/female":  "spritesheets/head/heads/human/female",
    "legs/male":    "spritesheets/legs/pants/male",
    # 여성 바지 에셋이 없어서 남성 바지 공용 사용
    "legs/female":  "spritesheets/legs/pants/male",
}

# 무기/방패 (구조가 다름 - 공격 타입별 하위 폴더)
WEAPON_ASSETS = {
    # {로컬경로: GitHub경로}
    # 검 - slash
    "weapon/longsword/slash.png":  "spritesheets/weapon/sword/longsword/attack_slash/longsword.png",
    "weapon/longsword/walk.png":   "spritesheets/weapon/sword/longsword/walk/longsword.png",
    # 방패 - round
    "shield/round/walk.png":       "spritesheets/shield/round/walk.png",
    "shield/round/slash.png":      "spritesheets/shield/round/slash.png",
    "shield/round/thrust.png":     "spritesheets/shield/round/thrust.png",
}


def download_file(url: str, dest: Path) -> bool:
    """단일 파일 다운로드"""
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        print(f"  [SKIP] {dest.relative_to(OUTPUT_DIR)} (이미 존재)")
        return True

    try:
        encoded_url = url.replace(" ", "%20")
        req = urllib.request.Request(encoded_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
            with open(dest, "wb") as f:
                f.write(data)
        print(f"  [OK] {dest.relative_to(OUTPUT_DIR)} ({len(data):,} bytes)")
        return True
    except Exception as e:
        print(f"  [FAIL] {dest.relative_to(OUTPUT_DIR)}: {e}")
        return False


def download_all():
    """기본 에셋 세트 다운로드"""
    print(f"=== LPC v2 에셋 다운로드 ===")
    print(f"저장 경로: {OUTPUT_DIR}\n")

    success, fail = 0, 0

    # 1) 캐릭터 바디 파츠 (애니메이션별)
    print("--- 캐릭터 바디 파츠 ---")
    for local_folder, github_folder in BODY_PARTS.items():
        for anim in STANDARD_ANIMS:
            url = f"{BASE_URL}/{github_folder}/{anim}.png"
            dest = OUTPUT_DIR / local_folder / f"{anim}.png"
            if download_file(url, dest):
                success += 1
            else:
                fail += 1

    # 2) 무기/방패 (개별 매핑)
    print("\n--- 무기 & 방패 ---")
    for local_path, github_path in WEAPON_ASSETS.items():
        url = f"{BASE_URL}/{github_path}"
        dest = OUTPUT_DIR / local_path
        if download_file(url, dest):
            success += 1
        else:
            fail += 1

    print(f"\n완료: {success} 성공, {fail} 실패")
    return fail == 0


def list_assets():
    """다운로드할 파일 목록 표시"""
    print("=== 다운로드할 에셋 목록 ===\n")

    print("--- 캐릭터 바디 파츠 ---")
    for local_folder, github_folder in BODY_PARTS.items():
        for anim in STANDARD_ANIMS:
            local = f"{local_folder}/{anim}.png"
            remote = f"{github_folder}/{anim}.png"
            print(f"  {local:<40s} <- {remote}")

    print("\n--- 무기 & 방패 ---")
    for local_path, github_path in WEAPON_ASSETS.items():
        print(f"  {local_path:<40s} <- {github_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LPC 스프라이트시트 에셋 다운로드")
    parser.add_argument("--list", action="store_true", help="다운로드할 파일 목록 표시")
    args = parser.parse_args()

    if args.list:
        list_assets()
    else:
        download_all()
