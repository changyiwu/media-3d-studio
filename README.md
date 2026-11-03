# media-3d-studio

用 AI Agent 操作本機 Blender，製作、修改、渲染與匯出 3D 模型及場景的作品庫。

本 repo（公開）只管**專案規則與範本**；作品本身（`.blend`、腳本、預覽、GLB、影片）都在 `output/`，不進 git，只走雲端硬碟同步。

## 開始之前

- 先讀 [AGENTS.md](AGENTS.md)（專案藍圖：資料夾結構、版本規則、渲染與安全規則），再讀 `handoff.md`（上次做到哪，不進 git）。
- Blender 的通用操作流程以已安裝的 `blender` 技能為準，本專案不另存一份；實測出的通用經驗寫回 `agent-setup-guide`。
- 做全程式產生的 3D 宣傳／廣告片時，先讀 [guides/程式動畫宣傳片製作指引.md](guides/程式動畫宣傳片製作指引.md)。
- 想直接跑跑看：[examples/最小宣傳片/](examples/最小宣傳片/) 是一支 8 秒的公開範例，四支腳本示範指引的完整骨架（時間軸、逐格烘焙、配樂、合成出片）。

## 目錄

```text
media-3d-studio/
├── AGENTS.md      專案藍圖（規則都在這裡）
├── CLAUDE.md      Claude Code 橋接檔（@AGENTS.md）
├── guides/        製作方法指引
├── examples/      可直接執行的公開範例腳本
├── templates/     發布資訊範本.md（正本在 media-youtube-publish，改正本再覆蓋）
├── assets/        共用輸入素材與跨作品角色：參考圖、貼圖、HDRI、外部模型、吉祥物（不進 git，只走雲端硬碟）
└── output/        作品，一件一個資料夾（不進 git）
    └── <作品>/    根目錄放最新版交付物與 scene.blend；中間產物在 work/，舊版在 舊版/vNN/
```

## 需要的環境

- 本機 Blender（以 `bpy` 腳本建模、算圖與匯出）
- 一個能載入 `blender` 技能的 AI Agent（Claude Code、Codex、OpenCode、Antigravity）
