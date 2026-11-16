# -*- coding: utf-8 -*-
"""第2回の候補を、生成に使った式とは別の原理で検算する。"""
import itertools
from fractions import Fraction as F
from math import gcd

import nnop_data as D
import nnop2_data as D2


def v_h1(vs):
    for v in vs:
        X1 = v['p']['X1']
        seq = v['p']['seq'].replace('→', '')
        # 1回ずつ順に掛けて確かめる（まとめて指数で計算しない）
        x = F(X1)
        for c in seq:
            x = x * (F(5, 2) if c == 'P' else F(3, 5) if c == 'Q' else F(2, 3))
        assert D.frac_html(x) == v['a'][0], v['p']
        # (2) 示した例が本当に条件を満たすか
        ex = v['a'][1].split('→', 1)[1].replace(' ', '').replace('→', '')
        y = F(v['p']['X2'])
        for c in ex:
            y = y * (F(5, 2) if c == 'P' else F(3, 5) if c == 'Q' else F(2, 3))
        assert len(ex) == 6 and set(ex) == set('PQR'), v['p']
        assert v['p']['lo'] < y < v['p']['hi'], (v['p'], y)
    return len(vs)


def v_h2(vs):
    for v in vs:
        S1, S2, S3 = (v['p'][k] for k in ('S1', 'S2', 'S3'))
        want = int(v['_chk'])
        # 4つの小三角形に分けて、条件がすべて成り立つか直接確かめる
        # [AOB]=x1 [BOC]=x2 [COD]=x3 [DOA]=x4
        x4 = F(want)
        k = F(S1 + S3 - S2, S2)                 # AO:OC
        x1, x2 = F(S1) * k / (1 + k), F(S1) / (1 + k)
        x3 = F(S3) / (1 + k)
        assert x1 + x2 == S1 and x3 + x4 == S3 and x2 + x3 == S2, v['p']
        assert x1 * x3 == x2 * x4, v['p']        # 対角線の性質
        assert all(x > 0 for x in (x1, x2, x3, x4)), v['p']
        assert f'{want} cm<sup>2</sup>' == v['a'][0]
    return len(vs)


def v_h3(vs):
    for v in vs:
        ca, cb, w = F(v['p']['ca']), F(v['p']['cb']), v['p']['w']
        x = F(int(v['a'][3]))
        # 実際に食塩を動かして確かめる（濃度の式を使い回さない）
        sA, sB, sC = ca * w / 100, cb * w / 100, F(0)
        wA = wB = wC = F(w)
        tA, tB = sA * x / wA, sB * x / wB            # AとBからxgずつ取り出す
        sA -= tA; wA -= x
        sB -= tB; wB -= x
        sC += tA + tB; wC += 2 * x
        cC = sC / wC * 100
        back = sC * x / wC                            # Cからxgずつ戻す
        sA += back; wA += x
        sB += back; wB += x
        sC -= 2 * back; wC -= 2 * x
        assert wA == w and wB == w and wC == w, v['p']
        assert sB / wB * 100 == cb, ('Bの濃さが変わっている', v['p'])
        assert cC == cb, v['p']
        assert v['a'][:3] == [f'{D.num(ca*w/100)} g', f'{D.num(cb*w/100)} g', f'{D.num(cb)}%']
    return len(vs)


def v_h4(vs):
    for v in vs:
        a, b, p, q = (v['p'][k] for k in ('a', 'b', 'p', 'q'))
        ae, ec, bf, fc = v['_chk']
        # 座標で組み立て直す（比の式を使い回さない）
        f = F(bf, bf + fc)
        B, C, Dp, A = (F(0), F(0)), (F(1), F(0)), (F(1), F(b)), (f, F(a))
        def cross(p1, p2, p3, p4):
            d = (p2[0]-p1[0])*(p4[1]-p3[1]) - (p2[1]-p1[1])*(p4[0]-p3[0])
            t = ((p3[0]-p1[0])*(p4[1]-p3[1]) - (p3[1]-p1[1])*(p4[0]-p3[0])) / d
            return (p1[0]+t*(p2[0]-p1[0]), p1[1]+t*(p2[1]-p1[1]))
        E = cross(A, C, B, Dp)
        area = lambda P, Q, R: abs((Q[0]-P[0])*(R[1]-P[1]) - (R[0]-P[0])*(Q[1]-P[1])) / 2
        assert D.ratio_of(area(A, B, E), area(Dp, C, E)) == (p, q), ('面積比が違う', v['p'])
        # AE:EC を座標から
        ae2 = abs(E[0]-A[0]) if A[0] != C[0] else abs(E[1]-A[1])
        ec2 = abs(C[0]-E[0]) if A[0] != C[0] else abs(C[1]-E[1])
        assert D.ratio_of(ae2, ec2) == (ae, ec), ('AE:ECが違う', v['p'])
        assert v['a'] == [f'{ae} : {ec}', f'{bf} : {fc}']
    return len(vs)


def v_h5(vs):
    for v in vs:
        a1, b1, a2, b2 = (v['p'][k] for k in ('a1', 'b1', 'a2', 'b2'))
        (r1, Dm, post, ts) = v['_chk']
        t = F(ts, 60)
        # (2) その時刻に2人が同じ場所にいるか、位置を直接計算して確かめる
        tTurn2 = F(Dm, a2)
        assert t > tTurn2, ('次朗がまだ折り返していない', v['p'])
        pos2 = Dm - b2 * (t - tTurn2)
        pos1 = a1 * t
        assert F(Dm, a1) >= t, ('太朗が先に公園に着いている', v['p'])
        assert pos1 == pos2 == F(Dm) - F(Dm) + pos1, v['p']
        assert pos1 == pos2, ('すれ違っていない', v['p'])
        # (3) 2回とも同じ地点ですれ違う条件を直接確かめる
        T1, T2 = F(1, a1) + F(1, b1), F(1, a2) + F(1, b2)
        assert (Dm - post) * T1 == post * T2, ('郵便局の位置が合わない', v['p'])
        assert v['a'] == [f'{r1[0]} : {r1[1]}', f'{Dm} m', f'{post} m']
    return len(vs)


def v_h6(vs):
    for v in vs:
        M, N, K, st, c, Q = (v['p'][k] for k in ('M', 'N', 'K', 'st', 'c', 'Q'))
        t3, t4 = v['p']['t3'], v['p']['t4']
        br = lambda n: n % M
        # ①は1から順に足して確かめる（公式を使わない）
        assert br(sum(range(1, K + 1))) == int(v['a'][0]), v['p']
        assert br(sum(br(n) for n in range(st, st + 4))) == int(v['a'][1]), v['p']
        assert br(br(N) * br(N) * br(N)) == int(v['a'][2]), v['p']
        assert br(br(c) * Q) == int(v['a'][3]), v['p']
        sm = min(P for P in range(1000, 10000) if br(br(P) * N) == t3)
        assert sm == int(v['a'][4]), v['p']
        # 【P,N】はくり返しかけ算そのものでも確かめる（pow を使わない）
        def rep(x, n):
            r = 1
            for _ in range(n):
                r = br(r * x)
            return r
        res = {p0: rep(p0, N) for p0 in range(M)}
        cnt = sum(1 for P in range(1000, 10000) if res[br(P)] == t4)
        assert f'{cnt} 個' == v['a'][5], v['p']
    return len(vs)


VERIFY2 = {'H1': v_h1, 'H2': v_h2, 'H3': v_h3, 'H4': v_h4, 'H5': v_h5, 'H6': v_h6}

OFFICIAL2 = {
    'H1': (['2252<span class="fr"><span class="fn">2</span><span class="fd">9</span></span>', None],
           {'X1': 2027, 'seq': 'R→R→P→R→P→Q'}),
    'H2': (['14 cm<sup>2</sup>'], {'S1': 175, 'S2': 126, 'S3': 35}),
    'H3': (['28.8 g', '7.2 g', '4%', '60'], {'ca': '16', 'cb': '4', 'w': 180}),
    'H4': (['1 : 3', '2 : 19'], {'a': 3, 'b': 7, 'p': 3, 'q': 19}),
    'H5': (['9 : 10', '1672 m', '792 m'],
           {'a1': 120, 'b1': 60, 'a2': 180, 'b2': 45, 'tm': '12分40秒'}),
    'H6': (['3', '5', '1', '0', '1000', '1286 個'],
           {'M': 7, 'N': 2027, 'K': 100, 'st': 1895, 'c': 3, 'Q': 7}),
}
