# テストジェネレーター — CLAUDE.md

小6の息子さんの受験勉強用に、印刷用テストをその場で作る**静的サイト**。
社会・理科・NNOP算数の3つのジェネレーターを配信している。

## 基本ルール
- **常に日本語で応答すること**
- **`public/` の中のHTMLを読もうとしない**（社会15MB・理科10MB・算数1.3MB）。
  中身を変えたいときは `tools/build_*.py` の側を直して作り直す
- `quiz_final.html` は旧システムの遺物（21.9MB）。使っていないし、読まない

## 構成

```
public/            ← これがサイトそのもの（Cloudflareはここを配る）
  index.html         トップ（3つのカード）
  shakai/index.html  社会テスト      全736問
  rika/index.html    理科テスト      全720問
  nnop/index.html    NNOP算数        6回分95問
tools/             ← ビルドスクリプトと問題データ
old_flask/         ← Renderで動かしていたころの一式（今は使っていない）
wrangler.jsonc     ← Cloudflareの配信設定
nnop_spec.md       ← NNOP算数の設計と「新しい回を足す手順」
```

ページはどれも**1枚もののHTML**で、図も画像もスクリプトも全部埋めこんである。
外部ファイルを読まないし、サーバとも通信しない。

| 作り直すとき | コマンド |
|---|---|
| 社会 | `python3 tools/build_shakai.py` |
| 理科 | `python3 tools/build_rika.py` |
| NNOP算数 | `python3 tools/build_nnop.py` |

NNOP算数のビルドは、独立検算と6回分の回帰テストが通らないと出力されない。

## ローカルで見る

```
python3 -m http.server 5050 --directory public
```

`/nnop` `/rika` `/shakai` は末尾スラッシュへリダイレクトされる。Cloudflare上でも同じ。

## 公開（Cloudflare Workers）

wrangler はログイン済み（`chenyizhen1117@gmail.com` のアカウント）。

```
npx wrangler deploy
```

- 公開先: **https://test1117.kk1117.workers.dev**
- 配信しているのは `public/` の4ファイルだけ。サーバ側のコードは無い
- Cloudflareが自動でbrotli圧縮する（算数1.37MB→92KB、社会16.2MB→11.9MB）
- 1ファイル25MiBの上限に対して最大が社会の15.5MBなので、容量の心配は無い

### 以前はRenderだった
2026年11月にCloudflareへ移した。Flaskは `render_template` でビルド済みHTMLを
返していただけなので、外しても中身は何も変わっていない。
漢字（対義語）テストのPDF生成だけはPythonが要るので、`old_flask/` に片づけてある
（詳しくは `old_flask/README.md`）。

## 注意
- 定期実行・監視は不要。cronは設定していない
- `NN TEST/`（原本PDFと答案画像）・`crop_tool.html`・`nnop_pages/` は
  .gitignore 済み。**絶対にコミットしない**
