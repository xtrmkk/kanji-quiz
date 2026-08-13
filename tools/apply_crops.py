# -*- coding: utf-8 -*-
"""crop_tool.html の出力欄（JSON複数行、カンマ区切り）を受け取り、
元解像度のPDFページPNGから実際にjpgを切り出して tools/figs/ に保存する。

  python3 tools/apply_crops.py <出力先figsフォルダ> <scale.jsonのパス> <元PNGフォルダ:prefix> [...] <<'EOF'
  {"fig":"q22_topo","page":"kokudo_p003","x":168,"y":1392,"w":822,"h":364},
  {"fig":"q6_symbols","page":"kokudo_p002","x":...}
  EOF

標準入力からJSON行（末尾カンマ・改行区切り）を読み込む。
"""
import json, os, sys
from PIL import Image


def load_crops(text):
    text = text.strip()
    if not text:
        return []
    # 末尾カンマや改行区切りのJSONオブジェクト列を配列として読めるようにする
    wrapped = '[' + text.rstrip(',') + ']'
    return json.loads(wrapped)


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    figs_dir = sys.argv[1]
    scale_path = sys.argv[2]
    sources = {}
    for arg in sys.argv[3:]:
        folder, prefix = arg.rsplit(':', 1)
        sources[prefix] = folder

    scale_map = json.load(open(scale_path, encoding='utf-8'))
    crops = load_crops(sys.stdin.read())
    os.makedirs(figs_dir, exist_ok=True)

    for c in crops:
        page_key = c['page']
        prefix = page_key.rsplit('_p', 1)[0]
        folder = sources.get(prefix)
        if folder is None:
            print(f'警告: prefix "{prefix}" に対応するフォルダが指定されていません -> スキップ ({page_key})')
            continue
        png_name = page_key[len(prefix) + 1:] + '.png'
        png_path = os.path.join(folder, png_name)
        im = Image.open(png_path).convert('RGB')
        scale = scale_map.get(page_key, 1.0)
        box = (
            round(c['x'] * scale),
            round(c['y'] * scale),
            round((c['x'] + c['w']) * scale),
            round((c['y'] + c['h']) * scale),
        )
        out_path = os.path.join(figs_dir, c['fig'] + '.jpg')
        im.crop(box).save(out_path, quality=90)
        print(f"{c['fig']}: {page_key} {box} -> {out_path}")


if __name__ == '__main__':
    main()
