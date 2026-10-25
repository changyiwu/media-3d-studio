# media-3d-studio（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。
> Claude Code 預設只在沒有 `CLAUDE.md` 時才讀 `AGENTS.md`，故由 `CLAUDE.md` 的 `@AGENTS.md` import 本檔（`CLAUDE.md` 只有這一行）；Claude 專屬規範寫在本檔〈Claude Code 專屬〉一節。

## 專案簡介

用 AI Agent 操作本機 Blender，製作、修改、渲染與匯出 3D 模型及場景。本專案只放**創作本身**：每件作品的 `.blend`、可重現的 Python 腳本、參考素材、預覽與交付紀錄。Blender 的通用操作流程與安全規則以已安裝的 `blender` 技能為準；在這裡實測出的通用經驗寫回 `agent-setup-guide`，作品專屬內容才留在本專案。

## 關鍵時程

- 2026-09-21：建立 `media-3d-studio`，完成專案初始化與本機 Git 基線。

## 目標與路線圖

- [x] 階段一：完成專案藍圖、資料夾結構與本機 Git 初始化
- [x] 階段二：建立第一件 Blender 作品，驗證建模、預覽、存檔與匯出流程
- [ ] 階段三：把跨作品可重用的 Blender 經驗回寫 `blender` 技能

## 資料夾結構

```text
media-3d-studio/
├── AGENTS.md            本檔（專案藍圖）
├── handoff.md           交接檔（不進 git，只走 GDrive）
├── CLAUDE.md            Claude Code 橋接檔（@AGENTS.md）
├── templates/          共用文件範本（發布資訊範本.md：YouTube／Facebook／Instagram）
├── assets/              共用輸入素材：參考圖、貼圖、HDRI、外部模型
└── output/              所有作品與產出集中於此（整個不進 git，只走 GDrive）
    └── <作品>/          一件作品一個資料夾
        ├── 發布資訊.md   該作品唯一的社群發布文案
        └── <版本>/       每個版本一個子資料夾
            ├── scene.blend  可繼續編輯的 Blender 原始檔
            ├── build_scene.py  可重現主要建模步驟的 bpy 腳本
            ├── <名稱>-<版本>.glb  交付模型（GLB／FBX／OBJ；只有最新版保留）
            ├── previews/    各視角驗收預覽
            ├── checkpoints/ 重要修改前的可回復版本
            ├── render-cache/ 逐格快取（frames/＋source.json）
            └── report.md    交付內容、限制與重跑方式
```

## 專案專屬規則

- Blender 工作一律載入 `blender` 技能；通用操作知識不在本專案複製一份。
- 每件作品使用 `output/<作品>/<版本>/`，每個版本至少保留 `.blend`、可重現的 `bpy` 腳本、預覽與 `report.md`；該版的 GLB、影片與逐格快取也放在同一個版本資料夾，不另開 `exports/`、`renders/` 之類的集中資料夾。
- 每個作品只有一份 `output/<作品>/發布資訊.md`（比照 media-short-film），依 `templates/發布資訊範本.md` 撰寫；文案以選定的發布版本為準，其他版本列在〈版本一覽〉，不在版本資料夾各寫一份，也不另建索引。核對實際製作方式、工具、素材來源與展示限制，文案和交付媒體須對應同一版本。
- 機械錶每個版本的資料夾內，包含影片與子資料夾在內只保留一個主要 `.blend`；將模型與要保留的動畫整合於主檔，不另留錶帶開合、攝影、剪輯或 `.blend1` 副本。影片、腳本與預覽放在對應機械錶版本資料夾內。
- 版本定稿後，checkpoint、`.blend1`、`render-cache/` 逐格快取與驗收抽幀屬中間產物，經使用者同意可丟資源回收筒；沒被 `gallery.html`、`index.html`、`report.md` 或 `發布資訊.md` 引用的驗收圖也算中間產物。仍在開發中的最新版快取，以及上述檔案引用的圖片要保留。
- 舊版本不保留交付用 GLB／FBX／OBJ，只有各作品最新版保留。移除前先確認保留的 `.blend` 能重新匯出每一種姿態，不能時照實寫明；移除後拿掉 `gallery.html`／`index.html` 的對應連結，並在該版 `report.md` 文末註明移除日期與重新匯出方式。
- 每個版本的腳本、log 與檢查用 json 放在它產出的版本資料夾，不集中堆在第一版。跨版本讀取輸入或共用腳本時，以 `Path(__file__).resolve().parent.parent/'<版本資料夾>'/…` 指向來源版本，不用同資料夾路徑。
- 修改既有 `.blend` 時預設另存新檔，不覆蓋使用者原始檔；只有使用者明確要求才可原地覆蓋。
- 重跑既有作品的重建腳本前，先確認輸入與覆寫範圍；保留手動修訂的主檔時，不得直接重建覆蓋。
- 場景修改後重渲染時，先移走與來源雜湊不符的舊格圖快取，避免混入舊畫面。
- 復原已移入 Windows 資源回收筒的舊作品前，先核對原路徑與同名資料夾，避免覆蓋可復原版本。
- 先用低成本預覽驗證構圖、比例與材質，再進行高解析或長時間渲染；預估超過 5 分鐘時先告知使用者。
- 任何來源不明的 `.blend` 都不啟用自動執行 Python；外部資產的授權與來源記在該作品的 `report.md`。
- 作品內容（`.blend`、腳本、報告、GLB、照片、影片與音樂）都在 `output/`，不進 Git，只走雲端硬碟同步；Git 只管專案規則與範本。換電腦前先等同步完成。
- 通用經驗寫回 `agent-setup-guide` 的 `blender` 技能；只適用於單一作品的選型、參數與素材留在本專案。

## 同步層級（本專案初始化至第三層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `AGENTS.md`＋`handoff.md`（不進 git，只走雲端硬碟）＋`CLAUDE.md`（橋接） | 每個 session |
| L2 | GitHub | [changyiwu/media-3d-studio](https://github.com/changyiwu/media-3d-studio)（**私有**） | 指定時 |
| L3 | Obsidian | `media-3d-studio/專案工作流程.md` | 有需要時 |

## 三個檔案的職責（依「時效性」分家，不是依「詳細程度」）

| 檔案 | 時效 | 寫入方式 | 放什麼 |
|------|------|---------|--------|
| `handoff.md` | **只對下一個 session 有效**，過期即丟 | 每次收工**整份重寫** | 做到哪、下一步、**這次**的暫時 workaround |
| `AGENTS.md`（本檔） | **長期有效**，每個 session 都適用 | 只有規則本身變了才改 | 目標、路線圖、常設規則、結構 |
| Obsidian（L3）／`git log` | **歷史**：發生過什麼、為什麼 | 只增不刪 | 決策紀錄、踩坑完整版、逐次進度 |

驗收標準：**`handoff.md` 整份刪掉，不應損失任何長期資訊**——會的話代表該升級進本檔卻沒升級。

**本檔不要出現的東西**（會無限膨脹，且開工每次都要重讀）：

- ❌ `## 最近進度`／逐次工作紀錄 → 有 L3 時寫 Obsidian；沒有就靠 `git log`
- ❌ 決策記錄、取捨理由、踩坑經過的完整版 → 留在 Obsidian 或作品的 `report.md`
- ✅ 只留「結論式的規則」：踩過的坑收斂成一條**祈使句**寫進〈工作約定〉或〈專案專屬規則〉

## 工作約定

- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- `handoff.md` **不進 git**（含真實電腦名與本機絕對路徑），已列入 `.gitignore`，跨電腦靠雲端硬碟同步——不要把它加回版控
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- 所有回應與文件使用繁體中文
- 修改前先確認計畫，優先保留原有資料結構
- repo 位於 GDrive；換電腦接手前先等雲端同步完成，再讀 `handoff.md` 與檢查 Git 狀態
- **作品與產出一律放 `output/<作品>/<版本>/`**：`.blend`、腳本、預覽、`report.md`、GLB、影片與逐格快取都放在對應版本資料夾；不另開 `blender/`、`renders/`、`exports/`、`outputs/` 之類的根目錄資料夾，`output/` 不進 git。
