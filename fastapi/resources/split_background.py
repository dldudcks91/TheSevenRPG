"""
배경 스프라이트시트 분할 스크립트

사용법:
  python split_background.py background_total.png --cols 3 --rows 7
  python split_background.py background_total.png --cols 7 --rows 3

입력: 여러 배경이 격자로 합쳐진 스프라이트시트
출력: bg_ch{챕터}_s{스테이지}.png 형태로 개별 파일 저장
"""

import argparse
from pathlib import Path
from PIL import Image


# 챕터별 스테이지 이름 (참고용)
STAGE_NAMES = {
    1: ["파멸의 진영", "핏빛 교전지대", "원한의 묘지"],
    2: ["변형의 경계", "독무의 심림", "부패한 뿌리"],
    3: ["모래에 묻힌 폐허", "저주받은 지하묘지", "황금 보물고"],
    4: ["얼어붙은 평원", "빙하 요새", "영구동결의 심부"],
    5: ["탐식의 입구", "맥동하는 미로", "소화의 심연"],
    6: ["부패한 정원", "유혹의 회랑", "욕망의 왕좌"],
    7: ["천상의 계단", "무너진 신전", "오만의 왕좌"],
}


def split_spritesheet(image_path: str, cols: int, rows: int, output_dir: str = None):
    """스프라이트시트를 격자로 분할하여 개별 파일로 저장"""
    img = Image.open(image_path)
    w, h = img.size
    cell_w = w // cols
    cell_h = h // rows

    if output_dir is None:
        output_dir = Path(image_path).parent
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"전체 이미지: {w}x{h}")
    print(f"격자: {cols}열 x {rows}행")
    print(f"개별 크기: {cell_w}x{cell_h}")
    print(f"출력 경로: {output_dir}")
    print("---")

    idx = 0
    for row in range(rows):
        for col in range(cols):
            idx += 1
            chapter = (idx - 1) // 3 + 1
            stage = (idx - 1) % 3 + 1

            if chapter > 7:
                break

            left = col * cell_w
            top = row * cell_h
            right = left + cell_w
            bottom = top + cell_h

            cropped = img.crop((left, top, right, bottom))
            filename = f"bg_ch{chapter}_s{stage}.png"
            cropped.save(output_dir / filename)

            stage_name = STAGE_NAMES.get(chapter, ["", "", ""])[stage - 1]
            print(f"  {filename} ({stage_name})")

    print(f"\n총 {min(idx, 21)}개 파일 저장 완료")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="배경 스프라이트시트 분할")
    parser.add_argument("image", help="스프라이트시트 이미지 경로")
    parser.add_argument("--cols", type=int, default=3, help="열 수 (기본: 3)")
    parser.add_argument("--rows", type=int, default=7, help="행 수 (기본: 7)")
    parser.add_argument("--output", type=str, default=None, help="출력 디렉토리 (기본: 이미지와 같은 폴더)")
    args = parser.parse_args()

    split_spritesheet(args.image, args.cols, args.rows, args.output)
