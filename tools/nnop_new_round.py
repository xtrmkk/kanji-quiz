# -*- coding: utf-8 -*-
"""NNOPに「新しい回」を足すための雛形を作り、ビルドに配線する。

3ファイル（rates / data / verify）を作って tools/build_nnop.py に差し込むまでを
自動でやる。中身（設問マスタ・生成器・検算）は人／Claudeが書く。

使い方
------
  python3 tools/nnop_new_round.py --n 5 --round 4 --label 第4回 \
          --prefix op4 --keys M1,M2,M3,M4,M5,M6

  --n       ファイル名の番号。tools/nnop5_data.py などになる
  --round   回のキー。数字でも文字列でもよい（夏期そっくりは 'N' を使った）
  --label   画面に出る名前（例: 第4回）
  --prefix  小問idの接頭辞（例: op4 → op4-1-1）
  --keys    大問のキー（例: M1,M2,...）。1つの大問が段に収まらないときは
            第1回のG6/G6aと同じ要領で M6,M6a のように分ける

作ったあとの流れは nnop_spec.md の「新しい回を足す手順」を見ること。
GROUPS は空で作るので、**この時点で python3 tools/build_nnop.py は通る**
（何も増えないだけ）。設問を書き足すたびに走らせて、検算と回帰テストを通す。
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


# ══════════════════════════════════════════════════════════════════
# 雛形
# ══════════════════════════════════════════════════════════════════
RATES = '''# -*- coding: utf-8 -*-
"""{label}・算数の設問一覧（早稲田アカデミーLMSの実測値）。

  (大問, 小問, 設問内容, 全体正答率, 配点, 息子さんの正誤)
  正誤: ○=正解 △=部分点 ×=不正解

LMSの「小問別成績」のスクリーンショットから、上から順に書き写す。
配点の合計が60点になるか、このファイルを直接走らせて確かめること。
"""
{var} = [
    # (1, '(1)', '…', 00, 0, '○'),
]


if __name__ == '__main__':
    import collections
    subs = {var}
    print(f'設問 {{len(subs)}} 問 ／ 配点合計 {{sum(s[4] for s in subs)}} 点')
    g = collections.OrderedDict()
    for q, sub, nm, rate, score, mark in subs:
        g.setdefault(q, []).append((sub, rate))
    for q, ss in g.items():
        print(f'  大問{{q}}: ' + '／'.join(f'{{s[0] or "—"}} {{s[1]}}%' for s in ss))
    print('正誤:', dict(collections.Counter(s[5] for s in subs)))
'''


DATA = '''# -*- coding: utf-8 -*-
"""{label}・算数の設問マスタと、採用可能なパラメータの全列挙。

第1〜3回・夏期そっくりと同じ方針（nnop_spec.md）。
**計算はすべてここ（ビルド時のPython）で終わらせる。**
ブラウザ側は、ここが出したパラメータと解答を文字として差し込むだけ。

  python3 tools/nnop{n}_data.py   … 各大問が何通り作れるか表示する
"""
import itertools
from fractions import Fraction as F
from math import gcd

from nnop_data import frac_html, improper_html, num, ratio_of   # 表示の小道具は共用


# ══════════════════════════════════════════════════════════════════
# 大問ごとの「採用できるパラメータの全列挙」
#   返すのは次の形のリスト。元の数値の組を**必ず先頭**に置くこと
#   （build_nnop.py の回帰テストが元の数値で公式解答と照合するため）。
#
#   {{'p': {{ 問題文に差し込む値 }},
#    'a': [ 解答（答欄の数だけ・HTML可） ],
#    '_chk': 検算用に取っておく途中結果 }}
# ══════════════════════════════════════════════════════════════════
{gens}

{varia}

# 計算欄の高さ（mm）。元の問題用紙を A3＝420mm として実測した値を入れる。
#   tools/nnop_pages.py で目盛り付き画像を出し、枠の上端と下端を読む。
#   0 を入れると「計算欄なし（答だけ）」になる。
{work} = {{
}}


# ══════════════════════════════════════════════════════════════════
# 設問マスタ
#   'vary' は数値を振るかどうか（図や構造が壊れる大問は False にして原寸で出す）
#   'ans' は答欄の前に出す小さなラベル。単位は答えの値のほうに入れる
#   'fig' はパラメータを混ぜられる（例 'tri345:{{pq}}'）
# ══════════════════════════════════════════════════════════════════
{groups} = [
    # {{
    #     'key': '{first_key}', 'round': {round!r}, 'field': 'speed',
    #     'title': '…', 'vary': True,
    #     'intro': '…{{a}}…', 'body': '', 'fig': None, 'figpos': 'right',
    #     'subs': [
    #         {{'id': '{prefix}-1-1', 'label': '(1)',
    #          'q': '…{{a}}…', 'rate': 00, 'score': 0, 'ans': [''],
    #          'how': '…（ヒント。文字式・方程式は使わない）'}},
    #     ],
    # }},
]


if __name__ == '__main__':
    for k, fn in {varia_name}.items():
        vs = fn()
        ex = vs[0]['a'] if vs else '（まだ空）'
        print(f'{{k}}: {{len(vs):4}}通り　例 {{ex}}')
'''


VERIFY = '''# -*- coding: utf-8 -*-
"""{label}の独立検算と、元の数値での回帰テスト。

生成器が使った式をそのまま使い回すと、式がまちがっていても一致してしまう。
ここでは**別の原理**で解き直して突き合わせる（nnop_spec.md 7.1 / 13章）。

  速さ   … 1秒（1分）ずつ動かして出来事を直接ひろう
  濃度   … 食塩の重さの保存で確かめる
  規則性 … 直接足し上げる／全数探索する
  平面図形 … 座標をとって靴ひも公式、曲線は数値積分（真のπ）
  場合の数 … 並びを全列挙して数える
"""
import itertools
import math
from fractions import Fraction as F

import nnop{n}_data as DX
from nnop_data import num, frac_html, improper_html


{verifs}

{vdict}

# ══════════════════════════════════════════════════════════════════
# 回帰テスト（元の{label}の数値 → 公式解答）
#   値が None の要素は照合しない。params は 'p' の一部だけでよい。
# ══════════════════════════════════════════════════════════════════
{official} = {{
    # '{first_key}': (['…'], {{'a': 0}}),
}}
'''


def main(argv=None):
    ap = argparse.ArgumentParser(description='NNOPに新しい回の雛形を作る')
    ap.add_argument('--n', required=True, help='ファイル名の番号（例 5）')
    ap.add_argument('--round', required=True, help="回のキー（例 4 や 'N2'）")
    ap.add_argument('--label', required=True, help='画面に出る名前（例 第4回）')
    ap.add_argument('--prefix', required=True, help='小問idの接頭辞（例 op4）')
    ap.add_argument('--keys', required=True, help='大問のキー（例 M1,M2,M3）')
    ap.add_argument('--force', action='store_true', help='既にあっても上書きする')
    a = ap.parse_args(argv)

    n = a.n
    keys = [k.strip() for k in a.keys.split(',') if k.strip()]
    if not keys:
        sys.exit('--keys が空')
    rnd = int(a.round) if re.fullmatch(r'-?\d+', a.round) else a.round

    varia_name = f'VARIANTS{n}'
    names = dict(
        n=n, label=a.label, prefix=a.prefix, round=rnd,
        var=f'{a.prefix.upper()}_SUBS',
        groups=f'GROUPS{n}', work=f'WORK_MM{n}',
        varia_name=varia_name, official=f'OFFICIAL{n}',
        first_key=keys[0],
    )

    gens = '\n\n'.join(
        f'def {k.lower()}_variants(limit=120):\n'
        f'    """{k}：…"""\n'
        f'    out = []\n'
        f'    # for ... :\n'
        f'    #     out.append({{\'p\': {{}}, \'a\': [], \'_chk\': None}})\n'
        f'    # 元の数値の組を先頭に並べ替える\n'
        f'    # out.sort(key=lambda v: 0 if v[\'p\'] == {{...}} else 1)\n'
        f'    return out[:limit]'
        for k in keys)
    varia = (f'{varia_name} = {{' +
             ', '.join(f"'{k}': {k.lower()}_variants" for k in keys) + '}')

    verifs = '\n\n'.join(
        f'def verify_{k.lower()}(vs):\n'
        f'    """{k}：別の原理で解き直して突き合わせる。"""\n'
        f'    for v in vs:\n'
        f'        pass\n'
        f'    return len(vs)'
        for k in keys)
    vdict = (f'VERIFY{n} = {{' +
             ', '.join(f"'{k}': verify_{k.lower()}" for k in keys) + '}')

    files = {
        f'nnop{n}_rates.py': RATES.format(**names),
        f'nnop{n}_data.py': DATA.format(gens=gens, varia=varia, **names),
        f'nnop{n}_verify.py': VERIFY.format(verifs=verifs, vdict=vdict, **names),
    }
    for fn, body in files.items():
        p = os.path.join(HERE, fn)
        if os.path.exists(p) and not a.force:
            sys.exit(f'{fn} は既にある（上書きするなら --force）')
        open(p, 'w', encoding='utf-8').write(body)
        print(f'作成: tools/{fn}')

    wire(n, rnd, a.label)
    print('\n配線: tools/build_nnop.py')
    print('\n次にやること（nnop_spec.md の「新しい回を足す手順」）:')
    print(f'  1. python3 tools/nnop_pages.py "NN TEST/…pdf" --list で構成を見る')
    print(f'  2. 問題ページと解答一覧を1回だけ読み、tools/nnop{n}_notes.md に'
          f'設問・配点・答え・計算欄mmを落とす')
    print(f'  3. tools/nnop{n}_rates.py → nnop{n}_data.py → nnop{n}_verify.py の順に書く')
    print( '  4. python3 tools/build_nnop.py を走らせて、検算と回帰テストを通す')
    return 0


def wire(n, rnd, label):
    """build_nnop.py に import・結合・検算・回帰テストを差し込む。"""
    p = os.path.join(HERE, 'build_nnop.py')
    s = open(p, encoding='utf-8').read()
    if f'nnop{n}_data' in s:
        print('build_nnop.py には既に配線されている（そのまま）')
        return

    def sub(old, new):
        nonlocal s
        assert old in s, f'build_nnop.py に目印が無い: {old[:40]}'
        s = s.replace(old, new, 1)

    sub('import nnop_fig as G           # noqa: E402',
        f'import nnop{n}_data as D{n}        # noqa: E402\n'
        f'import nnop{n}_verify as V{n}      # noqa: E402\n'
        'import nnop_fig as G           # noqa: E402')

    # ROUND_NAME / ROUND_ORDER
    m = re.search(r'ROUND_NAME = \{(.*?)\}\n', s, re.S)
    sub(m.group(0), f'ROUND_NAME = {{{m.group(1)}, {rnd!r}: {label!r}}}\n')
    m = re.search(r'ROUND_ORDER = \[(.*?)\]\n', s, re.S)
    sub(m.group(0), f'ROUND_ORDER = [{m.group(1)}, {rnd!r}]\n')

    for pat, tail in (
            (r'ALL_GROUPS = .*\n', f' + D{n}.GROUPS{n}'),
            (r'ALL_VARIANTS = \{.*\}\n', None),
            (r'ALL_WORK = \{.*\}\n', None)):
        m = re.search(pat, s)
        line = m.group(0).rstrip('\n')
        if tail:
            new = line + tail
        else:
            var = 'VARIANTS' if 'VARIANTS' in line else 'WORK_MM'
            new = line[:-1] + f', **D{n}.{var}{n}}}'
        sub(m.group(0), new + '\n')

    m = re.search(r'    verify = \{.*\}\n', s)
    sub(m.group(0), m.group(0).rstrip('\n')[:-1] + f', **V{n}.VERIFY{n}}}\n')

    m = list(re.finditer(r"    print\(f'  .*regression_of\(all_vs, .*\n", s))[-1]
    sub(m.group(0), m.group(0) +
        f"    print(f'  {label} {{regression_of(all_vs, V{n}.OFFICIAL{n})}} 大問すべて一致')\n")

    open(p, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    sys.exit(main())
