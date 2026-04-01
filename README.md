# Anki Vocabulary Automation Pipeline

在使用 anki 背單字的時候，我發現紀錄每個單字是最花時間的，那為什麼不用自動化一點的方式來達成。
本專案是想要用 nvim 強大的編輯能力來結合 python 爬蟲功能，從劍橋詞典抓取資料，達到在終端機內編輯與 anki.app 同步預覽的能力。

---

## 流程架構 (Pipeline Overview)

1.  **資料獲取 ([grab.py]("./grab.py"))**：從劍橋詞典爬取定義、例句與片語，並產出結構化 HTML。
2.  **編輯與診斷 ([anki.lua](~/.config/nvim/lua/ckstom/anki.lua))**：在 Neovim 內進行 HTML 標籤閉合檢查與單字提取。
3.  **無縫同步 (`AnkiConnect`)**：透過 API 自動在 Anki 中新增或更新卡片。

---

## 核心組件說明

### 1. 爬蟲引擎 ([grab.py]("./grab.py"))
* **動態內容解析**：自動區分「一般定義（紫色）」與「進階片語（綠色）」。
* **關鍵字高亮**：利用字串替換技術，自動將例句中的目標單字標記為綠色。
* **反爬機制**：模擬真實 Chrome 146 標頭並內建隨機延遲。

### 2. Neovim 同步模組 ([anki.lua](~/.config/nvim/lua/custom/anki.lua))
* **語法診斷引擎**：內建 `check_tags` 函式，利用 Stack 演算法檢查 `<h1>`, `<p>`, `<span>`, `<div>` 是否正確對稱閉合。
* **智慧同步邏輯**：
    * 自動檢查目標 Deck 是否存在，若無則自動創建。
    * **查重機制**：若單字已存在則執行 `updateNoteFields`（更新），若不存在則執行 `addNote`（新增）。
* **非同步通訊**：使用 `vim.fn.jobstart` 呼叫 `curl` 與 AnkiConnect 通訊，確保同步時不會卡住編輯器介面。

---

## 環境配置 (Configuration)

為了確保流程順暢，本專案建議搭配以下設定：

### Neovim 整合
* **<leader>+as** 快捷鍵：同時包含存檔（lsp 檢查語法）和同步功能，提升操作效率。
* **LSP Notify**：同步結果（成功/失敗）會透過 `vim.notify` 顯示在 Neovim 右上角，提供即時回饋。

### Anki 端設定
* **AnkiConnect 外掛**：必須安裝此套件（代碼：2055492159）並保持 Anki 開啟。
* **卡片模板**：建議使用 `Basic` 模板，並確保 `Front` 與 `Back` 欄位支援 HTML 渲染。

---

## 使用操作

1.  執行 `python3 grab.py` 產生 `anki.html`。
2.  在 Neovim 打開該檔案，確認內容。
3.  執行 `:lua require('custom.anki').sync_to_anki()` (或使用自定義快捷鍵)。
4.  看到右上方彈出「已同步更新/新增」通知後，製卡即完成！

---

## 格式規範 (XML Standard)
```xml
<deck>Vocabulary_7</deck>
<note>
  <front>
    <h1>單字</h1>
    <p style="color: gray">[詞性]</p>
  </front>
  <back>
    <h1>定義 (紫色)</h1>
    <ul><li>例句 (Highlighed)</li></ul>
  </back>
</note>
