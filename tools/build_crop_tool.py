# -*- coding: utf-8 -*-
"""PDFページ画像フォルダから、ブラウザでドラッグ選択して座標を得るクロップツールを生成する。

  python3 tools/build_crop_tool.py <出力html> <フォルダ名:prefix> [<フォルダ名:prefix> ...]

例:
  python3 tools/build_crop_tool.py /tmp/crop_tool.html \
      "/path/to/pdf_pages/1国土・自然・人口:kokudo" \
      "/path/to/pdf_pages/2都道府県・都市:todofuken"

生成したHTMLをブラウザで開き、ページを選んでドラッグで範囲選択→fig名を入力→
「クロップ追加」。複数追加したら出力欄のJSONをコピーし、
apply_crops.py に渡して実際のjpg切り出しを行う。

ページ画像はJPEG・最大幅1800pxに縮小して埋め込む（ファイルサイズを抑えるため）。
出力される座標はこの縮小後の座標なので、apply_crops.py側で元画像の解像度に
スケールし直してからクロップすること（縮小率は各ページごとに記録される）。
"""
import base64, json, os, sys
from io import BytesIO
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SKELETON = os.path.join(HERE, 'crop_tool_skeleton.html')
MAX_W = 1800


def build(out_path, sources):
    """sources: [(folder, prefix), ...]"""
    pages = {}
    page_list = []
    scale_map = {}  # key -> 元画像width / 埋め込み画像width

    for folder, prefix in sources:
        files = sorted(
            f for f in os.listdir(folder)
            if f.lower().endswith('.png') and '_rot' not in f
        )
        for f in files:
            key = f"{prefix}_{os.path.splitext(f)[0]}"
            im = Image.open(os.path.join(folder, f)).convert('RGB')
            w, h = im.size
            if w > MAX_W:
                r = MAX_W / w
                im_small = im.resize((MAX_W, round(h * r)))
                scale_map[key] = w / MAX_W
            else:
                im_small = im
                scale_map[key] = 1.0
            buf = BytesIO()
            im_small.save(buf, format='JPEG', quality=82)
            pages[key] = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
            page_list.append(key + '.jpg')

    skeleton = open(SKELETON, encoding='utf-8').read()
    out = skeleton.replace('/*__PAGES__*/', json.dumps(pages)[1:-1])
    out = out.replace('/*__PAGE_LIST__*/', json.dumps(page_list)[1:-1])
    open(out_path, 'w', encoding='utf-8').write(out)

    scale_path = os.path.splitext(out_path)[0] + '_scale.json'
    json.dump(scale_map, open(scale_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print(f'生成: {out_path} ({os.path.getsize(out_path)//1024} KB, {len(page_list)}ページ)')
    print(f'スケール情報: {scale_path}')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out_path = sys.argv[1]
    sources = []
    for arg in sys.argv[2:]:
        folder, prefix = arg.rsplit(':', 1)
        sources.append((folder, prefix))
    build(out_path, sources)
