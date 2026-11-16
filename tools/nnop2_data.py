# -*- coding: utf-8 -*-
"""NNOP第2回・算数の設問マスタと、採用可能なパラメータの全列挙。

第1回（nnop_data.py）と同じ方針。計算はすべてここで終わらせる。
正答率・配点は tools/nnop2_rates.py（早稲田アカデミーLMSの実測値）。
"""
import itertools
from fractions import Fraction as F
from math import gcd

from nnop_data import frac_html, num, ratio_of, BOX     # 表示の小道具は共用


# ══════════════════════════════════════════════════════════════════
# H1 操作P・Q・R（数の性質）
#   操作の倍率と例（X=200→120）は元のまま固定。(1)の数と並び、(2)の数と範囲を振る。
# ══════════════════════════════════════════════════════════════════
MUL = {'P': F(5, 2), 'Q': F(3, 5), 'R': F(2, 3)}
OPS = 'PQR'


def _apply(x, seq):
    v = F(x)
    for c in seq:
        v *= MUL[c]
    return v


def _mixed(f: F) -> str:
    return frac_html(f)


def h1_variants(limit=120):
    out = []
    # (1)：6回の並び。分母が手に負える大きさに収まるものだけ
    seqs = []
    for s in itertools.product(OPS, repeat=6):
        if len(set(s)) < 2:
            continue
        seqs.append(''.join(s))
    for X1 in (2027, 2024, 1800, 1215, 3024, 2430):
        for seq in seqs:
            r = _apply(X1, seq)
            if r.denominator > 30 or r < 100 or r > 20000:
                continue
            # (2)：X2 から n 回・P,Q,R をどれも1回以上・結果が範囲に入る
            for X2, lo, hi in ((200, 200, 400), (300, 300, 600), (160, 150, 300),
                               (500, 400, 800), (250, 200, 500)):
                combos = []
                for p in range(1, 5):
                    for q in range(1, 5):
                        r3 = 6 - p - q
                        if r3 < 1:
                            continue
                        v = F(X2) * MUL['P'] ** p * MUL['Q'] ** q * MUL['R'] ** r3
                        if lo < v < hi:
                            combos.append((p, q, r3, v))
                if len(combos) != 1:          # 答えが1通りに決まる組だけ採用
                    continue
                p, q, r3, v = combos[0]
                ex = 'P' * p + 'Q' * q + 'R' * r3
                out.append({'p': {'X1': X1, 'seq': '→'.join(seq), 'X2': X2,
                                  'lo': lo, 'hi': hi},
                            'a': [_mixed(r), f'（例）{X2} → ' + ' → '.join(ex)],
                            '_chk': (r, X2, lo, hi, (p, q, r3), v)})
                break
    out.sort(key=lambda v: 0 if (v['p']['X1'], v['p']['seq']) ==
             (2027, 'R→R→P→R→P→Q') else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# H2 面積比から三角形AOD（平面図形）
#   AOD = ACD × (ABC + ACD − DBC) ÷ (ABC + ACD)
# ══════════════════════════════════════════════════════════════════
def h2_variants(limit=120):
    out = []
    for S1 in range(60, 301, 5):              # ABC
        for S3 in range(10, 121, 5):          # ACD
            for S2 in range(20, 301):         # DBC
                if S2 >= S1 + S3 or S2 <= S3:
                    continue
                v = F(S3 * (S1 + S3 - S2), S1 + S3)
                if v.denominator != 1 or not (3 <= v <= S3 - 1):
                    continue
                out.append({'p': {'S1': S1, 'S2': S2, 'S3': S3},
                            'a': [f'{v} cm<sup>2</sup>'], '_chk': int(v)})
    out.sort(key=lambda x: 0 if (x['p']['S1'], x['p']['S2'], x['p']['S3']) ==
             (175, 126, 35) else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // (limit - 1))
    return head + rest[::step][:limit - 1]


# ══════════════════════════════════════════════════════════════════
# H3 3つのビーカーの食塩水（濃度）
#   Bの濃さが変わらない ⇔ Cに移した食塩水の濃さ＝Bの濃さ
#   → x = cb × w ÷ (ca − cb)、最後のCの濃さは必ず cb%
# ══════════════════════════════════════════════════════════════════
def h3_variants(limit=120):
    out = []
    for w in (180, 200, 240, 150, 300):
        for ca2 in range(4, 61):              # ca = ca2/2 （0.5%刻み）
            for cb2 in range(2, ca2):
                ca, cb = F(ca2, 2), F(cb2, 2)
                x = cb * w / (ca - cb)
                if x.denominator != 1 or not (10 <= x <= w * 3 // 4):
                    continue
                sa, sb = ca * w / 100, cb * w / 100
                if (sa * 10).denominator != 1 or (sb * 10).denominator != 1:
                    continue
                out.append({'p': {'ca': num(ca), 'cb': num(cb), 'w': w},
                            'a': [f'{num(sa)} g', f'{num(sb)} g',
                                  f'{num(cb)}%', str(int(x))],
                            '_chk': (sa, sb, cb, int(x))})
    out.sort(key=lambda v: 0 if (v['p']['ca'], v['p']['cb'], v['p']['w']) ==
             ('16', '4', 180) else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# H4 相似・面積比（平面図形）
#   AF:DC = a:b、[ABE]:[DCE] = p:q → AE:EC と BF:FC
# ══════════════════════════════════════════════════════════════════
def h4_solve(a, b, p, q):
    if a == b:
        return None
    u = F(b * p - a * q, a - b)               # [EBC]
    if u <= 0:
        return None
    s = F(p, p + u)                            # AE:AC
    t = F(a, b) * (1 - s)                      # BD上のEの位置
    if s >= 1:
        return None
    f = (t - s) / (1 - s)                      # Fの位置（BからBCの何倍か）
    if not (0 < f < 1):
        return None
    return ratio_of(F(p), u), ratio_of(f, 1 - f)


def h4_variants(limit=120):
    out = []
    for a in range(1, 10):
        for b in range(a + 1, 16):
            if gcd(a, b) != 1:
                continue
            for p in range(1, 12):
                for q in range(2, 40):
                    if gcd(p, q) != 1 or b * p >= a * q:
                        continue
                    r = h4_solve(a, b, p, q)
                    if not r:
                        continue
                    (ae, ec), (bf, fc) = r
                    if max(ae, ec) > 12 or max(bf, fc) > 25:
                        continue
                    if ae == ec or bf == fc:   # 1:1 は答えが見え見え
                        continue
                    out.append({'p': {'a': a, 'b': b, 'p': p, 'q': q},
                                'a': [f'{ae} : {ec}', f'{bf} : {fc}'],
                                '_chk': (ae, ec, bf, fc)})
    out.sort(key=lambda v: 0 if (v['p']['a'], v['p']['b'], v['p']['p'],
                                 v['p']['q']) == (3, 7, 3, 19) else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# H5 往復の速さ（速さ）
#   (1) 往復時間の比 T1:T2   (2) すれ違いから家〜公園   (3) 家〜郵便局 = D×T1/(T1+T2)
# ══════════════════════════════════════════════════════════════════
def h5_variants(limit=120):
    out = []
    V = list(range(30, 241, 15))
    for a1 in V:
        for b1 in V:
            if b1 >= a1:
                continue
            for a2 in V:
                for b2 in V:
                    if b2 >= a2 or a2 <= a1:
                        continue
                    T1, T2 = F(1, a1) + F(1, b1), F(1, a2) + F(1, b2)
                    if T1 == T2:
                        continue
                    r1 = ratio_of(T1, T2)
                    if max(r1) > 30:
                        continue
                    for ts in range(300, 1500, 20):        # すれ違いまでの秒数
                        t = F(ts, 60)
                        D = F((a1 + b2) * t, 1 + F(b2, a2))
                        if D.denominator != 1:
                            continue
                        D = int(D)
                        if not (600 <= D <= 4000):
                            continue
                        if not (F(D, a2) < t <= F(D, a1)):  # 次朗は折り返し済み／太朗はまだ
                            continue
                        post = D * T1 / (T1 + T2)
                        if post.denominator != 1:
                            continue
                        mm, ss = divmod(ts, 60)
                        tm = f'{mm}分{ss}秒' if ss else f'{mm}分'
                        out.append({'p': {'a1': a1, 'b1': b1, 'a2': a2, 'b2': b2,
                                          'tm': tm},
                                    'a': [f'{r1[0]} : {r1[1]}', f'{D} m',
                                          f'{int(post)} m'],
                                    '_chk': (r1, D, int(post), ts)})
    orig = [v for v in out if v['_chk'][3] == 760 and
            (v['p']['a1'], v['p']['b1'], v['p']['a2'], v['p']['b2']) == (120, 60, 180, 45)]
    rest = [v for v in out if v not in orig]
    step = max(1, len(rest) // max(1, limit - len(orig)))
    return orig + rest[::step][:limit - len(orig)]


# ══════════════════════════════════════════════════════════════════
# H6 約束記号（数の性質）  〈P〉= P を M で割った余り
# ══════════════════════════════════════════════════════════════════
def h6_variants(limit=120):
    out = []
    for M in (7, 9, 11, 13):
        for N in (2027, 2024, 2025):
            for K in (100, 120, 150, 200):
                for st in (1895, 2020, 1234, 3330):
                    for c, Q in ((3, 7), (4, 9), (5, 8), (6, 11)):
                        a1 = (K * (K + 1) // 2) % M
                        a2 = sum(n % M for n in range(st, st + 4)) % M
                        a3 = (N % M) ** 3 % M
                        a4 = ((c % M) * Q) % M
                        # (3) 〈［P,N］〉= t3 となる最小の4桁P
                        t3 = ((1000 % M) * N) % M
                        s3 = [P for P in range(1000, 10000) if ((P % M) * N) % M == t3]
                        if not s3:
                            continue
                        # (4) 〈【P,N】〉= t4 となる4桁Pの個数
                        t4 = pow(2 % M, N, M)
                        c4 = sum(1 for P in range(1000, 10000)
                                 if pow(P % M, N, M) == t4)
                        if not (200 <= c4 <= 4000):
                            continue
                        out.append({'p': {'M': M, 'N': N, 'K': K, 'st': st,
                                          'st1': st + 1, 'st2': st + 2, 'st3': st + 3,
                                          'c': c, 'Q': Q, 't3': t3, 't4': t4},
                                    'a': [str(a1), str(a2), str(a3), str(a4),
                                          str(min(s3)), f'{c4} 個'],
                                    '_chk': (a1, a2, a3, a4, min(s3), c4)})
    out.sort(key=lambda v: 0 if (v['p']['M'], v['p']['N'], v['p']['K'],
                                 v['p']['st'], v['p']['c'], v['p']['Q']) ==
             (7, 2027, 100, 1895, 3, 7) else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# 大問マスタ
# ══════════════════════════════════════════════════════════════════
A = '〈'
B = '〉'

GROUPS2 = [
    {
        'key': 'H1', 'round': 2, 'field': 'numth', 'title': '操作のくり返し', 'vary': True,
        'intro': 'ある数Xに対して、下の操作P、Q、Rを何回か行います。'
                 '<div class="box">［操作］　・操作P：2.5倍する。　'
                 '・操作Q：<span class="fr"><span class="fn">3</span>'
                 '<span class="fd">5</span></span>倍する。　'
                 '・操作R：<span class="fr"><span class="fn">2</span>'
                 '<span class="fd">3</span></span>倍する。</div>'
                 'また、Xに対して操作Pを1回、続けて操作Qを2回、さらに操作Rを1回行うことを'
                 '［X→P→Q→Q→R］と表すことにします。<br>'
                 '例えば、X＝200のとき、［200→Q→P→R→Q］は '
                 '200×<span class="fr"><span class="fn">3</span><span class="fd">5</span></span>'
                 '×2.5×<span class="fr"><span class="fn">2</span><span class="fd">3</span></span>'
                 '×<span class="fr"><span class="fn">3</span><span class="fd">5</span></span>'
                 ' を計算し、結果は120となります。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op2-1-1', 'label': '(1)',
             'q': '［{X1}→{seq}］の結果を答えなさい。', 'rate': 90, 'score': 3, 'ans': [''],
             'how': 'かけ算だけなので、操作の順番は答えに関係ない。'
                    'P・Q・Rがそれぞれ何回あるかを数えてまとめてかける。'},
            {'id': 'op2-1-2', 'label': '(2)',
             'q': '［{X2}→□→□→□→□→□→□］のようにX＝{X2}に対して、操作P、Q、Rを'
                  'どれも1回以上、全部で6回行った結果が{lo}より大きく{hi}より小さくなるように'
                  'するとき、□に入るP、Q、Rの一例を書き入れなさい。',
             'rate': 73, 'score': 4, 'ans': [''],
             'how': '順番は関係ないので「Pが何回・Qが何回・Rが何回」の組み合わせだけ調べればよい。'
                    '3つとも1回以上で合計6回だから、組み合わせは多くない。'},
        ],
    },
    {
        'key': 'H2', 'round': 2, 'field': 'plane', 'title': '面積比から三角形の面積', 'vary': True,
        'intro': '', 'body': '', 'fig': None,
        'subs': [
            {'id': 'op2-2-1', 'label': '',
             'q': '右の図において、三角形ABCの面積は{S1}cm<sup>2</sup>、'
                  '三角形DBCの面積は{S2}cm<sup>2</sup>、三角形ACDの面積は{S3}cm<sup>2</sup>です。'
                  'このとき、三角形AODの面積を求めなさい。ただし、図は正確とは限りません。',
             'rate': 62, 'score': 4, 'ans': [''], 'fig': 'quad', 'figpos': 'right',
             'how': '四角形ABCDを対角線ACで分けると三角形ABCと三角形ACDになる。'
                    '対角線BDで分けた三角形ABDの面積が出せる。'
                    'あとはAO:OCの比が分かれば、三角形ACDをその比で分ければよい。'},
        ],
    },
    {
        'key': 'H3', 'round': 2, 'field': 'dens', 'title': '3つのビーカーの食塩水', 'vary': True,
        'intro': '3つのビーカーA、B、Cがあり、Aには濃さが{ca}%、Bには濃さが{cb}%の食塩水が'
                 '{w}gずつ入っていて、Cには水が{w}g入っています。ただし、食塩水の濃さとは、'
                 '食塩水の重さに対する食塩の重さの割合のことです。<br>'
                 'まず、AとBから食塩水をxgずつとり出し、それらを両方ともCに入れて混ぜ合わせます。'
                 '<br>次に、Cから食塩水をxgずつとり出し、それらをそれぞれAとBに入れて'
                 '混ぜ合わせます。すると、Bの食塩水ははじめから最後までずっと濃さは'
                 '変わりませんでした。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op2-3-1', 'label': '(1)',
             'q': 'はじめにビーカーA、Bにはそれぞれ何gの食塩が含まれていましたか。',
             'rate': 94, 'score': 3, 'ans': ['A', 'B'],
             'how': '食塩の重さ ＝ 食塩水の重さ × 濃さ。'},
            {'id': 'op2-3-2', 'label': '(2)',
             'q': '最後にビーカーCの食塩水の濃さは何%になりましたか。',
             'rate': 67, 'score': 4, 'ans': [''],
             'how': 'Bの濃さが変わらなかったということは、Cから戻した食塩水の濃さが'
                    'Bの濃さとちょうど同じだったということ。'},
            {'id': 'op2-3-3', 'label': '(3)',
             'q': 'xにあてはまる値を答えなさい。',
             'rate': 50, 'score': 4, 'ans': [''],
             'how': 'Cの中は「水{w}g＋Aからxg＋Bからxg」。'
                    'その濃さが(2)の値になるようにxを求める。'},
        ],
    },
    {
        'key': 'H4', 'round': 2, 'field': 'plane', 'title': '相似と面積比', 'vary': True,
        'intro': '', 'body': '', 'fig': None,
        'subs': [
            {'id': 'op2-4-1', 'label': '',
             'q': '下の図のような、AF：DC＝{a}：{b}の三角形ABCと直角三角形DBCを'
                  '重ね合わせた図形があります。三角形ABEと三角形DCEの面積の比は、{p}：{q}です。'
                  'このとき、AE：EC、BF：FCをそれぞれ求めなさい。'
                  'ただし、図は正確とは限りません。',
             'rate': 14, 'score': 7, 'ans': ['AE：EC', 'BF：FC'], 'fig': 'tri2', 'figpos': 'bottom',
             'how': 'AFとDCはどちらもBCに垂直だから平行。高さの比がAF：DCになるので、'
                    '三角形ABCと三角形DBCの面積の比も同じ。'
                    'そこから三角形EBCの面積が出せて、AE：ECが分かる。'},
        ],
    },
    {
        'key': 'H5', 'round': 2, 'field': 'speed', 'title': '往復の速さ', 'vary': True,
        'intro': '太朗君と次朗君の兄弟が、家から公園までの道のりを途中の郵便局の前を通って'
                 '休まずに往復します。太朗君は出発してから行きは分速{a1}mで進み、'
                 '帰りは分速{b1}mで進みます。次朗君は出発してから行きは分速{a2}mで進み、'
                 '帰りは分速{b2}mで進みます。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op2-5-1', 'label': '(1)',
             'q': '太朗君と次朗君が家から公園までを往復するのにかかる時間の比を、'
                  '最も簡単な整数の比で答えなさい。',
             'rate': 78, 'score': 3, 'ans': ['太朗：次朗'],
             'how': '道のりを1としたときの往復の時間は「1÷行きの速さ＋1÷帰りの速さ」。'},
            {'id': 'op2-5-2', 'label': '(2)',
             'q': 'ある日、太朗君と次朗君は家から同時に出発したところ、出発してから'
                  '{tm}後にすれ違いました。家から公園までの道のりは何mですか。',
             'rate': 29, 'score': 5, 'ans': [''],
             'how': '次朗君の方が行きが速いので、先に公園で折り返してから出会う。'
                    '出会うまでに2人が進んだ道のりの合計を考える。'},
            {'id': 'op2-5-3', 'label': '(3)',
             'q': '次の日、太朗君は家から、次朗君は太朗君が家を出発した少し後に公園を'
                  '出発したところ、2人とも折り返す前に郵便局の前ですれ違い、折り返した後も'
                  '郵便局の前ですれ違いました。家から郵便局までの道のりは何mですか。',
             'rate': 2, 'score': 5, 'ans': [''],
             'how': '2回とも同じ場所ですれ違うということは、'
                    '「郵便局〜公園を太朗君が往復する時間」と「家〜郵便局を次朗君が往復する時間」'
                    'が等しいということ。(1)で求めた比がそのまま使える。'},
        ],
    },
    {
        'key': 'H6', 'round': 2, 'field': 'numth', 'title': '約束記号（あまり）', 'vary': True,
        'intro': '整数Pを{M}で割ったときの余りを' + A + 'P' + B + 'で表すことにします。<br>'
                 '例えば、' + A + '5' + B + '、' + A + '29' + B + 'のように求めます。また、'
                 + A + A + 'P' + B + B + 'のように重ねて使ったり、'
                 + A + 'の中を複数の数の計算の形で表したりすることもできるものとします。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op2-6-1', 'label': '(1)',
             'q': '次の①から③の値を求めなさい。<br>'
                  '①　' + A + '1＋2＋3＋…＋{K}' + B + '<br>'
                  '②　' + A + A + '{st}' + B + '＋' + A + '{st1}' + B + '＋' + A + '{st2}' + B
                  + '＋' + A + '{st3}' + B + B + '<br>'
                  '③　' + A + A + '{N}' + B + '×' + A + '{N}' + B + '×' + A + '{N}' + B + B,
             'rate': 80, 'score': 6, 'ans': ['①', '②', '③'],
             'how': '①は1から{K}までの和を先に出してから{M}で割る。'
                    '②③は先に中の余りを出してから、もう一度{M}で割る。'},
            {'id': 'op2-6-2', 'label': '(2)',
             'q': A + 'P' + B + 'をQ回足した値を［P，Q］と表すことにします。'
                  + A + '［{c}，{Q}］' + B + 'の値を求めなさい。',
             'rate': 76, 'score': 3, 'ans': [''],
             'how': A + '{c}' + B + 'を{Q}回足すだけ。出た数をもう一度{M}で割る。'},
            {'id': 'op2-6-3', 'label': '(3)',
             'q': A + '［P，{N}］' + B + '＝{t3} となるような4桁の整数Pのうち、'
                  '最も小さい数はいくつですか。',
             'rate': 28, 'score': 4, 'ans': [''],
             'how': 'Pそのものではなく' + A + 'P' + B + '（＝{M}で割った余り）だけで決まる。'
                    '余りを0から{M}−1まで試して、条件に合う余りを見つける。'},
            {'id': 'op2-6-4', 'label': '(4)',
             'q': A + 'P' + B + 'をQ回かけた値を【P，Q】と表すことにします。'
                  + A + '【P，{N}】' + B + '＝{t4} となるような4桁の整数Pは全部で何個ありますか。',
             'rate': 3, 'score': 5, 'ans': [''],
             'how': 'かけ算の余りはくり返すと循環する。'
                    '余りごとに循環のしかたを調べて、条件に合う余りを見つけてから'
                    '4桁の整数が何個あるかを数える。'},
        ],
    },
]

VARIANTS2 = {'H1': h1_variants, 'H2': h2_variants, 'H3': h3_variants,
             'H4': h4_variants, 'H5': h5_variants, 'H6': h6_variants}

# 計算欄の高さ（mm）。元の問題用紙の実測値。
WORK_MM2 = {
    'op2-1-1': 32, 'op2-1-2': 42,
    'op2-2-1': 58,
    'op2-3-1': 36, 'op2-3-2': 66, 'op2-3-3': 87,
    'op2-4-1': 90,          # 元は図こみで145mm。図は別に描くのでその分を引いた
    'op2-5-1': 33, 'op2-5-2': 88, 'op2-5-3': 87,
    'op2-6-1': 49, 'op2-6-2': 47, 'op2-6-3': 88, 'op2-6-4': 112,
}
