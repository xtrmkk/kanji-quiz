# -*- coding: utf-8 -*-
"""第4回・算数の設問マスタと、採用可能なパラメータの全列挙。

第1〜3回・夏期そっくりと同じ方針（nnop_spec.md）。
**計算はすべてここ（ビルド時のPython）で終わらせる。**
ブラウザ側は、ここが出したパラメータと解答を文字として差し込むだけ。

  python3 tools/nnop5_data.py   … 各大問が何通り作れるか表示する
"""
import itertools
from fractions import Fraction as F
from math import gcd, factorial

from nnop_data import frac_html, improper_html, num, ratio_of   # 表示の小道具は共用
from nnop_fig import KANA, rect3_parts                          # 図と共通の構造


# ══════════════════════════════════════════════════════════════════
# 大問ごとの「採用できるパラメータの全列挙」
#   返すのは次の形のリスト。元の数値の組を**必ず先頭**に置くこと
#   （build_nnop.py の回帰テストが元の数値で公式解答と照合するため）。
#
#   {'p': { 問題文に差し込む値 },
#    'a': [ 解答（答欄の数だけ・HTML可） ],
#    '_chk': 検算用に取っておく途中結果 }
# ══════════════════════════════════════════════════════════════════

# ── M1 配膳ロボット（つるかめ算①②・差集め算）──────────────────
# cA, cB … 1回に運ぶ皿数。pA,mA / pB,mB … 準備と往復にかかる分。
# 台数の内訳 a1,a2,a3 を先に決めて、問題文に出す数（皿の合計・差・時間の合計）を
# そこから逆算する。こうすると答えは必ず整数になる。
M1_CAP = [(10, 6), (12, 8), (10, 4), (12, 9), (9, 6), (8, 5)]
M1_TIM = [(3, 3, 1, 2), (2, 4, 1, 2), (4, 2, 2, 1), (3, 2, 1, 1), (5, 1, 2, 2)]
M1_N = [25, 20, 30, 24]
M1_FR = [(48, 60, 28), (40, 64, 32), (56, 52, 24), (44, 68, 36)]   # Nに対する%


def m1_variants(limit=120):
    """M1：つるかめ算2通りと差集め算。"""
    out = []
    for cA, cB in M1_CAP:
        for pA, mA, pB, mB in M1_TIM:
            tA, tB = pA + mA, pB + mB
            if tA <= tB:
                continue
            for N in M1_N:
                for f1, f2, f3 in M1_FR:
                    a1, a2, a3 = (round(N * f / 100) for f in (f1, f2, f3))
                    if len({a1, a2, a3}) < 3:
                        continue
                    if not all(2 <= a <= N - 2 for a in (a1, a2, a3)):
                        continue
                    P1 = cA * a1 + cB * (N - a1)
                    P2 = cA * a2 - cB * (N - a2)
                    T = tA * a3 + tB * (N - a3)
                    if P2 <= 0:
                        continue
                    plates = cA * a3 + cB * (N - a3)
                    out.append({
                        'p': {'cA': cA, 'cB': cB, 'pA': pA, 'mA': mA,
                              'pB': pB, 'mB': mB, 'N': N,
                              'P1': P1, 'P2': P2, 'T': T},
                        'a': [f'{a1} 台', f'{N - a1} 台',
                              f'{a2} 台', f'{N - a2} 台',
                              f'{plates} 皿'],
                        '_chk': (a1, a2, a3, plates),
                    })
                    if len(out) >= limit:
                        return out
    return out


# ── M2 平行四辺形（線分比と面積比）────────────────────────────
# AF:FD＝m:n。G＝AC∩FB、Hは三角形AGFと三角形GHCの面積が等しくなる点。
#   FG:GH:HB ＝ m(m+n) : m² : n(2m+n)
#   四角形FGCD:三角形HBC ＝ (m²+3mn+n²) : n(2m+n)
# m,nが互いに素ならどちらもこのままで既約になる（build側で確かめている）。
def m2_variants(limit=120):
    """M2：平行四辺形の線分比と面積比。"""
    pairs = [(3, 2)] + [(m, n) for m in range(1, 7) for n in range(1, 7)
                        if gcd(m, n) == 1 and (m, n) != (3, 2)]
    out = []
    for m, n in pairs:
        r = [m * (m + n), m * m, n * (2 * m + n)]
        g = gcd(gcd(r[0], r[1]), r[2])
        r = [v // g for v in r]
        s = [m * m + 3 * m * n + n * n, n * (2 * m + n)]
        g2 = gcd(s[0], s[1])
        s = [v // g2 for v in s]
        out.append({
            'p': {'m': m, 'n': n, 'mn': f'{m}x{n}'},
            'a': [' : '.join(str(v) for v in r), ' : '.join(str(v) for v in s)],
            '_chk': (r, s),
        })
        if len(out) >= limit:
            break
    return out


# ── M3 長方形を3k+1個の三角形に分ける ────────────────────────
# 対角線PR上にk個の点、辺QR上にk-1個の点をとり、ジグザグに区切る。
# 下側（三角形PQR）の2k個と、上側のPからいちばん近い1個が同じ面積。
# 聞くのは上側の j 番目（j=1がP寄り＝元の問題の「ケ」）。
def _m3_areas(k):
    a, x, tris = rect3_parts(k)
    up = [a[j] - a[j - 1] for j in range(1, k)] + [1 - a[-1]]
    return a, x, tris, [u / 2 for u in up]


def m3_variants(limit=120):
    """M3：等積の三角形から残りの面積を出す。"""
    combos = [(3, 1)] + [(k, j) for k in (2, 3, 4) for j in range(1, k + 1)
                         if (k, j) != (3, 1)]
    out = []
    for k, j in combos:
        a, x, tris, up = _m3_areas(k)
        tot = 3 * k + 1
        eq = [KANA[i] for i in range(2 * k)] + [KANA[tot - 1]]
        ask = KANA[tot - 1 - j]
        out.append({
            'p': {'k': k, 'TOT': tot, 'LAST': KANA[tot - 1],
                  'EQ': '、'.join(eq), 'ASK': ask},
            'a': [frac_html(up[j - 1]) + ' 倍'],
            '_chk': (up[j - 1], a, x),
        })
        if len(out) >= limit:
            break
    return out


# ── M4 円周上で出会う点（速さ）────────────────────────────────
# 1回の出会いでAが進む距離 step＝円周×vA/(vA+vB)。○は step の倍数（mod 円周）。
# か所の数 M＝円周/gcd(step,円周)。最も遠い○は gcd×(M÷2の商)。
def _m4_a():
    """前半（(1)(2)）に使える 円周・速さ・何回目 の組。"""
    out = []
    for vA in range(50, 91, 2):
        for vB in range(30, vA, 2):
            S, g = vA + vB, gcd(vA, vB)
            M = S // g
            if M not in (4, 5, 6, 7):
                continue
            for q in range(6, 16):
                L = S * q
                if not (700 <= L <= 1500) or L % 10:
                    continue
                step = vA * q
                for t in (3, 4):
                    if step * t % L == 0 or t >= M:
                        continue
                    out.append((L, vA, vB, t, step, g, M))
    return out


def _m4_b():
    """後半（(3)）に使える 円周・速さ の組。○の個数は奇数にする。"""
    out = []
    for vA in range(60, 96):
        for vB in range(50, vA):
            S, g = vA + vB, gcd(vA, vB)
            M = S // g
            if M % 2 == 0 or not (25 <= M <= 55):
                continue
            for q in range(40, 90):
                L = S * q
                if not (6000 <= L <= 12000) or L % 10:
                    continue
                out.append((L, vA, vB, vA * q, q * g, M))
    return out


def m4_variants(limit=120):
    """M4：円周上で出会う地点。"""
    A = _m4_a()
    B = _m4_b()
    A.sort(key=lambda v: 0 if v[:4] == (990, 66, 44, 3) else 1)
    B.sort(key=lambda v: 0 if v[:3] == (8910, 69, 66) else 1)
    out = []
    for i in range(limit):
        L1, vA1, vB1, t, step1, g1, M1 = A[i % len(A)]
        L2, vA2, vB2, step2, g2, M2 = B[(i * 7) % len(B)]
        if i == 0:
            assert (L1, vA1, vB1, t) == (990, 66, 44, 3)
            assert (L2, vA2, vB2) == (8910, 69, 66)
        out.append({
            'p': {'L1': L1, 'vA1': vA1, 'vB1': vB1, 't': t,
                  'L2': L2, 'vA2': vA2, 'vB2': vB2},
            'a': [f'{step1 * t % L1} mm', f'{M1} か所', f'{g2 * (M2 // 2)} mm'],
            '_chk': (step1, g1, M1, step2, g2, M2),
        })
    return out


# ── M5 円形に並べたカード（場合の数）─────────────────────────
# となり合う2枚の和がすべて奇数 ⇔ 奇数と偶数が交互に並ぶ。
# 1を上に固定すると、1から数えて偶数番目の位置が偶数のカードの席になる。
def _m5_pos(n, card):
    labs = [chr(ord('A') + i) for i in range(n - 1)]
    return [labs[i] for i in range(n - 1) if (i + 1) % 2 == (card + 1) % 2]


def _m5_cnt(n):
    return factorial(n // 2 - 1) * factorial(n // 2)


def _m5_div(n, d):
    ev = list(range(2, n + 1, 2))
    pr = sum(1 for p, q in itertools.permutations(ev, 2) if (p + q) % d == 0)
    return pr, pr * factorial(n // 2 - 2) * factorial(n // 2 - 1)


def m5_variants(limit=120):
    """M5：円形に並べたカードの数え上げ。"""
    combos = [(6, 3, 8, 10, 4)]
    for n1 in (6, 8):
        for card in range(2, n1 + 1):
            for n2 in (8, 10):
                for n3 in (10, 12):
                    for d in (4, 5, 6):
                        c = (n1, card, n2, n3, d)
                        if n3 <= n2 or c in combos:
                            continue
                        combos.append(c)
    out = []
    for n1, card, n2, n3, d in combos:
        pos = _m5_pos(n1, card)
        pr, cnt3 = _m5_div(n3, d)
        if not pos or pr == 0:
            continue
        out.append({
            'p': {'n1': n1, 'card': card, 'LAB': chr(ord('A') + n1 - 2),
                  'n2': n2, 'n3': n3, 'd': d},
            'a': ['、'.join(pos), f'{_m5_cnt(n2)} 通り', f'{cnt3} 通り'],
            '_chk': (pos, _m5_cnt(n2), pr, cnt3),
        })
        if len(out) >= limit:
            break
    return out


# ── M6／M6a 数の列A・列B（規則性）────────────────────────────
# 列A：次の数＝その数＋（その数をdaで割った余り）
# 列B：次の数＝その数＋（その数の一の位をdbで割った余り）＋1
def _seq_a(a0, da, hi, least):
    out, x = [], a0
    while x <= hi or len(out) < least:
        out.append(x)
        r = x % da
        if r == 0:
            return None                      # 余り0で止まってしまう組は使わない
        x += r
    return out


def _seq_b(b0, db, hi, least):
    out, x = [], b0
    while x <= hi or len(out) < least:
        out.append(x)
        x += (x % 10) % db + 1
    return out


def _m6_text(seq, n, rule_fmt):
    return '、'.join(str(v) for v in seq[:n]) + '、……'


def _m6_all(limit=120):
    combos = [(3, 5, 5, 3, 50, 1000, 5)]
    for a0 in (3, 1, 2, 4):
        for b0 in (5, 2, 7, 8):
            for db in (3, 4):
                for idx in (50, 40, 60):
                    for Nb in (1000, 2000, 500):
                        c = (a0, 5, b0, db, idx, Nb, 5)
                        if c not in combos:
                            combos.append(c)
    out = []
    for a0, da, b0, db, idx, Nb, cnt in combos:
        A = _seq_a(a0, da, Nb, idx)
        B = _seq_b(b0, db, Nb, idx)
        if A is None or len(A) < idx or len(B) < idx:
            continue
        sA, sB = set(A), set(B)
        com = sorted(sA & sB)
        if len(com) < cnt + 2 or not com:
            continue
        le = [v for v in com if v <= Nb]
        if not le:
            continue
        near = max(le)
        if near not in A or near not in B:
            continue
        only = sum(1 for v in range(1, Nb + 1) if (v in sA) ^ (v in sB))
        arule = f'{a0}から始まり、その数を{da}で割った余りを足した数を次の数とする'
        brule = (f'{b0}から始まり、その数の一の位を{db}で割った余りが'
                 + '、'.join(f'{r}のときは{r + 1}を' for r in range(db))
                 + '足した数を次の数とする')
        aex = ('、'.join(f'{A[i]}÷{da}＝{A[i] // da}あまり{A[i] % da}なので'
                         f'{A[i]}＋{A[i] % da}＝{A[i + 1]}' for i in range(3))
               + 'となるため、' + '、'.join(str(v) for v in A[:4]) + 'となります。')
        bex = ('、'.join(f'{B[i] % 10}÷{db}＝{B[i] % 10 // db}あまり{B[i] % 10 % db}なので'
                         f'{B[i]}＋{B[i] % 10 % db + 1}＝{B[i + 1]}' for i in range(3))
               + 'となるため、' + '、'.join(str(v) for v in B[:4]) + 'となります。')
        out.append({
            'p': {'a0': a0, 'da': da, 'b0': b0, 'db': db,
                  'idx': idx, 'Nb': Nb, 'cnt': cnt,
                  'ALIST': _m6_text(A, 12, arule), 'BLIST': _m6_text(B, 10, brule),
                  'ARULE': arule, 'BRULE': brule, 'AEX': aex, 'BEX': bex},
            '_a123': [str(A[idx - 1]), str(B[idx - 1]),
                      '、'.join(str(v) for v in com[:cnt])],
            '_a45': [str(near), f'{A.index(near) + 1} 番目',
                     f'{B.index(near) + 1} 番目', f'{only} 個'],
            '_chk': (len(sA), len(sB), len(com), near, only),
        })
        if len(out) >= limit:
            break
    return out


def m6_variants(limit=120):
    """M6：列A・列Bの(1)(2)(3)。"""
    return [{'p': v['p'], 'a': v['_a123'], '_chk': v['_chk']} for v in _m6_all(limit)]


def m6a_variants(limit=120):
    """M6a：列A・列Bの(4)(5)。"""
    return [{'p': v['p'], 'a': v['_a45'], '_chk': v['_chk']} for v in _m6_all(limit)]


VARIANTS5 = {'M1': m1_variants, 'M2': m2_variants, 'M3': m3_variants,
             'M4': m4_variants, 'M5': m5_variants, 'M6': m6_variants,
             'M6a': m6a_variants}

# 計算欄の高さ（mm）。元の問題用紙を A3＝420mm として実測した値（tools/nnop5_notes.md）。
#   0 を入れると「計算欄なし（答だけ）」になる。
WORK_MM5 = {
    'op4-1-1': 28, 'op4-1-2': 28, 'op4-1-3': 33,
    'op4-2': 60,
    'op4-3': 42,
    'op4-4-1': 30, 'op4-4-2': 44, 'op4-4-3': 54,
    'op4-5-1': 0, 'op4-5-2': 60, 'op4-5-3': 72,
    'op4-6-1': 55, 'op4-6-2': 60, 'op4-6-3': 43,
    'op4-6-4': 68, 'op4-6-5': 60,
}


# ══════════════════════════════════════════════════════════════════
# 設問マスタ
# ══════════════════════════════════════════════════════════════════
GROUPS5 = [
    {
        'key': 'M1', 'round': 4, 'field': 'toku', 'title': '配膳ロボット', 'vary': True,
        'intro': 'ある回転寿司店では、配膳ロボットAとBを使ってテーブル席へ皿を運んでいます。'
                 'ロボットAは、{cA}皿を積みこむための準備に{pA}分かかり、その後、'
                 '皿を運んでキッチンへもどるまでに{mA}分かかります。'
                 'ロボットBは、{cB}皿を積みこむための準備に{pB}分かかり、その後、'
                 '皿を運んでキッチンへもどるまでに{mB}分かかります。'
                 '以下の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op4-1-1', 'label': '(1)',
             'q': 'AとBが合わせて{N}台あります。{N}台がそれぞれ1回ずつ仕事をしたところ、'
                  '運んだ皿の合計は{P1}皿でした。AとBはそれぞれ何台ありますか。',
             'rate': 90, 'score': 3, 'ans': ['A', 'B'],
             'how': 'ぜんぶBだとすると {cB}×{N} 皿。実際との差を、'
                    '1台をAに取りかえるごとに増える {cA}−{cB} 皿で割る。'},
            {'id': 'op4-1-2', 'label': '(2)',
             'q': 'AとBが合わせて{N}台あります。{N}台がそれぞれ1回ずつ仕事をしたところ、'
                  'Aが運んだ皿の枚数はBが運んだ皿の枚数より{P2}枚多かったそうです。'
                  'AとBはそれぞれ何台ありますか。',
             'rate': 85, 'score': 3, 'ans': ['A', 'B'],
             'how': 'ぜんぶBだと差は −{cB}×{N}。1台をAに取りかえると差は {cA}＋{cB} ずつ'
                    '増える。そこから何台取りかえたかを出す。'},
            {'id': 'op4-1-3', 'label': '(3)',
             'q': 'AとBが合わせて{N}台あります。{N}台がそれぞれ1回ずつ仕事をしたところ、'
                  '仕事にかかった時間の合計は{T}分でした。このとき、{N}台が運んだ皿は'
                  '全部で何皿でしたか。',
             'rate': 79, 'score': 4, 'ans': [''],
             'how': '1台あたりの時間はAが {pA}＋{mA} 分、Bが {pB}＋{mB} 分。'
                    'まず時間のつるかめ算で台数を出してから、皿の数を数える。'},
        ],
    },
    {
        'key': 'M2', 'round': 4, 'field': 'plane', 'title': '平行四辺形の線分比と面積比',
        'vary': True,
        'intro': '図において、四角形ABCDは平行四辺形であり、AF：FD＝{m}：{n}です。'
                 'また、三角形AGFと三角形GHCの面積が等しいです。',
        'body': '', 'fig': 'para:{mn}', 'figpos': 'right',
        'subs': [
            {'id': 'op4-2', 'label': '',
             'q': 'このとき、FG：GH：HBの長さの比を最も簡単な整数の比で答えなさい。'
                  'また、四角形FGCDの面積と三角形HBCの面積の比を最も簡単な整数の比で'
                  '答えなさい。',
             'rate': 49, 'score': 7,
             'ans': ['FG : GH : HB ＝', '四角形FGCD : 三角形HBC ＝'],
             'how': 'まず三角形AGFと三角形GBCが相似（AF：BC＝{m}：{m}＋{n}）なので'
                    'FG：GBが分かる。三角形FBCの面積を1とすると、三角形AGFの面積も'
                    '同じ比でおさえられるので、GHが三角形FBCの何倍かが出る。'},
        ],
    },
    {
        'key': 'M3', 'round': 4, 'field': 'plane', 'title': '長方形を三角形に分ける',
        'vary': True,
        'intro': '図の長方形PQRSを対角線PRといくつかの直線で区切り、'
                 'アから{LAST}の{TOT}個の三角形に分けました。'
                 'このとき、{EQ}の面積は同じです。',
        'body': '', 'fig': 'rect3:{k}', 'figpos': 'bottom',
        'subs': [
            {'id': 'op4-3', 'label': '',
             'q': 'このとき、{ASK}の面積は、長方形全体の面積の何倍の大きさですか。'
                  'ただし、図は正確とは限りません。',
             'rate': 63, 'score': 5, 'ans': [''],
             'how': '対角線の下側にある{TOT}個のうちの三角形は全部で長方形の半分。'
                    'そこから1個分の面積が決まる。Sを頂点とする三角形の面積は、'
                    '対角線PR上での底辺の長さに比例するので、順に場所を追っていける。'},
        ],
    },
    {
        'key': 'M4', 'round': 4, 'field': 'speed', 'title': '円周上で出会う地点',
        'vary': True,
        'intro': '円周{L1}mmの円があります。点Aと点Bは同じ地点Pを同時に出発し、'
                 '反対方向に進みます。点Aは時計回りに分速{vA1}mmで、'
                 '点Bは反時計回りに分速{vB1}mmで進みます。'
                 '点Aと点Bが出会うごとに、その地点に○をつけることにしました。'
                 '以下の問いに答えなさい。',
        'body': '', 'fig': 'meet:P', 'figpos': 'right',
        'subs': [
            {'id': 'op4-4-1', 'label': '(1)',
             'q': '出発してから{t}回目につけた○は、地点Pから時計回りに何mmのところですか。',
             'rate': 87, 'score': 3, 'ans': [''],
             'how': '2点が出会うまでに進む道のりの合計は円周ぶん。'
                    '1回の出会いで点Aが進む道のりを出し、それを{t}倍して'
                    '円周で割ったあまりを見る。'},
            {'id': 'op4-4-2', 'label': '(2)',
             'q': '○をつけた地点は、全部で何か所ありますか。',
             'rate': 73, 'score': 4, 'ans': [''],
             'how': '○の位置は「1回ぶんの道のり」の倍数。'
                    'それと円周の最大公約数ぶんの間かくで円周上に等しく並ぶ。'},
            {'id': 'op4-4-3', 'label': '(3)',
             'q': '円周{L2}mmの円があります。点Aと点Bは同じ地点Qを同時に出発し、'
                  '反対方向に進みます。点Aは時計回りに分速{vA2}mmで、'
                  '点Bは反時計回りに分速{vB2}mmで進みます。'
                  '点Aと点Bが出会うごとに、その地点に○をつけることにしました。'
                  '○をつけた地点のうち、地点Qから最も遠い地点は、'
                  '地点Qから何mm離れていますか。',
             'rate': 35, 'score': 5, 'ans': [''], 'fig': 'meet:Q', 'figpos': 'right',
             'how': '(2)と同じように○は等間かくに並ぶ。個数が奇数なら'
                    '真向かいには○が無いので、半周のすぐ手前の○までの道のりを答える。'},
        ],
    },
    {
        'key': 'M5', 'round': 4, 'field': 'case', 'title': '円形に並べたカード',
        'vary': True,
        'intro': '整数が書かれたカードを円形に並べます。ただし、となり合う2枚のカードに'
                 '書かれた数の和は、すべて奇数であるものとします。以下の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op4-5-1', 'label': '(1)',
             'q': '1から{n1}までの整数が書かれた{n1}枚のカードを1枚ずつ使います。'
                  '1を右図の位置に固定したとき、{card}が置くことのできる位置を、'
                  '右のAから{LAB}の中からすべて答えなさい。',
             'rate': 89, 'score': 3, 'ans': [''], 'fig': 'ringL:{n1}', 'figpos': 'right',
             'how': '和がすべて奇数ということは、奇数と偶数が交互に並ぶということ。'
                    '1の位置から数えて、どの位置が奇数の席になるかを見る。'},
            {'id': 'op4-5-2', 'label': '(2)',
             'q': '1を右図の位置に固定して、1から{n2}までの整数が書かれた{n2}枚のカードを'
                  '1回ずつ使います。並べ方は全部で何通りありますか。',
             'rate': 76, 'score': 3, 'ans': [''], 'fig': 'ring:{n2}', 'figpos': 'right',
             'how': '奇数の席と偶数の席が交互に決まってしまう。'
                    '残りの奇数どうし・偶数どうしの並べかえを、それぞれ階乗で数える。'},
            {'id': 'op4-5-3', 'label': '(3)',
             'q': '1を右図の位置に固定して、1から{n3}までの整数が書かれた{n3}枚のカードを'
                  '1回ずつ使います。1の両どなりにある2枚のカードに書かれた数の和が'
                  '{d}の倍数になるような並べ方は何通りありますか。',
             'rate': 28, 'score': 4, 'ans': [''], 'fig': 'ring:{n3}', 'figpos': 'right',
             'how': '1の両どなりは偶数の席。和が{d}の倍数になる偶数の組を先に書き出し、'
                    '左右の入れかえで2倍してから、残りのカードの並べかえをかける。'},
        ],
    },
    {
        'key': 'M6', 'round': 4, 'field': 'rule', 'title': '数の列Aと列B', 'vary': True,
        'intro': '次のような数の列Aと列Bがあります。<br>'
                 '・列A：{ALIST}<br>・列B：{BLIST}<br>'
                 '列A、列Bはそれぞれ下のような規則で並んでいます。<br>'
                 '　列Aの規則：{ARULE}<br>　列Bの規則：{BRULE}<br>'
                 '列Aの前から4つを考えると、{AEX}'
                 '列Bの前から4つを考えると、{BEX}このとき、次の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op4-6-1', 'label': '(1)',
             'q': '列Aの{idx}番目の数を求めなさい。',
             'rate': 68, 'score': 2, 'ans': [''],
             'how': '何項かごとに同じだけ増える「かたまり」になっている。'
                    '1かたまりの項数と増える量を見つけて、{idx}番目がどこかを数える。'},
            {'id': 'op4-6-2', 'label': '(2)',
             'q': '列Bの{idx}番目の数を求めなさい。',
             'rate': 44, 'score': 3, 'ans': [''],
             'how': '一の位だけを追いかけると、同じ並びがくり返される。'
                    'はじめのうちはその輪に入っていないので、そこを別に数える。'},
            {'id': 'op4-6-3', 'label': '(3)',
             'q': '列Aと列Bのどちらにも現れる数を、小さい方から順に{cnt}つ書きなさい。',
             'rate': 64, 'score': 3, 'ans': [''],
             'how': 'それぞれの列に現れる数の「一の位」をそろえて書き出し、'
                    '両方に出てくる一の位をひろう。'},
        ],
    },
    {
        'key': 'M6a', 'round': 4, 'field': 'rule', 'title': '数の列Aと列B（後半）',
        'vary': True,
        'intro': '次のような数の列Aと列Bがあります。<br>'
                 '・列A：{ALIST}<br>・列B：{BLIST}<br>'
                 '列A、列Bはそれぞれ下のような規則で並んでいます。<br>'
                 '　列Aの規則：{ARULE}<br>　列Bの規則：{BRULE}<br>'
                 '列Aの前から4つを考えると、{AEX}'
                 '列Bの前から4つを考えると、{BEX}このとき、次の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op4-6-4', 'label': '(4)',
             'q': '列Aと列Bのどちらにも現れる数のうち、{Nb}以下の数で{Nb}に最も近い数を'
                  '求めなさい。また、その数は列A、列Bのそれぞれ前から数えて何番目の数ですか。',
             'rate': 26, 'score': 4,
             'ans': ['{Nb}に最も近い数', '列A', '列B'],
             'how': '両方に現れる数は一の位で決まる。{Nb}以下でいちばん大きいものを見つけ、'
                    '1かたまりが何項・何ずつ増えるかから、前から何番目かを逆算する。'},
            {'id': 'op4-6-5', 'label': '(5)',
             'q': '1から{Nb}までの整数の中で、列Aと列Bの「どちらか一方にしか現れない数」は'
                  '全部で何個ありますか。',
             'rate': 6, 'score': 4, 'ans': [''],
             'how': '（列Aの個数）＋（列Bの個数）−（両方に現れる数の個数）×2。'
                    '列の始まりのところだけ規則から外れるので、そこを数え落とさないこと。'},
        ],
    },
]


if __name__ == '__main__':
    for k, fn in VARIANTS5.items():
        vs = fn()
        ex = vs[0]['a'] if vs else '（まだ空）'
        print(f'{k}: {len(vs):4}通り　例 {ex}')
