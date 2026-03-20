"""
LPC Spritesheet 레이어 합성 스크립트 (v2 - 오버사이즈 무기 대응)

캐릭터 바디 파츠 레이어를 애니메이션별로 합성한다.
무기 에셋이 192x192 오버사이즈 프레임인 경우 자동 감지하여
캐릭터(64x64)를 중앙 배치 후 합성한다.

LPC v2 포맷:
    - 캐릭터 파츠: (프레임수 × 64)px wide × (4방향 × 64)px tall
    - 무기 파츠: (프레임수 × 192)px wide × (4방향 × 192)px tall (오버사이즈)
    - 방향 순서: N(↑), W(←), S(↓), E(→)

사용법:
    python lpc_compose.py                          # 기본 (남성 전사)
    python lpc_compose.py --preset warrior_male
    python lpc_compose.py --list-presets
    python lpc_compose.py --custom-weapon path/to/weapon_slash.png --anim slash
"""

import argparse
import sys
from pathlib import Path
from PIL import Image

ASSETS_DIR = Path(__file__).parent.parent / "public" / "img" / "lpc" / "assets"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "img" / "lpc" / "composed"

FRAME_SM = 64   # 캐릭터 프레임 크기
FRAME_LG = 192  # 오버사이즈 무기 프레임 크기
OVERSIZE_OFFSET = (FRAME_LG - FRAME_SM) // 2  # 64px

# 애니메이션 정보 (프레임 수)
ANIM_FRAMES = {
    "idle": 2,
    "walk": 9,
    "run": 9,
    "slash": 6,
    "thrust": 8,
    "spellcast": 7,
    "shoot": 13,
    "hurt": 6,
}

# 합성 z-order (낮을수록 뒤)
LAYER_Z = {
    "body": 10,
    "head": 15,
    "legs": 20,
    "torso": 25,
    "shield": 28,
    "weapon": 30,
}

# 프리셋
PRESETS = {
    "warrior_male": {
        "name": "Male Warrior (검+방패)",
        "base_layers": ["body/male", "head/male", "legs/male"],
        "weapon_layers": {
            "slash":  ["weapon/longsword/slash.png", "shield/round/slash.png"],
            "walk":   ["weapon/longsword/walk.png", "shield/round/walk.png"],
            "thrust": ["shield/round/thrust.png"],
        },
    },
    "warrior_female": {
        "name": "Female Warrior (검+방패)",
        "base_layers": ["body/female", "head/female", "legs/female"],
        "weapon_layers": {
            "slash":  ["weapon/longsword/slash.png", "shield/round/slash.png"],
            "walk":   ["weapon/longsword/walk.png", "shield/round/walk.png"],
            "thrust": ["shield/round/thrust.png"],
        },
    },
    "base_male": {
        "name": "Male Base (무기 없음)",
        "base_layers": ["body/male", "head/male", "legs/male"],
        "weapon_layers": {},
    },
    "base_female": {
        "name": "Female Base (무기 없음)",
        "base_layers": ["body/female", "head/female", "legs/female"],
        "weapon_layers": {},
    },
}


def get_layer_z(path: str) -> int:
    for key, z in LAYER_Z.items():
        if key in path:
            return z
    return 50


def is_oversize(img: Image.Image, expected_frames: int) -> bool:
    """오버사이즈 프레임(192x192) 사용 여부 판별"""
    frame_w = img.size[0] // expected_frames if expected_frames > 0 else img.size[0]
    return frame_w > FRAME_SM


def compose_animation(anim_name: str, base_layers: list, weapon_paths: list,
                       output_path: Path) -> bool:
    """특정 애니메이션에 대해 레이어 합성 (오버사이즈 무기 자동 대응)"""

    num_frames = ANIM_FRAMES.get(anim_name, 6)
    num_dirs = 4

    # 레이어 로드 및 분류
    normal_layers = []  # 64x64 프레임
    oversize_layers = []  # 192x192 프레임

    # 기본 레이어 (body, head, legs)
    for base_folder in sorted(base_layers, key=get_layer_z):
        img_path = ASSETS_DIR / base_folder / f"{anim_name}.png"
        if not img_path.exists():
            continue
        img = Image.open(img_path).convert("RGBA")
        normal_layers.append((get_layer_z(base_folder), img, base_folder))

    # 무기/방패 레이어
    for wp in weapon_paths:
        img_path = ASSETS_DIR / wp
        if not img_path.exists():
            continue
        img = Image.open(img_path).convert("RGBA")
        if is_oversize(img, num_frames):
            oversize_layers.append((get_layer_z(wp), img, wp))
        else:
            normal_layers.append((get_layer_z(wp), img, wp))

    if not normal_layers and not oversize_layers:
        return False

    # z-order 정렬
    normal_layers.sort(key=lambda x: x[0])
    oversize_layers.sort(key=lambda x: x[0])

    has_oversize = len(oversize_layers) > 0

    if not has_oversize:
        # 단순 합성 (모두 64x64)
        max_w = max(img.size[0] for _, img, _ in normal_layers)
        max_h = max(img.size[1] for _, img, _ in normal_layers)
        canvas = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
        for _, img, _ in normal_layers:
            if img.size != canvas.size:
                temp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                temp.paste(img, (0, 0))
                img = temp
            canvas = Image.alpha_composite(canvas, img)
    else:
        # 오버사이즈 합성: 프레임 단위로 처리
        # 먼저 normal 레이어들을 합성
        ref_size = normal_layers[0][1].size if normal_layers else (num_frames * FRAME_SM, num_dirs * FRAME_SM)
        char_sheet = Image.new("RGBA", ref_size, (0, 0, 0, 0))
        for _, img, _ in normal_layers:
            if img.size != char_sheet.size:
                temp = Image.new("RGBA", char_sheet.size, (0, 0, 0, 0))
                temp.paste(img, (0, 0))
                img = temp
            char_sheet = Image.alpha_composite(char_sheet, img)

        # 최종 캔버스 (64x64 기준 출력, 무기 포함)
        canvas = Image.new("RGBA", (num_frames * FRAME_SM, num_dirs * FRAME_SM), (0, 0, 0, 0))

        for d in range(num_dirs):
            for f in range(num_frames):
                # 캐릭터 프레임 추출
                cx, cy = f * FRAME_SM, d * FRAME_SM
                if cx + FRAME_SM <= char_sheet.size[0] and cy + FRAME_SM <= char_sheet.size[1]:
                    char_frame = char_sheet.crop((cx, cy, cx + FRAME_SM, cy + FRAME_SM))
                else:
                    char_frame = Image.new("RGBA", (FRAME_SM, FRAME_SM), (0, 0, 0, 0))

                # 192x192 캔버스에 캐릭터 중앙 배치
                combined = Image.new("RGBA", (FRAME_LG, FRAME_LG), (0, 0, 0, 0))
                combined.paste(char_frame, (OVERSIZE_OFFSET, OVERSIZE_OFFSET))

                # 오버사이즈 무기 레이어 합성
                for _, weap_img, _ in oversize_layers:
                    wx, wy = f * FRAME_LG, d * FRAME_LG
                    if wx + FRAME_LG <= weap_img.size[0] and wy + FRAME_LG <= weap_img.size[1]:
                        weap_frame = weap_img.crop((wx, wy, wx + FRAME_LG, wy + FRAME_LG))
                        combined = Image.alpha_composite(combined, weap_frame)

                # 중앙 64x64 영역 추출하여 최종 캔버스에 배치
                result_frame = combined.crop((
                    OVERSIZE_OFFSET, OVERSIZE_OFFSET,
                    OVERSIZE_OFFSET + FRAME_SM, OVERSIZE_OFFSET + FRAME_SM
                ))
                canvas.paste(result_frame, (cx, cy))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, "PNG")
    return True


def compose_preset(preset_key: str) -> list:
    """프리셋 기반 전체 애니메이션 합성"""
    preset = PRESETS[preset_key]
    print(f"=== {preset['name']} 합성 ===\n")

    output_files = []
    preset_dir = OUTPUT_DIR / preset_key

    for anim_name in ANIM_FRAMES:
        weapon_paths = preset["weapon_layers"].get(anim_name, [])
        output_path = preset_dir / f"{anim_name}.png"

        print(f"  [{anim_name}]", end="")
        if weapon_paths:
            print(f" + {', '.join(Path(w).stem for w in weapon_paths)}", end="")

        if compose_animation(anim_name, preset["base_layers"], weapon_paths, output_path):
            img = Image.open(output_path)
            print(f" -> {img.size[0]}x{img.size[1]}")
            output_files.append(output_path)
        else:
            print(" -> SKIP (에셋 없음)")

    print(f"\n합성 완료: {len(output_files)}개 -> {preset_dir}")
    return output_files


def compose_with_custom_weapon(weapon_path: str, anim: str, gender: str = "male",
                                  output_name: str = "custom"):
    """커스텀 무기 이미지를 기본 캐릭터에 합성"""
    print(f"=== 커스텀 무기 합성 ===")
    print(f"  무기: {weapon_path}")
    print(f"  애니메이션: {anim}")
    print(f"  성별: {gender}\n")

    base_layers = [f"body/{gender}", f"head/{gender}", f"legs/{gender}"]
    weapon_full = Path(weapon_path)

    if not weapon_full.exists():
        print(f"[ERROR] 파일 없음: {weapon_full}")
        sys.exit(1)

    output_path = OUTPUT_DIR / output_name / f"{anim}.png"
    if compose_animation(anim, base_layers, [weapon_path], output_path):
        img = Image.open(output_path)
        print(f"\n저장: {output_path} ({img.size[0]}x{img.size[1]})")
    else:
        print("\n합성 실패")


def list_presets():
    print("=== 사용 가능한 프리셋 ===\n")
    for key, preset in PRESETS.items():
        print(f"  {key}: {preset['name']}")
        print(f"    바디: {', '.join(preset['base_layers'])}")
        if preset['weapon_layers']:
            for anim, weapons in preset['weapon_layers'].items():
                print(f"    {anim}: {', '.join(weapons)}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LPC 스프라이트시트 레이어 합성 (v2)")
    parser.add_argument("--preset", type=str, help="프리셋 이름")
    parser.add_argument("--custom-weapon", type=str, help="커스텀 무기 PNG 경로")
    parser.add_argument("--anim", type=str, default="slash", help="애니메이션")
    parser.add_argument("--gender", type=str, default="male", help="성별")
    parser.add_argument("--output", type=str, default="custom", help="출력 폴더명")
    parser.add_argument("--list-presets", action="store_true", help="프리셋 목록")
    args = parser.parse_args()

    if args.list_presets:
        list_presets()
    elif args.custom_weapon:
        compose_with_custom_weapon(args.custom_weapon, args.anim, args.gender, args.output)
    elif args.preset:
        if args.preset not in PRESETS:
            print(f"알 수 없는 프리셋: {args.preset}")
            list_presets()
            sys.exit(1)
        compose_preset(args.preset)
    else:
        for key in PRESETS:
            compose_preset(key)
            print()
