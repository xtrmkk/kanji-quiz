# -*- coding: utf-8 -*-
"""NNOPランダムテスト：設問マスタと、採用可能なパラメータの全列挙。

設計は nnop_spec.md（第3版）に従う。
**計算はすべてここ（ビルド時のPython）で終わらせる。**
ブラウザ側は、ここが出したパラメータと解答を文字として差し込むだけで、
いっさい計算しない。JS側に計算バグが入り込む余地をなくすため。

  python3 tools/nnop_data.py      … 自己検証を走らせる
"""
from fractions import Fraction as F
from math import gcd

# ── 分野 ──────────────────────────────────────────────────────────
FIELDS = [
    ('speed', '速さ'),
    ('plane', '平面図形'),
    ('case',  '場合の数'),
    ('dens',  '濃度'),
    ('rule',  '規則性'),
    ('unit',  '単位換算'),
    ('numth', '数の性質'),
]


# ── 表示のための小道具 ────────────────────────────────────────────
def frac_html(f: F) -> str:
    """分数をHTMLにする。帯分数にできるものは帯分数で。"""
    if f.denominator == 1:
        return str(f.numerator)
    whole, rem = divmod(f.numerator, f.denominator)
    body = f'<span class="fr"><span class="fn">{rem}</span><span class="fd">{f.denominator}</span></span>'
    return (f'{whole}{body}' if whole else body)


def improper_html(f: F) -> str:
    """仮分数のまま表示する（帯分数にしない）。"""
    return f'<span class="fr"><span class="fn">{f.numerator}</span><span class="fd">{f.denominator}</span></span>'


def num(x: F) -> str:
    """小数（整数なら整数、割り切れる小数はそのまま）。"""
    if x.denominator == 1:
        return str(x.numerator)
    v = float(x)
    s = f'{v:.10f}'.rstrip('0').rstrip('.')
    return s


def ratio_of(a: F, b: F):
    m = a.denominator * b.denominator // gcd(a.denominator, b.denominator)
    i1, i2 = int(a * m), int(b * m)
    g = gcd(i1, i2)
    return i1 // g, i2 // g


# ══════════════════════════════════════════════════════════════════
# G1 時間の単位換算（変える）
# ══════════════════════════════════════════════════════════════════
def g1_variants():
    out = []
    for D in (3, 4, 5, 6, 10, 12, 15, 20, 30):
        for N in range(100, 3000):
            if gcd(N, D) != 1:
                continue
            total_sec = N * 60 // D
            if N * 60 % D:
                continue
            if not (3600 <= total_sec <= 6 * 3600):      # 1〜6時間
                continue
            h, rem = divmod(total_sec, 3600)
            m, s = divmod(rem, 60)
            if s == 0 or m == 0:                         # 3つとも埋まる問題にする
                continue
            out.append({'p': {'N': N, 'D': D},
                        'a': [str(h), str(m), str(s)]})
    # 元の問題（2027/12分）を先頭に置く
    out.sort(key=lambda v: 0 if (v['p']['N'], v['p']['D']) == (2027, 12) else 1)
    return out[:150]


# ══════════════════════════════════════════════════════════════════
# G2 おうぎ形・円（半径6固定、角だけ変える）
# ══════════════════════════════════════════════════════════════════
G2_ANGLES = (20, 10, 25, 30, 15)      # 20°（元の問題）を先頭に。15°は紛らわしいので最後


def g2_variants():
    out = []
    r = 6
    for a in G2_ANGLES:
        assert (r * r * (90 - 2 * a)) % 180 == 0, (r, a)
        s1 = F(314, 100) * r * r * F(90 - 2 * a, 360)
        s2 = F(314, 100) * r * r * F(a, 90)
        assert s1.denominator in (1, 2, 4, 5, 10, 20, 25, 50, 100), s1
        out.append({'p': {'r': r, 'a': a}, 'a': [num(s1), num(s2)]})
    return out


# ══════════════════════════════════════════════════════════════════
# G3 食塩水（変える）
# ══════════════════════════════════════════════════════════════════
def _nice(x: F) -> bool:
    return (x / F(1, 2)).denominator == 1


def g3_all():
    out = []
    for u in range(1, 31):                       # p = u/2 → 0.5〜15%
        for v in range(1, 31):
            for w in range(1, 31):
                p, q, r = F(u, 2), F(v, 2), F(w, 2)
                if len({p, q, r}) < 3:
                    continue
                c1, c2, c3 = (p + 2 * q) / 3, (q + 2 * r) / 3, (r + 2 * p) / 3
                if not all(_nice(x) for x in (c1, c2, c3)):
                    continue
                if c1 == c2 == c3:
                    continue
                a1, a2 = (p + q + r) / 3, (2 * p + q) / 3
                if not (_nice(a1) and _nice(a2)):
                    continue
                out.append((p, q, r, c1, c2, c3, a1, a2))
    return out


def g3_variants(limit=150):
    allc = g3_all()
    orig = (F(5), F(2), F(13, 2))
    picked = [t for t in allc if (t[0], t[1], t[2]) == orig]
    rest = [t for t in allc if (t[0], t[1], t[2]) != orig]
    step = max(1, len(rest) // (limit - 1))
    picked += rest[::step][:limit - 1]
    out = []
    for p, q, r, c1, c2, c3, a1, a2 in picked:
        out.append({'p': {'c1': num(c1), 'c2': num(c2), 'c3': num(c3)},
                    'a': [num(a1) + '%', num(a2) + '%', num(q) + '%'],
                    '_pqr': (num(p), num(q), num(r))})
    return out


# ══════════════════════════════════════════════════════════════════
# G4 速さ（変える）
# ══════════════════════════════════════════════════════════════════
def g4_all():
    V = list(range(40, 201, 10))
    out = []
    for v1 in V:
        for v2 in V:
            if v1 <= v2:
                continue
            for v3 in V:
                if not (v2 < v3 < v1):
                    continue
                if v1 * (v3 - v2) <= 2 * v2 * v2:          # C > 0
                    continue
                for k in (2, 3, 4):
                    if k * v2 <= v3:                        # 次朗が先に着く
                        continue
                    cd = F(v1 * (v3 - v2) - 2 * v2 * v2, (v1 + v2) * (v3 - v2))
                    coef = cd * (F(1, v3) - F(1, k * v2))
                    for T in range(30, 181, 10):
                        D = F(T, 60) / coef
                        if D.denominator != 1:
                            continue
                        D = int(D)
                        if D % 10 or not (800 <= D <= 6000):
                            continue
                        HP, PS, C = F(v1 * D, v1 + v2), F(v2 * D, v1 + v2), cd * D
                        if any(x.denominator != 1 for x in (HP, PS, C)):
                            continue
                        r1 = ratio_of(F(v1), F(v2))
                        r2 = ratio_of(HP - C, PS)
                        if max(r1 + r2) > 20:
                            continue
                        if r2 == (1, 1):       # (2)が1:1だと答えが見え見えになる
                            continue
                        out.append((v1, v2, v3, k, T, D, r1, r2, int(HP), int(C)))
    return out


def g4_variants(limit=150):
    allc = g4_all()
    orig = (160, 60, 140, 3, 80, 2640)
    picked = [t for t in allc if t[:6] == orig]
    rest = [t for t in allc if t[:6] != orig]
    step = max(1, len(rest) // (limit - 1))
    picked += rest[::step][:limit - 1]
    out = []
    for v1, v2, v3, k, T, D, r1, r2, HP, C in picked:
        out.append({'p': {'v1': v1, 'v2': v2, 'v3': v3, 'k': k, 'T': T},
                    'a': [f'{r1[0]} : {r1[1]}', f'{r2[0]} : {r2[1]}', f'{D} m'],
                    '_chk': {'D': D, 'HP': HP, 'C': C}})
    return out


# ══════════════════════════════════════════════════════════════════
# G5 正八角形とサイコロ（固定）
# ══════════════════════════════════════════════════════════════════
N_POLY, M_DICE = 8, 6


def g5_solve(n=N_POLY, m=M_DICE):
    def d(x, y):
        t = abs(x - y) % n
        return min(t, n - t)
    c = [0, 0, 0]
    for u in range(1, m + 1):
        for v in range(1, m + 1):
            P, Q = u % n, (-v) % n
            if P == 0 or Q == 0 or P == Q:          # 三角形にならない
                c[0] += 1
                continue
            s1, s2, s3 = d(0, P), d(0, Q), d(P, Q)
            if s1 == s2:
                c[1] += 1
            if s1 == s2 or s1 == s3 or s2 == s3:
                c[2] += 1
    return c


def g5_variants():
    c = g5_solve()
    return [{'p': {'n': N_POLY}, 'a': [f'{c[0]} 通り', f'{c[1]} 通り', f'{c[2]} 通り']}]


# ══════════════════════════════════════════════════════════════════
# G6 規則性 前半  ア(n) = 1/(n(n+1))
# ══════════════════════════════════════════════════════════════════
def g6_variants(limit=120):
    out = []
    for N in range(15, 41):
        for (P2, Q2) in ((12, 55), (10, 40), (15, 60), (20, 50), (11, 44)):
            a1 = F(1, N * (N + 1))
            cnt = Q2 - P2 + 1
            a2 = cnt - (F(1, P2) - F(1, Q2 + 1))
            out.append({'p': {'N': N, 'P2': P2, 'Q2': Q2},
                        'a': [frac_html(a1) + ' cm<sup>2</sup>',
                              frac_html(a2) + ' cm<sup>2</sup>'],
                        '_chk': (a1, a2)})
    # 元の問題（25番目／12〜55番目）を先頭へ
    out.sort(key=lambda v: 0 if (v['p']['N'], v['p']['P2'], v['p']['Q2']) == (25, 12, 55) else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# G6a 規則性 後半  ウ(n) = 1/((2n-1)(2n+1))
# ══════════════════════════════════════════════════════════════════
def g6a_unique(P, Q):
    k = Q - P + 1
    M = (2 * P - 1) * (2 * Q + 1)
    if k < 2 or k >= M:
        return False
    S = F(k * (M - 1), M)
    kk = S.numerator // S.denominator + 1
    if kk != k:
        return False
    AB = k / (k - S)
    if AB.denominator != 1 or AB.numerator != M:
        return False
    hit = []
    for A in range(1, int(M ** 0.5) + 1):
        if M % A == 0 and M // A - A == 2 * k:
            hit.append(((A + 1) // 2, (M // A - 1) // 2))
    return hit == [(P, Q)]


def g6a_variants(limit=120):
    out = []
    for P3, Q3 in ((3, 10), (2, 9), (4, 12), (3, 8), (5, 14)):
        wa = (F(1, 2 * P3 - 1) - F(1, 2 * Q3 + 1)) / 2
        cnt3 = Q3 - P3 + 1
        ea = cnt3 - wa
        for P4 in range(3, 13):
            for Q4 in range(P4 + 1, 26):
                if (P3, Q3) == (P4, Q4):
                    continue
                if not g6a_unique(P4, Q4):
                    continue
                k = Q4 - P4 + 1
                M = (2 * P4 - 1) * (2 * Q4 + 1)
                S = F(k * (M - 1), M)
                if len(str(S.numerator)) > 4:
                    continue
                out.append({'p': {'P3': P3, 'Q3': Q3, 'S': improper_html(S)},
                            'a': [frac_html(wa) + ' cm<sup>2</sup>',
                                  frac_html(ea) + ' cm<sup>2</sup>',
                                  f'{k} 個',
                                  f'P = {P4}、Q = {Q4}'],
                            '_chk': (wa, ea, k, P4, Q4, S)})
    # 元の問題（3〜10番目／P=7,Q=15）を先頭へ
    out.sort(key=lambda v: 0 if (v['p']['P3'], v['p']['Q3']) == (3, 10)
             and v['a'][3] == 'P = 7、Q = 15' else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# 大問マスタ（問題文のひな形。{…} はパラメータで差し替える）
# ══════════════════════════════════════════════════════════════════
BOX = '<span class="bx">{}</span>'

GROUPS = [
    {
        'key': 'G1', 'round': 1, 'field': 'unit', 'title': '時間の単位換算', 'vary': True,
        'intro': '次のア〜ウの□にあてはまる数をそれぞれ答えなさい。'
                 'ただし、アとイにはできるだけ大きい整数が入るものとします。',
        'body': '<div class="formula"><span class="fr"><span class="fn">{N}</span>'
                '<span class="fd">{D}</span></span> 分 ＝ ' + BOX.format('ア') + ' 時間 '
                + BOX.format('イ') + ' 分 ' + BOX.format('ウ') + ' 秒</div>',
        'fig': None,
        'subs': [{'id': 'op1-1', 'label': '', 'q': '', 'rate': 85, 'score': 4,
                  'ans': ['ア', 'イ', 'ウ'],
                  'how': '帯分数に直すのが速い。{N}÷{D} を「商とあまり」にして、'
                         '商を60で割ると時間と分、残ったあまりの分数に60をかけると秒になる。'}],
    },
    {
        'key': 'G2', 'round': 1, 'field': 'plane', 'title': 'おうぎ形と円の求積', 'vary': True,
        'intro': '', 'body': '', 'fig': None,
        'subs': [
            {'id': 'op1-2-1', 'label': '(1)',
             'q': '右の図は、半径{r}cm、中心角が90°のおうぎ形に直線を4本引いたものです。'
                  '●の角度がともに{a}°のとき、色のついた部分の面積は何cm<sup>2</sup>ですか。',
             'rate': 86, 'score': 3, 'ans': [''], 'fig': 'ogi', 'figpos': 'right',
             'how': '2つの直角三角形の面積が等しいので差し引きゼロ。'
                    '色のついた部分は中心角 90−{a}×2 のおうぎ形に置きかえられる。'},
            {'id': 'op1-2-2', 'label': '(2)',
             'q': '右の図は、半径{r}cmの円に直線を8本引いたものです。'
                  '○の角度がともに{a}°のとき、色のついた部分の面積は何cm<sup>2</sup>ですか。',
             'rate': 58, 'score': 4, 'ans': [''], 'fig': 'circle', 'figpos': 'right',
             'how': '円の中に(1)と同じ図形がちょうど4つある。'
                    '残りを横の直径で二等分したものが色のついた部分。'},
        ],
    },
    {
        'key': 'G3', 'round': 1, 'field': 'dens', 'title': '食塩水', 'vary': True,
        'intro': '3種類の食塩水P、Q、Rがあります。P100gとQ200gを混ぜると濃さが{c1}%になり、'
                 'Q100gとR200gを混ぜると濃さが{c2}%になり、R100gとP200gを混ぜると濃さが{c3}%に'
                 'なります。ただし、濃さとは、食塩水の重さに対する食塩の重さの割合のことです。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op1-3-1', 'label': '(1)',
             'q': '食塩水P、Q、Rを100gずつ混ぜると、濃さは何%になりますか。',
             'rate': 72, 'score': 3, 'ans': [''],
             'how': '3つの混ぜ方をぜんぶ合わせると、P・Q・Rが同じ重さずつになる。1組分にもどす。'},
            {'id': 'op1-3-2', 'label': '(2)',
             'q': '食塩水P200gとQ100gを混ぜると、濃さは何%になりますか。',
             'rate': 29, 'score': 4, 'ans': [''],
             'how': '(1)の食塩水を2組分用意し、そこから「Q100g＋R200g」にふくまれる食塩を'
                    '差し引くと、P200g＋Q100gの食塩が出る。'},
            {'id': 'op1-3-3', 'label': '(3)',
             'q': '食塩水Qの濃さは何%ですか。',
             'rate': 22, 'score': 4, 'ans': [''],
             'how': '(2)でP200g＋Q100gが分かった。問題文のP100g＋Q200gと見くらべて、'
                    '足し引きでQだけを取り出す。'},
        ],
    },
    {
        'key': 'G4', 'round': 1, 'field': 'speed', 'title': '速さ', 'vary': True,
        'intro': '家から駅までまっすぐな道があります。太朗君が家から分速{v1}mで駅に向かって'
                 '出発しました。次朗君は駅から家に向かって分速{v2}mで太朗君と同時に出発しました。'
                 '太朗君と次朗君は途中の郵便局の前ですれ違い、太朗君はそこから進む速さを'
                 '分速{v3}mに変え、駅に着くと速さを変えずに家に向かって進みました。'
                 '次朗君は途中で太朗君に追いつかれ、そこから進む速さを{k}倍に変え、'
                 '太朗君よりも{T}秒早く家に着きました。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op1-4-1', 'label': '(1)',
             'q': '家から郵便局までと、郵便局から駅までの道のりの比を、'
                  'もっとも簡単な整数の比で答えなさい。',
             'rate': 88, 'score': 3, 'ans': [''],
             'how': '同じ時間に進んだのだから、道のりの比は速さの比と同じ。'},
            {'id': 'op1-4-2', 'label': '(2)',
             'q': '次朗君が太朗君に追いつかれた地点から郵便局までと、郵便局から駅までの'
                  '道のりの比を、もっとも簡単な整数の比で答えなさい。',
             'rate': 25, 'score': 3, 'ans': [''],
             'how': 'すれ違ってから追いつくまでに、太朗君は「郵便局〜駅の往復＋追いついた地点まで」、'
                    '次朗君は「追いついた地点まで」だけ進む。その道のりの比は速さの比。'
                    '差にあたる分が往復2つ分になる。'},
            {'id': 'op1-4-3', 'label': '(3)',
             'q': '家から駅までの道のりは何mですか。',
             'rate': 13, 'score': 4, 'ans': [''],
             'how': '追いついた地点から家までは、2人とも同じ道のり。'
                    'かかる時間の比は速さの逆比になるので、その差が{T}秒にあたる。'},
        ],
    },
    {
        'key': 'G5', 'round': 1, 'field': 'case', 'title': '正八角形とサイコロ', 'vary': False,
        'intro': '右の図のような正八角形があります。2つの点P、Qは、はじめ頂点Aにあります。'
                 '大小2つのサイコロを同時に1回振り、大きいサイコロの出た目と同じ数だけ点Pを'
                 '反時計回りに、小さいサイコロの出た目と同じ数だけ点Qを時計回りに、'
                 'となりの頂点に動かします。このとき、頂点Aと点P、点Qを結んでできる図形を'
                 '図形Xとします。<br>例えば、大きいサイコロの出た目が4、小さいサイコロの出た目が'
                 '1のとき、点Pは頂点Eに動き、点Qは頂点Hに動き、図形Xは（直角）三角形になります。',
        'body': '', 'fig': 'octagon', 'figpos': 'right',
        'subs': [
            {'id': 'op1-5-1', 'label': '(1)',
             'q': '図形Xが三角形にならないような目の出方は全部で何通りありますか。',
             'rate': 64, 'score': 3, 'ans': [''],
             'how': '三角形にならないのは、点Pと点Qが重なるとき。'
                    '大きい目と小さい目の和が8になる場合を数える。'},
            {'id': 'op1-5-2', 'label': '(2)',
             'q': '図形Xが、辺APと辺AQが等しい二等辺三角形になるような目の出方は'
                  '全部で何通りありますか。',
             'rate': 53, 'score': 4, 'ans': [''],
             'how': 'APとAQが等しいのは、大きい目と小さい目が同じとき。'
                    'ただし(1)で三角形にならない場合は除く。'},
            {'id': 'op1-5-3', 'label': '(3)',
             'q': '図形Xが二等辺三角形になるような目の出方は、(2)の場合を含めて'
                  '全部で何通りありますか。',
             'rate': 5, 'score': 5, 'ans': [''],
             'how': '(2)はAP＝AQ。残りはAP＝PQ、AQ＝PQ の場合。'
                    '辺の長さは「頂点どうしのへだたり（少ない方の回り方）」が同じかどうかで決まる。'},
        ],
    },
    {
        'key': 'G6', 'round': 1, 'field': 'rule', 'title': '正三角形の分割（前半）', 'vary': True,
        'intro': '面積が1cm<sup>2</sup>の正三角形の紙がたくさんあります。'
                 '1番目の正三角形の紙から順に、太線の2辺をあるきまりにしたがって等しく分けた点（●）'
                 'のうち、○の頂点に近い方の点どうしを結んだ直線で2つに切り分けます。'
                 '切り分けた2枚のうち、面積の小さい方をア、面積の大きい方をイと表すことにします。'
                 'ただし、1番目のみアの面積とイの面積は等しいです。',
        'body': '', 'fig': 'tri_front', 'figpos': 'bottom',
        'subs': [
            {'id': 'op1-6-1', 'label': '(1)',
             'q': '{N}番目のアの面積は何cm<sup>2</sup>ですか。',
             'rate': 66, 'score': 2, 'ans': [''],
             'how': '2番目は 1/2×1/3、3番目は 1/3×1/4。n番目は 1/n×1/(n+1) になっている。'},
            {'id': 'op1-6-2', 'label': '(2)',
             'q': '{P2}番目から{Q2}番目までのイの面積の和は何cm<sup>2</sup>ですか。',
             'rate': 14, 'score': 2, 'ans': [''],
             'how': 'イ＝1−ア。まず「1」を個数分だけ足し、そこからアの和を引く。'
                    'アは 1/n − 1/(n+1) の形に分けられるので、並べると途中が打ち消し合う。'},
        ],
    },
    {
        'key': 'G6a', 'round': 1, 'field': 'rule', 'title': '正三角形の分割（後半）', 'vary': True,
        'intro': '面積が1cm<sup>2</sup>の正三角形の紙がたくさんあります。'
                 '1番目の正三角形の紙から順に、太線の2辺をあるきまりにしたがって等しく分けた点（●）'
                 'のうち、○の頂点に近い方の点どうしを結んだ直線で2つに切り分けます。'
                 '切り分けた2枚のうち、面積の小さい方をウ、面積の大きい方をエと表すことにします。',
        'body': '', 'fig': 'tri_back', 'figpos': 'bottom',
        'subs': [
            {'id': 'op1-6-3', 'label': '(1)',
             'q': '{P3}番目から{Q3}番目までのウの面積の和と、エの面積の和は'
                  'それぞれ何cm<sup>2</sup>ですか。',
             'rate': 15, 'score': 3, 'ans': ['ウ', 'エ'],
             'how': '1番目は 1/1×1/3、2番目は 1/3×1/5、3番目は 1/5×1/7。'
                    'ウは「差の半分」の形に分けられるので、並べると途中が打ち消し合う。'
                    'エ＝1−ウ。'},
            {'id': 'op1-6-4-1', 'label': '(2)①',
             'q': 'P番目からQ番目までの連続したいくつかのエの面積の和を仮分数で表すと '
                  '{S} cm<sup>2</sup> になりました。全部で何個のエを加えましたか。',
             'rate': 13, 'score': 4, 'ans': [''],
             'how': 'エは1より少しだけ小さい。だから和は「個数より少しだけ小さい数」になる。'
                    '仮分数を整数部分で見れば、個数は整数部分より1つ大きい。'},
            {'id': 'op1-6-4-2', 'label': '(2)②',
             'q': 'P、Qにあてはまる整数をそれぞれ答えなさい。',
             'rate': 4, 'score': 5, 'ans': [''],
             'how': '（個数）−（和）＝（個数）÷（分母にあたる積）なので、積が分かる。'
                    'その積を2つの奇数のかけ算に分け、差が（個数）の2倍になる組を探す。'},
        ],
    },
]

VARIANTS = {
    'G1': g1_variants, 'G2': g2_variants, 'G3': g3_variants, 'G4': g4_variants,
    'G5': g5_variants, 'G6': g6_variants, 'G6a': g6a_variants,
}


# ── 計算欄の高さ（mm・A3のとき）──────────────────────────────────
# 元の問題用紙は各小問に計算欄（枠）があり、その下に解答の枠がある。
# 手が動く量に合わせて小問ごとに決める。
WORK_MM = {
    'op1-1': 26,
    'op1-2-1': 30, 'op1-2-2': 32,
    'op1-3-1': 30, 'op1-3-2': 36, 'op1-3-3': 26,
    'op1-4-1': 26, 'op1-4-2': 40, 'op1-4-3': 40,
    'op1-5-1': 30, 'op1-5-2': 30, 'op1-5-3': 42,
    'op1-6-1': 26, 'op1-6-2': 34,
    'op1-6-3': 34, 'op1-6-4-1': 30, 'op1-6-4-2': 34,
}
