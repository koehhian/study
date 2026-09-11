# Sam Koeh Study — Codex 接管說明

> 本檔案是給 Codex 的專案接管文件。請先完整閱讀，再修改、部署或重構本 repository。

## 1. 專案目標

建立並長期維護一個以 GitHub Pages 發布的個人研究出版網站：

- 正式入口：`https://study.samkoeh.com/`
- GitHub repository：`koehhian/study`
- 預設 branch：`main`
- Pages 發布來源：`main` branch 的 repository root `/`
- 技術原則：純 HTML / CSS / JavaScript，可直接由 GitHub Pages 靜態託管，不依賴伺服器端 runtime。

這個網站不是要求每篇研究都長得一樣，而是採「統一出版品牌 + 各專題保留自己的視覺語言」。全站最低視覺與出版規則見 `STYLE_CONTRACT.md`。

## 2. DNS / 網域狀態

使用者擁有 `samkoeh.com`，DNS 目前由 Squarespace Domains 管理。

已完成 DNS 設定：

```text
Type: CNAME
Name: study
Data: koehhian.github.io
TTL: 4 hrs
```

也就是：

```text
study.samkoeh.com -> koehhian.github.io
```

不要修改既有的其他子網域，例如 `blog.samkoeh.com`、`code.samkoeh.com`。

Payload 已包含根目錄 `CNAME` 檔案，內容應保持：

```text
study.samkoeh.com
```

## 3. 使用者會放進 repository path 的檔案

同一目錄會有：

```text
CODEX_HANDOFF.md
samkoeh-study-codex-payload.zip
```

請把 ZIP **解壓到 repository root**，不要形成額外的 `study-site/` 或其他巢狀外層目錄。

解壓後預期至少為：

```text
/
├── .nojekyll
├── CNAME
├── README.md
├── STYLE_CONTRACT.md
├── index.html
├── assets/
│   └── site.css
└── reformation/
    └── index.html
```

## 4. 第一版網站內容

### 首頁 `/`

`index.html` 是 Sam Koeh Study 的統一入口，目前列出第一個研究專題。

首頁定位：

- 乾淨、克制、偏研究出版風格
- 固定品牌：`SAM KOEH STUDY`
- 專題卡片作為研究庫入口
- 不追求每一篇專題共用完全相同的內頁模板

### 第一篇 `/reformation/`

`reformation/index.html` 是第一篇正式互動研究：

**《羅馬教會的偏離如何累積：改教家批判的歷史時間線》**

原始頁面已有：

- 68 個歷史節點
- 多主題篩選
- 文字搜尋
- 錨點導覽
- JSON 匯出
- 列印 / 另存 PDF
- 內嵌及外部歷史圖像
- 完整文獻目錄
- 手機版與 print CSS

目前已在該頁加入輕量的 `SAM KOEH · STUDY ← 首頁` 返回入口。除非有明確 bug，請不要為了統一風格而重做這篇專題的主要視覺設計。

## 5. 接管後立即執行的工作

請依序完成：

1. 確認目前工作目錄確實是 `koehhian/study` 的 local checkout，且 remote 指向正確 repository。
2. 先檢查現有 repository 內容與 `git status`，不要盲目覆蓋未知的使用者修改。
3. 解壓 `samkoeh-study-codex-payload.zip` 到 repository root。
4. 驗證目錄結構沒有多包一層資料夾。
5. 驗證 `CNAME` 內容為 `study.samkoeh.com`。
6. 驗證 `.nojekyll` 存在。
7. 檢查 `index.html` 與 `reformation/index.html` 的相對路徑、返回首頁連結、CSS 載入及手機版。
8. 不得破壞 reformation 頁既有的搜尋、篩選、JSON 匯出、列印、錨點與圖像功能。
9. 本地可用簡單 static server 做 smoke test，例如 Python HTTP server；不要因此增加 Python runtime 依賴到網站本身。
10. 若可使用 GitHub CLI 且有足夠 repo admin 權限，檢查 GitHub Pages 是否設定為 `main` + `/ (root)`，Custom Domain 是否為 `study.samkoeh.com`。若權限不足，不要猜測成功，清楚告知使用者剩下哪個 GitHub UI 步驟要做。
11. 完成後 commit 並 push 到 `main`。建議第一個 commit message：

```text
Launch Sam Koeh Study
```

12. 部署後驗證：

```text
https://study.samkoeh.com/
https://study.samkoeh.com/reformation/
```

DNS 若尚未完全傳播，可同時用 GitHub Pages 預設網址做暫時性檢查，但要注意自訂網域與 project path 的 base path 差異，不可為了暫時測試而破壞正式網域下的路徑。

## 6. GitHub Pages 設定目標

最終設定應為：

```text
Settings -> Pages
Source: Deploy from a branch
Branch: main
Folder: / (root)
Custom domain: study.samkoeh.com
Enforce HTTPS: On（DNS/憑證允許後）
```

如果 GitHub 自動生成或更新根目錄 `CNAME`，其內容仍應為：

```text
study.samkoeh.com
```

## 7. 長期維護規則

每次加入新 AI 生成 HTML 專題：

1. 先讀 `STYLE_CONTRACT.md`。
2. 每個獨立專題放在自己的 slug 目錄，例如：

```text
/reformation/
/rsa/
/riemann/
/taiwan-history/
```

3. 每個專題的正式入口優先採：

```text
/<slug>/index.html
```

4. 每個專題必須能返回 `https://study.samkoeh.com/`。
5. 專題自己的 CSS / JS 儘量限制作用域，避免污染全站。
6. 若專題是單檔 self-contained HTML，原則上可保持單檔，不必強拆 assets。
7. 新增專題後，同步更新首頁研究卡片 / 索引。
8. 不得為了視覺統一而刪除研究頁的來源、證據界線、圖表、互動或可讀性功能。
9. 若未來專題數量顯著增加，再考慮以 JSON manifest 或小型 build step 自動生成首頁；第一版不要過度工程化。

## 8. 美術與品牌原則

核心概念：**像同一間博物館裡的不同展覽。**

固定的是：

- Sam Koeh Study 品牌辨識
- 返回首頁
- 基本可讀性
- 手機相容
- 引用 / 來源不被弱化
- URL 與資訊架構

可變的是：

- 專題色彩
- 排版語言
- 圖表風格
- 互動方式
- 歷史感 / 科技感 / 數學視覺化等題材風格

禁止把全站做成僵硬的單一模板，也禁止每篇完全看不出屬於同一網站。

## 9. 變更原則

- 對不確定的既有內容，先檢查再改。
- 不要擅自刪除研究資料或大幅重寫研究內容。
- 內容事實修訂與網站工程修訂分開處理。
- 每次大改前先看 git diff；大改後做 smoke test。
- 若發現原始研究頁有 bug，可修，但要在完成報告裡列明修了什麼。
- 不要把任何 secret、token、credential 寫入 repository。

## 10. 完成後回報格式

完成第一輪接管後，請簡潔回報：

```text
1. 已做的檔案 / 結構變更
2. GitHub Pages / Custom Domain 狀態
3. 已驗證的 URL
4. 仍需使用者手動完成的項目（若有）
5. git commit SHA
6. 發現但尚未處理的問題
```
