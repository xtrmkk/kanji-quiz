# -*- coding: utf-8 -*-
"""第4回の独立検算と、元の数値での回帰テスト。

生成器が使った式をそのまま使い回すと、式がまちがっていても一致してしまう。
ここでは**別の原理**で解き直して突き合わせる（nnop_spec.md 7.1 / 13章）。

  M1  … 台数を0から全部ためして、問題文の条件に合う組が1つだけか確かめる
  M2  … 座標をとって靴ひも公式で面積を実測し、Hは「面積が等しくなる点」として求め直す
  M3  … 三角形を座標から組み直し、10個すべての面積を靴ひも公式ではかる
  M4  … 出会いを1回ずつ進めて○の位置を実際に並べ、そこから数え直す
  M5  … 並べ方を全列挙して数える
  M6  … 列を「繰り返しに入るまで」と「1周期」に分け、閉じた式で項・個数を出し直す
"""
import itertools
from fractions import Fraction as F
from math import gcd

import nnop5_data as DX
from nnop_data import num, frac_html, improper_html
from nnop_fig import rect3_parts


def _shoelace(pts):
    s = F(0)
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


# ══════════════════════════════════════════════════════════════════
def verify_m1(vs):
    """M1：台数を0から全部ためして、問題文の条件に合う組を直接さがす。"""
    for v in vs:
        p = v['p']
        cA, cB, N = p['cA'], p['cB'], p['N']
        tA, tB = p['pA'] + p['mA'], p['pB'] + p['mB']
        h1 = [a for a in range(N + 1) if cA * a + cB * (N - a) == p['P1']]
        h2 = [a for a in range(N + 1) if cA * a - cB * (N - a) == p['P2']]
        h3 = [a for a in range(N + 1) if tA * a + tB * (N - a) == p['T']]
        assert len(h1) == len(h2) == len(h3) == 1, (p, h1, h2, h3)
        a1, a2, a3 = h1[0], h2[0], h3[0]
        assert 2 <= min(a1, a2, a3) and max(a1, a2, a3) <= N - 2, p
        got = [f'{a1} 台', f'{N - a1} 台', f'{a2} 台', f'{N - a2} 台',
               f'{cA * a3 + cB * (N - a3)} 皿']
        assert got == v['a'], (p, got, v['a'])
        assert (a1, a2, a3) == v['_chk'][:3]
    return len(vs)


def _signed(pts):
    """符号つきの面積（uの1次式になるので、面積の条件をそのまま解ける）。"""
    s = F(0)
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += x1 * y2 - x2 * y1
    return s / 2


def _ratio(a: F, b: F):
    den = a.denominator * b.denominator // gcd(a.denominator, b.denominator)
    x, y = int(a * den), int(b * den)
    g = gcd(x, y)
    return x // g, y // g


def verify_m2(vs):
    """M2：座標をとり、靴ひも公式で面積をはかって比を出し直す。

    Hは「三角形GHCの面積が三角形AGFと等しくなる点」として、
    符号つき面積の1次方程式を解いて求める（生成器が使った比の式は使わない）。
    """
    for v in vs:
        m, n = v['p']['m'], v['p']['n']
        L = m + n
        A, D = (F(0), F(0)), (F(L), F(0))
        B, C = (F(1), F(-2)), (F(L + 1), F(-2))      # ずらしても比は変わらない
        Fp = (F(m), F(0))
        # G＝直線ACと直線FBの交点を連立で解く
        #   A + s(C−A) = F + u(B−F)  の y 成分から s = u、x 成分から s を決める
        s = F(m, (L + 1) - (1 - m))
        G = (s * C[0], s * C[1])
        aAGF = _shoelace([A, G, Fp])
        onFB = lambda u: (Fp[0] + u * (B[0] - Fp[0]), Fp[1] + u * (B[1] - Fp[1]))
        g0, g1 = _signed([G, onFB(F(0)), C]), _signed([G, onFB(F(1)), C])
        cand = [(t - g0) / (g1 - g0) for t in (aAGF, -aAGF)]
        tG = (G[0] - Fp[0]) / (B[0] - Fp[0]) if B[0] != Fp[0] \
            else (G[1] - Fp[1]) / (B[1] - Fp[1])
        hits = [u for u in cand if tG < u <= 1]
        assert len(hits) == 1, (m, n, cand, tG)
        uH = hits[0]
        H = onFB(uH)
        assert _shoelace([G, H, C]) == aAGF, (m, n)
        r = [tG, uH - tG, 1 - uH]
        den = 1
        for x in r:
            den = den * x.denominator // gcd(den, x.denominator)
        ri = [int(x * den) for x in r]
        g = gcd(gcd(ri[0], ri[1]), ri[2])
        ri = [x // g for x in ri]
        q, t = _shoelace([Fp, G, C, D]), _shoelace([H, B, C])
        got = [' : '.join(map(str, ri)),
               ' : '.join(map(str, _ratio(q, t)))]
        assert got == v['a'], (m, n, got, v['a'])
        assert [ri, list(_ratio(q, t))] == [v['_chk'][0], v['_chk'][1]]
    return len(vs)


def verify_m3(vs):
    """M3：三角形を座標から組み直し、全部の面積を靴ひも公式ではかる。"""
    for v in vs:
        k = v['p']['k']
        a, x, tris = rect3_parts(k)
        pts = {'P': (F(0), F(1)), 'S': (F(1), F(1)),
               'B0': (F(0), F(0)), f'B{k}': (F(1), F(0))}
        for i, ai in enumerate(a, 1):
            pts[f'V{i}'] = (ai, 1 - ai)
        for i, xi in enumerate(x, 1):
            pts[f'B{i}'] = (xi, F(0))
        ar = [_shoelace([pts[t] for t in tri]) for tri in tris]
        assert sum(ar) == 1, (k, sum(ar))          # 長方形（面積1）をうめつくす
        eq = ar[:2 * k] + [ar[-1]]
        assert len(set(eq)) == 1 and eq[0] == F(1, 4 * k), (k, eq)
        i = DX.KANA.index(v['p']['ASK'])
        assert frac_html(ar[i]) + ' 倍' == v['a'][0], (k, i, v['a'])
        assert ar[i] == v['_chk'][0]
    return len(vs)


def verify_m4(vs):
    """M4：出会いを1回ずつ進めて○の位置を実際に並べ、そこから数え直す。"""
    for v in vs:
        p = v['p']
        for L, vA, vB, tag in ((p['L1'], p['vA1'], p['vB1'], 'A'),
                               (p['L2'], p['vA2'], p['vB2'], 'B')):
            pos, x, seen = [], 0, set()
            for _ in range(4000):
                x = (x + F(L * vA, vA + vB)) % L
                if x in seen:
                    break
                seen.add(x)
                pos.append(x)
            else:
                raise AssertionError(('○が閉じない', p))
            assert all(q.denominator == 1 for q in pos), (p, '○が整数mmでない')
            if tag == 'A':
                step = F(L * vA, vA + vB)
                assert v['a'][0] == f'{int(step * p["t"] % L)} mm', (p, v['a'])
                assert v['a'][1] == f'{len(pos)} か所', (p, len(pos))
            else:
                far = max(min(q, L - q) for q in pos)
                assert len(pos) % 2 == 1, (p, '○の数が偶数')
                assert v['a'][2] == f'{int(far)} mm', (p, far, v['a'])
    return len(vs)


_M5_CACHE = {}


def _m5_brute(n, d):
    """1を位置0に固定して並べ方を全列挙し、(3が置ける位置, 総数, 和がdの倍数) を返す。"""
    key = (n, d)
    if key in _M5_CACHE:
        return _M5_CACHE[key]
    rest = list(range(2, n + 1))
    total = 0
    okdiv = 0
    where = {c: set() for c in range(1, n + 1)}
    for perm in itertools.permutations(rest):
        row = (1,) + perm
        if any((row[i] + row[(i + 1) % n]) % 2 == 0 for i in range(n)):
            continue
        total += 1
        for i, c in enumerate(row):
            where[c].add(i)
        if (row[1] + row[-1]) % d == 0:
            okdiv += 1
    _M5_CACHE[key] = (where, total, okdiv)
    return _M5_CACHE[key]


def _m5_brute_big(n, d):
    """大きいnは、奇数の席と偶数の席に分けてから並べ方を全列挙する。

    「奇数と偶数が交互に並ぶ」ことはn=6,8の総当たり（_m5_brute）で確かめてある。
    """
    key = ('big', n, d)
    if key in _M5_CACHE:
        return _M5_CACHE[key]
    odds = list(range(3, n + 1, 2))
    evens = list(range(2, n + 1, 2))
    total = okdiv = 0
    row = [0] * n
    row[0] = 1
    for op in itertools.permutations(odds):
        for i, c in enumerate(op):
            row[2 * (i + 1)] = c
        for ep in itertools.permutations(evens):
            for i, c in enumerate(ep):
                row[2 * i + 1] = c
            if any((row[i] + row[(i + 1) % n]) % 2 == 0 for i in range(n)):
                continue
            total += 1
            if (row[1] + row[-1]) % d == 0:
                okdiv += 1
    _M5_CACHE[key] = (total, okdiv)
    return _M5_CACHE[key]


def verify_m5(vs):
    """M5：並べ方を全列挙して数える。"""
    for v in vs:
        p = v['p']
        where, _, _ = _m5_brute(p['n1'], 4)
        labs = sorted(chr(ord('A') + i - 1) for i in where[p['card']])
        assert '、'.join(labs) == v['a'][0], (p, labs, v['a'])
        if p['n2'] <= 8:
            _, total, _ = _m5_brute(p['n2'], 4)
        else:
            total, _ = _m5_brute_big(p['n2'], 4)
        assert f'{total} 通り' == v['a'][1], (p, total, v['a'])
        if p['n3'] <= 8:
            _, _, okdiv = _m5_brute(p['n3'], p['d'])
        else:
            _, okdiv = _m5_brute_big(p['n3'], p['d'])
        assert f'{okdiv} 通り' == v['a'][2], (p, okdiv, v['a'])
    return len(vs)


# ── M6：列を「繰り返しに入るまで」と「1周期」に分けて閉じた式で解き直す ──
def _blocks(nxt, start):
    """一の位が一周するまでをたどり、(前置きの項, 1周期の項, 1周期の増分) を返す。"""
    seen, terms, x = {}, [], start
    while (x % 10) not in seen:
        seen[x % 10] = len(terms)
        terms.append(x)
        x = nxt(x)
    t0 = seen[x % 10]
    cyc = terms[t0:]
    return terms[:t0], cyc, x - terms[t0]


class _Seq:
    def __init__(self, nxt, start):
        self.pre, self.cyc, self.inc = _blocks(nxt, start)
        self.t0, self.c = len(self.pre), len(self.cyc)

    def term(self, i):                      # 0始まり
        if i < self.t0:
            return self.pre[i]
        j = i - self.t0
        return self.cyc[j % self.c] + self.inc * (j // self.c)

    def index(self, v):                     # 0始まり。無ければ None
        if v in self.pre:
            return self.pre.index(v)
        for j, b in enumerate(self.cyc):
            if v >= b and (v - b) % self.inc == 0:
                return self.t0 + j + self.c * ((v - b) // self.inc)
        return None

    def has(self, v):
        return self.index(v) is not None

    def count_upto(self, N):
        c = sum(1 for v in self.pre if v <= N)
        for b in self.cyc:
            if b <= N:
                c += (N - b) // self.inc + 1
        return c


def _m6_check(v):
    p = v['p']
    da, db = p['da'], p['db']
    A = _Seq(lambda x: x + x % da, p['a0'])
    B = _Seq(lambda x: x + (x % 10) % db + 1, p['b0'])
    idx, Nb, cnt = p['idx'], p['Nb'], p['cnt']
    com = [x for x in range(1, Nb + 1) if A.has(x) and B.has(x)]
    near = max(x for x in com)
    only = A.count_upto(Nb) + B.count_upto(Nb) - 2 * len(com)
    # 列の見た目（問題文に出している並び）も閉じた式で出し直す
    alist = '、'.join(str(A.term(i)) for i in range(12)) + '、……'
    blist = '、'.join(str(B.term(i)) for i in range(10)) + '、……'
    assert alist == p['ALIST'] and blist == p['BLIST'], p
    return (A, B, com, near, only, idx, cnt)


def verify_m6(vs):
    """M6：(1)(2)(3)を閉じた式で出し直す。"""
    for v in vs:
        A, B, com, near, only, idx, cnt = _m6_check(v)
        got = [str(A.term(idx - 1)), str(B.term(idx - 1)),
               '、'.join(str(x) for x in com[:cnt])]
        assert got == v['a'], (v['p'], got, v['a'])
    return len(vs)


def verify_m6a(vs):
    """M6a：(4)(5)を閉じた式で出し直す。"""
    for v in vs:
        A, B, com, near, only, idx, cnt = _m6_check(v)
        got = [str(near), f'{A.index(near) + 1} 番目', f'{B.index(near) + 1} 番目',
               f'{only} 個']
        assert got == v['a'], (v['p'], got, v['a'])
        assert v['_chk'][4] == only, v['p']
    return len(vs)


VERIFY5 = {'M1': verify_m1, 'M2': verify_m2, 'M3': verify_m3, 'M4': verify_m4,
           'M5': verify_m5, 'M6': verify_m6, 'M6a': verify_m6a}

# ══════════════════════════════════════════════════════════════════
# 回帰テスト（元の第4回の数値 → 公式解答）
#   値が None の要素は照合しない。params は 'p' の一部だけでよい。
# ══════════════════════════════════════════════════════════════════
OFFICIAL5 = {
    'M1': (['12 台', '13 台', '15 台', '10 台', '178 皿'],
           {'cA': 10, 'cB': 6, 'N': 25, 'P1': 198, 'P2': 90, 'T': 96}),
    'M2': (['15 : 9 : 16', '31 : 16'], {'m': 3, 'n': 2}),
    'M3': (['<span class="fr"><span class="fn">5</span><span class="fd">48</span></span> 倍'],
           {'k': 3, 'ASK': 'ケ'}),
    'M4': (['792 mm', '5 か所', '4356 mm'],
           {'L1': 990, 'vA1': 66, 'vB1': 44, 't': 3,
            'L2': 8910, 'vA2': 69, 'vB2': 66}),
    'M5': (['B、D', '144 通り', '1152 通り'],
           {'n1': 6, 'card': 3, 'n2': 8, 'n3': 10, 'd': 4}),
    'M6': (['126', '79', '13、16、17、19、23'],
           {'a0': 3, 'b0': 5, 'db': 3, 'idx': 50, 'Nb': 1000}),
    'M6a': (['999', '400 番目', '694 番目', '303 個'],
            {'a0': 3, 'b0': 5, 'db': 3, 'idx': 50, 'Nb': 1000}),
}
