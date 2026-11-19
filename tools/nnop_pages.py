# -*- coding: utf-8 -*-
"""NNOPの問題用紙PDFを「読むための画像」に変換する。

スキャンされた問題用紙はページが湾曲していて、枠線の自動検出はうまくいかない
（第3回のときに4通り試してすべて失敗した）。そこで **mmの目盛りを重ねた画像**を
出し、目で読んで計算欄の高さを測る。

使い方
------
  # まずページ構成を見る
  python3 tools/nnop_pages.py "NN TEST/算数第4回.pdf" --list

  # 問題ページだけ、目盛り付き・本文だけを切り出す（既定）
  python3 tools/nnop_pages.py "NN TEST/算数第4回.pdf" --pages 1-3

  # 解答一覧だけを目盛りなしで（解説は回帰テストが落ちたときだけ読む）
  python3 tools/nnop_pages.py "NN TEST/算数第4回.pdf" --pages 4 --no-grid --full

  # 1列ずつ大きく見たいとき
  python3 tools/nnop_pages.py "NN TEST/算数第4回.pdf" --pages 1 --cols

出力は既定で /tmp ではなく --out で指定した場所。省略すると
  $CLAUDE_SCRATCH/nnop_pages/  （無ければカレントの nnop_pages/）

読むときの約束
--------------
* 画像は**1回だけ**読む。読んだその場で、設問・配点・答え・計算欄の高さ(mm)を
  テキスト（例: tools/nnop4_notes.md）に落とし、以後は画像を読み返さない。
* 既定の幅は 900px。mmの目盛りを読むにはこれで足りる。
  文字が潰れて読めないときだけ --width 1300 に上げる。
"""
import argparse
import os
import sys

import fitz                                  # PyMuPDF
from PIL import Image, ImageDraw

A3_H_MM = 420.0                              # NNOPの問題用紙はA3（297×420mm）


def _outdir(arg):
    if arg:
        return arg
    sc = os.environ.get('CLAUDE_SCRATCH') or os.environ.get('SCRATCHPAD')
    return os.path.join(sc, 'nnop_pages') if sc else 'nnop_pages'


def parse_pages(spec, n):
    """'1-3,5' → [0,1,2,4]（0始まり）。None なら全ページ。"""
    if not spec:
        return list(range(n))
    out = []
    for part in spec.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            out += list(range(int(a) - 1, int(b)))
        else:
            out.append(int(part) - 1)
    return [i for i in out if 0 <= i < n]


def render(page, width, clip=None):
    rect = clip or page.rect
    z = width / rect.width
    pm = page.get_pixmap(matrix=fitz.Matrix(z, z), clip=clip)
    return Image.frombytes('RGB', (pm.width, pm.height), pm.samples), z


def add_grid(img, mm_top, mm_per_px, step=10):
    """画像に mm の目盛りを重ねる。mm_top はこの画像の上端が用紙の何mmか。"""
    dr = ImageDraw.Draw(img)
    W, H = img.size
    first = int(mm_top // step) * step
    mmv = first
    while True:
        y = int((mmv - mm_top) / mm_per_px)
        if y > H:
            break
        if y >= 0:
            major = (mmv % 50 == 0)
            dr.line([(0, y), (W, y)], fill=(255, 0, 0) if major else (0, 160, 255),
                    width=2 if major else 1)
            if mmv % 20 == 0:
                dr.text((3, y + 2), str(mmv), fill=(255, 0, 0))
        mmv += step
    return img


def main(argv=None):
    ap = argparse.ArgumentParser(description='NNOPの問題用紙PDFを読むための画像にする')
    ap.add_argument('pdf')
    ap.add_argument('--pages', help="例 '1-3' や '1,4'（省略で全ページ）")
    ap.add_argument('--out', help='出力フォルダ')
    ap.add_argument('--width', type=int, default=900, help='画像の幅px（既定900）')
    ap.add_argument('--grid-step', type=int, default=10, help='目盛りの間隔mm（既定10）')
    ap.add_argument('--no-grid', action='store_true', help='目盛りを重ねない')
    ap.add_argument('--full', action='store_true',
                    help='ヘッダ・フッタも含めてページ全体を出す')
    ap.add_argument('--top', type=float, default=45.0,
                    help='本文の上端mm（既定45。--full で無視）')
    ap.add_argument('--bottom', type=float, default=372.0,
                    help='本文の下端mm（既定372。--full で無視）')
    ap.add_argument('--cols', action='store_true',
                    help='左列・右列を別々の画像にも出す')
    ap.add_argument('--page-mm', type=float, default=A3_H_MM,
                    help='用紙の縦mm（既定420＝A3）')
    ap.add_argument('--rotate', type=int, default=0,
                    help='ページを時計回りに回す角度（90/180/270）。'
                         '横向きにスキャンされたページ用。右端に見出しがあるなら270')
    ap.add_argument('--list', action='store_true', help='ページ構成だけ表示して終わる')
    a = ap.parse_args(argv)

    if not os.path.exists(a.pdf):
        sys.exit(f'PDFが見つからない: {a.pdf}')
    doc = fitz.open(a.pdf)

    if a.list:
        print(f'{a.pdf}  {doc.page_count}ページ')
        for i in range(doc.page_count):
            p = doc[i]
            t = len(p.get_text().strip())
            kind = 'テキストあり' if t else 'スキャン画像'
            print(f'  p{i+1:02d}  {p.rect.width:.0f}x{p.rect.height:.0f}  {kind}')
        print('\n※ NNOPは 問題用紙（その1〜3）→ 解答一覧 → 解説 の順に並んでいることが多い。')
        return 0

    out = _outdir(a.out)
    os.makedirs(out, exist_ok=True)
    made = []
    for i in parse_pages(a.pages, doc.page_count):
        p = doc[i]
        if a.rotate:
            p.set_rotation((p.rotation + a.rotate) % 360)
        H = p.rect.height
        if a.full:
            y0, y1 = 0.0, H
            mm_top = 0.0
        else:
            y0 = H * (a.top / a.page_mm)
            y1 = H * (a.bottom / a.page_mm)
            mm_top = a.top
        clip = fitz.Rect(0, y0, p.rect.width, y1)

        img, z = render(p, a.width, clip)
        mm_per_px = a.page_mm / H / z          # 画像1pxが何mmか
        if not a.no_grid:
            add_grid(img, mm_top, mm_per_px, a.grid_step)
        f = os.path.join(out, f'p{i+1:02d}.png')
        img.save(f)
        made.append((f, img.size, mm_per_px))

        if a.cols:
            W = p.rect.width
            for nm, f0, f1 in (('L', 0.04, 0.50), ('R', 0.50, 0.98)):
                c = fitz.Rect(W * f0, y0, W * f1, y1)
                ci, cz = render(p, int(a.width * 0.62), c)
                cmm = a.page_mm / H / cz
                if not a.no_grid:
                    add_grid(ci, mm_top, cmm, a.grid_step)
                cf = os.path.join(out, f'p{i+1:02d}{nm}.png')
                ci.save(cf)
                made.append((cf, ci.size, cmm))

    for f, (w, h), mmpx in made:
        print(f'{f}  {w}x{h}  1mm={1/mmpx:.1f}px')
    print(f'\n画像の上端は用紙の {0.0 if a.full else a.top:.0f}mm。'
          f'赤線が50mmごと、青線が{a.grid_step}mmごと、数字は20mmごと。')
    print('読んだら、設問・配点・答え・計算欄の高さ(mm)をテキストに落として、'
          '画像は読み返さないこと。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
