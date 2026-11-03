"""全片唯一的時間軸：Blender（shots.py）、配樂（synth.py）、合成（composite.py）都 import 這一份。

改節奏、段落長度或字卡只改這裡，三邊一起跟著動。
"""

FPS = 24
BPM = 120
BEAT = FPS * 60 // BPM          # 一拍 12 格
BAR = BEAT * 4                  # 一小節 48 格

WIDTH, HEIGHT = 1920, 1080

# 段落（起格含、迄格不含）：每段一小節，全片 4 小節＝192 格＝8 秒
SEGMENTS = [
    ("開場", 0 * BAR, 1 * BAR),   # 方塊從天而降，彈兩下站好
    ("標題", 1 * BAR, 2 * BAR),   # 跟著拍子點頭，標題卡出現
    ("跳躍", 2 * BAR, 3 * BAR),   # 每拍跳一下，最後一跳轉一圈
    ("片尾", 3 * BAR, 4 * BAR),   # 鏡頭拉遠，片尾卡
]
FRAMES = SEGMENTS[-1][2]


def seg(name):
    """回傳段落的 (起格, 迄格)。"""
    for n, a, b in SEGMENTS:
        if n == name:
            return a, b
    raise KeyError(name)


# 攝影機關鍵點：(格數, 位置, 看向, 焦距 mm)，相鄰兩點之間緩動內插
CAMERA = [
    (0,          (0.0, -14.0, 6.0), (0.0, 0.0, 2.0), 50),
    (1 * BAR,    (0.0, -9.0, 2.5),  (0.0, 0.0, 0.9), 50),
    (2 * BAR,    (6.0, -8.0, 2.0),  (0.0, 0.0, 1.0), 40),
    (3 * BAR,    (-5.0, -8.0, 3.0), (0.0, 0.0, 1.2), 40),
    (FRAMES - 1, (0.0, -16.0, 5.0), (0.0, 0.0, 1.5), 50),
]

# 跳躍段每拍起跳一次；落地格同時是配樂的音效點
HOPS = [seg("跳躍")[0] + i * BEAT for i in range(4)]
HOP_LEN = BEAT                  # 一跳 12 格
HOP_HEIGHT = 1.4

# 眨眼（離散事件）：起格，持續 3 格
BLINKS = [30, 70, 130, 170]

# 字卡（2D 合成層，不在 Blender 裡排字）：(起格, 迄格, 大標, 副標)
CARDS = [
    (seg("標題")[0] + BEAT // 2, seg("跳躍")[0] + BEAT, "HELLO, CUBE", "a minimal code-only promo"),
    (seg("片尾")[0] + BEAT,      FRAMES,                 "MADE WITH CODE", "0 hand-set keyframes"),
]
