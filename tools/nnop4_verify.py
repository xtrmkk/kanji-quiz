# -*- coding: utf-8 -*-
"""夏期そっくりテストの独立検算と、元の数値での回帰テスト。

生成器が使った式をそのまま使い回さず、別の原理で解き直して突き合わせる。
"""
import itertools
import math
from fractions import Fraction as F

import nnop4_data as D4
from nnop_data import num, frac_html, improper_html


# ══════════════════════════════════════════════════════════════════
# N1 食塩水 … 実際に入れ替えて、食塩の重さから濃さを出し直す
# ══════════════════════════════════════════════════════════════════
def verify_n1(vs):
    for v in vs:
        p = v['p']
        wa, wb = p['wa'], p['wb']
        ca, cb = F(p['ca']), F(p['cb'])
        c, x, sa, sb = v['_chk']
        assert sa == ca * wa / 100 and sb == cb * wb / 100
        # (1) 食塩の重さの和 ÷ 全体
        assert (sa + sb) / (wa + wb) * 100 == c
        # (2) x g を入れ替えたあと、両方の濃さが本当に等しいか
        ia = sa - sa * F(x, wa) + sb * F(x, wb)      # Aに残った食塩＋Bから来た食塩
        ib = sb - sb * F(x, wb) + sa * F(x, wa)
        assert ia / wa == ib / wb, (p, ia / wa, ib / wb)
        assert ia / wa * 100 == c, (p, ia / wa * 100, c)
        assert v['a'] == [f'{num(c)}%', f'{x} g']
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# N2 買った個数 … 別のまわし方で全数探索して数え直す
# ══════════════════════════════════════════════════════════════════
def verify_n2(vs):
    for v in vs:
        p = v['p']
        a, b, c, T = p['a'], p['b'], p['c'], p['T']
        assert (a + 1) % 40 == 0 and b == a + 40 and c == a + 80
        again = []
        for x in range(1, T // a + 1):
            rest = T - a * x
            for y in range(1, rest // b + 1):
                r2 = rest - b * y
                if r2 > 0 and r2 % c == 0:
                    again.append((x, y, r2 // c))
        xs, sol = v['_chk']
        assert sorted(again) == sorted(sol), (p, len(again), len(sol))
        assert sorted({z[0] for z in again}) == xs, (p, xs)
        assert v['a'][0] == '、'.join(str(z) for z in xs) + ' 個'
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# N3 6分割の直角三角形 … 図を座標で組み直し、面積を実測する
# ══════════════════════════════════════════════════════════════════
def _n3_areas(L):
    """●の辺がすべて L の折れ線で図を組み、6つの三角形の面積を返す。"""
    th = math.radians(15)
    B = (0.0, 0.0)
    A = (0.0, float(L))
    C = (L / math.tan(th), 0.0)

    def on(seg, src):
        """線分 seg 上で src から距離 L の点（x が大きい方）。"""
        (px, py), (qx, qy) = seg
        dx, dy = qx - px, qy - py
        sx, sy = src
        aa = dx * dx + dy * dy
        bb = 2 * ((px - sx) * dx + (py - sy) * dy)
        cc = (px - sx) ** 2 + (py - sy) ** 2 - L * L
        dd = bb * bb - 4 * aa * cc
        ts = [(-bb + math.sqrt(dd)) / (2 * aa), (-bb - math.sqrt(dd)) / (2 * aa)]
        pts = [(px + t * dx, py + t * dy) for t in ts if -1e-9 <= t <= 1 + 1e-9]
        pts = [q for q in pts if q[0] > sx + 1e-9]
        return max(pts, key=lambda q: q[0])

    U1 = on((A, C), B)
    V1 = on((B, C), U1)
    U2 = on((A, C), V1)
    V2 = on((B, C), U2)
    # V2 から C までも L でなければ図が合わない
    assert abs(math.dist(V2, C) - L) < 1e-6, (L, math.dist(V2, C))
    # V1 から真上に引いた線と AC の交点
    t = (V1[0] - A[0]) / (C[0] - A[0])
    W = (V1[0], A[1] + t * (C[1] - A[1]))

    def ar(*ps):
        s = 0.0
        for (x1, y1), (x2, y2) in zip(ps, ps[1:] + ps[:1]):
            s += x1 * y2 - x2 * y1
        return abs(s) / 2

    return {'ア': ar(A, B, U1), 'イ': ar(B, U1, V1), 'ウ': ar(U1, W, V1),
            'エ': ar(W, V1, U2), 'オ': ar(V1, U2, V2), 'カ': ar(U2, V2, C),
            'ABC': ar(A, B, C)}


def verify_n3(vs):
    for v in vs:
        L = v['p']['L']
        g = _n3_areas(L)
        a, we, ka = v['_chk']
        assert abs(g['ア'] - a) < 1e-6, (L, g['ア'], a)
        assert abs(g['ウ'] + g['エ'] - we) < 1e-6, (L, g['ウ'] + g['エ'], we)
        assert abs(g['カ'] - ka) < 1e-6, (L, g['カ'], ka)
        assert abs(g['イ'] - g['オ']) < 1e-6, (L, g['イ'], g['オ'])
        # (3) ABC ＝ ウ×5 ＋ エ×3
        assert abs(g['ABC'] - (g['ウ'] * 5 + g['エ'] * 3)) < 1e-6, (L, g)
        assert abs(sum(g[k] for k in 'アイウエオカ') - g['ABC']) < 1e-6
        assert v['a'] == [f'{a} cm<sup>2</sup>', f'{we} cm<sup>2</sup>',
                          f'{ka} cm<sup>2</sup>', '1 : 1', '5', '3']
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# N4 流水算 … 出来事の時刻を分数で積み上げて、予定通りかを確かめる
# ══════════════════════════════════════════════════════════════════
def verify_n4(vs):
    for v in vs:
        p = v['p']
        r, vv, T, h, t1, h2 = (p[k] for k in ('r', 'v', 'T', 'h', 't1', 'h2'))
        k = F(p['k'])
        d, t, rest = v['_chk']
        up, dn = vv - r, vv + r
        # 予定：上り＋休憩＋下り ＝ T 分
        plan = d / up * 60 + h + d / dn * 60
        assert plan == T, (p, plan, T)
        # 当日：出発→停止→流される→修理後に上る→休憩→下る
        gone = up * F(t1, 60)
        assert gone == d - rest and 0 < gone < d, (p, gone, d)
        back = r * t / 60                       # 流された道のり
        remain = rest + back
        up2 = k * vv - r
        total = t1 + t + remain / up2 * 60 + h2 + d / dn * 60
        assert total == T, (p, total, T)
        sec = t * 60
        mm, ss = divmod(int(sec), 60)
        assert v['a'] == [f'{num(d)} km', f'{mm} 分{ss} 秒間']
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# N5 直角三角形と円 … 座標と数値積分（真のπ）で確かめる
# ══════════════════════════════════════════════════════════════════
def _integ(lo, hi, f, n=40000):
    s, dx = 0.0, (hi - lo) / n
    for i in range(n):
        s += f(lo + (i + .5) * dx) * dx
    return s


def verify_n5(vs):
    for v in vs:
        p = v['p']
        pp, qq, W, c = p['p'], p['q'], p['W'], p['c']
        s1, s2, s3 = v['_chk']
        # (1) 合同な直角三角形2枚。角ABCが直角になることを座標で確かめる
        B = (0.0, 0.0)
        A = (-qq, pp * 1.0)          # 左の三角形（直角は左下）
        C = (pp * 1.0, qq * 1.0)     # 右の三角形（直角は右下）… 脚を入れかえる
        A = (-pp, qq * 1.0)
        C = (qq * 1.0, pp * 1.0)
        ab = math.dist(A, B)
        bc = math.dist(B, C)
        assert abs(ab - bc) < 1e-9 and abs(ab ** 2 - (pp * pp + qq * qq)) < 1e-9
        dot = (A[0] - B[0]) * (C[0] - B[0]) + (A[1] - B[1]) * (C[1] - B[1])
        assert abs(dot) < 1e-9, (p, dot)
        area1 = abs((A[0] - B[0]) * (C[1] - B[1]) - (C[0] - B[0]) * (A[1] - B[1])) / 2
        assert abs(area1 - float(s1)) < 1e-9, (p, area1, s1)
        # (2)(3) 円の配置を組み立てる
        h = F(W - c, 2)
        i = F(W + c, 2)
        d, f = i, h                    # DH＝OI、FI＝OH
        r2 = h * h + d * d
        assert r2 == i * i + f * f == F(W * W + c * c, 2)
        # 2本の点線は垂直か（傾きが ±1 になる）
        assert d + f == h + i == W
        # 四角形DEGF（台形）の面積
        trap = (2 * d + 2 * f) / 2 * W
        assert trap == s2, (p, trap, s2)
        # 斜線部分：数値積分（真のπ）で弓形2つを直接はかる
        r = math.sqrt(float(r2))
        seg = (_integ(-r, -float(h), lambda x: 2 * math.sqrt(max(r * r - x * x, 0)))
               + _integ(float(i), r, lambda x: 2 * math.sqrt(max(r * r - x * x, 0))))
        want = math.pi * float(r2) / 2 - 2 * float(h) * float(i)
        assert abs(seg - want) < 1e-3, (p, seg, want)
        # 児童に見せる値は3.14で厳密に
        exact = F(314, 100) * r2 / 2 - 2 * h * i
        assert exact == s3, (p, exact, s3)
        assert v['a'] == [f'{num(s1)} cm<sup>2</sup>', f'{W * W} cm<sup>2</sup>',
                          f'{num(s3)} cm<sup>2</sup>']
    return len(vs)


# ══════════════════════════════════════════════════════════════════
# N6 循環小数 … 筆算（あまりの列）で小数を出し直す
# ══════════════════════════════════════════════════════════════════
def _long_div(f: F):
    """筆算で (整数部, 非循環部, 循環部) を出す。"""
    w, rem = divmod(f.numerator, f.denominator)
    d = f.denominator
    seen, out = {}, []
    while rem and rem not in seen:
        seen[rem] = len(out)
        rem *= 10
        out.append(rem // d)
        rem %= d
    if rem == 0:
        return str(w), ''.join(map(str, out)), ''
    k = seen[rem]
    return str(w), ''.join(map(str, out[:k])), ''.join(map(str, out[k:]))


def verify_n6(vs):
    """(1)(2)：筆算（あまりの列）で小数を出し直す。"""
    for v in vs:
        f1, f2, f3, cl = v['_chk']
        for f, got in zip((f1, f2, f3), v['a'][:3]):
            w, pre, rep = _long_div(f)
            assert (w, pre, rep) == D4.rep_decimal(f), (f,)
            assert got == D4.dec_html(f), (f, got)
        for j, cel in enumerate(cl):
            assert v['a'][3 + j] == D4.dec_html(F(cel, 13)), (cel,)
        # 表に隠した4つが本文の答と同じ順番か
        assert v['p']['hide'] == ','.join(str(x) for x in cl)
        for n in range(1, 16):
            cell = D4.improper_html(F(n, 13))
            assert cell in v['p']['table'], (n,)
    return len(vs)


def verify_n6a(vs):
    """(3)(4)：直接数え上げ・全数探索で確かめる。"""
    for v in vs:
        cnt, first_n = v['_chk']
        K, rr = v['p']['K'], v['p']['r']
        n = len([t for t in range(1, K + 1) if t % 13 == rr % 13])
        assert n == cnt, (v['p'], n, cnt)
        assert v['a'][0] == f'{cnt} 個'
        assert first_n == _first_all_ten(), first_n
        assert v['a'][1] == frac_html(F(first_n, 13))
    return len(vs)


_FIRST = None


def _first_all_ten():
    global _FIRST
    if _FIRST is None:
        n = 1
        while True:
            f = F(n, 13)
            w, pre, rep = _long_div(f)
            if set(w + pre + rep) >= set('0123456789'):
                _FIRST = n
                break
            n += 1
    return _FIRST


VERIFY4 = {'N1': verify_n1, 'N2': verify_n2, 'N3': verify_n3,
           'N4': verify_n4, 'N5': verify_n5, 'N6': verify_n6,
           'N6a': verify_n6a}


# ══════════════════════════════════════════════════════════════════
# 回帰テスト（元の夏期そっくりテストの数値 → 公式解答）
# ══════════════════════════════════════════════════════════════════
OFFICIAL4 = {
    'N1': (['6.8%', '240 g'], {'wa': 400, 'wb': 600, 'ca': '8', 'cb': '6'}),
    'N2': (['18、19、20、21 個'], {'a': 39, 'T': 1453}),
    'N3': (['16 cm<sup>2</sup>', '32 cm<sup>2</sup>', '16 cm<sup>2</sup>',
            '1 : 1', '5', '3'], {'L': 8}),
    'N4': (['15.75 km', '18 分20 秒間'],
           {'r': 3, 'v': 24, 'T': 100, 'h': 20, 't1': 23, 'k': '1.5', 'h2': 8}),
    'N5': (['12.5 cm<sup>2</sup>', '144 cm<sup>2</sup>', '46.18 cm<sup>2</sup>'],
           {'p': 3, 'q': 4, 'W': 12, 'c': 2}),
    'N6': ([None] * 7, {'hide': '2,4,7,15'}),
    'N6a': (['156 個', None], {'K': 2027, 'r': 5}),
}
