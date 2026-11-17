# -*- coding: utf-8 -*-
"""第5回の独立検算と、元の数値での回帰テスト。

生成器が使った式をそのまま使い回すと、式がまちがっていても一致してしまう。
ここでは**別の原理**で解き直して突き合わせる（nnop_spec.md 7.1 / 13章）。

  R1  虫食い算 … 100通りの筆算を全部やって、条件に合う組をひろい直す
  R2  濃度　　 … 答えのAとBから砂糖の重さを組み立て直し、問題文の濃さに戻るか見る
  R3  場合の数 … 組み合わせの式＋包除原理（生成器は配り方のDP）
  R4  速さ　　 … 1区間ずつ直線の交点を解いて、出会いを実際にひろう
  R5  平面図形 … 長方形の位置を座標でとり、重なりの長方形を直接はかる
  R6  規則性　 … あまりで数え上げる閉じた式（生成器は実際にふるいにかけている）
"""
import collections
from fractions import Fraction as F
from math import comb

import nnop6_data as DX


# ── R1 ───────────────────────────────────────────────────────────
def verify_r1(vs):
    """全部の筆算をやり直して、答えの組がもれなく一致するか見る。"""
    for v in vs:
        p = v['p']
        f, pat = p['f'], (p['d1'], p['d2'], p['d4'], p['d5'])
        got = []
        for a in range(10):
            for b in range(10):
                if a > b:
                    continue                      # ア≦イ
                n1, n2 = 101 * f + 10 * a, 101 * f + 10 * b
                s = str(n1 * n2)
                if len(s) == 5 and (s[0], s[1], s[3], s[4]) == pat:
                    got.append((a, b, int(s[2])))
        want = '、'.join(f'（{a}、{b}、{c}）' for a, b, c in got)
        assert got, ('解が無い', p)
        assert want == v['a'][0], ('R1 が合わない', p, want, v['a'][0])
    return len(vs)


# ── R2 ───────────────────────────────────────────────────────────
def verify_r2(vs):
    """答えのA・Bから砂糖の重さを積み上げ、問題文の濃さに戻るか確かめる。"""
    for v in vs:
        p = v['p']
        W = F(p['W'])
        c0, cl, ch = (F(p[k]) / 100 for k in ('c0', 'cl', 'ch'))
        A = F(v['a'][1].split()[0])
        B = F(v['a'][2].split()[0])
        S = W + A + B
        sP = c0 * W + cl * A + ch * B          # 砂糖の重さ（P）
        sQ = c0 * W + cl * B + ch * A          # 砂糖の重さ（Q）
        assert sP / S * 100 == F(p['P']), ('Pの濃さが合わない', p)
        assert sQ / S * 100 == F(p['Q']), ('Qの濃さが合わない', p)
        # (1)：PとQを混ぜる＝砂糖も重さも足す
        mixed = (sP + sQ) / (2 * S) * 100
        assert v['a'][0] == DX.num(mixed) + ' %', ('混ぜた濃さ', p, mixed)
        # 和差算の筋道（問題が解ける形になっているか）
        assert A + B == W * (mixed - c0 * 100) / ((cl + ch) * 50 - mixed), ('和', p)
        assert B - A == (F(p['P']) - F(p['Q'])) * S / ((ch - cl) * 100), ('差', p)
        assert A != B and A > 0, ('AとBが同じ', p)
        assert (A + B) % 10 == 0 and (B - A) % 10 == 0, ('和差がきれいでない', p)
    return len(vs)


# ── R3 ───────────────────────────────────────────────────────────
def verify_r3(vs):
    """組み合わせの式と包除原理で出し直す（生成器は配り方のDP）。"""
    for v in vs:
        T, m, U = v['p']['T'], v['p']['m'], v['p']['U']
        a1 = comb(T - m + 2, 2)                       # 残りを3クラスへ（0個可）
        a2 = comb(T - 1, 3)                           # 4クラスへ1個以上
        a3 = 0
        for j in range(5):                            # 包除原理（U個をこえるクラス数）
            r = T - j * U - 4                         # 各クラスに1個ずつ配ったあと
            if r < 0:
                break
            a3 += (-1) ** j * comb(4, j) * comb(r + 3, 3)
        assert v['a'] == [f'{a1} 通り', f'{a2} 通り', f'{a3} 通り'], \
            ('R3 が合わない', v['p'], v['a'], [a1, a2, a3])
    return len(vs)


# ── R4 ───────────────────────────────────────────────────────────
def _meets(L, vj, vt, T):
    """折り返しの時刻で区切り、各区間で1次式の交点を解いて出会いをひろう。"""
    L, vj, vt, T = F(L), F(vj), F(vt), F(T)

    def pos(v, t):
        d = (v * t) % (2 * L)
        return d if d <= L else 2 * L - d

    def arrow(v, t):                                   # +1 往き / −1 帰り
        return 1 if ((v * t) // L) % 2 == 0 else -1

    ts = {F(0), T}
    for v in (vj, vt):
        k = 1
        while F(k) * L / v < T:
            ts.add(F(k) * L / v)
            k += 1
    ts = sorted(ts)
    out = []
    for t0, t1 in zip(ts, ts[1:]):
        tm = (t0 + t1) / 2
        sj, st = arrow(vj, tm), arrow(vt, tm)
        if sj == st:
            continue                                   # 同じ向き＝追いつき
        den = sj * vj - st * vt
        if den == 0:
            continue
        t = t0 + (pos(vt, t0) - pos(vj, t0)) / den
        if t0 <= t <= t1:
            x = pos(vj, t)
            if 0 < x < L and (not out or out[-1][0] != t):
                out.append((t, x))
    return out


def verify_r4(vs):
    """時刻を追って出会いを実際にひろい、(1)(2)(3)を出し直す。"""
    for v in vs:
        p = v['p']
        L, vj, T = p['L'], p['vj'], p['T']
        assert vj * T == 2 * L, ('次朗がちょうど1往復になっていない', p)
        m1 = _meets(L, vj, p['v1'], T)
        u1 = sorted({x for _, x in m1})
        assert v['a'][0] == f'{len(u1)} か所', ('(1)', p, u1)
        assert len(u1) == len(m1), ('(1) 場所が重なっている', p)
        m2 = _meets(L, vj, p['v2'], T)
        u2 = sorted({x for _, x in m2})
        want = [f'{int(x)} m' for x in u2] + [''] * (3 - len(u2))
        assert v['a'][1:4] == want, ('(2)', p, want, v['a'][1:4])
        # (3) 範囲のはしと中を、実際に数えて確かめる
        n = p['n']
        lo, hi = vj * (n - 1), vj * n
        assert v['a'][4] == f'{lo} m より大きく', ('(3)下限', p)
        assert v['a'][5].startswith(f'{hi} m '), ('(3)上限', p)
        assert len(_meets(L, vj, lo, T)) < n, ('(3) 下限が入ってしまう', p)
        inside = len(_meets(L, vj, hi, T)) == n
        assert v['a'][5].endswith('以下' if inside else '未満'), ('(3) 上限の言い方', p)
        for f_ in (F(1, 7), F(1, 2), F(6, 7)):
            vt = lo + (hi - lo) * f_
            assert len(_meets(L, vj, vt, T)) == n, ('(3) 範囲の中で回数がちがう', p, vt)
    return len(vs)


# ── R5 ───────────────────────────────────────────────────────────
def _overlap(W, H, p1, q1, p2, q2):
    """左上(横p1・たてq1)と右下(横p2・たてq2)の重なりを座標から直接はかる。"""
    ax0, ax1, ay0, ay1 = 0, p1, 0, q1                  # 左上の長方形
    bx0, bx1, by0, by1 = W - p2, W, H - q2, H          # 右下の長方形
    w = min(ax1, bx1) - max(ax0, bx0)
    h = min(ay1, by1) - max(ay0, by0)
    return w * h if w > 0 and h > 0 else 0


def verify_r5(vs):
    """すべての(たて,横)を座標で置いてみて、重なりが面積Aになる置き方を数え直す。"""
    for v in vs:
        p = v['p']
        W, H, A = p['W'], p['H'], p['A']
        same, perp = [], []
        for a in range(1, max(W, H) + 1):
            for b in range(1, max(W, H) + 1):
                if a == b:
                    continue                            # 正方形は除く
                if a <= W and b <= H:                   # 同じ向き（2枚とも 横a・たてb）
                    if _overlap(W, H, a, b, a, b) == A:
                        same.append((a, b))
                if a <= W and b <= H and b <= W and a <= H and a < b:
                    # 直角向き（左上 横a・たてb ／ 右下 横b・たてa）。組は1回だけ数える
                    if _overlap(W, H, a, b, b, a) == A:
                        perp.append((a, b))
        assert v['a'][0] == f'{len(same)} 通り', ('(1)', p, same)
        assert v['a'][1] == f'{len(same) + len(perp)} 通り', ('(2)', p, same, perp)
        # 図2の例の重なりが問題文の数と合うか
        e1, e2 = p['e1'], p['e2']
        assert _overlap(W, H, e1, e2, e2, e1) == p['EX'], ('図2の例', p)
        assert p['EX'] != A, ('例の面積が問題と同じ', p)
    return len(vs)


# ── R6 / R6a ─────────────────────────────────────────────────────
def _r6_closed(N):
    """あまりで数え上げる閉じた式（生成器は実際にふるいにかけている）。

    n行目に残るのは A列=6n−5 と E列=6n−1（1行目だけは 2・3・5 が残る）。
      5の倍数になるのは n≡0（A列）と n≡1（E列）…ただし E列の5そのものは消さない
      7の倍数になるのは n≡2（A列）と n≡6（E列）…ただし A列の7そのものは消さない
    """
    rows = N // 6
    two5 = sum(1 for n in range(2, rows + 1) if n % 5 not in (0, 1))
    alive5 = 3                                          # 1行目の 2・3・5
    for n in range(2, rows + 1):
        alive5 += 2 - (1 if n % 5 in (0, 1) else 0)
    two7 = 0
    for n in range(2, rows + 1):
        a_gone = (n % 5 == 0) or (n % 7 == 2 and 6 * n - 5 != 7)
        e_gone = (n % 5 == 1) or (n % 7 == 6 and 6 * n - 1 != 7)
        if not a_gone and not e_gone:
            two7 += 1
    return two5, alive5, two7


def _r6_row(N, S):
    """和がSになる行を、和差算（2つの数の差は4）から直接出す。"""
    small = (S - 4) // 2
    assert small * 2 + 4 == S, ('和が奇数', N, S)
    assert small % 6 == 1, ('A列の数になっていない', N, S)
    return small // 6 + 1


def verify_r6(vs):
    for v in vs:
        N, S = v['p']['N'], v['p']['S']
        two5, alive5, _ = _r6_closed(N)
        n = _r6_row(N, S)
        assert v['a'] == [f'{n} 行目', f'{two5} 行', f'{alive5} 個'], \
            ('R6 が合わない', v['p'], v['a'], [n, two5, alive5])
    return len(vs)


def verify_r6a(vs):
    for v in vs:
        _, _, two7 = _r6_closed(v['p']['N'])
        assert v['a'] == [f'{two7} 行'], ('R6a が合わない', v['p'], v['a'], two7)
    return len(vs)


VERIFY6 = {'R1': verify_r1, 'R2': verify_r2, 'R3': verify_r3, 'R4': verify_r4,
           'R5': verify_r5, 'R6': verify_r6, 'R6a': verify_r6a}

# ══════════════════════════════════════════════════════════════════
# 回帰テスト（元の第5回の数値 → 公式解答）
#   値が None の要素は照合しない。params は 'p' の一部だけでよい。
# ══════════════════════════════════════════════════════════════════
OFFICIAL6 = {
    'R1':  (['（0、2、8）、（1、1、9）'], {'pat': '2-4444'}),
    'R2':  (['6.25 %', '180 g', '220 g'], {'key': '80-5-2-11-180-220'}),
    'R3':  (['28 通り', '364 通り', '284 通り'], {'key': '15-9-8'}),
    'R4':  (['4 か所', '200 m', '400 m', '', '400 m より大きく', '450 m 未満'],
            {'key': '50-24-180-250-9'}),
    'R5':  (['2 通り', '5 通り'], {'key': '11-30'}),
    'R6':  (['30 行目', '60 行', '162 個'], {'key': '600-354'}),
    'R6a': (['44 行'], {'key': '600-354'}),
}
