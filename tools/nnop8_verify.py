# -*- coding: utf-8 -*-
"""予想②の独立検算と、元の数値での回帰テスト。

生成器が使った式をそのまま使い回すと、式がまちがっていても一致してしまう。
ここでは**別の原理**で解き直して突き合わせる（nnop_spec.md 7.1 / 13章）。

  T1 消去算   … 個数を0から総当たりして、材料をちょうど使い切る組をひろう
                 （生成器は2元1次の連立を行列式で解いている）
  T2 平面図形 … 正六角形を座標で置き、15°の線6本の交点から内側の正六角形を
                 組み立てて、靴ひも公式で面積をはかる（生成器は答えを持つだけ）
  T3 場合の数 … 素数2・3・5の指数の組ごとに通り数をたたみこみ（DP）、
                 (指数+1)の積として約数の個数を出す（生成器は1296通りの全列挙）
  T4 速さ     … 1秒ずつタクシーとB班を動かして、拾う地点と到着時刻を直接ひろう
                 （生成器は y＝2wx/(V+w) の式）
  T5 場合の数 … ○×の並びを4^n通り全部作り、同じ部屋のときは逆という決まりで
                 ふるいにかける（生成器は分岐しながら枝を伸ばしている）
"""
import itertools
import math
from collections import Counter
from fractions import Fraction as F

import nnop8_data as DX
from nnop_data import num, frac_html, improper_html


# ── T1 2種類の製品と2種類の材料 ──────────────────────────────
def verify_t1(vs):
    """T1：個数を総当たりして、条件に合う組をひろい直す。"""
    for v in vs:
        q = v['p']
        cA, cB, dA, dB = q['cA'], q['cB'], q['dA'], q['dB']
        C0, D0 = int(round(float(q['C0']) * 1000)), int(round(float(q['D0']) * 1000))
        p, r, u, w = q['p'], q['q'], q['u'], q['v']
        # (1) 製品Aだけを1個ずつ増やしていき、作れなくなる手前で止める
        n = 0
        while cA * (n + 1) <= C0 and dA * (n + 1) <= D0:
            n += 1
        rc, rd = C0 - cA * n, D0 - dA * n
        assert (rc == 0) != (rd == 0), (q['key'], rc, rd)
        want = f'材料{"C" if rc else "D"}が{rc or rd}g余る'
        assert v['a'][0] == want, (q['key'], v['a'][0], want)
        # (2) 個数の組を総当たり
        hit = [(a, b) for a in range(C0 // cA + 1) for b in range(C0 // cB + 1)
               if cA * a + cB * b == C0 and dA * a + dB * b == D0]
        assert len(hit) == 1, (q['key'], hit)
        assert v['a'][1] == f'{hit[0][0]} 個' and v['a'][2] == f'{hit[0][1]} 個', \
            (q['key'], hit, v['a'])
        # (3) 「製品Aを u 個・製品Bを w 個」を1組として、組の数を総当たり
        got = []
        for k in range(1, 401):
            addC = (cA * u + cB * w) * k - C0
            addD = (dA * u + dB * w) * k - D0
            if addC <= 0 or addD <= 0:
                continue
            if addC * r == addD * p:                  # 追加は p : r
                got.append((addC, addD))
        assert len(got) == 1, (q['key'], got)
        assert v['a'][3] == f'{DX._kg(got[0][0])} kg', (q['key'], v['a'][3], got)
        assert v['a'][4] == f'{DX._kg(got[0][1])} kg', (q['key'], v['a'][4], got)
    return len(vs)


# ── T2 正六角形と二等辺三角形 ────────────────────────────────
def _shoelace(P):
    s = 0.0
    for i in range(len(P)):
        x1, y1 = P[i]
        x2, y2 = P[(i + 1) % len(P)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def _ang(c, p, q):
    """点cでの角pcqを度で返す。"""
    a = math.atan2(p[1] - c[1], p[0] - c[0])
    b = math.atan2(q[1] - c[1], q[0] - c[0])
    d = math.degrees(abs(a - b)) % 360
    return min(d, 360 - d)


def _cross_pt(a, ad, b, bd):
    """点aから向きad、点bから向きbd の2直線の交点。"""
    det = ad[0] * (-bd[1]) - ad[1] * (-bd[0])
    t = ((b[0] - a[0]) * (-bd[1]) - (b[1] - a[1]) * (-bd[0])) / det
    return (a[0] + t * ad[0], a[1] + t * ad[1])


def verify_t2(vs):
    """T2：座標をとって、3枚の図の主張を実際にはかり直す。"""
    for v in vs:
        # 図1：正六角形（外接円の半径1・上が頂点）、BC は1辺、A は頂角120°の頂点
        V = [(math.cos(math.radians(90 + 60 * k)),
              math.sin(math.radians(90 + 60 * k))) for k in range(6)]
        B, C = V[2], V[3]                              # 210°と270°の頂点
        A = (math.cos(math.radians(240)) / math.sqrt(3),
             math.sin(math.radians(240)) / math.sqrt(3))
        assert abs(math.dist(A, B) - math.dist(A, C)) < 1e-12, '図1 AB≠AC'
        assert abs(_ang(A, B, C) - 120) < 1e-9, ('図1 頂角', _ang(A, B, C))
        ratio1 = _shoelace(V) / _shoelace([A, B, C])
        assert abs(ratio1 - 18) < 1e-9, ('図1 の倍率', ratio1)
        assert v['a'][0] == f'{round(ratio1)} 倍', v['a'][0]

        # 図2：AB＝AC＝AD、∠BAC＝120°、AD∥BC → ∠DBC
        B2, C2 = (0.0, 0.0), (1.0, 0.0)
        A2 = (0.5, 1 / (2 * math.sqrt(3)))             # 頂角120°の二等辺三角形
        L = math.dist(A2, B2)
        D2 = (A2[0] + L, A2[1])                        # AD∥BC、AD＝AB
        assert abs(math.dist(A2, C2) - L) < 1e-12 and abs(math.dist(A2, D2) - L) < 1e-12
        assert abs(_ang(A2, B2, C2) - 120) < 1e-9
        ang = _ang(B2, D2, C2)
        assert abs(ang - 15) < 1e-9, ('図2 ∠DBC', ang)
        assert v['a'][1] == f'{round(ang)} 度', v['a'][1]

        # 図3：各頂点から「次の辺と15°」の線を引き、その交点で内側の正六角形を作る
        dirs = []
        for k in range(6):                              # V[k] から V[k+1] の向きを15°回す
            nx, ny = V[(k + 1) % 6][0] - V[k][0], V[(k + 1) % 6][1] - V[k][1]
            t = math.atan2(ny, nx) + math.radians(15)   # 辺から内側へ15°
            dirs.append((math.cos(t), math.sin(t)))
        inner = [_cross_pt(V[k], dirs[k], V[(k + 1) % 6], dirs[(k + 1) % 6])
                 for k in range(6)]
        # 内側の6点が正六角形か（中心からのきょりと向きが等間隔）
        rs = [math.hypot(*pt) for pt in inner]
        assert max(rs) - min(rs) < 1e-9, ('図3 内側が正六角形でない', rs)
        # 図（nnop_fig.hex3_svg）は内側を「15°回して √(2/3) 倍」で描いている
        assert abs(rs[0] - math.sqrt(2 / 3)) < 1e-9, ('図3 内側の半径', rs[0])
        for k, pt in enumerate(inner):
            a = math.degrees(math.atan2(pt[1], pt[0])) % 360
            assert abs((a - (165 + 60 * k) % 360 + 180) % 360 - 180) < 1e-7, \
                ('図3 内側の頂点の向き', k, a)
        tri = [[V[k], V[(k + 1) % 6], inner[k]] for k in range(6)]
        areas = [_shoelace(t) for t in tri]
        assert max(areas) - min(areas) < 1e-9, ('図3 三角形が合同でない', areas)
        tot, ins = _shoelace(V), _shoelace(inner)
        assert abs(tot - (ins + sum(areas))) < 1e-9, '図3 しきつめになっていない'
        assert abs(tot / areas[0] - 18) < 1e-9, ('図3 の三角形', tot / areas[0])
        ratio3 = ins / tot
        assert abs(ratio3 - 2 / 3) < 1e-9, ('図3 の倍率', ratio3)
        assert v['a'][2] == f'{frac_html(F(2, 3))} 倍', v['a'][2]
    return len(vs)


# ── T3 さいころの目の積の約数 ────────────────────────────────
def _t3_dp(t: int) -> Counter:
    """素数2・3・5の指数の組ごとに通り数をたたみこみ、約数の個数で数え直す。"""
    face = {1: (0, 0, 0), 2: (1, 0, 0), 3: (0, 1, 0),
            4: (2, 0, 0), 5: (0, 0, 1), 6: (1, 1, 0)}
    dp = {(0, 0, 0): 1}
    for _ in range(t):
        nxt = Counter()
        for (a, b, c), n in dp.items():
            for e in face.values():
                nxt[(a + e[0], b + e[1], c + e[2])] += n
        dp = nxt
    out = Counter()
    for (a, b, c), n in dp.items():
        out[(a + 1) * (b + 1) * (c + 1)] += n
    return out


def verify_t3(vs):
    """T3：指数のたたみこみで数え直す（生成器の全列挙とは別の原理）。"""
    cache = {}
    for v in vs:
        q = v['p']
        t = q['t']
        if t not in cache:
            cache[t] = _t3_dp(t)
            assert sum(cache[t].values()) == 6 ** t, t
        tbl = cache[t]
        for d, got in ((q['d1'], v['a'][0]), (q['d2'], v['a'][1]),
                       (q['d3'], v['a'][2])):
            assert got == f'{tbl.get(d, 0)} 通り', (q['key'], d, got, tbl.get(d, 0))
    return len(vs)


# ── T4 タクシーと徒歩でT地へ ─────────────────────────────────
def _t4_sim(L, V, w, x, step=1 / 3600):
    """1秒ずつ動かして、(タクシーがB班を拾う地点, A班の到着, B班の到着) を返す。
    タクシーは S→P（x km）→引き返し、B班は歩いて進む。出会ったところで乗せる。"""
    t = 0.0
    prev_t, prev_gap = 0.0, x                      # 先頭はタクシーが前にいる
    y = None
    while t < 24:
        t += step
        taxi = V * t if t <= x / V else x - V * (t - x / V)
        walk = w * t
        gap = taxi - walk
        if gap <= 0:                               # 入れかわった＝出会った
            f = prev_gap / (prev_gap - gap)
            tm = prev_t + (t - prev_t) * f
            y = w * tm
            break
        prev_t, prev_gap = t, gap
    assert y is not None, (L, V, w, x)
    tA = x / V + (L - x) / w
    tB = y / w + (L - y) / V
    return y, tA, tB


def verify_t4(vs):
    """T4：出会う地点を1秒きざみで直接ひろい、到着時刻を出し直す。"""
    for v in vs:
        q = v['p']
        L, V, w, x1, T = q['L'], q['V'], q['w'], q['x1'], q['T']
        # (1)
        y, tA, tB = _t4_sim(L, V, w, x1)
        d = (tB - tA) * 60
        assert v['a'][0] == f'{"B" if d < 0 else "A"}班が{abs(round(d))}分早い', \
            (q['key'], v['a'][0], d)
        assert abs(d - round(d)) < 2e-3, (q['key'], d)
        # (2) 答えのxで、ほんとうに同時に着くか
        x2 = float(v['_chk'][3])
        _, a2, b2 = _t4_sim(L, V, w, x2)
        assert abs(a2 - b2) * 60 < 2e-3, (q['key'], (a2 - b2) * 60)
        # (3) 答えのxで、ほんとうに T 分だけ早く着くか
        x3 = float(v['_chk'][4])
        _, a3, b3 = _t4_sim(L, V, w, x3)
        assert abs((b3 - a3) * 60 - T) < 2e-3, (q['key'], (b3 - a3) * 60, T)
        # 表示（帯分数）も合っているか
        assert v['a'][1] == frac_html(v['_chk'][3]) and v['a'][2] == frac_html(v['_chk'][4])
    return len(vs)


# ── T5 じゃんけんと部屋の移動 ────────────────────────────────
def _t5_all(n, start):
    """○×の並びを4^n通り全部作り、決まりに合うものだけ残す（総当たり）。"""
    ok = []
    for ra in itertools.product((True, False), repeat=n):
        for rb in itertools.product((True, False), repeat=n):
            a = b = start
            good = True
            for i in range(n):
                if a == b and ra[i] == rb[i]:
                    good = False                   # 同じ部屋なら○×は逆のはず
                    break
                a, b = DX._t5_move(a, ra[i]), DX._t5_move(b, rb[i])
            if good and a == b:
                ok.append((ra, rb))
    return ok


def _t5_dp(n, start):
    """2人がどの部屋にいるかだけを見て、通り数を数え上げる（DP）。"""
    dp = Counter({(start, start): 1})
    for _ in range(n):
        nxt = Counter()
        for (a, b), c in dp.items():
            cand = ([(True, False), (False, True)] if a == b
                    else list(itertools.product((True, False), repeat=2)))
            for wa, wb in cand:
                nxt[(DX._t5_move(a, wa), DX._t5_move(b, wb))] += c
        dp = nxt
    return sum(c for (a, b), c in dp.items() if a == b)


def verify_t5(vs):
    """T5：総当たりでふるい、DPで数え直す。"""
    for v in vs:
        q = v['p']
        st, n3 = q['st'], q['n3']
        base = _t5_all(3, st)
        # (1) 3回目が「A君{w1}・B君{w2}」になるものはただ1通り
        aw = (q['w1'] == '勝ち')
        hit = [(ra, rb) for ra, rb in base if ra[2] is aw and rb[2] is not aw]
        assert len(hit) == 1, (q['key'], len(hit))
        assert v['a'][0] == DX._ox(hit[0][0][:2]), (q['key'], v['a'][0])
        assert v['a'][1] == DX._ox(hit[0][1][:2]), (q['key'], v['a'][1])
        # (2) 3回で同じ部屋になる記録をすべて
        lst = [f'A{DX._ox(x)}／B{DX._ox(y)}' for x, y in base]
        half = (len(lst) + 1) // 2
        assert v['a'][2] == '、'.join(lst[:half]), (q['key'], v['a'][2])
        assert v['a'][3] == '、'.join(lst[half:]), (q['key'], v['a'][3])
        assert len(set(lst)) == len(lst), (q['key'], '記録が重複している')
        # (3) n3 回のときの通り数（総当たりとDPの両方で）
        cnt = _t5_dp(n3, st)
        assert cnt == len(_t5_all(n3, st)), (q['key'], cnt)
        assert v['a'][4] == f'{cnt} 通り', (q['key'], v['a'][4], cnt)
    return len(vs)


VERIFY8 = {'T1': verify_t1, 'T2': verify_t2, 'T3': verify_t3,
           'T4': verify_t4, 'T5': verify_t5}

# ══════════════════════════════════════════════════════════════════
# 回帰テスト（元の予想②の数値 → 公式解答）
#   値が None の要素は照合しない。params は 'p' の一部だけでよい。
# ══════════════════════════════════════════════════════════════════
OFFICIAL8 = {
    'T1': (['材料Cが200g余る', '70 個', '15 個', '1.8 kg', '1.4 kg'],
           {'key': '1020-1510-1000-1200-97-32'}),
    'T2': (['18 倍', '15 度', f'{frac_html(F(2, 3))} 倍'], {'key': 'hex'}),
    'T3': (['12 通り', '22 通り', '64 通り'], {'key': '4-234'}),
    'T4': (['B班が16分早い', '10', frac_html(F(43, 4))], {'key': '12-36-4-9-12'}),
    'T5': (['××', '○○',
            'A○○○／B×○○、A○○×／B××○、A○××／B×○×',
            'A×○○／B○○○、A×○×／B○××、A××○／B○○×',
            '22 通り'], {'key': '1-o-4'}),
}
