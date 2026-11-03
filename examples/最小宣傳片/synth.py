"""用 numpy 合成配樂與音效，讀同一份時間軸，所以拍點和畫面自然對齊。

    uv run --with numpy python synth.py <輸出.wav>
"""
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import timeline as T  # noqa: E402

SR = 48000
N = int(T.FRAMES / T.FPS * SR)


def at(frame):
    return int(frame / T.FPS * SR)


def kick():
    t = np.arange(int(0.3 * SR)) / SR
    freq = 50 + 90 * np.exp(-t * 30)                    # 往下滑的正弦
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 9)


def hat(rng):
    t = np.arange(int(0.05 * SR)) / SR
    n = np.diff(rng.standard_normal(len(t) + 1))         # 一階差分＝粗略高通
    return n * np.exp(-t * 80) * 0.15


def pop():
    t = np.arange(int(0.12 * SR)) / SR
    freq = 600 + 900 * t / t[-1]                         # 往上滑的「啵」
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 35) * 0.5


def pad(freqs, length):
    t = np.arange(length) / SR
    env = np.minimum(1, t / 0.05) * np.minimum(1, (length - np.arange(length)) / (0.2 * SR))
    tone = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) for f in freqs)
    return tone * env * 0.06


def place(buf, clip, frame):
    i = at(frame)
    j = min(len(buf), i + len(clip))
    buf[i:j] += clip[: j - i]


def main(out):
    rng = np.random.default_rng(0)  # 固定 seed，重跑結果一樣
    mix = np.zeros(N)

    # 和弦進行：每小節一個（C、Am、F、G）
    chords = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
    for i, (_, a, b) in enumerate(T.SEGMENTS):
        place(mix, pad(chords[i % 4], at(b) - at(a)), a)

    # 開場那小節只有和弦，第二小節起進鼓
    for f in range(T.seg("標題")[0], T.FRAMES, T.BEAT):
        place(mix, kick(), f)
        place(mix, hat(rng), f + T.BEAT // 2)

    # 音效：方塊落地、每次跳躍落地、字卡出現
    place(mix, pop(), T.seg("開場")[0] + T.BAR * 2 // 3)
    for h in T.HOPS:
        place(mix, pop() * 0.6, h + T.HOP_LEN)
    for start, *_ in T.CARDS:
        place(mix, pop(), start)

    mix *= 10 ** (-3 / 20) / max(1e-9, np.abs(mix).max())  # 峰值壓到 −3 dBFS
    pcm = (np.repeat(mix[:, None], 2, axis=1) * 32767).astype("<i2")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out} ({N / SR:.1f} s)")


if __name__ == "__main__":
    main(sys.argv[1])
