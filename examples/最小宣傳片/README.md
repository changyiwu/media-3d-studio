# 最小宣傳片（範例）

一支 8 秒、全程用程式產生的 3D 小短片：橘色方塊從天而降、跟著拍子點頭、跳四下轉一圈，配上標題卡和片尾卡。內容故意做得很簡單，用來示範 [程式動畫宣傳片製作指引](../../guides/程式動畫宣傳片製作指引.md) 的骨架：

```text
timeline.py   全片唯一的時間軸（FPS、BPM、段落、攝影機關鍵點、跳躍、眨眼、字卡）
shots.py      Blender：建場景 → 格數函式逐格烘成線性 F-Curve → 透明背景逐格算圖
synth.py      numpy：讀同一份時間軸合成配樂與音效，拍點自然對齊畫面
composite.py  Pillow：漸層背景＋光暈＋3D 逐格＋字卡，接 ffmpeg 合音軌出片
```

本 repo 的正式作品不公開原始碼；這個範例是另外寫的，可以自由拿去改。

## 需要的環境

- Blender 4.4 以上（用到 `Action.fcurve_ensure_for_datablock`；在 5.2 實測過）
- Python 3.10 以上、[uv](https://docs.astral.sh/uv/)（或自己 `pip install numpy pillow`）
- `ffmpeg` 在 PATH 上

## 跑起來

在本資料夾執行。逐格 PNG 建議放本機暫存資料夾，不要放雲端硬碟。以下 `$S` 換成你的暫存路徑（絕對路徑）。

```bash
blender -b --factory-startup -P shots.py -- --out "$S" --scale 0.25 --samples 8 --step 6
```

```bash
uv run --with numpy python synth.py "$S/score.wav"
```

```bash
uv run --with pillow python composite.py --frames "$S/frames" --audio "$S/score.wav" --out "$S/demo.mp4"
```

第一行是低成本預覽（1/4 解析度、8 samples、每 6 格算一張），約 5 秒。正式版改成：

```bash
blender -b --factory-startup -P shots.py -- --out "$S" --scale 1 --samples 64 --step 1 --motion-blur
```

輸出：`$S/scene.blend`（可以打開看烘好的動畫）、`$S/frames/f_####.png`、`$S/score.wav`、`$S/demo.mp4`。

## 看點

| 做法 | 在哪裡 |
|---|---|
| 一份時間軸三邊共用：改 `BPM` 或段落長度，畫面、音樂、字卡一起跟著動 | `timeline.py` |
| 120 BPM × 24 fps → 一拍 12 格，跳躍、點頭、鼓點都落在整拍上 | `timeline.py` 的 `BEAT` |
| 動畫寫成「格數 → 數值」的函式（緩動、拋物線、擠壓伸展），不手調關鍵幀 | `shots.py` 的 `camera_at`、`body_at` |
| 逐格烘成線性 F-Curve，動態模糊才正確 | `shots.py` 的 `bake()` |
| 方塊原點放在底面，壓扁時腳不離地 | `shots.py` 的 `build()` |
| 透明背景＋地板依距離淡出，避免硬地平線；面光設 `visible_camera = False` | `shots.py` 的 `floor_material()` |
| 3D 只算主體，背景、光暈、字卡都在 2D 合成：改字不必重算 3D | `composite.py` |
| 預覽跳格算圖時，合成沿用前一張，片長不變 | `composite.py` 的 `main()` |
| 固定亂數 seed，重跑結果一樣 | `synth.py` |

## 改來改去

- 換節奏：改 `timeline.py` 的 `BPM`（要讓 `FPS * 60 / BPM` 是整數）。
- 換運鏡：改 `CAMERA` 關鍵點表。
- 換字：改 `CARDS`，只要重跑 `composite.py`。中文字卡要把 `composite.py` 的 `FONTS` 換成中文字型（Windows 內附的 Noto Sans TC 是可變字型，直接用會是最細的字重）。
- 換主角：改 `shots.py` 的 `build()`；角色要跨作品重用時，把建模寫成獨立模組再 import。
