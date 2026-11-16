# -*- coding: utf-8 -*-
"""NNOP第3回の独立検算と、元の数値での回帰テスト。

生成器が使った式をそのまま使い回すと、式がまちがっていても一致してしまう。
ここでは**別の原理**で解き直して突き合わせる（nnop_spec.md 7.1）。
"""
import itertools
import math
import re
from fractions import Fraction as F

import nnop3_data as D3


# ── 小道具 ────────────────────────────────────────────────────────
def _parse(html):
    """improper_html / 整数文字列 を Fraction に戻す。"""
    m = re.search(r'<span class="fn">(-?\d+)</span><span class="fd">(\d+)</span>', html)
    return F(int(m.group(1)), int(m.group(2))) if m else F(int(html))


# ══════════════════════════════════════════════════════════════════
# K1 計算問題 … 表示されている分数そのものから計算し直す
# ══════════════════════════════════════════════════════════════════
def verify_k1(vs):
    for v in vs:
        p = v['p']
        f1, f2, f3, f4, f5, f6 = (_parse(p[k]) for k in
                                  ('f1', 'f2', 'f3', 'f4', 'f5', 'f6'))
        val = ((f1 - f2) / (f3 - f4) - (f5 - f6)) * F(p['m'], 2027)
        assert f1 > f2 and f3 > f4 and f5 > f6, p
        assert (f1 - f2) / (f3 - f4) > (f5 - f6), p
        assert _parse(v['a'][0]) == val, (p, v['a'])
        assert val.denominator == 2027, (p, val)
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# K2 池のまわり … 1秒ずつ動かして、追いついた瞬間を直接ひろう
# ══════════════════════════════════════════════════════════════════
def verify_k2(vs):
    for v in vs:
        p = v['p']
        L, va, vb, vc, n = (p[k] for k in ('L', 'va', 'vb', 'vc', 'n'))
        t1, d1, k, gap = v['_chk']
        # 追いつく＝BとAの位置が一致（出発時はのぞく）
        hits = []
        t = 0
        while len(hits) < n:
            t += 1
            if (vb * t - va * t) % L == 0:
                hits.append((t, (va * t) % L))
        assert hits[0] == (t1, d1), (p, hits[0], (t1, d1))
        assert len({h[1] for h in hits}) == k, (p, {h[1] for h in hits}, k)
        tn = hits[n - 1][0]
        assert ((vc * tn) - (va * tn)) % L == gap, p
        assert v['a'] == [f'{t1} 秒後', f'{d1} m', f'{k} か所', f'{gap} m']
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# K3 長方形の中の四角形 … 座標をとって多角形の面積公式で確かめる
# ══════════════════════════════════════════════════════════════════
def _shoelace(pts):
    s = 0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        s += x1 * y2 - x2 * y1
    return abs(F(s, 2))


def _ebfd(ab, bc, ed, df):
    """A(0,ab) D(bc,ab) C(bc,0) B(0,0)、E は AD 上、F は DC 上。"""
    E = (bc - ed, ab)
    D_ = (bc, ab)
    Fp = (bc, ab - df)
    B = (0, 0)
    return _shoelace([E, B, Fp, D_])


def verify_k3(vs):
    for v in vs:
        p = v['p']
        bc = p['AE'] + p['ED']
        s1 = _ebfd(p['AB'], bc, p['ED'], p['DF'])
        assert s1 == v['_chk'][0], (p, s1)
        assert v['a'][0] == f'{int(s1)} cm<sup>2</sup>'
        # (2) 三角形EBF＝S2 となる AB＋BC
        g, S2 = p['g'], p['S2']
        tot = v['_chk'][1]
        # AB＋BC が tot になる組を1つ作って、三角形EBFの面積を実測する
        found = False
        for ab in range(g, tot - g + 1):
            bc2 = tot - ab
            if bc2 < g:
                continue
            E = (bc2 - g, ab)
            Fp = (bc2, ab - g)
            B = (0, 0)
            if _shoelace([E, B, Fp]) == S2:
                found = True
                break
        assert found, ('(2)が成り立つ長方形が無い', p)
        assert v['a'][1] == f'{tot} cm'
        # (3) すべての組で四角形EBFDの面積が S3 になるか、座標で確かめる
        e3, f3, S3 = p['e3'], p['f3'], p['S3']
        sol = v['_chk'][2]
        for ab, bc3 in sol:
            assert _ebfd(ab, bc3, e3, f3) == S3, (p, ab, bc3)
        # 数え落とし・数えすぎが無いか、別のまわし方で全数探索
        again = [(ab, bc3) for ab in range(1, 4 * S3) for bc3 in range(1, 4 * S3)
                 if ab >= f3 and bc3 >= e3 and e3 * ab + f3 * bc3 == 2 * S3]
        assert sorted(again) == sorted(sol), (p, again, sol)
        assert v['a'][2] == f'{len(sol)} 通り'
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# K4 ○と● … 実際に全部の並びを作って数える
# ══════════════════════════════════════════════════════════════════
def verify_k4(vs):
    for v in vs:
        p, q = v['p']['p'], v['p']['q']
        n2, n3 = v['p']['n2'], v['p']['n3']
        seq = '○' * p + '●' * q
        allp = set(itertools.permutations(seq))
        a1 = len(allp)
        a2 = len([x for x in allp if '●' * q in ''.join(x)])
        def run_ok(perm, want, kind):
            s = ''.join('奇' if x % 2 else '偶' for x in perm)
            return (kind * want) not in s
        a3 = sum(1 for x in itertools.permutations(range(1, n2 + 1))
                 if run_ok(x, q, '奇'))
        a4 = sum(1 for x in itertools.permutations(range(1, n3 + 1))
                 if run_ok(x, q, '奇') and run_ok(x, q, '偶'))
        assert (a1, a2, a3, a4) == v['_chk'], (v['p'], (a1, a2, a3, a4), v['_chk'])
        assert v['a'] == [f'{a1} 通り', f'{a2} 通り', f'{a3} 通り', f'{a4} 通り']
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# K5 転がる正三角形 … 実際に転がして、弧を座標で記録する
# ══════════════════════════════════════════════════════════════════
def _perim(d, s):
    """1辺 2s の正方形を時計回りに進んだ距離 d の点。出発点は左上の角。"""
    P = 8 * s
    d %= P
    if d <= 2 * s:
        return (d, 2 * s)
    if d <= 4 * s:
        return (2 * s, 2 * s - (d - 2 * s))
    if d <= 6 * s:
        return (2 * s - (d - 4 * s), 0)
    return (0, d - 6 * s)


def _roll(s, laps=1):
    """正三角形を転がし、各頂点が描く弧 (中心, 始角, 終角) を集める。"""
    tri = {'A': _perim(0, s), 'C': _perim(s, s),
           'B': (s / 2, 2 * s + s * math.sqrt(3) / 2)}
    order = ['C', 'B', 'A']          # 1手目・2手目・3手目の軸
    arcs = {'A': [], 'B': [], 'C': []}
    for i in range(1, 8 * laps + 1):
        piv = order[(i - 1) % 3]
        ang = 210 if i % 2 == 0 else 120          # 正方形の角では90°多く回る
        cx, cy = tri[piv]
        th = -math.radians(ang)                   # 時計回り
        for k in 'ABC':
            if k == piv:
                continue
            x, y = tri[k]
            a0 = math.atan2(y - cy, x - cx)
            nx = cx + (x - cx) * math.cos(th) - (y - cy) * math.sin(th)
            ny = cy + (x - cx) * math.sin(th) + (y - cy) * math.cos(th)
            arcs[k].append(((round(cx, 6), round(cy, 6)), a0, a0 + th))
            tri[k] = (nx, ny)
        # 軸の頂点が次に接する点へ（位置は変わらない）
        assert abs(math.dist(tri[piv], _perim(i * s, s))) < 1e-6, (i, tri[piv])
    return arcs


def _covered(arcs_by_vertex):
    """3本の道のうち2本以上が重なっている角度の合計（度）。"""
    from collections import defaultdict
    per_center = defaultdict(lambda: defaultdict(list))
    for v, lst in arcs_by_vertex.items():
        for c, a0, a1 in lst:
            lo, hi = sorted((a0, a1))
            per_center[c][v].append((lo, hi))
    total = 0.0
    for c, byv in per_center.items():
        # 角度を細かく刻んで、何本の道が通っているか数える
        edges = sorted({x for lst in byv.values() for seg in lst for x in seg})
        for lo, hi in zip(edges, edges[1:]):
            mid = (lo + hi) / 2
            n = sum(1 for v, lst in byv.items()
                    if any(a <= mid <= b for a, b in lst))
            if n >= 2:
                total += math.degrees(hi - lo)
    return total


def verify_k5(vs):
    for v in vs:
        s = v['p']['s']
        arcs = _roll(s, laps=1)
        degA = sum(abs(math.degrees(a1 - a0)) for _, a0, a1 in arcs['A'])
        assert abs(degA - 990) < 1e-6, (s, degA)
        dbl = _covered(arcs)
        assert abs(dbl - 840) < 1e-4, (s, dbl)
        a1 = F(314, 100) * 2 * s * F(990, 360)
        a2 = F(314, 100) * 2 * s * F(840, 360)
        assert (a1, a2) == v['_chk'], v['p']
        assert v['a'] == [f'{D3.num(a1)} cm', f'{D3.num(a2)} cm']
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# K6 数表Aと数列B … 公式で出し直して、並べて作った列と突き合わせる
# ══════════════════════════════════════════════════════════════════
def _tri(k):
    return k * (k + 1) // 2


def _k6_formula(N, nrow):
    """最終段が欠けていてもよいように、段の端を N で打ち切って出す。"""
    def hi(t):
        return min(_tri(t), N)

    def lo(t):
        return _tri(t - 1) + 1

    def first_in_b(t):
        return lo(t) if t % 2 else hi(t)

    def last_in_b(t):
        return hi(t) if t % 2 else lo(t)

    return first_in_b, last_in_b


def verify_k6(vs):
    """(1)①②・(2)：公式で出し直して、並べて作った列と突き合わせる。"""
    for v in vs:
        p = v['p']
        N, x, y, k = (p[t] for t in ('N', 'x', 'y', 'k'))
        seg, pos, iy, bk, nrow = v['_chk']
        assert _tri(seg - 1) < x <= _tri(seg) and pos == x - _tri(seg - 1)
        r = seg_of(y)
        off = y - _tri(r - 1)
        idx = _tri(r - 1) + (off if r % 2 else r - off + 1)
        assert idx == iy, (p, idx, iy)
        r2 = 1
        while _tri(r2) < k:
            r2 += 1
        off2 = k - _tri(r2 - 1)
        val = _tri(r2 - 1) + (off2 if r2 % 2 else min(_tri(r2), N) - _tri(r2 - 1)
                              - off2 + 1)
        assert val == bk, (p, val, bk)
        assert v['a'] == [f'{seg} 段目', f'左から{pos} 番目', f'{iy} 番目', str(bk)]
    return len(vs)


def verify_k6a(vs):
    """(3)(4)：境目の和を公式で出し直す。"""
    for v in vs:
        p = v['p']
        N, S, d = p['N'], p['S'], p['d']
        m3, n3, ndiv, nrow = v['_chk']
        j = int(round(S ** .5)) - 1
        assert j % 2 == 1 and (j + 1) ** 2 == S, (p, j)
        assert (m3, n3) == (_tri(j), _tri(j + 1)), (p, m3, n3)
        first_in_b, last_in_b = _k6_formula(N, nrow)
        cnt = 0
        for jj in range(1, nrow):
            tot = last_in_b(jj) + first_in_b(jj + 1)
            if jj + 1 < nrow:      # 完全な段どうしなら公式とも一致するはず
                want = (jj + 1) ** 2 if jj % 2 else jj * jj + 2
                assert tot == want, (p, jj, tot, want)
            if tot % d == 0:
                cnt += 1
        assert cnt == ndiv, (p, cnt, ndiv)
        assert v['a'] == [str(m3), str(n3), f'{ndiv} 通り']
    return len(vs)


def seg_of(x):
    k = 1
    while _tri(k) < x:
        k += 1
    return k


VERIFY3 = {'K1': verify_k1, 'K2': verify_k2, 'K3': verify_k3,
           'K4': verify_k4, 'K5': verify_k5, 'K6': verify_k6,
           'K6a': verify_k6a}


# ══════════════════════════════════════════════════════════════════
# 回帰テスト（元のNNOP第3回の数値 → 公式解答）
#   ※ 6(4) は公式解答が 31通り だが、最終段（65段目）の境目を数え落としている。
#      正しくは 32通り。ここでは正しい値で照合する。
# ══════════════════════════════════════════════════════════════════
OFFICIAL3 = {
    'K1': (['<span class="fr"><span class="fn">39</span><span class="fd">2027</span></span>'],
           {'m': 45}),
    'K2': (['280 秒後', '560 m', '3 か所', '280 m'],
           {'L': 840, 'va': 2, 'vb': 5, 'vc': 7, 'n': 23}),
    'K3': (['75 cm<sup>2</sup>', '26 cm', '7 通り'],
           {'AB': 18, 'AE': 21, 'ED': 3, 'DF': 4, 'g': 6, 'S2': 60,
            'e3': 4, 'f3': 6, 'S3': 60}),
    'K4': (['10 通り', '3 通り', '84 通り', '504 通り'], {'q': 3}),
    'K5': (['103.62 cm', '87.92 cm'], {'s': 6}),
    'K6': (['10 段目', '左から5 番目', '75 番目', '2070'],
           {'N': 2100, 'x': 50, 'y': 70, 'k': 2027}),
    # 6(4) の公式解答は31通りだが、最終段（65段目）の境目を数え落としている。
    # 実際に数列Bを並べて数えると32通り。ここでは正しい値で照合する。
    'K6a': (['1035', '1081', '32 通り'], {'N': 2100, 'S': 2116}),
}
