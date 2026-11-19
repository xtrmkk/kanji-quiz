# -*- coding: utf-8 -*-
"""予想①の独立検算と、元の数値での回帰テスト。

生成器が使った式をそのまま使い回すと、式がまちがっていても一致してしまう。
ここでは**別の原理**で解き直して突き合わせる（nnop_spec.md 7.1 / 13章）。

  S1 割合と比   … 個数を総当たりして、比と売り上げの両方に合う組をひろう
  S2 公約数     … 積の約数を全部調べ、最大公約数を直接はかる
  S3 立体図形   … 立方体の辺と平面の交点から切り口の多角形を組み、靴ひも公式ではかる
  S4 速さ       … 1秒ずつ2人を動かして、すれちがう瞬間を直接ひろう
  S5 平面図形   … 正多角形を座標で置き、鏡に映した多角形との重なりを切り取って実測する
  S6 場合の数   … 6枚のカードを実際に裏返して全数しらべる
"""
import itertools
import math
from fractions import Fraction as F

import nnop7_data as DX
from nnop_data import num, frac_html, improper_html


def verify_s1(vs):
    """S1：個数を総当たりして、比と売り上げの両方に合う組をひろい直す。"""
    for v in vs:
        q = v['p']
        a, b, p, r, s, N = q['a'], q['b'], q['p'], q['r'], q['s'], q['N']
        qq, T1 = q['q'], q['T1']
        # (1) 売り上げが T1 になる (x, y) を全部ひろい、個数の比が p:q のものを取る
        hit = []
        for x in range(0, T1 // a + 1):
            rest = T1 - a * x
            if rest % b:
                continue
            y = rest // b
            if x * qq == y * p and x and y:
                hit.append((x, y))
        assert len(hit) == 1, (q['key'], hit)
        assert v['a'][0] == f'{hit[0][0] + hit[0][1]} 個', (q['key'], hit, v['a'])
        # (2) 個数の合計が N で、売り上げの比が r:s になる (x, y)
        hit2 = [(x, N - x) for x in range(1, N)
                if (a * x) * s == (b * (N - x)) * r]
        assert len(hit2) == 1, (q['key'], hit2)
        x, y = hit2[0]
        assert v['a'][1] == f'{a * x + b * y} 円', (q['key'], v['a'])
    return len(vs)


def verify_s2(vs):
    """S2：積の約数を全部調べ、最大公約数を直接はかってひろい直す。"""
    for v in vs:
        M = v['p']['M']
        got = sorted({A for A in DX._divisors(M)
                      if A * A < M and math.gcd(A, M // A) > 1 and 10 <= A <= 99})
        assert v['a'][0] == '、'.join(str(A) for A in got), (v['p']['key'], got, v['a'])
    return len(vs)


def _s4_pos(t, up, t1, d, L, qd):
    """時刻 t（分）での P君と Q君の位置（A地点からの道のり）。"""
    if t <= t1:
        p = up * t
    elif t <= t1 + d:
        p = up * t1 - (t - t1)
    else:
        p = up * t1 - d + up * (t - t1 - d)
    return p, L - qd * t


def _s4_meet(up, t1, d, L, qd, step=1 / 60):
    """1秒ずつ動かして、2人の位置が入れかわる瞬間をひろう（線形なので間を補間）。"""
    prev_t, prev = 0.0, L
    t = step
    while t < 400:
        p, qpos = _s4_pos(t, up, t1, d, L, qd)
        gap = qpos - p
        if gap <= 0:
            return prev_t + (t - prev_t) * prev / (prev - gap)
        prev_t, prev = t, gap
        t += step
    return None


def verify_s4(vs):
    """S4：1秒ずつ2人を動かして、すれちがう瞬間を直接ひろう。"""
    for v in vs:
        q = v['p']
        T0, t1, d, T1, rc = q['T0'], q['t1'], q['d'], q['T1'], q['rc']
        e = T1 - d - T0
        pv = (d + e) / e
        up = pv - 1
        L = up * T0
        qd = rc / 100 * pv + 1
        # (2)
        t = _s4_meet(up, t1, d, L, qd)
        assert t is not None and t1 < t <= t1 + d, (q['key'], t)
        m, sec = int(t + 1e-9), round((t - int(t + 1e-9)) * 60)
        want = f'{m}分{sec}秒後' if sec else f'{m}分後'
        assert v['a'][1] == want, (q['key'], v['a'][1], want, t)
        # (3) 境目の s では「P君が再びこぎ始める瞬間」にちょうど出会い、
        #     1秒早く変えると出会いが遅れて、もう流されている間には会えない
        slow = float(v['a'][2].replace('後', '').replace('分', ' ').replace('秒', '').split()[0])
        ss = v['a'][2].replace('後', '')
        mm = int(ss.split('分')[0])
        sc = int(ss.split('分')[1].replace('秒', '') or 0) if '秒' in ss else 0
        s_low = mm + sc / 60
        half = rc / 100 * pv / 2

        def meet_with(s):
            """Q君が s 分で静水の速さを半分にしたときの、すれちがう時刻。"""
            qd2 = half + 1
            prev_t, prev = 0.0, L
            t, step = 1 / 60, 1 / 60
            while t < 400:
                p, _ = _s4_pos(t, up, t1, d, L, qd)
                qpos = L - (qd * min(t, s) + qd2 * max(0.0, t - s))
                gap = qpos - p
                if gap <= 0:
                    return prev_t + (t - prev_t) * prev / (prev - gap)
                prev_t, prev = t, gap
                t += step
            return None

        t_at = meet_with(s_low)
        assert t_at is not None and abs(t_at - (t1 + d)) < 2e-3, (q['key'], t_at, t1 + d)
        t_before = meet_with(s_low - 1 / 60)
        assert t_before is None or t_before > t1 + d + 1e-9, (q['key'], t_before)
        # (1) 比
        n1, n2 = (d + e), e
        g = math.gcd(n1, n2)
        assert v['a'][0] == f'{n1 // g} ： {n2 // g}', (q['key'], v['a'][0])
    return len(vs)


# ── S3 立方体の切り口 ────────────────────────────────────────
def _cube_section(a, c):
    """立方体 [0,a]³ を平面 x+y−z=c で切った断面の面積。
    辺と平面の交点をひろって多角形にし、平面の上で靴ひも公式ではかる。"""
    V = [(x, y, z) for x in (0, a) for y in (0, a) for z in (0, a)]
    E = [(p, q) for p, q in itertools.combinations(V, 2)
         if sum(1 for i in range(3) if p[i] != q[i]) == 1]
    f = lambda p: p[0] + p[1] - p[2]
    pts = []
    for p, q in E:
        fp, fq = f(p) - c, f(q) - c
        if fp == 0:
            pts.append(p)
        if fq == 0:
            pts.append(q)
        if fp * fq < 0:
            t = fp / (fp - fq)
            pts.append(tuple(p[i] + t * (q[i] - p[i]) for i in range(3)))
    pts = list({tuple(round(v, 9) for v in p) for p in pts})
    if len(pts) < 3:
        return 0.0
    cx = [sum(p[i] for p in pts) / len(pts) for i in range(3)]
    u = (1 / math.sqrt(2), -1 / math.sqrt(2), 0.0)
    nr = (1 / math.sqrt(3), 1 / math.sqrt(3), -1 / math.sqrt(3))
    w = (nr[1] * u[2] - nr[2] * u[1], nr[2] * u[0] - nr[0] * u[2],
         nr[0] * u[1] - nr[1] * u[0])
    pr = [(sum((p[i] - cx[i]) * u[i] for i in range(3)),
           sum((p[i] - cx[i]) * w[i] for i in range(3))) for p in pts]
    order = sorted(range(len(pts)), key=lambda i: math.atan2(pr[i][1], pr[i][0]))
    s = 0.0
    for i in range(len(order)):
        x1, y1 = pr[order[i]]
        x2, y2 = pr[order[(i + 1) % len(order)]]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def verify_s3(vs):
    """S3：切り口の多角形を実際に組み立てて面積をはかり、比を出し直す。"""
    for v in vs:
        q = v['p']
        a, n = q['a'], q['n']
        S = _cube_section(a, 0.0)
        for k, got in ((q['k1'], v['a'][0]), (q['k2'], v['a'][1])):
            area = _cube_section(a, a * k / n)
            want = F(n * n + 2 * k * n - 2 * k * k, n * n)
            assert abs(area / S - float(want)) < 1e-9, (q['key'], k, area / S)
            assert got == f'{frac_html(want)} 倍', (q['key'], got)
    return len(vs)


# ── S5 2つ重ねた正n角形 ──────────────────────────────────────
def _poly_area(P):
    s = 0.0
    for i in range(len(P)):
        x1, y1 = P[i]
        x2, y2 = P[(i + 1) % len(P)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def _clip(sub, a, b):
    """凸多角形 sub を、有向直線 ab の左側で切り取る。"""
    out = []
    side = lambda p: (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
    for i in range(len(sub)):
        c, d = sub[i], sub[(i + 1) % len(sub)]
        sc, sd = side(c), side(d)
        if sc >= -1e-12:
            out.append(c)
        if sc * sd < 0:
            t = sc / (sc - sd)
            out.append((c[0] + t * (d[0] - c[0]), c[1] + t * (d[1] - c[1])))
    return out


def verify_s5(vs):
    """S5：正多角形を座標で置き、鏡に映したものとの重なりを切り取って実測する。"""
    for v in vs:
        n, S = v['p']['n'], v['p']['S']
        V = [(math.sin(2 * math.pi * k / n), math.cos(2 * math.pi * k / n))
             for k in range(n)][::-1]
        i0 = max(range(n), key=lambda i: V[i][1])
        V = V[i0:] + V[:i0]
        A, C, B = V[0], V[n // 2], V[n // 2 + 1]
        M = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
        dx, dy = M[0] - A[0], M[1] - A[1]
        dl = math.hypot(dx, dy)
        dx, dy = dx / dl, dy / dl

        def mir(p):
            vx, vy = p[0] - A[0], p[1] - A[1]
            t = vx * dx + vy * dy
            return (A[0] + 2 * t * dx - vx, A[1] + 2 * t * dy - vy)

        Wv = [mir(p) for p in V][::-1]
        inter = V[:]
        for i in range(len(Wv)):
            inter = _clip(inter, Wv[i], Wv[(i + 1) % len(Wv)])
        tot = _poly_area(V)
        sc = S / tot
        got = [_poly_area([(0, 0), B, C]) * sc, _poly_area([A, B, C]) * sc,
               _poly_area([A, M, C]) * sc,
               2 * (tot - _poly_area(inter)) * sc]
        want = [S / n, 2 * S / n, S / n, 4 * S / n]
        for g, w in zip(got, want):
            assert abs(g - w) < 1e-7, (v['p']['key'], got, want)
        for a, w in zip(v['a'], want):
            assert a == f'{int(round(w))} cm<sup>2</sup>', (v['p']['key'], a, w)
    return len(vs)


# ── S6 / S6a カードを裏返す3つの操作 ──────────────────────────
def _flips(a, b, c, m=6):
    """カードごとに「何回裏返されたか」を数え、奇数回のものを裏とする。"""
    back = set()
    for x in range(1, m + 1):
        t = 0
        t += 1 if x % 2 == a % 2 else 0          # 〈操作1〉
        t += 1 if x % b == 0 else 0              # 〈操作2〉 b の倍数
        t += 1 if c % x == 0 else 0              # 〈操作3〉 c の約数
        if t % 2:
            back.add(x)
    return back


def _fmt(st):
    return '、'.join(str(x) for x in sorted(st))


def verify_s6(vs):
    """S6：裏返された回数の偶奇で数え直し、(2)の答えは総当たりで一意を確かめる。"""
    for v in vs:
        q = v['p']
        assert v['a'][0] == _fmt(_flips(q['a1'], q['b1'], q['c1'])), (q['key'],)
        want = set(int(x) for x in q['bk2'].split('、'))
        hit = [b for b in range(1, 7) if _flips(q['a2'], b, q['c2']) == want]
        assert hit == [int(v['a'][1])], (q['key'], hit, v['a'][1])
    return len(vs)


def verify_s6a(vs):
    """S6a：(3)は総当たりで一意を確かめ、(4)は1回目の偶奇で分けて数え直す。"""
    for v in vs:
        q = v['p']
        want = set(int(x) for x in q['bk3'].split('、'))
        hit = [(b, c) for b in range(1, 7) for c in range(1, 7)
               if _flips(q['a3'], b, c) == want]
        assert hit == [(int(v['a'][0]), int(v['a'][1]))], (q['key'], hit, v['a'])
        # (4) 表が {fr4} ＝ 裏がその補集合。1回目の偶奇ごとに (b,c) を数える
        front = set(int(x) for x in q['fr4'].split('、'))
        back = set(range(1, 7)) - front
        tot = 0
        for first in (1, 2):                     # 1=奇数のとき, 2=偶数のとき
            k = sum(1 for b in range(1, 7) for c in range(1, 7)
                    if _flips(first, b, c) == back)
            tot += 3 * k                         # 1回目の目は奇数3通り・偶数3通り
        assert v['a'][2] == f'{tot} 通り', (q['key'], v['a'][2], tot)
    return len(vs)


VERIFY7 = {'S1': verify_s1, 'S2': verify_s2, 'S3': verify_s3, 'S4': verify_s4,
           'S5': verify_s5, 'S6': verify_s6, 'S6a': verify_s6a}

# ══════════════════════════════════════════════════════════════════
# 回帰テスト（元の予想①の数値 → 公式解答）
# ══════════════════════════════════════════════════════════════════
OFFICIAL7 = {
    'S1': (['56 個', '12000 円'], {'key': '150-400-43-8-23-2'}),
    'S2': (['15、21、30、33、42、66'], {'key': '3-770'}),
    'S3': ([f'{frac_html(F(3, 2))} 倍', f'{frac_html(F(11, 8))} 倍'],
           {'key': '4-4-2-3'}),
    'S4': (['5 ： 1', '28分45秒後', '16分30秒後'], {'key': '60-25-16-4-45'}),
    'S5': (['8 cm<sup>2</sup>', '16 cm<sup>2</sup>', '8 cm<sup>2</sup>',
            '32 cm<sup>2</sup>'], {'key': '12-96'}),
    'S6': (['2、4、5、6', '4'], {'key': '432-334-246'}),
    'S6a': (['4', '5', '9 通り'], {'key': '432-145-235'}),
}
