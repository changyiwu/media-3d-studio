"""2D 合成：漸層背景＋3D 逐格（透明背景）＋字卡＋暗角，接 ffmpeg 合音軌出片。

    uv run --with pillow python composite.py --frames <shots 輸出>/frames --audio <配樂.wav> --out <成片.mp4>

預覽時 shots.py 跳格算圖，缺的格沿用前一張已算好的圖，片長不變。
字卡在這裡畫，改字不必重算 3D。
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import timeline as T  # noqa: E402

FONTS = [  # 依序嘗試；都沒有就用 Pillow 內建字型
    "C:/Windows/Fonts/segoeuib.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def font(size):
    for p in FONTS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


def background(w, h):
    """上深下淺的直向漸層，配一圈暗角。"""
    top, bottom = (14, 12, 30), (52, 30, 70)
    grad = Image.linear_gradient("L").resize((w, h))
    bg = Image.composite(Image.new("RGB", (w, h), bottom), Image.new("RGB", (w, h), top), grad)
    vignette = Image.radial_gradient("L").resize((w, h)).point(lambda v: int(v * 0.6))
    return Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), bg, vignette)


def card_alpha(f, start, end, fade=6):
    return max(0.0, min(1.0, (f - start) / fade, (end - f) / fade))


def draw_cards(img, f):
    w, h = img.size
    for start, end, title, sub in T.CARDS:
        a = card_alpha(f, start, end)
        if a <= 0:
            continue
        layer = Image.new("RGBA", img.size)
        d = ImageDraw.Draw(layer)
        rise = int((1 - a) * h * 0.02)                  # 淡入時往上浮一點
        d.text((w / 2, h * 0.16 + rise), title, font=font(int(h * 0.09)),
               fill=(255, 255, 255, int(255 * a)), anchor="mm")
        d.text((w / 2, h * 0.25 + rise), sub, font=font(int(h * 0.035)),
               fill=(255, 190, 120, int(255 * a)), anchor="mm")
        img.alpha_composite(layer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--crf", type=int, default=21)
    a = ap.parse_args()

    rendered = {int(p.stem.split("_")[-1]): p for p in Path(a.frames).glob("f_*.png")}
    if not rendered:
        sys.exit(f"找不到逐格 PNG：{a.frames}")
    w, h = Image.open(next(iter(rendered.values()))).size
    w, h = w // 2 * 2, h // 2 * 2                       # H.264 需要偶數尺寸
    bg = background(w, h).convert("RGBA")
    glow = Image.new("RGBA", (w, h))

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(T.FPS), "-i", "-",
        "-i", a.audio,
        "-c:v", "libx264", "-crf", str(a.crf), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-map_metadata", "-1",
        a.out,
    ], stdin=subprocess.PIPE)

    last = None
    for f in range(T.FRAMES):
        if f in rendered:
            last = Image.open(rendered[f]).convert("RGBA").crop((0, 0, w, h))
            # 主體後面加一層柔光：用 alpha 模糊放大當光暈
            glow = Image.new("RGBA", (w, h), (255, 140, 60, 0))
            glow.putalpha(last.getchannel("A").filter(ImageFilter.GaussianBlur(h * 0.05)).point(lambda v: v // 3))
        frame = bg.copy()
        frame.alpha_composite(glow)
        frame.alpha_composite(last)
        draw_cards(frame, f)
        ff.stdin.write(frame.convert("RGB").tobytes())

    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg 失敗")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
