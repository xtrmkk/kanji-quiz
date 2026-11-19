# -*- coding: utf-8 -*-
"""予想②（麻布中予想テスト②）・算数の設問マスタと、採用可能なパラメータの全列挙。

第1〜5回・予想①と同じ方針（nnop_spec.md）。
**計算はすべてここ（ビルド時のPython）で終わらせる。**
ブラウザ側は、ここが出したパラメータと解答を文字として差し込むだけ。

  python3 tools/nnop8_data.py   … 各大問が何通り作れるか表示する

大問2だけは数値を振らない（'vary': False）。正六角形の面積が二等辺三角形の
**整数倍**になるのは「正六角形・頂角120°」の組だけで、角や多角形を変えると
(1)の答えが無理数になり、図3のしきつめも成り立たなくなるため
（くわしくは tools/nnop8_notes.md）。
"""
import itertools
from collections import Counter
from fractions import Fraction as F
from math import gcd

from nnop_data import frac_html, improper_html, num, ratio_of   # 表示の小道具は共用


def _kg(g: int) -> str:
    """グラムを kg の表示にする（1000 → 1、1800 → 1.8）。"""
    return num(F(g, 1000))


def _solve2(a1, b1, c1, a2, b2, c2):
    """a1x+b1y=c1, a2x+b2y=c2 を解く（分数のまま）。解けなければ None。"""
    det = a1 * b2 - a2 * b1
    if det == 0:
        return None
    return F(c1 * b2 - c2 * b1, det), F(a1 * c2 - a2 * c1, det)


# ══════════════════════════════════════════════════════════════════
# T1 2種類の製品と2種類の材料（消去算）
#   製品A1個に 材料C cA g・材料D dA g、製品B1個に cB g・dB g。
#   はじめにある材料は C0 g と D0 g。
#   (1) 製品Aだけ作る  (2) ちょうど使い切る個数  (3) 材料を p:q で足して u:v で作る
# ══════════════════════════════════════════════════════════════════
def t1_variants(limit=120):
    """T1：1個あたりの材料・はじめの量・追加の比・作る比を振る。"""
    out = []
    for cA, cB in ((10, 20), (10, 15), (15, 25), (20, 30), (10, 25), (15, 20)):
        for dA, dB in ((15, 10), (20, 10), (25, 15), (30, 20), (20, 5), (25, 10)):
            if (cA - cB) * (dA - dB) >= 0:      # たすきがけになる組だけ
                continue
            if cA * dB - cB * dA == 0:
                continue
            for C0 in range(600, 2600, 100):
                for D0 in range(600, 2600, 100):
                    # (1) 製品Aだけをできるだけ多く作る
                    n1 = min(C0 // cA, D0 // dA)
                    rc, rd = C0 - cA * n1, D0 - dA * n1
                    if (rc == 0) == (rd == 0):          # 片方だけが余る組にかぎる
                        continue
                    if (rc or rd) % 100:                # 余りは100gの倍数
                        continue
                    if not 20 <= n1 <= 200:
                        continue
                    # (2) ちょうど使い切る
                    s = _solve2(cA, cB, C0, dA, dB, D0)
                    if s is None:
                        continue
                    a2, b2 = s
                    if a2.denominator != 1 or b2.denominator != 1:
                        continue
                    a2, b2 = int(a2), int(b2)
                    if not (5 <= a2 <= 200 and 5 <= b2 <= 200):
                        continue
                    for p, q in ((9, 7), (5, 4), (7, 5), (4, 3), (6, 5), (3, 2)):
                        for u, v in ((3, 2), (2, 1), (4, 3), (5, 3), (5, 2)):
                            # (材料Cの式) (cA u + cB v)k = C0 + p x
                            # (材料Dの式) (dA u + dB v)k = D0 + q x
                            s2 = _solve2(cA * u + cB * v, -p, C0,
                                         dA * u + dB * v, -q, D0)
                            if s2 is None:
                                continue
                            k, x = s2
                            if k <= 0 or x <= 0 or k.denominator != 1:
                                continue
                            addC, addD = p * x, q * x
                            if addC % 100 or addD % 100:        # 追加は0.1kg単位
                                continue
                            if not (500 <= addC <= 4000 and 500 <= addD <= 4000):
                                continue
                            if u * k > 400 or v * k > 400:
                                continue
                            mat = 'C' if rc else 'D'
                            out.append({
                                'p': {'cA': cA, 'cB': cB, 'dA': dA, 'dB': dB,
                                      'C0': _kg(C0), 'D0': _kg(D0),
                                      'p': p, 'q': q, 'u': u, 'v': v,
                                      'fg': f'{cA}-{cB}-{dA}-{dB}',
                                      'key': f'{cA}{cB}-{dA}{dB}-{C0}-{D0}-'
                                             f'{p}{q}-{u}{v}'},
                                'a': [f'材料{mat}が{rc or rd}g余る',
                                      f'{a2} 個', f'{b2} 個',
                                      f'{_kg(int(addC))} kg', f'{_kg(int(addD))} kg'],
                                '_chk': (n1, rc, rd, a2, b2,
                                         int(addC), int(addD), int(k)),
                            })
    out.sort(key=lambda v: 0 if v['p']['key'] ==
             '1020-1510-1000-1200-97-32' else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# T2 正六角形と二等辺三角形（平面図形）※数値は振らない
#   図1 頂角120°・底辺が1辺の二等辺三角形 → 正六角形はその18倍
#   図2 AD∥BC・AB＝AC＝AD・∠BAC＝120° → ∠DBC＝15度
#   図3 15°の線6本でできる内側の正六角形 → 1−6×(1/18)＝2/3倍
# ══════════════════════════════════════════════════════════════════
def t2_variants(limit=120):
    """T2：図のつくりが決まっているので1通りだけ。"""
    return [{
        'p': {'key': 'hex'},
        'a': ['18 倍', '15 度', f'{frac_html(F(2, 3))} 倍'],
        '_chk': (18, 15, F(2, 3)),
    }]


# ══════════════════════════════════════════════════════════════════
# T3 さいころの目の積の約数の個数（場合の数）
#   さいころを t 回ふって出た目の積を N とし、約数が d 個になる出方を数える。
# ══════════════════════════════════════════════════════════════════
def _divisor_count(n: int) -> int:
    c, d, i = 1, n, 2
    while i * i <= d:
        e = 0
        while d % i == 0:
            d //= i
            e += 1
        c *= e + 1
        i += 1
    return c * 2 if d > 1 else c


def _t3_table(t: int) -> Counter:
    """さいころ t 回の出方を全部ならべ、積の約数の個数ごとに数える。"""
    cnt = Counter()
    for tup in itertools.product(range(1, 7), repeat=t):
        pr = 1
        for x in tup:
            pr *= x
        cnt[_divisor_count(pr)] += 1
    return cnt


def t3_variants(limit=120):
    """T3：さいころの回数と、約数の個数3つを振る。"""
    out = []
    for t in (4, 3, 5):
        cnt = _t3_table(t)
        for d1, d2, d3 in itertools.combinations((2, 3, 4, 5, 6, 7, 8), 3):
            ns = [cnt.get(d, 0) for d in (d1, d2, d3)]
            if any(not 5 <= n <= 160 for n in ns):
                continue
            if not ns[0] < ns[1] < ns[2]:
                continue                       # 元の問題と同じく、あとほどむずかしく
            out.append({
                'p': {'t': t, 'd1': d1, 'd2': d2, 'd3': d3,
                      'key': f'{t}-{d1}{d2}{d3}'},
                'a': [f'{n} 通り' for n in ns],
                '_chk': tuple(ns),
            })
    out.sort(key=lambda v: 0 if v['p']['key'] == '4-234' else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# T4 タクシーと徒歩でT地へ（速さ）
#   S地からT地まで L km。タクシー 時速V km、徒歩 時速w km。
#   A班は x km の地点で降りて歩き、タクシーは引き返して y km の地点で
#   歩いてきたB班を乗せる。タクシーが (2x−y)、B班が y を同じ時間で進むので
#     y ＝ 2wx ÷ (V＋w)
#   A班の到着 ＝ x/V ＋ (L−x)/w ／ B班の到着 ＝ y/w ＋ (L−y)/V
# ══════════════════════════════════════════════════════════════════
def _t4_times(L, V, w, x):
    y = F(2 * w * x, V + w)
    return y, F(x, V) + F(L - x, w), y / w + F(L - y, V)


def t4_variants(limit=120):
    """T4：道のり・タクシーと徒歩の速さ・(1)のx・(3)の時間差を振る。"""
    out = []
    for L in (12, 10, 15, 18, 20, 24):
        for V in (36, 30, 40, 45, 48, 60):
            for w in (4, 5, 6):
                if V <= w * 4:
                    continue
                x2 = F(L * (V + w), V + 3 * w)             # (2) 同時に着く x
                if x2.denominator != 1 or not 0 < x2 < L:
                    continue
                for x1 in range(1, L):                     # (1) の x
                    if x1 == x2:
                        continue
                    y1, tA, tB = _t4_times(L, V, w, x1)
                    if not 0 < y1 < x1:
                        continue
                    diff = (tB - tA) * 60
                    if diff.denominator != 1 or not 5 <= abs(diff) <= 40:
                        continue
                    if (tA * 60).denominator != 1 or (tB * 60).denominator != 1:
                        continue
                    for T in (6, 10, 12, 15, 18, 20):      # (3) A班がT分早い
                        x3 = ((F(T, 60) * V * w + L * (V - w)) * (V + w)
                              / ((V - w) * (V + 3 * w)))
                        if not 0 < x3 < L or x3.denominator not in (1, 2, 4, 8):
                            continue
                        y3 = F(2 * w * x3, V + w)
                        if not 0 < y3 < x3:
                            continue
                        out.append({
                            'p': {'L': L, 'V': V, 'w': w, 'x1': x1, 'T': T,
                                  'key': f'{L}-{V}-{w}-{x1}-{T}'},
                            'a': [f'{"B" if diff < 0 else "A"}班が'
                                  f'{abs(int(diff))}分早い',
                                  frac_html(x2), frac_html(x3)],
                            '_chk': (y1, tA, tB, x2, x3),
                        })
    out.sort(key=lambda v: 0 if v['p']['key'] == '12-36-4-9-12' else 1)
    return out[:limit]


# ══════════════════════════════════════════════════════════════════
# T5 じゃんけんと部屋の移動（場合の数）
#   ①勝→② ①負→①／②勝→③ ②負→①／③勝→③ ③負→②
#   A君とB君が同じ部屋にいる回は2人で対戦するので○×がかならず逆になり、
#   別の部屋にいる回はそれぞれ独立に勝ち負けが決まる。
# ══════════════════════════════════════════════════════════════════
def _t5_move(room: int, win: bool) -> int:
    if room == 1:
        return 2 if win else 1
    if room == 2:
        return 3 if win else 1
    return 3 if win else 2


def _t5_records(n: int, start: int):
    """n回のあとA君とB君が同じ部屋になる (A の○×, B の○×) を全部返す。"""
    out = []

    def rec(i, a, b, ra, rb):
        if i == n:
            if a == b:
                out.append((tuple(ra), tuple(rb)))
            return
        cand = ([(True, False), (False, True)] if a == b
                else list(itertools.product((True, False), repeat=2)))
        for wa, wb in cand:
            rec(i + 1, _t5_move(a, wa), _t5_move(b, wb), ra + [wa], rb + [wb])

    rec(0, start, start, [], [])
    return out


def _ox(rec) -> str:
    return ''.join('○' if x else '×' for x in rec)


_T5_WHO = {
    1: '①の部屋にA君とB君が、②の部屋にC君とD君が、③の部屋にE君とF君が',
    2: '①の部屋にC君とD君が、②の部屋にA君とB君が、③の部屋にE君とF君が',
    3: '①の部屋にC君とD君が、②の部屋にE君とF君が、③の部屋にA君とB君が',
}


def t5_variants(limit=120):
    """T5：はじめの部屋・3回目の勝敗・最後の問いの回数を振る。"""
    out = []
    for start in (1, 2, 3):
        base = _t5_records(3, start)
        for aw in (True, False):
            hit = [(ra, rb) for ra, rb in base if ra[2] is aw and rb[2] is not aw]
            if len(hit) != 1:                    # (1) の答えが1通りに決まる組だけ
                continue
            ra, rb = hit[0]
            half = (len(base) + 1) // 2
            lst = [f'A{_ox(x)}／B{_ox(y)}' for x, y in base]
            for n3 in (4, 5):
                cnt = len(_t5_records(n3, start))
                out.append({
                    'p': {'st': start, 'who': _T5_WHO[start], 'n3': n3,
                          'w1': '勝ち' if aw else '負け',
                          'w2': '負けて' if aw else '勝って',
                          'key': f'{start}-{"o" if aw else "x"}-{n3}'},
                    'a': [_ox(ra[:2]), _ox(rb[:2]),
                          '、'.join(lst[:half]), '、'.join(lst[half:]),
                          f'{cnt} 通り'],
                    '_chk': (base, ra, rb, cnt),
                })
    out.sort(key=lambda v: 0 if v['p']['key'] == '1-o-4' else 1)
    return out[:limit]


VARIANTS8 = {'T1': t1_variants, 'T2': t2_variants, 'T3': t3_variants,
             'T4': t4_variants, 'T5': t5_variants}

# 計算欄の高さ（mm）。予想②は用紙のmmを測っていないので、予想①・第5回の
# 似た設問に合わせた目安の値（tools/nnop8_notes.md）。
WORK_MM8 = {
    'oy2-1-1': 40, 'oy2-1-2': 54, 'oy2-1-3': 70,
    'oy2-2-1': 34, 'oy2-2-2': 44, 'oy2-2-3': 52,
    'oy2-3-1': 36, 'oy2-3-2': 54, 'oy2-3-3': 68,
    'oy2-4-1': 48, 'oy2-4-2': 46, 'oy2-4-3': 56,
    'oy2-5-1': 34, 'oy2-5-2': 58, 'oy2-5-3': 70,
}


GROUPS8 = [
    {
        'key': 'T1', 'round': 'Y2', 'field': 'toku',
        'title': '2種類の製品と2種類の材料', 'vary': True,
        'intro': '右の表は、2種類の製品A、Bをそれぞれ1個作るのに必要な材料C、Dの'
                 '量を表したものです。製品Aと製品Bを作るのに、はじめに材料Cを'
                 '{C0}kg、材料Dを{D0}kg用意しました。',
        'body': '', 'fig': 'mat:{fg}', 'figpos': 'right',
        'subs': [
            {'id': 'oy2-1-1', 'label': '(1)',
             'q': 'はじめに用意した材料を使って、製品Aのみをできるだけ多く作ると、'
                  'どちらの材料が何g余りますか。',
             'rate': 88, 'score': 4, 'ans': [''],
             'how': '製品Aを1個作ると材料Cは{cA}g、材料Dは{dA}g減る。'
                    'それぞれの材料だけを見て何個分あるかを出し、'
                    '**少ないほうが作れる個数**になる。'
                    'その個数だけ作ったときに、もう一方がどれだけ残るかを調べる。'},
            {'id': 'oy2-1-2', 'label': '(2)',
             'q': 'はじめに用意した材料を使って、製品A、Bをそれぞれ何個か作ると、'
                  '材料C、Dはすべてなくなりました。このとき、製品A、Bは'
                  'それぞれ何個作れましたか。',
             'rate': 72, 'score': 4, 'ans': ['製品A ＝', '製品B ＝'],
             'how': '材料Cの式と材料Dの式を、どちらかの製品の個数がそろうように'
                    '何倍かしてから引く（消去算）。'
                    '片方の製品の個数が消えて、もう片方の個数が出る。'},
            {'id': 'oy2-1-3', 'label': '(3)',
             'q': 'はじめに用意した材料に、さらに材料C、Dを{p}：{q}の割合で'
                  '追加したところ、製品A、Bを{u}：{v}の割合で作ることが'
                  'できました。このとき、追加した材料C、Dはそれぞれ何kgですか。',
             'rate': 42, 'score': 4, 'ans': ['材料C ＝', '材料D ＝'],
             'how': '製品Aを{u}個・製品Bを{v}個を1組として、その組を何組か作ったと'
                    '考える。1組で使う材料C・Dの重さを出し、'
                    '「はじめの量＋追加した量」と等しいとおく。'
                    '追加した量は{p}：{q}なので、追加の1あたりを①として、'
                    '組の数と①の2つが出るように2つの式を組み合わせる。'},
        ],
    },
    {
        'key': 'T2', 'round': 'Y2', 'field': 'plane',
        'title': '正六角形と二等辺三角形', 'vary': False,
        'intro': '下の各図について、次の問いに答えなさい。',
        'body': '', 'fig': 'hex3', 'figpos': 'bottom',
        'subs': [
            {'id': 'oy2-2-1', 'label': '(1)',
             'q': '図1の正六角形の面積は、二等辺三角形ABCの面積の何倍ですか。',
             'rate': 82, 'score': 4, 'ans': [''],
             'how': '正六角形は、中心と2つの頂点を結んでできる正三角形6個に分けられる。'
                    '三角形ABCは、そのうちの1つ（正三角形）と底辺が同じ。'
                    '頂角が120度なので高さが何分の一になるかを考えると、'
                    '正三角形の何分の一かが出る。'},
            {'id': 'oy2-2-2', 'label': '(2)',
             'q': '図2の四角形ABCDにおいて、ADとBCは平行、角BACは120度、'
                  'AB＝AC＝ADとなっています。このとき、角DBCの大きさは何度ですか。',
             'rate': 58, 'score': 4, 'ans': ['', ],
             'how': '二等辺三角形ABCの底角をまず出す。'
                    'ADとBCが平行だから、角DACは角ACBと等しい（さっ角）。'
                    'すると角DABが分かり、AB＝ADの二等辺三角形ABDの底角も出る。'
                    '角DBCは、角ABCから角ABDを引いたもの。'},
            {'id': 'oy2-2-3', 'label': '(3)',
             'q': '図3のように、正六角形ABCDEFの内側に6つの合同な三角形を'
                  'しきつめて、内側に正六角形PQRSTUを作りました。このとき、'
                  '正六角形PQRSTUの面積は、正六角形ABCDEFの面積の何倍ですか。',
             'rate': 26, 'score': 4, 'ans': [''],
             'how': '三角形の1つ（たとえば三角形BCR）は、正六角形の1辺BCが底辺。'
                    '15度の線が引いてあるので、(2)から、その頂点は'
                    '**図1の点Aと同じ高さの線**の上にある。'
                    'だから三角形1つの面積は図1の三角形と同じ。'
                    '6つ分を正六角形から取りのぞけばよい。'},
        ],
    },
    {
        'key': 'T3', 'round': 'Y2', 'field': 'case',
        'title': 'さいころの目の積の約数', 'vary': True,
        'intro': 'さいころを{t}回ふって、出た目の数の積をNとします。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'oy2-3-1', 'label': '(1)',
             'q': 'Nの約数の個数が{d1}個となる目の出方は何通りありますか。',
             'rate': 78, 'score': 4, 'ans': [''],
             'how': '約数の個数は、素数の積に分けたときの「同じ素数が何個あるか」'
                    'に1を足してかけ合わせたもの。'
                    'まず約数が{d1}個になるNの形をすべて書き出し、'
                    'そのNになるさいころの目の組と、その並べ方を数える。'},
            {'id': 'oy2-3-2', 'label': '(2)',
             'q': 'Nの約数の個数が{d2}個となる目の出方は何通りありますか。',
             'rate': 44, 'score': 4, 'ans': [''],
             'how': '(1)と同じで、まずNの形をすべて出す。'
                    '同じNでも目の組が何通りもあることに注意する'
                    '（4＝4×1×1…と4＝2×2×1…など）。'
                    '組ごとに並べ方（同じ目があるときは重なりを割る）を数える。'},
            {'id': 'oy2-3-3', 'label': '(3)',
             'q': 'Nの約数の個数が{d3}個となる目の出方は何通りありますか。',
             'rate': 20, 'score': 4, 'ans': [''],
             'how': '約数が{d3}個になるNの形を、まちがいなく全部あげるのが山場。'
                    '1以外の目が何個出るかで場合分けし、'
                    'それぞれで目の組と並べ方を数えて足す。'},
        ],
    },
    {
        'key': 'T4', 'round': 'Y2', 'field': 'speed',
        'title': 'タクシーと徒歩でT地へ', 'vary': True,
        'intro': '6人が3人ずつ、2つの班A、Bに分かれてS地から{L}km離れたT地へ'
                 'タクシーで行く予定でしたが、タクシーが1台しかなかったので、'
                 'A班はタクシー、B班は徒歩で同時にS地を出発しました。途中、A班は'
                 'S地からxkmのP地点でタクシーを降りて徒歩でT地へ向かい、'
                 'タクシーは引き返してS地からykmのQ地点でB班を乗せてT地へ'
                 '向かいました。',
        'body': 'タクシーの速さを時速{V}km、徒歩の速さを時速{w}km、タクシーの'
                '乗り降りにかかる時間は考えないものとします。',
        'fig': None,
        'subs': [
            {'id': 'oy2-4-1', 'label': '(1)',
             'q': 'x＝{x1}のとき、どちらの班の方が何分早くT地に着きますか。',
             'rate': 70, 'score': 4, 'ans': [''],
             'how': 'まずタクシーがB班を拾う地点yを出す。'
                    'タクシーが {x1}×2−y km 進む間に、B班は y km 歩く。'
                    '進む道のりの比が速さの比になることから y が出る。'
                    'あとはそれぞれの班の時間を足して比べる。'},
            {'id': 'oy2-4-2', 'label': '(2)',
             'q': 'A班とB班がT地に同時に着くとき、xにあてはまる数を求めなさい。',
             'rate': 52, 'score': 4, 'ans': ['x ＝'],
             'how': 'y はいつでも x の決まった割合になる（(1)と同じ考え方）。'
                    'A班は「タクシー x km ＋ 徒歩 {L}−x km」、'
                    'B班は「徒歩 y km ＋ タクシー {L}−y km」。'
                    '同時に着くということは、'
                    'A班が歩く道のりとB班が歩く道のりの時間差がつり合うということ。'},
            {'id': 'oy2-4-3', 'label': '(3)',
             'q': 'A班がB班より{T}分早くT地に着くとき、xに'
                  'あてはまる数を求めなさい。',
             'rate': 30, 'score': 4, 'ans': ['x ＝'],
             'how': 'xを(2)より大きくすると、A班はタクシーに長く乗るので早く着く。'
                    'xが1km増えると差が何分変わるかを調べ、'
                    '(2)のときの差0分から{T}分にするには'
                    '何km増やせばよいかを考える。'},
        ],
    },
    {
        'key': 'T5', 'round': 'Y2', 'field': 'case',
        'title': 'じゃんけんと部屋の移動', 'vary': True,
        'intro': '①、②、③の3つの部屋があります。{who}います。各部屋で、勝負が'
                 'つくまでじゃんけんをし、その結果によって次の（ア）〜（ウ）の'
                 'ルールで部屋の移動を行い、これをくり返します。ただし、部屋を'
                 '「移動する」とは、部屋に「とどまる」ことも含めるものとします。'
                 '<br>（ア）①の部屋でじゃんけんに勝った人は②の部屋に移動し、'
                 '負けた人は①の部屋にとどまる'
                 '<br>（イ）②の部屋でじゃんけんに勝った人は③の部屋に移動し、'
                 '負けた人は①の部屋に移動する'
                 '<br>（ウ）③の部屋でじゃんけんに勝った人は③の部屋にとどまり、'
                 '負けた人は②の部屋に移動する'
                 '<br>A君とB君は「勝敗記録表」に、勝ったときは○、負けたときは×を'
                 'つけて記入します。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'oy2-5-1', 'label': '(1)',
             'q': '3回目のじゃんけんでA君が{w1}、B君が{w2}部屋を移動したところ、'
                  'A君とB君は1つの部屋になりました。このとき、1回目と2回目の'
                  '勝敗を、A君とB君それぞれについて○×で答えなさい。',
             'rate': 68, 'score': 4, 'ans': ['A君', 'B君'],
             'how': '2人が同じ部屋にいる回は、その2人で対戦するので○×が'
                    'かならず逆になる。はじめは2人とも同じ部屋なので、'
                    '1回目は必ず一方が○、もう一方が×。'
                    'そこから部屋を書き出して、3回目のあとに同じ部屋に'
                    'なるものをさがす。',
             },
            {'id': 'oy2-5-2', 'label': '(2)',
             'q': '3回目のじゃんけんを行い、その結果、部屋を移動したところ、'
                  'A君とB君は同じ部屋になりました。このとき、A君とB君の勝敗'
                  '記録表として考えられるものを、(1)のものも含めてすべて'
                  '答えなさい。（1回目から順に、A君とB君の○×を組にして書く）',
             'rate': 36, 'score': 4, 'ans': ['', ''],
             'how': '1回目のあと2人は別の部屋になる。'
                    '別の部屋にいる回は、2人の勝ち負けは関わりなく決まるので'
                    '4通りに分かれる。'
                    '部屋の組み合わせを樹形図で全部たどり、'
                    '3回目のあとに同じ部屋になるものを拾う。'},
            {'id': 'oy2-5-3', 'label': '(3)',
             'q': '{n3}回目のじゃんけんを行い、その結果、部屋を移動したところ、'
                  'A君とB君は同じ部屋になりました。このとき、A君とB君の勝敗'
                  '記録表の○×のつけ方は何通り考えられますか。',
             'rate': 14, 'score': 4, 'ans': [''],
             'how': '「2人がどの部屋とどの部屋にいるか」だけを見て、'
                    'その組み合わせごとに何通りあるかを1回ずつ数え上げていく。'
                    '同じ部屋なら次は2通り、別の部屋なら4通りに分かれる。'
                    '最後に同じ部屋になっているものを合計する。'},
        ],
    },
]


if __name__ == '__main__':
    for k, fn in VARIANTS8.items():
        vs = fn()
        ex = vs[0]['a'] if vs else '（まだ空）'
        print(f'{k}: {len(vs):4}通り　例 {ex}')
