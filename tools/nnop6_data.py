# -*- coding: utf-8 -*-
"""第5回・算数の設問マスタと、採用可能なパラメータの全列挙。

第1〜4回・夏期そっくりと同じ方針（nnop_spec.md）。
**計算はすべてここ（ビルド時のPython）で終わらせる。**
ブラウザ側は、ここが出したパラメータと解答を文字として差し込むだけ。

  python3 tools/nnop6_data.py   … 各大問が何通り作れるか表示する
"""
import collections
import itertools
from fractions import Fraction as F
from math import gcd

from nnop_data import num                       # 表示の小道具は共用


# ══════════════════════════════════════════════════════════════════
# 大問ごとの「採用できるパラメータの全列挙」
#   返すのは次の形のリスト。元の数値の組を**必ず先頭**に置くこと
#   （build_nnop.py の回帰テストが元の数値で公式解答と照合するため）。
#
#   {'p': { 問題文に差し込む値 },
#    'a': [ 解答（答欄の数だけ・HTML可） ],
#    '_chk': 検算用に取っておく途中結果 }
# ══════════════════════════════════════════════════════════════════

# ── R1 虫食い算 ───────────────────────────────────────────────
# 「fアf × fイf ＝ d1 d2 ウ d4 d5」。fアf＝101f+10ア。
# 積が5けたで、外側の4けた（千万…ではなく 1,2,4,5番目）が同じになる (ア,イ) が
# 2つ以上あるものだけを採用する。元の問題は f=2・4 4 ウ 4 4。
def r1_variants(limit=120):
    """R1：虫食い算（積のまん中の1けたが伏せてある）。"""
    out = []
    for f in range(1, 10):
        g = collections.defaultdict(list)
        for a in range(10):
            for b in range(a, 10):
                s = str((101 * f + 10 * a) * (101 * f + 10 * b))
                if len(s) == 5:
                    g[(s[0], s[1], s[3], s[4])].append((a, b, int(s[2])))
        for (d1, d2, d4, d5), sols in sorted(g.items()):
            if not 2 <= len(sols) <= 4:
                continue
            if len({c for _, _, c in sols}) != len(sols):
                continue                        # ウが重なる組は答えがまぎらわしい
            out.append({
                'p': {'f': f, 'd1': d1, 'd2': d2, 'd4': d4, 'd5': d5,
                      'pat': f'{f}-{d1}{d2}{d4}{d5}'},
                'a': ['、'.join(f'（{a}、{b}、{c}）' for a, b, c in sols)],
                '_chk': sols,
            })
    out.sort(key=lambda v: 0 if v['p']['pat'] == '2-4444' else 1)
    return out[:limit]


# ── R2 砂糖水（濃度）─────────────────────────────────────────
# c0%の砂糖水 Wg に cl%をAg、ch%をBg 混ぜて P%。
# 同じWgに cl%をBg、ch%をAg 混ぜて Q%。
#   (1) PとQを混ぜた濃さ ＝ (P+Q)/2       （重さが等しいので平均）
#   (2) 和差算で A+B と B−A を出す
R2_CONC = [(5, 2, 11), (6, 3, 12), (4, 1, 10), (5, 1, 9),
           (8, 4, 14), (6, 2, 10), (7, 3, 13), (4, 2, 12)]
R2_W = [80, 60, 100, 120]
_DEC3 = {1, 2, 4, 5, 8, 10, 20, 25, 40, 50, 100, 125, 200, 250, 500, 1000}


def r2_variants(limit=120):
    """R2：2通りの混ぜ方からAとBを求める。"""
    out = []
    for W in R2_W:
        for c0, cl, ch in R2_CONC:
            for A in range(20, 401, 20):
                for B in range(A + 20, 401, 20):
                    S = W + A + B
                    P = F(c0 * W + cl * A + ch * B, S)
                    Q = F(c0 * W + cl * B + ch * A, S)
                    M = (P + Q) / 2
                    if P.denominator not in _DEC3 or Q.denominator not in _DEC3:
                        continue
                    if M.denominator not in _DEC3 or M.denominator > 100:
                        continue
                    if not (cl < Q < P < ch):
                        continue
                    out.append({
                        'p': {'W': W, 'c0': num(F(c0)), 'cl': num(F(cl)),
                              'ch': num(F(ch)), 'P': num(P), 'Q': num(Q),
                              'key': f'{W}-{c0}-{cl}-{ch}-{A}-{B}'},
                        'a': [num(M) + ' %', f'{A} g', f'{B} g'],
                        '_chk': (A, B, S),
                    })
    out.sort(key=lambda v: 0 if v['p']['key'] == '80-5-2-11-180-220' else 1)
    return out[:limit]


# ── R3 缶詰（場合の数）───────────────────────────────────────
# 4つのクラスで合計T個。(1) 1組がm個のときの残り3クラス、(2) 全クラス1個以上、
# (3) 全クラス1個以上U個以下。
def _r3_count(T, k, lo, hi):
    """k人にT個を配る通り数（各人 lo〜hi 個）を直接数える。"""
    ways = [0] * (T + 1)
    ways[0] = 1
    for _ in range(k):
        nxt = [0] * (T + 1)
        for s, w in enumerate(ways):
            if not w:
                continue
            for x in range(lo, min(hi, T - s) + 1):
                nxt[s + x] += w
        ways = nxt
    return ways[T]


def r3_variants(limit=120):
    """R3：缶詰の集め方。"""
    out = []
    for T in (15, 13, 14, 16, 17, 18):
        for m in range(max(4, T // 2), T):
            for U in range(T // 4 + 2, T - 3):
                a1 = _r3_count(T - m, 3, 0, T - m)
                a2 = _r3_count(T, 4, 1, T)
                a3 = _r3_count(T, 4, 1, U)
                if not (1 < a1 < 200 and a3 < a2):
                    continue
                out.append({
                    'p': {'T': T, 'm': m, 'U': U, 'key': f'{T}-{m}-{U}'},
                    'a': [f'{a1} 通り', f'{a2} 通り', f'{a3} 通り'],
                    '_chk': (a1, a2, a3),
                })
    out.sort(key=lambda v: 0 if v['p']['key'] == '15-9-8' else 1)
    return out[:limit]


# ── R4 すれちがい（速さ）─────────────────────────────────────
# 長さLの道をP→Qと往復。次朗は分速vj、太朗は分速vt、どちらもT分間。
# **vj×T＝2L**（次朗がちょうど1往復）に固定する。元の問題もこの形。
#
# 折り返しをのばして考えると、2人が向かい合って出会うのは
#   (vt+vj)×t ＝ 2L×k （k＝1,2,…）
# のときだけ。ただしその場所がP地点かQ地点になる k は「すれちがい」ではない。
def _r4_meet(L, vj, vt, T):
    """すれちがう場所（Pからの距離・分数）を順に並べて返す。"""
    s = vt + vj
    K = (T * s) // (2 * L)
    pos = []
    for k in range(1, K + 1):
        u = F(2 * k * vt, s)                 # 進んだ道のり ÷ L
        r = u % 2
        d = r if r <= 1 else 2 - r
        if d == 0 or d == 1:                 # P地点・Q地点での折り返しは除く
            continue
        pos.append(d * L)
    return pos


R4_BASE = [(50, 24), (40, 30), (60, 20), (50, 32), (60, 25),
           (80, 20), (40, 25), (70, 20), (50, 20), (60, 30)]


def r4_variants(limit=120):
    """R4：往復する2人のすれちがい。"""
    out = []
    for vj, T in R4_BASE:
        L = vj * T // 2
        if vj * T != 2 * L:
            continue
        cand = [v for v in range(vj * 3, vj * 9 + 1, 10) if v % 10 == 0]
        for v1 in cand:
            p1 = _r4_meet(L, vj, v1, T)
            if not (3 <= len(p1) <= 6) or len(set(p1)) != len(p1):
                continue                      # (1)は「何か所」。場所が重ならない組だけ
            for v2 in cand:
                if v2 == v1:
                    continue
                p2 = _r4_meet(L, vj, v2, T)
                u2 = sorted(set(p2))
                if not (2 <= len(u2) <= 3) or len(p2) <= len(u2):
                    continue                  # (2)は同じ場所を何度も通る組だけ
                if any(x.denominator != 1 for x in u2):
                    continue                  # 答えは整数mだけ
                for n in (9, 8, 10, 11):
                    lo, hi = vj * (n - 1), vj * n
                    tail = '未満' if n % 2 else '以下'
                    out.append({
                        'p': {'L': L, 'vj': vj, 'T': T, 'v1': v1, 'v2': v2, 'n': n,
                              'key': f'{vj}-{T}-{v1}-{v2}-{n}'},
                        'a': [f'{len(p1)} か所'] +
                             [f'{int(x)} m' for x in u2] + [''] * (3 - len(u2)) +
                             [f'{lo} m より大きく', f'{hi} m {tail}'],
                        '_chk': (len(p1), u2, lo, hi, tail),
                    })
    out.sort(key=lambda v: 0 if v['p']['key'] == '50-24-180-250-9' else 1)
    return out[:limit]


# ── R5 台紙にはる2枚の長方形（平面図形）──────────────────────
# 台紙は たてH・横W（W＝H+1、Hは奇数）。左上と右下に合同な長方形をはる。
#   重なり ＝ (左上の横＋右下の横−W)×(左上のたて＋右下のたて−H)
#   (1) 同じ向き  … (2p−W)(2q−H)＝A。たて側は奇数・横側は偶数
#   (2) 左上を横の向きに … 直角向きなら (s−W)(s−H)＝A（連続する2数の積）
#       公式解説はここに (1) の答えを足している（nnop6_notes.md 参照）
def _r5_sets(W, H, A):
    same = [(p, q) for p in range(1, W + 1) for q in range(1, H + 1)
            if p != q and 2 * p - W > 0 and 2 * q - H > 0
            and (2 * p - W) * (2 * q - H) == A]
    ss = [x for x in range(W + 1, 2 * H + 1) if (x - W) * (x - H) == A]
    perp = []
    if ss:
        s = ss[0]
        perp = [(p, s - p) for p in range(1, s)
                if p < s - p and p <= H and s - p <= H]
    return same, perp, (ss[0] if ss else None)


def r5_variants(limit=120):
    """R5：重なりの面積から2辺の長さをしぼりこむ。"""
    out = []
    for H in (11, 9, 13, 15, 17):
        W = H + 1
        for A in (30, 12, 42, 56, 72):
            same, perp, s = _r5_sets(W, H, A)
            if not same or not perp or len(same) > 4:
                continue
            e1, e2 = H - 1, 5                    # 図2の例（直角向き）
            if e1 == e2 or e1 + e2 == s or e1 + e2 <= W:
                continue
            ex = (e1 + e2 - W) * (e1 + e2 - H)
            out.append({
                'p': {'W': W, 'H': H, 'A': A, 'e1': e1, 'e2': e2, 'EX': ex,
                      'key': f'{H}-{A}'},
                'a': [f'{len(same)} 通り', f'{len(same) + len(perp)} 通り'],
                '_chk': (same, perp, s, ex),
            })
    out.sort(key=lambda v: 0 if v['p']['key'] == '11-30' else 1)
    return out[:limit]


# ── R6 / R6a ふるい（規則性）────────────────────────────────
# 1〜N を横6個ずつ並べる。「1」と「2以外の2の倍数」「3以外の3の倍数」を消すと、
# 各行にはA列(6n−5)とE列(6n−1)だけが残る（1行目だけは2・3・5の3個）。
def _r6_sieve(N, primes):
    alive = set(range(2, N + 1))
    for p in primes:
        alive -= {x for x in alive if x % p == 0 and x != p}
    return alive


def _r6_rows(alive, N, cols=6):
    r = collections.Counter((x - 1) // cols + 1 for x in alive)
    return r


def _r6_all(limit=120):
    out = []
    for N in (600, 480, 540, 660, 720, 900):
        rows = N // 6
        a23 = _r6_sieve(N, (2, 3))
        a235 = _r6_sieve(N, (2, 3, 5))
        a2357 = _r6_sieve(N, (2, 3, 5, 7))
        c2 = sum(1 for v in _r6_rows(a235, N).values() if v == 2)
        c3 = len(a235)
        c4 = sum(1 for v in _r6_rows(a2357, N).values() if v == 2)
        byrow = collections.defaultdict(list)
        for x in a23:
            byrow[(x - 1) // 6 + 1].append(x)
        for n in (30, 12, 18, 25, 40, 50, 60, 75):
            if not (2 <= n <= rows):
                continue
            S = sum(byrow[n])
            if len(byrow[n]) != 2:
                continue
            out.append({
                'p': {'N': N, 'rows': rows, 'S': S, 'key': f'{N}-{S}'},
                '_a123': [f'{n} 行目', f'{c2} 行', f'{c3} 個'],
                '_a4': [f'{c4} 行'],
                '_chk': (n, c2, c3, c4),
            })
    out.sort(key=lambda v: 0 if v['p']['key'] == '600-354' else 1)
    return out[:limit]


def r6_variants(limit=120):
    """R6：ふるいの(1)(2)(3)。"""
    return [{'p': v['p'], 'a': v['_a123'], '_chk': v['_chk']} for v in _r6_all(limit)]


def r6a_variants(limit=120):
    """R6a：ふるいの(4)。"""
    return [{'p': v['p'], 'a': v['_a4'], '_chk': v['_chk']} for v in _r6_all(limit)]


VARIANTS6 = {'R1': r1_variants, 'R2': r2_variants, 'R3': r3_variants,
             'R4': r4_variants, 'R5': r5_variants, 'R6': r6_variants,
             'R6a': r6a_variants}

# 計算欄の高さ（mm）。元の問題用紙を A3＝420mm として実測した値（tools/nnop6_notes.md）。
#   0 を入れると「計算欄なし（答だけ）」になる。
WORK_MM6 = {
    'op5-1': 68,
    'op5-2-1': 0, 'op5-2-2': 70,
    'op5-3-1': 48, 'op5-3-2': 47, 'op5-3-3': 75,
    'op5-4-1': 45, 'op5-4-2': 43, 'op5-4-3': 60,
    'op5-5-1': 47, 'op5-5-2': 60,
    'op5-6-1': 60, 'op5-6-2': 53, 'op5-6-3': 44,
    'op5-6-4': 90,
}


# ══════════════════════════════════════════════════════════════════
# 設問マスタ
# ══════════════════════════════════════════════════════════════════
_R6_INTRO = ('下の表のように、1から順に{N}まで整数を横に6個ずつ並べました。'
             'この表を使って、あるきまりで数を消していく作業を行います。'
             '左から1番目の列をA列、2番目の列をB列……6番目の列をF列と呼ぶことにします。')

GROUPS6 = [
    {
        'key': 'R1', 'round': 5, 'field': 'numth', 'title': '虫食い算', 'vary': True,
        'intro': '', 'body': '', 'fig': None,
        'subs': [
            {'id': 'op5-1', 'label': '',
             'q': '次の式が成り立つとき、整数ア、イ、ウにあてはまる1けたの整数の'
                  '組み合わせをすべて答えなさい。ただし、アはイ以下の整数であるものとします。'
                  '<div class="mishiki">{f}［ア］{f} × {f}［イ］{f} ＝ '
                  '{d1}{d2}［ウ］{d4}{d5}</div>',
             'rate': 60, 'score': 5, 'ans': ['（ア、イ、ウ）＝'],
             'how': 'かけられる数もかける数も{f}□{f}の形なので、いちばん小さいのは'
                    '{f}0{f}。積は{d1}{d2}000以上{d1}{d2}999以下だから、'
                    '大きいほうの数がどこまで大きくなれるかで候補をしぼる。'
                    'アはイ以下なので、残った候補の組だけを筆算で確かめればよい。'},
        ],
    },
    {
        'key': 'R2', 'round': 5, 'field': 'dens', 'title': '2通りの混ぜ方と砂糖水',
        'vary': True,
        'intro': '{c0}%の砂糖水{W}gに{cl}%の砂糖水をAg、{ch}%の砂糖水をBg加えて混ぜると、'
                 '濃さが{P}%の砂糖水Pができました。また、{c0}%の砂糖水{W}gに'
                 '{cl}%の砂糖水をBg、{ch}%の砂糖水をAg加えて混ぜると、'
                 '濃さが{Q}%の砂糖水Qができました。ただし、砂糖水の濃さとは、'
                 '砂糖水の重さに対する砂糖の重さの割合のことです。以下の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op5-2-1', 'label': '(1)',
             'q': '砂糖水PとQを混ぜ合わせると、何%の濃さになりますか。',
             'rate': 90, 'score': 2, 'ans': [''],
             'how': 'PとQは重さが同じ（どちらも{W}＋A＋Bg）なので、'
                    '混ぜた濃さは2つの濃さのちょうど真ん中になる。'},
            {'id': 'op5-2-2', 'label': '(2)',
             'q': 'A、Bにあてはまる数を求めなさい。',
             'rate': 18, 'score': 4, 'ans': ['A', 'B'],
             'how': 'PとQを合わせると、{c0}%が{W}×2g、{cl}%と{ch}%が'
                    'どちらも（A＋B）gになる。(1)の濃さを使ったてんびん図で'
                    'A＋Bが出る。次に、PとQの濃さの差は'
                    '（{ch}−{cl}）%ぶんの砂糖がA と B で入れかわったぶんなので、'
                    'B−Aが出る。あとは和差算。'},
        ],
    },
    {
        'key': 'R3', 'round': 5, 'field': 'case', 'title': '缶詰の集め方', 'vary': True,
        'intro': 'ある小学校でフードドライブ（家庭で余っている食品を持ち寄る活動）が'
                 '行われ、5年生の4つのクラス（1組、2組、3組、4組）で合計{T}個の缶詰が'
                 '集まりました。各クラスが集めた缶詰の個数について、次の問いに答えなさい。'
                 'ただし、缶詰が0個のクラスがあってもよいものとします。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op5-3-1', 'label': '(1)',
             'q': '1組が{m}個の缶詰を集めたとき、残り3つのクラス（2組、3組、4組）の'
                  '缶詰の集まり方は全部で何通りありますか。',
             'rate': 70, 'score': 3, 'ans': [''],
             'how': '残りは{T}−{m}個。これを3つのクラスに分けるので、'
                    '○を{T}−{m}個ならべて仕切り2本を入れる場所の選び方を数える。'},
            {'id': 'op5-3-2', 'label': '(2)',
             'q': 'どのクラスも必ず1個以上の缶詰を集めたとき、4つのクラスの缶詰の'
                  '集まり方は全部で何通りありますか。',
             'rate': 32, 'score': 4, 'ans': [''],
             'how': '○を{T}個ならべ、すきま（{T}−1か所）から仕切り3本の場所を選ぶ。'},
            {'id': 'op5-3-3', 'label': '(3)',
             'q': 'どのクラスが集めた缶詰の個数も1個以上{U}個以下であったとき、'
                  '4つのクラスの缶詰の集まり方は全部で何通りありますか。',
             'rate': 6, 'score': 5, 'ans': [''],
             'how': '(2)から「どれか1つのクラスが{U}個をこえる場合」を引く。'
                    'そのクラスに先に{U}＋1個わたしてから残りを配ると考えると数えやすい。'
                    '2つのクラスが同時にこえることがないかも確かめる。'},
        ],
    },
    {
        'key': 'R4', 'round': 5, 'field': 'speed', 'title': '往復する2人のすれちがい',
        'vary': True,
        'intro': 'P地点とQ地点を結ぶ{L}mのまっすぐな道があります。太朗君は自転車で、'
                 '次朗君は分速{vj}mで歩いて同時にP地点を出発し、P地点とQ地点の間を'
                 '休まず{T}分間進みます。2人はそれぞれ一定の速さで進み、'
                 'P地点・Q地点に着くとすぐに折り返します。「すれちがう」とは、'
                 '反対方向から向かい合って進んできた2人が出会うことを指します。'
                 '以下の問いに答えなさい。',
        'body': '', 'fig': None,
        'subs': [
            {'id': 'op5-4-1', 'label': '(1)',
             'q': '太朗君の速さを分速{v1}mとするとき、2人がすれちがう地点は'
                  '全部で何か所ありますか。',
             'rate': 56, 'score': 3, 'ans': [''],
             'how': '2人が向かい合って出会うのは、2人の進んだ道のりの合計が'
                    '{L}×2mふえるごとに1回。ただし、その場所がP地点やQ地点に'
                    'なってしまうときは「すれちがい」ではないので除く。'},
            {'id': 'op5-4-2', 'label': '(2)',
             'q': '太朗君の速さを分速{v2}mとするとき、2人がすれちがった地点は'
                  'P地点から何m離れていますか。ただし、答えの欄はすべて使うとは限りません。',
             'rate': 49, 'score': 4, 'ans': ['', '', ''],
             'how': '(1)と同じく、道のりの合計が{L}×2mふえるたびの時刻を出し、'
                    'そのときの太朗君の位置を折り返しを考えながら求める。'
                    '同じ場所を何度も通ることがあるので、場所は重ならないようにまとめる。'},
            {'id': 'op5-4-3', 'label': '(3)',
             'q': '2人が全部で{n}回すれちがうとき、太朗君の速さの範囲を答えなさい。'
                  '答は「以上」または「より大きく」のいずれか、「以下」または「未満」の'
                  'いずれかをそれぞれ○で囲んで答えなさい。',
             'rate': 13, 'score': 4, 'ans': ['分速', '分速'],
             'how': '{T}分間に2人が進む道のりの合計は（太朗君の分速＋{vj}）×{T}m。'
                    'これが{L}×2mの何個ぶんかが、すれちがいの回数のもとになる。'
                    'ちょうど割り切れるときは出会う場所がP地点・Q地点になって'
                    '回数が減るので、はしをふくむかどうかを1つずつ確かめる。'},
        ],
    },
    {
        'key': 'R5', 'round': 5, 'field': 'plane', 'title': '台紙にはる2枚の長方形',
        'vary': True,
        'intro': '図1のような、たて{H}cm、横{W}cmの長方形の台紙ABCDがあります。'
                 'これに、別の2枚の合同な長方形をはりつけます。はりつける長方形は、'
                 'たての長さも横の長さも整数とし、正方形は長方形に含まないものとします。'
                 '1枚は長方形の左の辺が辺ABに、上の辺が辺ADに重なるようにし、'
                 'もう1枚の長方形は右の辺が辺DCに、下の辺が辺BCに重なるように'
                 'はりつけます。例えば、下の図2は2辺の長さが{e2}cm、{e1}cmの2枚の'
                 '長方形をはりつけたもので、ぬりつぶされた部分は、2枚の長方形の'
                 '重なりの部分で、面積は{EX}cm<sup>2</sup>です。以下の問いに答えなさい。',
        'body': '', 'fig': 'dai:{W}x{H}x{e1}x{e2}', 'figpos': 'bottom',
        'subs': [
            {'id': 'op5-5-1', 'label': '(1)',
             'q': '2枚の長方形を同じ向きに置いたところ、重なりの部分の面積が'
                  '{A}cm<sup>2</sup>になりました。このとき、長方形の2辺として'
                  '考えられる長さの組み合わせは全部で何通りありますか。',
             'rate': 32, 'score': 4, 'ans': [''],
             'how': '長方形の横を□、たてを△とすると、重なりの横は□×2−{W}、'
                    'たては△×2−{H}。{H}は奇数なので重なりのたては奇数、'
                    '重なりの横は偶数。{A}を「偶数×奇数」に分ける分け方から'
                    '□と△を出す（台紙からはみ出す組は除く）。'},
            {'id': 'op5-5-2', 'label': '(2)',
             'q': '辺AB、辺ADに重なるように置く方の長方形を横の向きにして'
                  '2枚の長方形を置いたところ、重なりの部分の面積が'
                  '{A}cm<sup>2</sup>になりました。このとき、長方形の2辺として'
                  '考えられる長さの組み合わせは全部で何通りありますか。',
             'rate': 4, 'score': 5, 'ans': [''],
             'how': '2枚が直角の向きになるときは、2辺を□と△として'
                    '重なりの横が□＋△−{W}、たてが□＋△−{H}。'
                    'この2つは1だけちがうので、{A}を「連続する2つの数の積」に'
                    '分ければ□＋△が決まる。(1)で求めた置き方も答えに入れること。'},
        ],
    },
    {
        'key': 'R6', 'round': 5, 'field': 'rule', 'title': '表から数を消していく',
        'vary': True,
        'intro': _R6_INTRO,
        'body': '', 'fig': 'sieve:{N}', 'figpos': 'bottom',
        'subs': [
            {'id': 'op5-6-1', 'label': '(1)',
             'q': 'はじめに、表の中の「1」を消します。次に、「2以外の2の倍数」と'
                  '「3以外の3の倍数」をすべて消しました。このとき、同じ行に残っている'
                  '2つで、それらの数の和がちょうど{S}になるのは、何行目ですか。',
             'rate': 79, 'score': 4, 'ans': [''],
             'how': '2でも3でも割り切れない数はA列とE列にしか出てこない。'
                    'その2つは4だけちがうので、和{S}との和差算で2つの数が決まる。'},
            {'id': 'op5-6-2', 'label': '(2)',
             'q': '(1)に続けて、さらに「5以外の5の倍数」をすべて消す作業を行います。'
                  'このとき、同じ行に2つの数だけが消されずに残っている行は、'
                  '全部で何行ありますか。',
             'rate': 49, 'score': 4, 'ans': [''],
             'how': 'A列・E列の数が5の倍数になる行は5行ごとにあらわれる。'
                    '5行をひとまとまりにして、そのうち何行が2つとも残るかを数える。'
                    '1行目は2・3・5が残るので別あつかい。'},
            {'id': 'op5-6-3', 'label': '(3)',
             'q': '(2)のとき、表に残っている数は全部で何個ですか。',
             'rate': 35, 'score': 4, 'ans': [''],
             'how': '2でも3でも5でも割り切れない数は、30個ごとに8個ある。'
                    '{N}÷30を使って数え、消さずに残した2・3・5と、'
                    'はじめに消した1のぶんを調整する。'},
        ],
    },
    {
        'key': 'R6a', 'round': 5, 'field': 'rule', 'title': '表から数を消していく',
        'vary': True,
        'intro': _R6_INTRO,
        'body': '', 'fig': 'sieve:{N}', 'figpos': 'bottom',
        'subs': [
            {'id': 'op5-6-4', 'label': '(4)',
             'q': '表の中の「1」を消し、次に「2以外の2の倍数」「3以外の3の倍数」'
                  '「5以外の5の倍数」「7以外の7の倍数」をすべて消す作業を行いました。'
                  'このとき、同じ行に2つの数だけが消されずに残っている行は、'
                  '全部で何行ありますか。',
             'rate': 4, 'score': 5, 'ans': [''],
             'how': '5までのふるいが終わった時点で2つ残る行は5行ごとに3行ある。'
                    'そこからA列・E列の数が7の倍数になる行を取り除く。'
                    '7の倍数になる行は7行ごとにあらわれるので、'
                    '5と7の最小公倍数の35行をひとまとまりにして数える。'
                    '7そのものは消さないことに注意。'},
        ],
    },
]


if __name__ == '__main__':
    for k, fn in VARIANTS6.items():
        vs = fn()
        ex = vs[0]['a'] if vs else '（まだ空）'
        print(f'{k}: {len(vs):4}通り　例 {ex}')
