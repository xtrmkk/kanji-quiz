# -*- coding: utf-8 -*-
"""夏期集中特訓そっくりテスト・算数の設問マスタと、採用可能なパラメータの全列挙。

第1〜3回と同じ方針。計算はすべてここ（ビルド時のPython）で終わらせる。
正答率・配点は tools/nnop3_rates.py の NATSU_SUBS（早稲田アカデミーLMSの実測値）。

  python3 tools/nnop4_data.py   … 自己検証
"""
import itertools
from fractions import Fraction as F
from math import gcd

from nnop_data import frac_html, improper_html, num


# ══════════════════════════════════════════════════════════════════
# 共通：循環小数の表示
# ══════════════════════════════════════════════════════════════════
def rep_decimal(f: F):
    """分数を (整数部, 非循環部, 循環部) の文字列にする。"""
    whole, rem = divmod(f.numerator, f.denominator)
    d = f.denominator
    digits, seen = [], {}
    i = 0
    while rem and rem not in seen:
        seen[rem] = i
        rem *= 10
        digits.append(str(rem // d))
        rem %= d
        i += 1
    if rem == 0:
        return str(whole), ''.join(digits), ''
    k = seen[rem]
    return str(whole), ''.join(digits[:k]), ''.join(digits[k:])


def dec_html(f: F) -> str:
    """0.1(・)714285(・) のように、循環節の最初と最後に点をつけた表示。"""
    w, pre, rep = rep_decimal(f)
    if not rep:
        s = f'{w}.{pre}' if pre else w
        return s
    if len(rep) == 1:
        body = f'<span class="dt">{rep}</span>'
    else:
        body = (f'<span class="dt">{rep[0]}</span>{rep[1:-1]}'
                f'<span class="dt">{rep[-1]}</span>')
    return f'{w}.{pre}{body}'


def mixed_html(f: F) -> str:
    return frac_html(f)


# ══════════════════════════════════════════════════════════════════
# N1 食塩水の入れ替え（濃度）
#   同じ重さずつ入れ替えて濃さが等しくなる ⇔ 全部混ぜた濃さになる
#   くみ出す量 x ＝ wA×wB ÷ (wA＋wB)   （濃さによらない）
# ══════════════════════════════════════════════════════════════════
def n1_variants(limit=120):
    out = []
    for wa in (400, 300, 200, 500, 600, 240, 360):
        for wb in (600, 400, 300, 500, 800, 360, 240):
            if wa == wb:
                continue
            x = F(wa * wb, wa + wb)
            if x.denominator != 1 or not (50 <= x < min(wa, wb)):
                continue
            for ca2 in range(4, 41):              # ca = ca2/2（0.5%きざみ）
                for cb2 in range(2, ca2):
                    ca, cb = F(ca2, 2), F(cb2, 2)
                    sa, sb = ca * wa / 100, cb * wb / 100
                    if sa.denominator != 1 or sb.denominator != 1:
                        continue
                    c = (sa + sb) / (wa + wb) * 100
                    if (c * 10).denominator != 1:
                        continue
                    if not (2 <= c <= 18):
                        continue
                    out.append({
                        'p': {'wa': wa, 'wb': wb, 'ca': num(ca), 'cb': num(cb)},
                        'a': [f'{num(c)}%', f'{int(x)} g'],
                        '_chk': (c, int(x), sa, sb),
                    })
    out.sort(key=lambda v: 0 if (v['p']['wa'], v['p']['wb'], v['p']['ca'],
                                 v['p']['cb']) == (400, 600, '8', '6') else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // max(1, limit - 1))
    return head + rest[::step][:limit - 1]


# ══════════════════════════════════════════════════════════════════
# N2 アメ・ガム・チョコの個数（数の性質）
#   値段は a 円・(a+40) 円・(a+80) 円。a+1 が40の倍数になるものだけ使う。
# ══════════════════════════════════════════════════════════════════
def n2_solve(a, T):
    sol = []
    for z in range(1, T // (a + 80) + 1):
        for y in range(1, (T - (a + 80) * z) // (a + 40) + 1):
            rest = T - (a + 80) * z - (a + 40) * y
            if rest <= 0 or rest % a:
                continue
            x = rest // a
            if x >= 1:
                sol.append((x, y, z))
    return sol


def n2_variants(limit=120):
    out = []
    for a in (39, 79, 119):
        for T in range(a * 12, a * 40):
            sol = n2_solve(a, T)
            if not sol:
                continue
            if len({x + y + z for x, y, z in sol}) != 1:   # 個数の合計が1通りに決まること
                continue
            xs = sorted({x for x, _, _ in sol})
            if not (3 <= len(xs) <= 5):
                continue
            if xs != list(range(xs[0], xs[-1] + 1)):       # 連続した値になるものを選ぶ
                continue
            out.append({
                'p': {'a': a, 'b': a + 40, 'c': a + 80, 'T': T},
                'a': ['、'.join(f'{x}' for x in xs) + ' 個'],
                '_chk': (xs, sol),
            })
    out.sort(key=lambda v: 0 if (v['p']['a'], v['p']['T']) == (39, 1453) else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // max(1, limit - 1))
    return head + rest[::step][:limit - 1]


# ══════════════════════════════════════════════════════════════════
# N3 直角三角形を6つに分けた図（平面図形）
#   ●のついた辺はすべて AB と同じ長さ。角Bは90°、角Cは15°になる。
#   ア＝カ＝L×L÷4、ウ＋エ＝L×L÷2、イ：オ＝1：1、ABC＝ウ×5＋エ×3
# ══════════════════════════════════════════════════════════════════
def n3_variants(limit=120):
    out = []
    for L in range(4, 29, 2):
        a = F(L * L, 4)
        if a.denominator != 1:
            continue
        out.append({
            'p': {'L': L},
            'a': [f'{int(a)} cm<sup>2</sup>', f'{int(a) * 2} cm<sup>2</sup>',
                  f'{int(a)} cm<sup>2</sup>', '1 : 1', '5', '3'],
            '_chk': (int(a), int(a) * 2, int(a)),
        })
    out.sort(key=lambda v: 0 if v['p']['L'] == 8 else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# N4 流水算（速さ）
# ══════════════════════════════════════════════════════════════════
def n4_plan(v, r, T, h):
    """予定から片道の道のりを出す。"""
    up, dn = v - r, v + r
    t = F(T - h, 60)                      # 走っている時間（時間）
    return t / (F(1, up) + F(1, dn))


def n4_stop(v, r, d, t1, k, h2, T):
    """エンジンが止まっていた時間（分）。"""
    up, dn = v - r, v + r
    u2 = k * v - r
    gone = up * F(t1, 60)
    rest = d - gone
    if rest <= 0:
        return None
    rhs = T - t1 - h2 - 60 * d / dn
    t = (rhs * u2 - 60 * rest) / (k * v)
    return t, rest


def n4_variants(limit=120):
    out = []
    for r in (3, 2, 4, 5):
        for v in (24, 21, 27, 30, 18):
            for T, h in ((100, 20), (120, 20), (110, 15), (90, 15), (130, 25)):
                d = n4_plan(v, r, T, h)
                if (d * 100).denominator != 1 or not (8 <= d <= 40):
                    continue
                for t1 in (23, 18, 25, 30, 20, 15):
                    for k in (F(3, 2), F(5, 4), F(2, 1)):
                        if (k * v).denominator != 1:
                            continue
                        for h2 in (8, 5, 10, 12):
                            if h2 >= h:
                                pass
                            got = n4_stop(v, r, d, t1, k, h2, T)
                            if not got:
                                continue
                            t, rest = got
                            if t <= 0 or t > 60:
                                continue
                            sec = t * 60
                            if sec.denominator != 1:
                                continue
                            mm, ss = divmod(int(sec), 60)
                            if ss % 10:
                                continue
                            out.append({
                                'p': {'r': r, 'v': v, 'T0': '9時',
                                      'T': T, 'h': h, 't1': t1,
                                      'k': num(k), 'h2': h2,
                                      'back': _clock(9 * 60 + T),
                                      'stop': _clock(9 * 60 + t1)},
                                'a': [f'{num(d)} km', f'{mm} 分{ss} 秒間'],
                                '_chk': (d, t, rest),
                            })
    out.sort(key=lambda z: 0 if (z['p']['r'], z['p']['v'], z['p']['T'], z['p']['h'],
                                 z['p']['t1'], z['p']['k'], z['p']['h2']) ==
             (3, 24, 100, 20, 23, '1.5', 8) else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // max(1, limit - 1))
    return head + rest[::step][:limit - 1]


def _clock(mins):
    h, m = divmod(mins, 60)
    return f'{h}時{m}分' if m else f'{h}時'


# ══════════════════════════════════════════════════════════════════
# N5 直角三角形と円（平面図形）
#   (1) 合同な直角三角形2枚 → 斜辺×斜辺÷2
#   (2) 四角形DEGF ＝ HI×HI
#   (3) 半円 − 三角形ODE − 三角形OFG
# ══════════════════════════════════════════════════════════════════
TRIPLES = ((3, 4), (6, 8), (5, 12), (9, 12), (8, 15), (12, 16), (7, 24), (20, 21))


def n5_variants(limit=120):
    out = []
    for p, q in TRIPLES:
        s1 = F(p * p + q * q, 2)
        if (s1 * 10).denominator != 1:
            continue
        for W in (12, 10, 14, 16, 20, 18):
            for c in (2, 4, 6, 8):
                if c >= W:
                    continue
                s3 = F(314, 100) * F(W * W + c * c, 4) - F(W * W - c * c, 2)
                if (s3 * 100).denominator != 1 or s3 <= 0:
                    continue
                out.append({
                    'p': {'p': p, 'q': q, 'm': int((p * p + q * q) ** .5),
                          'W': W, 'c': c, 'pq': f'{p}-{q}'},
                    'a': [f'{num(s1)} cm<sup>2</sup>', f'{W * W} cm<sup>2</sup>',
                          f'{num(s3)} cm<sup>2</sup>'],
                    '_chk': (s1, W * W, s3),
                })
    out.sort(key=lambda v: 0 if (v['p']['p'], v['p']['q'], v['p']['W'],
                                 v['p']['c']) == (3, 4, 12, 2) else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // max(1, limit - 1))
    return head + rest[::step][:limit - 1]


# ══════════════════════════════════════════════════════════════════
# N6 循環小数（数の性質）
# ══════════════════════════════════════════════════════════════════
Q13 = 13


def _cycle_digits(r, q=Q13):
    return set(rep_decimal(F(r, q))[2])


def n6_first_all_ten(q=Q13):
    """小数で表したとき0〜9の10種類すべてが初めて現れる分数（分子を返す）。"""
    best = None
    for r in range(1, q):
        need = set('0123456789') - _cycle_digits(r, q)
        # 整数部にこれらの数字がすべて要る。最小は数字を小さい順に並べたもの
        ds = sorted(need)
        if ds and ds[0] == '0' and len(ds) > 1:
            ds = [ds[1], '0'] + ds[2:]        # 先頭に0は置けない
        w = int(''.join(ds)) if ds else 0
        n = q * w + r
        if best is None or n < best[0]:
            best = (n, w, r)
    return best


def n6_table(hide):
    """分母13の分数の表。hide の4つは ア・イ・ウ・エ にする。"""
    mark = dict(zip(hide, 'アイウエ'))
    cells = []
    for n in range(1, 16):
        f = F(n, Q13)
        body = (f'<b>{mark[n]}</b>' if n in mark
                else (str(n // Q13) if f.denominator == 1 else dec_html(f)))
        # 13/13 を 1/1 に約分して出さない（分母13のまま見せる）
        frac = (f'<span class="fr"><span class="fn">{n}</span>'
                f'<span class="fd">{Q13}</span></span>')
        cells.append(f'<td>{frac}<span class="eq">＝</span>'
                     f'{body}</td>')
    rows = []
    for r in range(5):
        rows.append('<tr>' + cells[r] + cells[r + 5] + cells[r + 10] + '</tr>')
    return '<table class="t13">' + ''.join(rows) + '</table>'


def n6_variants(limit=120):
    first_n, first_w, first_r = n6_first_all_ten()
    out = []
    fin = [F(9, 25), F(7, 20), F(3, 8), F(13, 40), F(11, 16), F(21, 50), F(17, 25)]
    mix = [(1, F(5, 7)), (2, F(3, 7)), (1, F(4, 11)), (3, F(2, 7)), (2, F(7, 11))]
    deep = [(3, F(41, 333)), (2, F(17, 27)), (4, F(23, 37)), (1, F(104, 333)),
            (5, F(11, 27))]
    cells = [(2, 4, 7, 15), (3, 5, 8, 14), (6, 9, 11, 15), (2, 7, 10, 14),
             (4, 6, 9, 12)]
    for i, (f1, (w2, f2), (w3, f3), cl) in enumerate(
            itertools.product(fin, mix, deep, cells)):
        for K, rr in ((2027, 5), (1800, 7), (2100, 3), (1500, 9), (2400, 11)):
            cnt = (K - rr) // Q13 + 1 if rr <= K else 0
            out.append({
                'p': {'f1': improper_html(f1),
                      'f2': frac_html(w2 + f2), 'f3': frac_html(w3 + f3),
                      'K': K, 'r': rr,
                      'rf': frac_html(F(rr, Q13)),
                      'c1': cl[0], 'c2': cl[1], 'c3': cl[2], 'c4': cl[3],
                      'hide': ','.join(str(x) for x in cl),
                      'table': n6_table(cl)},
                'a': [dec_html(f1), dec_html(w2 + f2), dec_html(w3 + f3),
                      dec_html(F(cl[0], Q13)), dec_html(F(cl[1], Q13)),
                      dec_html(F(cl[2], Q13)), dec_html(F(cl[3], Q13)),
                      f'{cnt} 個', frac_html(F(first_n, Q13))],
                '_chk': (f1, w2 + f2, w3 + f3, cl, cnt, first_n),
            })
            break
    out.sort(key=lambda v: 0 if (v['p']['K'], v['p']['r'], v['p']['hide']) ==
             (2027, 5, '2,4,7,15') and v['p']['f1'] ==
             improper_html(F(9, 25)) else 1)
    head, rest = out[:1], out[1:]
    step = max(1, len(rest) // max(1, limit - 1))
    return head + rest[::step][:limit - 1]


# ══════════════════════════════════════════════════════════════════
# 設問マスタ
# ══════════════════════════════════════════════════════════════════
_NATSU = 'N'

GROUPS4 = [
    {
        'key': 'N1', 'round': _NATSU, 'field': 'dens', 'title': '食塩水の入れ替え',
        'vary': True,
        'intro': '濃さ{ca}%の食塩水Aが{wa}g、濃さ{cb}%の食塩水Bが{wb}gあります。'
                 'ただし、食塩水の濃さとは、食塩水の重さに対する食塩の重さの割合の'
                 'ことです。以下の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'nat-1-1', 'label': '(1)',
             'q': 'AとBをすべて混ぜ合わせたら濃さは何%になりますか。',
             'rate': 96, 'score': 3, 'ans': [''],
             'how': '食塩の重さ＝食塩水の重さ×濃さ。'
                    'AとBの食塩を合わせ、全体の重さで割る。'},
            {'id': 'nat-1-2', 'label': '(2)',
             'q': 'A、Bから同じ重さの食塩水をくみ出し、それぞれもう一方の食塩水に'
                  '混ぜたところ、2つの食塩水の濃さが等しくなりました。'
                  '食塩水Aからくみ出した食塩水の重さは何gですか。',
             'rate': 82, 'score': 4, 'ans': [''],
             'how': '2つの濃さが等しくなったということは、'
                    'どちらも(1)で求めた濃さになったということ。'
                    'Aの中身は「もとのAが残った分」と「Bから来た分」の混合と考える。'},
        ],
    },
    {
        'key': 'N2', 'round': _NATSU, 'field': 'numth', 'title': '買った個数を調べる',
        'vary': True, 'intro': '', 'body': '', 'fig': None,
        'subs': [
            {'id': 'nat-2-1', 'label': '',
             'q': '1個{a}円のアメと1個{b}円のガムと1個{c}円のチョコレートを'
                  'それぞれ何個か買ったところ、代金は合計で{T}円でした。このとき、'
                  'アメは何個買いましたか。考えられる個数をすべて求めなさい。ただし、'
                  'アメ、ガム、チョコレートはいずれも1個以上買ったものとします。',
             'rate': 18, 'score': 5, 'ans': [''],
             'how': '3つの値段はどれも1を足すと40の倍数になる。'
                    '代金の式に「買った個数の合計」を足すと、左side が40の倍数になるので、'
                    '合計の個数がしぼれる。そのあとガムとチョコの組を調べる。'},
        ],
    },
    {
        'key': 'N3', 'round': _NATSU, 'field': 'plane', 'title': '6つに分けた直角三角形',
        'vary': True,
        'intro': '直角三角形ABCを図のようにアからカの6つの三角形に分割しました。'
                 '辺ABの長さは{L}cmで、●をつけた辺の長さはすべて等しくなっています。'
                 '以下の問いに答えなさい。',
        'body': '', 'fig': 'tri6:{L}', 'figpos': 'bottom',
        'subs': [
            {'id': 'nat-3-1', 'label': '(1)',
             'q': '三角形アの面積、三角形ウと三角形エの面積の和、三角形カの面積は'
                  'それぞれ何cm<sup>2</sup>ですか。',
             'rate': 93, 'score': 3, 'ans': ['ア', 'ウ＋エ', 'カ'],
             'how': '三角形イが正三角形になることから、角度が次々に決まる。'
                    'アは30°・60°・90°の三角定規の形で、'
                    '一番長い辺と一番短い辺の比が2：1になることを使う。'
                    'ウとエは合わせると直角二等辺三角形になる。'},
            {'id': 'nat-3-2', 'label': '(2)',
             'q': '三角形イと三角形オの面積の比を最も簡単な整数の比で答えなさい。',
             'rate': 77, 'score': 3, 'ans': [''],
             'how': 'イは1辺{L}cmの正三角形。'
                    'オも2つに切り分けると、同じ三角定規2枚分の面積になる。'},
            {'id': 'nat-3-3', 'label': '(3)',
             'q': '直角三角形ABCの面積は、三角形ウの面積の何倍かと三角形エの面積の'
                  '何倍かの和で表すことができます。たとえば、三角形ウの面積の2倍と'
                  '三角形エの面積の5倍との和になっていることを、ウ×2＋エ×5 と表す'
                  'こととします。ウ×□＋エ×□ の式にあてはまる数をそれぞれ答えなさい。'
                  'ただし、2つの□に入る数は同じ数とは限りません。',
             'rate': 7, 'score': 5, 'ans': ['ウ×', '＋エ×'],
             'how': 'イ・オはウとエでどう表せるかを考える。'
                    'ア・カもウとエの何倍かで表せるので、6つをすべて足し合わせる。'},
        ],
    },
    {
        'key': 'N4', 'round': _NATSU, 'field': 'speed', 'title': '流水算とエンジン停止',
        'vary': True,
        'intro': '流れの速さが時速{r}kmである川の下流のA地点と上流のB地点を、'
                 '静水時の速さが時速{v}kmの船で往復します。太郎君は午前{T0}に'
                 'A地点を出発し、B地点に到着後に{h}分休憩して、午前{back}に'
                 'A地点に戻る予定を立てました。予定通りにA地点を出発しましたが、'
                 '午前{stop}に船のエンジンが止まり、川の流れの速さで船が'
                 '戻されてしまいました。戻されている間に急いで修理をし、修理後は、'
                 '船の静水時の速さを{k}倍にして、再びB地点に向かいました。'
                 'B地点に到着後、休憩時間を{h2}分に変えて、船の速さをもとに戻して'
                 'A地点に向かったところ、予定通り午前{back}にA地点に'
                 '戻ることができました。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'nat-4-1', 'label': '(1)',
             'q': 'A地点からB地点までの道のりは何kmですか。',
             'rate': 68, 'score': 4, 'ans': [''],
             'how': '上りは時速（{v}−{r}）km、下りは時速（{v}＋{r}）km。'
                    '休憩をのぞいた走っている時間が往復ぶんの時間になる。'},
            {'id': 'nat-4-2', 'label': '(2)',
             'q': '船のエンジンが止まっていた時間は何分何秒間ですか。',
             'rate': 18, 'score': 5, 'ans': [''],
             'how': '止まっている間は時速{r}kmで下流へ戻される。'
                    '「止まっていた時間」を□分として、'
                    '出発から帰着までの時間をぜんぶ足した式をつくる。'},
        ],
    },
    {
        'key': 'N5', 'round': _NATSU, 'field': 'plane', 'title': '直角三角形と円',
        'vary': True, 'intro': '次の問いに答えなさい。', 'body': '', 'fig': None,
        'subs': [
            {'id': 'nat-5-1', 'label': '(1)',
             'q': '右の図1は、3つの辺の長さが{p}cm、{q}cm、{m}cmの合同'
                  '（形も大きさも同じ）な2つの直角三角形が一直線上に点Bで'
                  'ぴったりくっついてできた図です。このとき、三角形ABCの面積は'
                  '何cm<sup>2</sup>ですか。',
             'rate': 94, 'score': 3, 'ans': [''],
             'fig': 'tri345:{pq}', 'figpos': 'right',
             'how': '2つの直角三角形が合同なので、角ABCは直角になる。'
                    'ABもBCも{m}cmだから、直角をはさむ2辺が{m}cmの三角形。'},
            {'id': 'nat-5-2', 'label': '(2)',
             'q': '下の図2は、PQを直径とする円です。OはPQのまん中の点で、'
                  '点D、E、F、Gは円周上にあります。'
                  '点D、E、G、Fを直線で結んでできる四角形の面積は何cm<sup>2</sup>ですか。',
             'rate': 69, 'score': 4, 'ans': [''],
             'fig': 'circ:{W}', 'figpos': 'bottom',
             'how': '四角形DEGFは、DEとFGが平行な台形。'
                    '2本の点線が垂直に交わることから、DH＝OI、FI＝OH が導ける。'
                    '上底と下底の和がHIと同じ長さになる。'},
            {'id': 'nat-5-3', 'label': '(3)',
             'q': 'PHの長さがQIの長さより{c}cm長いとき、斜線部分の面積は'
                  '何cm<sup>2</sup>ですか。円周率は3.14とします。',
             'rate': 9, 'score': 5, 'ans': [''],
             'how': '2つの斜線部分のおうぎ形を合わせると、ちょうど半円になる。'
                    '半円から三角形ODEと三角形OFGをひけばよい。'
                    '半径×半径は、正方形をつくる考え方で出せる。'},
        ],
    },
    {
        'key': 'N6', 'round': _NATSU, 'field': 'numth', 'title': '循環小数',
        'vary': True,
        'intro': '<span class="fr"><span class="fn">1</span><span class="fd">9</span></span>'
                 '＝0.111111…、'
                 '<span class="fr"><span class="fn">7</span><span class="fd">11</span></span>'
                 '＝0.63636363…、'
                 '6<span class="fr"><span class="fn">152</span><span class="fd">303</span></span>'
                 '＝6.501650165016… のように、小数点以下のある桁から先で同じ数字の列が'
                 '無限に繰り返される小数を「循環小数」と呼び、繰り返される数字の列を'
                 '「循環節」と呼びます。また、循環小数を表すときは、'
                 '0.111111…＝0.<span class="dt">1</span>、'
                 '0.63636363…＝0.<span class="dt">6</span><span class="dt">3</span>、'
                 '6.501650165016…＝6.<span class="dt">5</span>01'
                 '<span class="dt">6</span> というように、小数点以下の循環節の'
                 '始まりの数字と終わりの数字（1桁の数が繰り返される場合はその数だけ）の'
                 '上に「・」をつけて表します。以下の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'nat-6-1', 'label': '(1)',
             'q': '次の分数を小数で表しなさい。答えが循環小数になる場合は、'
                  '上の表し方にならって答えなさい。'
                  '<div class="formula">① {f1}　　② {f2}　　③ {f3}</div>',
             'rate': 73, 'score': 3, 'ans': ['①', '②', '③'],
             'how': '分母が 2 と 5 だけでできている分数は、わり切れる小数になる。'
                    'そうでなければ、わり算のあまりがくり返すところを探す。'},
            {'id': 'nat-6-2', 'label': '(2)',
             'q': '分母が13で、分子が1以上の整数である分数を小さい順に並べた列を'
                  '考えます。下の表は、整数になるものは整数で、それ以外は循環小数で'
                  '前から15番目までを表したものです。'
                  '表のア、イ、ウ、エにあてはまる数をそれぞれ答えなさい。'
                  '{table}',
             'rate': 71, 'score': 4, 'ans': ['ア', 'イ', 'ウ', 'エ'],
             'how': '13分の1の循環節 076923 をずらすと出てくるものと、'
                    '13分の2の循環節 153846 をずらすと出てくるものの2種類しかない。'},
        ],
    },
    {
        'key': 'N6a', 'round': _NATSU, 'field': 'numth', 'title': '分母13の分数の列', 'vary': True,
        'intro': '循環小数は、小数点以下の循環節の始まりの数字と終わりの数字'
                 '（1桁の数が繰り返される場合はその数だけ）の上に「・」をつけて、'
                 '0.111111…＝0.<span class="dt">1</span>、'
                 '0.63636363…＝0.<span class="dt">6</span><span class="dt">3</span> '
                 'のように表します。'
                 '分母が13で、分子が1以上の整数である分数を小さい順に並べた次の列を'
                 '考えます。'
                 '<div class="tbl wrap"><span class="fr"><span class="fn">1</span>'
                 '<span class="fd">13</span></span>、'
                 '<span class="fr"><span class="fn">2</span><span class="fd">13</span></span>、'
                 '<span class="fr"><span class="fn">3</span><span class="fd">13</span></span>、'
                 '<span class="fr"><span class="fn">4</span><span class="fd">13</span></span>、'
                 '<span class="fr"><span class="fn">5</span><span class="fd">13</span></span>、'
                 '…</div>'
                 'これらの分数のうち、整数になるもの以外を小数で表すと、すべて循環小数と'
                 'なります。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'nat-6-3', 'label': '(1)',
             'q': '前から数えて{K}番目までの分数で、小数で表したときに{rf}と'
                  '小数点以下が同じになる分数は、{rf}を含めて全部で何個ありますか。',
             'rate': 58, 'score': 4, 'ans': [''],
             'how': '小数点以下が同じ＝13で割ったあまりが同じ。'
                    '{r}、{r}＋13、{r}＋26、… と13ずつ増える。'},
            {'id': 'nat-6-4', 'label': '(2)',
             'q': '<span class="fr"><span class="fn">1</span><span class="fd">13</span></span>'
                  'を小数で表すと0、2、3、6、7、9の6種類の数字が現れます。同様に、'
                  '<span class="fr"><span class="fn">8</span><span class="fd">13</span></span>'
                  'は0、1、3、4、5、6、8の7種類の数字が、'
                  '1<span class="fr"><span class="fn">1</span><span class="fd">13</span></span>'
                  'は0、1、2、3、6、7、9の7種類の数字が現れます。'
                  '小数で表したときに0から9までの10種類の数字すべてが初めて現れる分数を'
                  '帯分数で答えなさい。',
             'rate': 15, 'score': 5, 'ans': [''],
             'how': '循環節は2種類しかないので、足りない数字は整数部分で補うしかない。'
                    '足りない4つの数字をいちばん小さく並べた整数が、整数部分になる。'},
        ],
    },
]

def n6_head_variants(limit=120):
    """(1)(2)：循環小数になおす"""
    out = []
    for v in n6_variants(limit):
        out.append({'p': {k: v['p'][k] for k in ('f1', 'f2', 'f3', 'table', 'hide')},
                    'a': v['a'][0:7], '_chk': v['_chk'][:4]})
    return out


def n6a_variants(limit=120):
    """(3)(4)：分母13の分数の列を調べる"""
    out = []
    for v in n6_variants(limit):
        out.append({'p': {k: v['p'][k] for k in ('K', 'r', 'rf')},
                    'a': v['a'][7:9],
                    '_chk': (v['_chk'][4], v['_chk'][5])})
    return out


VARIANTS4 = {'N1': n1_variants, 'N2': n2_variants, 'N3': n3_variants,
             'N4': n4_variants, 'N5': n5_variants,
             'N6': n6_head_variants, 'N6a': n6a_variants}

# 計算欄の高さ（mm）。元の問題用紙の実測値。0 は「計算欄なし（答だけ）」。
WORK_MM4 = {
    'nat-1-1': 24, 'nat-1-2': 55,
    'nat-2-1': 100,
    'nat-3-1': 32, 'nat-3-2': 0, 'nat-3-3': 70,   # (3)の元は図こみで98mm
    'nat-4-1': 105, 'nat-4-2': 86,
    'nat-5-1': 27, 'nat-5-2': 26, 'nat-5-3': 62,
    'nat-6-1': 54, 'nat-6-2': 0,
    'nat-6-3': 44, 'nat-6-4': 119,
}


if __name__ == '__main__':
    for k, fn in VARIANTS4.items():
        vs = fn()
        print(f'{k}: {len(vs):4}通り　例 {vs[0]["a"]}')
