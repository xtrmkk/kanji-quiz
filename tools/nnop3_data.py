# -*- coding: utf-8 -*-
"""NNOP第3回・算数の設問マスタと、採用可能なパラメータの全列挙。

第1回（nnop_data.py）・第2回（nnop2_data.py）と同じ方針。
計算はすべてここ（ビルド時のPython）で終わらせる。
正答率・配点は tools/nnop3_rates.py（早稲田アカデミーLMSの実測値）。

  python3 tools/nnop3_data.py   … 自己検証
"""
import itertools
from fractions import Fraction as F
from math import gcd, factorial, comb

from nnop_data import frac_html, improper_html, num     # 表示の小道具は共用


# ══════════════════════════════════════════════════════════════════
# 共通：数列B（数表Aを蛇行につなげた列）
# ══════════════════════════════════════════════════════════════════
def rows_of(N):
    """1〜N を三角形に並べたときの各段（リスト）。最終段は欠けていてよい。"""
    out, s, k = [], 1, 1
    while s <= N:
        e = min(s + k - 1, N)
        out.append(list(range(s, e + 1)))
        s, k = e + 1, k + 1
    return out


def seq_b(N):
    """奇数段は左→右、偶数段は右→左でつないだ数列B。"""
    b = []
    for i, row in enumerate(rows_of(N)):
        b += row if i % 2 == 0 else row[::-1]
    return b


def pos_in_table(x):
    """数表Aで x が何段目の左から何番目か。"""
    k = 1
    while k * (k + 1) // 2 < x:
        k += 1
    return k, x - (k - 1) * k // 2


# ══════════════════════════════════════════════════════════════════
# K1 計算問題（計算）
#   ｛(f1−f2) ÷ (f3−f4) − (f5−f6)｝× m/2027
# ══════════════════════════════════════════════════════════════════
_DENS = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18, 20, 21, 24, 25, 30, 40)


def _diff_pairs():
    """差ごとに「見栄えのよい2つの真分数の組」をためる。"""
    best = {}
    for d1 in _DENS:
        for d2 in _DENS:
            if d1 == d2:
                continue
            for n1 in range(1, d1):
                if gcd(n1, d1) != 1:
                    continue
                for n2 in range(1, d2):
                    if gcd(n2, d2) != 1:
                        continue
                    v = F(n1, d1) - F(n2, d2)
                    if v <= 0 or v.denominator > 24:
                        continue
                    key = v
                    cand = (F(n1, d1), F(n2, d2))
                    # 分母がばらけていて、かつ大きすぎない組を好む
                    score = (max(d1, d2), abs(d1 - d2) == 0, d1 + d2)
                    if key not in best or score < best[key][0]:
                        best[key] = (score, cand)
    return {k: v[1] for k, v in best.items()}


def _fh(f: F) -> str:
    return improper_html(f) if f.denominator != 1 else str(f.numerator)


def k1_variants(limit=120):
    pairs = _diff_pairs()
    # 元の問題の組を最優先で入れておく
    pairs[F(4, 9)] = (F(5, 6), F(7, 18))
    pairs[F(5, 12)] = (F(3, 4), F(1, 3))
    pairs[F(1, 5)] = (F(5, 8), F(17, 40))
    keys = sorted(pairs)
    out, seen = [], set()
    for x1 in keys:
        for x2 in keys:
            x3 = x1 / x2
            if not (1 < x3 < 3) or x3.denominator > 20 or x3.denominator == 1:
                continue
            for x4 in keys:
                x5 = x3 - x4
                if x5 <= 0 or x5.denominator > 20 or x5.numerator > 40:
                    continue
                m = 3 * x5.denominator
                if m > 99 or x5.denominator < 5:
                    continue
                ans = F(3 * x5.numerator, 2027)
                if ans.denominator != 2027 or ans.numerator > 99:
                    continue
                key = (x1, x2, x4)
                if key in seen:
                    continue
                seen.add(key)
                f1, f2 = pairs[x1]
                f3, f4 = pairs[x2]
                f5, f6 = pairs[x4]
                out.append({
                    'p': {'f1': _fh(f1), 'f2': _fh(f2), 'f3': _fh(f3), 'f4': _fh(f4),
                          'f5': _fh(f5), 'f6': _fh(f6), 'm': m,
                          '_x1': str(x1), '_x2': str(x2), '_x3': str(x3),
                          '_x4': str(x4), '_x5': str(x5)},
                    'a': [improper_html(ans)],
                    '_chk': (f1, f2, f3, f4, f5, f6, m, ans),
                })
    orig = (F(4, 9), F(5, 12), F(1, 5))
    out.sort(key=lambda v: 0 if (F(v['p']['_x1']), F(v['p']['_x2']),
                                 F(v['p']['_x4'])) == orig else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // max(1, limit - 1))
    return head + rest[::step][:limit - 1]


# ══════════════════════════════════════════════════════════════════
# K2 円形の池で追いつく（速さ）
# ══════════════════════════════════════════════════════════════════
def k2_variants(limit=120):
    out = []
    for L in (840, 720, 900, 960, 1080, 1200, 1260):
        for va, vb, vc in itertools.product(range(2, 9), repeat=3):
            if not (va < vb < vc):
                continue
            if L % (vb - va):
                continue
            t1 = L // (vb - va)                      # 初めて追いつくまでの秒数
            if not (60 <= t1 <= 600):
                continue
            d1 = (va * t1) % L                       # 追いついた地点
            if d1 == 0:
                continue
            k = L // gcd(d1, L)                      # 追いつく地点の数
            if not (2 <= k <= 6):
                continue
            for n in (23, 17, 19, 29, 31, 37):
                gap = ((vc - va) * n * t1) % L
                if gap == 0 or gap == d1 * 0:
                    continue
                if gap % 10:
                    continue
                out.append({
                    'p': {'L': L, 'va': va, 'vb': vb, 'vc': vc, 'n': n},
                    'a': [f'{t1} 秒後', f'{d1} m', f'{k} か所', f'{gap} m'],
                    '_chk': (t1, d1, k, gap),
                })
                break
    out.sort(key=lambda v: 0 if (v['p']['L'], v['p']['va'], v['p']['vb'],
                                 v['p']['vc'], v['p']['n']) ==
             (840, 2, 5, 7, 23) else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // max(1, limit - 1))
    return head + rest[::step][:limit - 1]


# ══════════════════════════════════════════════════════════════════
# K3 長方形の中の四角形EBFD（平面図形）
#   四角形EBFD ＝ (ED×AB ＋ DF×BC) ÷ 2
# ══════════════════════════════════════════════════════════════════
def k3_count(e, f, S):
    """e×AB + f×BC = 2S の、AB≧f・BC≧e をみたす整数の組の数。"""
    sol = []
    for ab in range(1, 2 * S // e + 1):
        rest = 2 * S - e * ab
        if rest <= 0 or rest % f:
            continue
        bc = rest // f
        if ab >= f and bc >= e:
            sol.append((ab, bc))
    return sol


def k3_variants(limit=120):
    """(1)(2)(3) の材料を別々に列挙し、組み合わせて1つの大問にする。"""
    # (1) AB・AE・ED・DF
    p1 = []
    for ab in (18, 16, 20, 24, 14, 22, 26):
        for ed in (3, 4, 5, 2, 6):
            for ae in (21, 18, 16, 20, 24, 15, 27):
                bc = ae + ed
                for df in (4, 3, 5, 6, 2):
                    if df >= ab:
                        continue
                    s1 = F(ed * ab + df * bc, 2)
                    if s1.denominator != 1 or not (40 <= s1 <= 160):
                        continue
                    p1.append(({'AB': ab, 'AE': ae, 'ED': ed, 'DF': df}, int(s1)))
    p1.sort(key=lambda z: 0 if (z[0]['AB'], z[0]['AE'], z[0]['ED'], z[0]['DF'])
            == (18, 21, 3, 4) else 1)

    # (2) ED＝DF＝g、三角形EBF＝S2 → AB＋BC
    p2 = []
    for g in (6, 4, 8, 5, 10):
        for s2 in range(30, 161):
            tot = F(2 * s2, g) + g
            if tot.denominator != 1 or not (16 <= tot <= 70):
                continue
            if tot < 2 * g:          # AB も BC も g 以上でなければ長方形にならない
                continue
            p2.append(({'g': g, 'S2': s2}, int(tot)))
    p2.sort(key=lambda z: 0 if (z[0]['g'], z[0]['S2']) == (6, 60) else 1)

    # (3) ED＝e3、DF＝f3、四角形EBFD＝S3 → 組の数
    p3 = []
    for e3, f3 in ((4, 6), (3, 6), (4, 8), (6, 4), (2, 6), (6, 8), (5, 10), (4, 10)):
        for s3 in range(40, 161):
            sol = k3_count(e3, f3, s3)
            if not (4 <= len(sol) <= 9):
                continue
            p3.append(({'e3': e3, 'f3': f3, 'S3': s3}, sol))
    p3.sort(key=lambda z: 0 if (z[0]['e3'], z[0]['f3'], z[0]['S3']) == (4, 6, 60) else 1)

    out = []
    n = min(limit, max(len(p1), len(p2), len(p3)))
    for i in range(n):
        a1, v1 = p1[(i * 7) % len(p1)] if i else p1[0]
        a2, v2 = p2[(i * 5) % len(p2)] if i else p2[0]
        a3, v3 = p3[(i * 3) % len(p3)] if i else p3[0]
        out.append({
            'p': {**a1, **a2, **a3},
            'a': [f'{v1} cm<sup>2</sup>', f'{v2} cm', f'{len(v3)} 通り'],
            '_chk': (v1, v2, v3),
        })
    return out


# ══════════════════════════════════════════════════════════════════
# K4 ○と●の並べ方（場合の数）
#   ○が p 個、●が q 個（p = q−1）
# ══════════════════════════════════════════════════════════════════
def k4_variants(limit=120):
    out = []
    for q in (3, 4):
        p = q - 1
        a1 = comb(p + q, p)                       # ①並べ方
        a2 = p + 1                                # ②●がq個連続
        n2 = 2 * q - 1                            # (2) 1〜n2
        a3 = factorial(n2) - a2 * factorial(q) * factorial(p)
        n3 = 2 * q                                # (3) 1〜n3
        a4 = (factorial(n3) - 2 * factorial(q + 1) * factorial(q)
              + 2 * factorial(q) ** 2)
        out.append({
            'p': {'p': p, 'q': q, 'n2': n2, 'n3': n3},
            'a': [f'{a1} 通り', f'{a2} 通り', f'{a3} 通り', f'{a4} 通り'],
            '_chk': (a1, a2, a3, a4),
        })
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# K5 正方形のまわりを転がる正三角形（平面図形）
#   正方形の1辺は正三角形の1辺の2倍。角の合計は 990°／840° で変わらない。
# ══════════════════════════════════════════════════════════════════
def k5_variants(limit=120):
    out = []
    for s in (6, 3, 9, 12, 15, 18):
        a1 = F(314, 100) * 2 * s * F(990, 360)
        a2 = F(314, 100) * 2 * s * F(840, 360)
        if a1.denominator != 1 and (a1 * 100).denominator != 1:
            continue
        if a2.denominator != 1 and (a2 * 100).denominator != 1:
            continue
        out.append({
            'p': {'s': s, 'sq': 2 * s},
            'a': [f'{num(a1)} cm', f'{num(a2)} cm'],
            '_chk': (a1, a2),
        })
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# K6 数表Aと数列B（規則性）
# ══════════════════════════════════════════════════════════════════
def k6_one(N, d=6):
    """数列Bを作り、問いの材料をそろえる。"""
    B = seq_b(N)
    rows = rows_of(N)
    idx = {v: i for i, v in enumerate(B)}
    # となり合う2数の和
    sums = [(B[i], B[i + 1], B[i] + B[i + 1]) for i in range(len(B) - 1)]
    div = [(m, n) for m, n, s in sums if s % d == 0]
    return B, rows, idx, sums, div


def _k6_all():
    out = []
    for N in (2100, 1830, 2250, 1953, 2415, 2600):
        B, rows, idx, sums, div = k6_one(N)
        nrow = len(rows)
        # (3) 奇数段→偶数段の境目は、和が「偶数の2乗」になる。
        #     段数のおよそ7割の位置を選んで、手ごろな大きさにする。
        t = max(2, int(round(nrow * 0.7 / 2)) * 2)        # j+1（偶数）
        j = t - 1                                         # 奇数段 j と段 j+1 の境目
        while j >= 1 and (j + 1) * (j + 2) // 2 > N:
            j -= 2
        if j < 1:
            continue
        m3 = j * (j + 1) // 2
        n3 = (j + 1) * (j + 2) // 2
        s3 = m3 + n3
        assert (m3, n3) in [(a, b) for a, b, _ in sums], (N, m3, n3)
        for x in (50, 63, 77, 92, 44):
            if x <= N:
                break
        seg, pos = pos_in_table(x)
        for y in (70, 86, 58, 103):
            if y <= N:
                break
        for k in (2027, 1800, 1500, 2100):
            if k <= N:
                break
        out.append({'N': N, 'x': x, 'y': y, 'k': k, 'S': s3, 'd': 6,
                    'seg': seg, 'pos': pos, 'iy': idx[y] + 1, 'bk': B[k - 1],
                    'm3': m3, 'n3': n3, 'ndiv': len(div), 'nrow': nrow})
    return out


def k6_variants(limit=120):
    """(1)①②・(2)：数表Aと数列Bの中の位置"""
    out = []
    for z in _k6_all():
        out.append({
            'p': {t: z[t] for t in ('N', 'x', 'y', 'k')},
            'a': [f'{z["seg"]} 段目', f'左から{z["pos"]} 番目',
                  f'{z["iy"]} 番目', str(z['bk'])],
            '_chk': (z['seg'], z['pos'], z['iy'], z['bk'], z['nrow']),
        })
    return out[:limit]


def k6a_variants(limit=120):
    """(3)(4)：となり合う2数の和"""
    out = []
    for z in _k6_all():
        out.append({
            'p': {t: z[t] for t in ('N', 'S', 'd')},
            'a': [str(z['m3']), str(z['n3']), f'{z["ndiv"]} 通り'],
            '_chk': (z['m3'], z['n3'], z['ndiv'], z['nrow']),
        })
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# 設問マスタ
# ══════════════════════════════════════════════════════════════════
_NUM = '<span class="fr"><span class="fn">{}</span><span class="fd">{}</span></span>'

GROUPS3 = [
    {
        'key': 'K1', 'round': 3, 'field': 'calc', 'title': '計算問題', 'vary': True,
        'intro': '', 'body': '', 'fig': None,
        'subs': [
            {'id': 'op3-1-1', 'label': '',
             'q': '次の計算をしなさい。'
                  '<div class="formula">｛（{f1}−{f2}）÷（{f3}−{f4}）−（{f5}−{f6}）｝'
                  '×<span class="fr"><span class="fn">{m}</span>'
                  '<span class="fd">2027</span></span></div>',
             'rate': 83, 'score': 3, 'ans': [''],
             'how': 'かっこの中を先に、通分して計算する。'
                    '最後のかけ算は、約分できるところを先に約分すると速い。'},
        ],
    },
    {
        'key': 'K2', 'round': 3, 'field': 'speed', 'title': '池のまわりで追いつく', 'vary': True,
        'intro': '円形の池の周りに1周{L}mの道があります。A、B、Cの3人が同じ地点Pを同時に出発し、'
                 'それぞれAは秒速{va}m、Bは秒速{vb}m、Cは秒速{vc}mの速さで矢印の方向'
                 '（時計回り）に進み続けます。',
        'body': '', 'fig': 'pond', 'figpos': 'right',
        'subs': [
            {'id': 'op3-2-1', 'label': '(1)',
             'q': 'BがAに初めて追いつくのは、出発してから何秒後ですか。'
                  'また、追いついたのはPから時計回りに何mの地点ですか。',
             'rate': 93, 'score': 2, 'ans': ['', ''],
             'how': '1周分の差がつくまでの時間を求める。'
                    '差がつく速さは 秒速{vb}m −秒速{va}m。'
                    '地点はAが進んだ道のりを1周で割った「あまり」で考える。'},
            {'id': 'op3-2-2', 'label': '(2)',
             'q': 'BがAに追いつく地点として考えられるのは、全部で何か所ありますか。',
             'rate': 81, 'score': 3, 'ans': [''],
             'how': '1回追いつくごとに、追いつく地点は同じだけ先に進む。'
                    '何回かでPにもどってくるので、そこまでの地点の数を数える。'},
            {'id': 'op3-2-3', 'label': '(3)',
             'q': 'BがAに{n}回目に追いついたとき、CはAから時計回りに何m離れたところにいますか。',
             'rate': 52, 'score': 4, 'ans': [''],
             'how': '{n}回目に追いつく時刻を出す。'
                    'CとAの差は「（秒速{vc}m −秒速{va}m）×時間」を1周で割ったあまり。'},
        ],
    },
    {
        'key': 'K3', 'round': 3, 'field': 'plane', 'title': '長方形の中の四角形', 'vary': True,
        'intro': '右の図の長方形ABCDの辺AD、辺DC上にそれぞれ点E、点Fをとり、'
                 '四角形EBFDをつくります。以下の問いに答えなさい。',
        'body': '', 'fig': 'rect', 'figpos': 'right',
        'subs': [
            {'id': 'op3-3-1', 'label': '(1)',
             'q': 'AB＝{AB}cm、AE＝{AE}cm、ED＝{ED}cm、DF＝{DF}cmのとき、'
                  '四角形EBFDの面積は何cm<sup>2</sup>ですか。',
             'rate': 75, 'score': 3, 'ans': [''],
             'how': '長方形全体から、三角形ABEと三角形FBCをひく。'
                    '四角形EBFDを対角線BDで2つの三角形に分けてもよい。'},
            {'id': 'op3-3-2', 'label': '(2)',
             'q': 'EDとDFの長さがともに{g}cmで、三角形EBFの面積が{S2}cm<sup>2</sup>になるとき、'
                  '辺ABと辺BCの長さの和は何cmですか。',
             'rate': 42, 'score': 3, 'ans': [''],
             'how': '四角形EBFD ＝ 三角形EBF ＋ 三角形EDF。'
                    '四角形EBFDをBDで分けると、三角形EBD＝{g}×AB÷2、'
                    '三角形DBF＝{g}×BC÷2 になる。'},
            {'id': 'op3-3-3', 'label': '(3)',
             'q': 'EDの長さが{e3}cm、DFの長さが{f3}cmで、四角形EBFDの面積が'
                  '{S3}cm<sup>2</sup>になるとき、辺ABと辺BCの長さとして考えられる'
                  '組み合わせは全部で何通りありますか。'
                  'ただし、辺の長さは単位をcmで表したときに整数となる場合で答えなさい。',
             'rate': 9, 'score': 4, 'ans': [''],
             'how': '(2)と同じように、{e3}×AB÷2 ＋ {f3}×BC÷2 ＝ {S3} の式をつくる。'
                    'ABは{f3}以上、BCは{e3}以上であることに注意して表に書き出す。'},
        ],
    },
    {
        'key': 'K4', 'round': 3, 'field': 'case', 'title': '○と●の並べ方', 'vary': True,
        'intro': '以下の問いに答えなさい。', 'body': '', 'fig': None,
        'subs': [
            {'id': 'op3-4-1', 'label': '(1)①',
             'q': '○が{p}個、●が{q}個、全部で{n2}個あります。'
                  'これらを横1列に並べるとき、全部で何通りの並べ方がありますか。',
             'rate': 85, 'score': 2, 'ans': [''],
             'how': '{n2}か所のうち、○を置く{p}か所を選べばよい。'},
            {'id': 'op3-4-2', 'label': '(1)②',
             'q': '●が{q}個連続する並べ方は、全部で何通りありますか。',
             'rate': 89, 'score': 3, 'ans': [''],
             'how': '●{q}個をひとかたまりにして、かたまりと○{p}個を並べると考える。'
                    '少ないので書き出してもよい。'},
            {'id': 'op3-4-3', 'label': '(2)',
             'q': '1、2、…、{n2}の{n2}つの整数を横1列に並べるとき、'
                  '奇数が{q}個連続しないような並べ方は、全部で何通りありますか。',
             'rate': 44, 'score': 4, 'ans': [''],
             'how': '●＝奇数、○＝偶数と考えると(1)がそのまま使える。'
                    '全部の並べ方から「奇数が{q}個連続する並べ方」をひく（余事象）。'},
            {'id': 'op3-4-4', 'label': '(3)',
             'q': '1、2、…、{n3}の{n3}つの整数を横1列に並べるとき、'
                  '偶数も奇数も{q}個連続しないような並べ方は、全部で何通りありますか。',
             'rate': 26, 'score': 4, 'ans': [''],
             'how': '(1)(2)を真似る。まず偶奇だけの並び方で場合分けし、'
                    '「奇数が{q}個連続」と「偶数が{q}個連続」の重なりを引きすぎないように数える。'},
        ],
    },
    {
        'key': 'K5', 'round': 3, 'field': 'plane', 'title': '転がる正三角形', 'vary': True,
        'intro': '右の図のように1辺が{sq}cmの正方形のまわりを、1辺{s}cmの正三角形ABCが'
                 'すべることなく矢印の方向に転がります。円周率は3.14とします。',
        'body': '', 'fig': 'roll', 'figpos': 'right',
        'subs': [
            {'id': 'op3-5-1', 'label': '(1)',
             'q': '正三角形ABCが元の位置に1周して戻ってくるまでに、'
                  '頂点Aが動いたあとの線の長さは何cmですか。',
             'rate': 62, 'score': 4, 'ans': [''],
             'how': 'Aが動くのは半径{s}cmのおうぎ形の弧。'
                    '正方形の角では210°、辺の途中では120°回る。'
                    'Aが中心になっているところは動かないことに注意。'},
            {'id': 'op3-5-2', 'label': '(2)',
             'q': '正三角形ABCの3つの頂点がすべて元の状態と同じ位置に初めて戻ってくるまで'
                  '転がりました。このとき、正三角形の頂点Aが動いたあとの線の中で、'
                  '2回通過して重なった部分の長さの和は全部で何cmですか。'
                  'ただし、2回通過していても、線の長さは1回分として答えなさい。',
             'rate': 11, 'score': 4, 'ans': [''],
             'how': '3つの頂点が元に戻るのは3周したとき。'
                    'Aは2周目にCの線を、3周目にBの線をなぞる。'
                    'つまり3種類の線のうち2本が重なっている部分を探せばよい。'},
        ],
    },
    {
        'key': 'K6', 'round': 3, 'field': 'rule', 'title': '数表Aと数列B', 'vary': True,
        'intro': 'あるきまりにしたがって1から{N}までの{N}個の整数を並べた数表Aがあります。',
        'body': '<div class="tbl">数表A<br>'
                '1段目｜1<br>2段目｜2　3<br>3段目｜4　5　6<br>4段目｜7　8　9　10<br>'
                '5段目｜11　12　13　14　15<br>6段目｜16　17　18　19　20　21<br>'
                '7段目｜22　・　・　・　・　・　・<br>　　　｜　・<br></div>'
                '<div class="g-intro">さらに、数表Aの各段について、'
                '・奇数段は、左から右へ並べた列　・偶数段は、右から左へ並べた列'
                'を交互にくり返してつなげて並べ、1つの数列Bをつくります。</div>'
                '<div class="tbl wrap">数列B<br>'
                '1、3、2、4、5、6、10、9、8、7、11、12、13、14、15、21、20、19、…、{N}</div>',
        'fig': None,
        'subs': [
            {'id': 'op3-6-1', 'label': '(1)①',
             'q': '数表Aにおいて、{x}は何段目の左から何番目にありますか。',
             'rate': 92, 'score': 2, 'ans': ['', ''],
             'how': '1＋2＋3＋… と足していき、{x}をこえる手前までが前の段。'},
            {'id': 'op3-6-2', 'label': '(1)②',
             'q': '数列Bにおいて、{y}は左から何番目にありますか。',
             'rate': 72, 'score': 3, 'ans': [''],
             'how': 'まず{y}が何段目にあるかを出す。'
                    '偶数段なら大きい順に並んでいるので、段の中の位置に注意する。'},
            {'id': 'op3-6-3', 'label': '(2)',
             'q': '数列Bにおいて、左から{k}番目の数を答えなさい。',
             'rate': 31, 'score': 3, 'ans': [''],
             'how': '1＋2＋…＋□ が{k}をこえる手前までで、何段目かを決める。'
                    '偶数段なら大きい順なので、段の最後ではなく最初の数から数える。'},
        ],
    },
    {
        'key': 'K6a', 'round': 3, 'field': 'rule', 'title': 'となり合う2数の和', 'vary': True,
        'intro': 'あるきまりにしたがって1から{N}までの{N}個の整数を並べた数表Aがあります。',
        'body': '<div class="tbl">数表A<br>'
                '1段目｜1<br>2段目｜2　3<br>3段目｜4　5　6<br>4段目｜7　8　9　10<br>'
                '5段目｜11　12　13　14　15<br>6段目｜16　17　18　19　20　21<br>'
                '7段目｜22　・　・　・　・　・　・<br>　　　｜　・<br></div>'
                '<div class="g-intro">さらに、数表Aの各段について、'
                '・奇数段は、左から右へ並べた列　・偶数段は、右から左へ並べた列'
                'を交互にくり返してつなげて並べ、1つの数列Bをつくります。</div>'
                '<div class="tbl wrap">数列B<br>'
                '1、3、2、4、5、6、10、9、8、7、11、12、13、14、15、21、20、19、…、{N}</div>',
        'fig': None,
        'subs': [
            {'id': 'op3-6-4', 'label': '(1)',
             'q': '数列Bにおいて、となり合う2つの数m、nの和を［m，n］と表すことにします。'
                  '例えば、［5，6］＝11、［7，11］＝18、［19，18］＝37、［66，78］＝144 です。'
                  '［m，n］＝{S}となるとき、m、nにあてはまる数を求めなさい。',
             'rate': 21, 'score': 4, 'ans': ['m', 'n'],
             'how': '同じ段の中でとなり合う2数は、偶数と奇数だから和は必ず奇数。'
                    '{S}は偶数なので、段の境目しかない。'
                    '境目の和を小さい方から書き出すと、平方数が出てくる。'},
            {'id': 'op3-6-5', 'label': '(2)',
             'q': '［m，n］の値が{d}で割り切れるようなm、nの組み合わせは何通りありますか。',
             'rate': 1, 'score': 5, 'ans': [''],
             'how': '{d}で割り切れる数は偶数なので、やはり段の境目だけを調べればよい。'
                    '境目の和を順に書き出して{d}で割ったあまりを見ると、くり返しが見つかる。'
                    '最後の段まで数え落とさないこと。'},
        ],
    },
]

VARIANTS3 = {'K1': k1_variants, 'K2': k2_variants, 'K3': k3_variants,
             'K4': k4_variants, 'K5': k5_variants, 'K6': k6_variants, 'K6a': k6a_variants}

# 計算欄の高さ（mm）。元の問題用紙の実測値。
WORK_MM3 = {
    'op3-1-1': 30,
    'op3-2-1': 28, 'op3-2-2': 34, 'op3-2-3': 33,
    'op3-3-1': 27, 'op3-3-2': 62, 'op3-3-3': 55,
    'op3-4-1': 20, 'op3-4-2': 30, 'op3-4-3': 35, 'op3-4-4': 80,
    'op3-5-1': 75, 'op3-5-2': 90,   # 元は作図欄こみで82/101mm
    'op3-6-1': 25, 'op3-6-2': 72, 'op3-6-3': 40, 'op3-6-4': 61, 'op3-6-5': 85,
}


if __name__ == '__main__':
    for k, fn in VARIANTS3.items():
        vs = fn()
        print(f'{k}: {len(vs):4}通り　例 {vs[0]["a"]}')
