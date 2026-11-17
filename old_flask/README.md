# Render（Flask）で動かしていたころの一式

2026年11月にCloudflareの静的配信へ移したときに、ここへ片づけた。
**今のサイトはこのフォルダをまったく使っていない。**

| ファイル | 何だったか |
|---|---|
| `app.py` | Flask本体。`/` `/shakai` `/rika` `/nnop` でHTMLを返し、`/generate` で漢字テストPDFを返していた |
| `render.yaml` | Renderの無料プランの設定（gunicorn） |
| `requirements.txt` | flask / reportlab / gunicorn |
| `kanji_quiz_gen.py` | 漢字（対義語）テストPDFの組版。reportlabのCIDフォント（HeiseiKakuGo-W5・HeiseiMin-W3）を使う |
| `kanji_quiz_data.py` | 対義語224組のデータ |

社会・理科・算数の3ページは、もともとビルド済みの1枚もののHTMLを
`render_template` で返していただけなので、Flaskを外しても中身は何も変わっていない。

## 漢字テストをまた使いたくなったら

PDF生成だけはサーバ（Python）が要るので、選択肢は3つ。

1. このフォルダを戻してRenderに置き直す（`public/index.html` にカードを足す）
2. ブラウザ側でPDFを作るように書き直す（日本語フォントの埋めこみが必要）
3. Cloudflare Containers など、Pythonが動く場所に `/generate` だけ置く

データ（`kanji_quiz_data.py` の224組）はここに残してあるので、作り直しにはならない。
