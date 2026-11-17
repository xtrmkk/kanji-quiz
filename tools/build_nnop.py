# -*- coding: utf-8 -*-
"""NNOPランダムテストのHTMLを生成する。

  python3 tools/build_nnop.py

tools/nnop_template.html に、tools/nnop_data.py が出した設問マスタ・候補と
tools/nnop_fig.py が描いたSVGを埋めこんで templates/nnop.html を作る。

ビルド前に必ず検証を走らせる（nnop_spec.md 7章）。
 1. 独立検算  … 生成器とは別の原理で解答を出し直して突き合わせる
 2. 回帰テスト … 元のNNOPの数値で公式解答と一致するか
"""
import json, math, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import nnop_data as D          # noqa: E402
import nnop2_data as D2        # noqa: E402
import nnop2_verify as V2      # noqa: E402
import nnop3_data as D3        # noqa: E402
import nnop3_verify as V3      # noqa: E402
import nnop4_data as D4        # noqa: E402
import nnop4_verify as V4      # noqa: E402
import nnop5_data as D5        # noqa: E402
import nnop5_verify as V5      # noqa: E402
import nnop6_data as D6        # noqa: E402
import nnop6_verify as V6      # noqa: E402
import nnop_fig as G           # noqa: E402

ROUND_NAME = {1: '第1回', 2: '第2回', 3: '第3回', 'N': '夏期そっくり', 4: '第4回', 5: '第5回'}
ROUND_ORDER = [1, 2, 3, 'N', 4, 5]

ALL_GROUPS = D.GROUPS + D2.GROUPS2 + D3.GROUPS3 + D4.GROUPS4 + D5.GROUPS5 + D6.GROUPS6
ALL_VARIANTS = {**D.VARIANTS, **D2.VARIANTS2, **D3.VARIANTS3, **D4.VARIANTS4, **D5.VARIANTS5, **D6.VARIANTS6}
ALL_WORK = {**D.WORK_MM, **D2.WORK_MM2, **D3.WORK_MM3, **D4.WORK_MM4, **D5.WORK_MM5, **D6.WORK_MM6}


# ══════════════════════════════════════════════════════════════════
# 1. 独立検算
# ══════════════════════════════════════════════════════════════════
def verify_g1(vs):
    for v in vs:
        N, D_ = v['p']['N'], v['p']['D']
        h, m, s = (int(x) for x in v['a'])
        # 逆向きに組み立て直す
        assert F(h * 3600 + m * 60 + s, 60) == F(N, D_), (N, D_)
        assert 0 <= m < 60 and 0 <= s < 60 and h >= 1
    return len(vs)


def verify_g2(vs):
    """数値積分（真のπ）で図形の面積を確かめ、表示用は3.14で厳密に出し直す。"""
    def integ(lo, hi, f, n=40000):
        s = 0.0
        dy = (hi - lo) / n
        for i in range(n):
            y = lo + (i + 0.5) * dy
            s += f(y) * dy
        return s
    for v in vs:
        r, a = v['p']['r'], v['p']['a']
        ar, br = math.radians(a), math.radians(90 - a)
        y1, y2 = r * math.sin(ar), r * math.sin(br)
        half = lambda y: math.sqrt(max(r * r - y * y, 0.0))
        # (1) 縦の半径〜弧、2本の弦の間
        s1 = integ(y1, y2, half)
        assert abs(s1 - math.pi * r * r * (90 - 2 * a) / 360) < 1e-6, (r, a, s1)
        # (2) 上のキャップ＋中心下の帯
        s2 = integ(y2, r, lambda y: 2 * half(y)) + integ(-y1, 0, lambda y: 2 * half(y))
        assert abs(s2 - math.pi * r * r * a / 90) < 1e-5, (r, a, s2)
        # 表示用（3.14）は厳密な分数で
        assert v['a'][0] == D.num(F(314, 100) * r * r * F(90 - 2 * a, 360))
        assert v['a'][1] == D.num(F(314, 100) * r * r * F(a, 90))
    return len(vs)


def verify_g3(vs):
    """食塩の重さの保存で確かめる（濃度の式を使い回さない）。"""
    for v in vs:
        p, q, r = (F(x) if '.' not in x else F(x) for x in v['_pqr'])
        p, q, r = (F(x).limit_denominator(100) for x in
                   (F(v['_pqr'][0]), F(v['_pqr'][1]), F(v['_pqr'][2])))
        c1, c2, c3 = (F(v['p'][k]) for k in ('c1', 'c2', 'c3'))
        # 問題文の3条件：食塩の重さ＝重さ×濃さ
        assert 100 * p + 200 * q == 300 * c1
        assert 100 * q + 200 * r == 300 * c2
        assert 100 * r + 200 * p == 300 * c3
        # 解答
        assert D.num((100 * p + 100 * q + 100 * r) / 300) + '%' == v['a'][0]
        assert D.num((200 * p + 100 * q) / 300) + '%' == v['a'][1]
        assert D.num(q) + '%' == v['a'][2]
    return len(vs)


def verify_g4(vs):
    """出来事の時刻を厳密な分数で求め、順序と時間差を直接確かめる。"""
    for v in vs:
        v1, v2, v3, k, T = (v['p'][x] for x in ('v1', 'v2', 'v3', 'k', 'T'))
        Dm = v['_chk']['D']
        t1 = F(Dm, v1 + v2)                      # すれ違う時刻
        HP, PS = v1 * t1, v2 * t1
        tS = t1 + F(PS, v3)                      # 太朗が駅に着く時刻
        # 追いつく時刻：D - v3(t - tS) = HP - v2(t - t1)
        t2 = F(Dm - HP + v3 * tS - v2 * t1, v3 - v2)
        C = HP - v2 * (t2 - t1)
        assert t2 >= tS, ('折り返す前に追いついている', v['p'])
        assert 0 < C < HP < Dm, ('追いつく場所がおかしい', v['p'])
        t_jiro = t2 + F(C, k * v2)
        t_taro = t2 + F(C, v3)
        assert t_taro - t_jiro == F(T, 60), ('時間差が合わない', v['p'])
        assert C == v['_chk']['C'] and HP == v['_chk']['HP']
        assert v['a'][2] == f'{Dm} m'
    return len(vs)


def verify_g5(vs):
    """別の書き方でもう一度数える。"""
    n, m = D.N_POLY, D.M_DICE
    import itertools
    pos = lambda u, s: (u * s) % n
    notri = iso1 = iso2 = 0
    for u, w in itertools.product(range(1, m + 1), repeat=2):
        P, Q = pos(u, 1), pos(w, -1)
        pts = [0, P, Q]
        if len(set(pts)) < 3:
            notri += 1
            continue
        def leng(x, y):
            t = (x - y) % n
            return min(t, n - t)
        AP, AQ, PQ = leng(0, P), leng(0, Q), leng(P, Q)
        if AP == AQ:
            iso1 += 1
        if len({AP, AQ, PQ}) < 3:
            iso2 += 1
    got = [f'{notri} 通り', f'{iso1} 通り', f'{iso2} 通り']
    assert got == vs[0]['a'], (got, vs[0]['a'])
    return len(vs)


def verify_g6(vs):
    """各項を直接足し上げて、差の形の式と突き合わせる。"""
    for v in vs:
        N, P2, Q2 = (v['p'][x] for x in ('N', 'P2', 'Q2'))
        a1 = F(1, N * (N + 1))
        a2 = sum((1 - F(1, n * (n + 1)) for n in range(P2, Q2 + 1)), F(0))
        assert (a1, a2) == v['_chk'], v['p']
        assert D.frac_html(a1) + ' cm<sup>2</sup>' == v['a'][0]
        assert D.frac_html(a2) + ' cm<sup>2</sup>' == v['a'][1]
    return len(vs)


def verify_g6a(vs):
    for v in vs:
        P3, Q3 = v['p']['P3'], v['p']['Q3']
        wa = sum((F(1, (2 * n - 1) * (2 * n + 1)) for n in range(P3, Q3 + 1)), F(0))
        ea = sum((1 - F(1, (2 * n - 1) * (2 * n + 1)) for n in range(P3, Q3 + 1)), F(0))
        w2, e2, k, P4, Q4, S = v['_chk']
        assert (wa, ea) == (w2, e2), v['p']
        # (4) も直接足し上げて確かめる
        S2 = sum((1 - F(1, (2 * n - 1) * (2 * n + 1)) for n in range(P4, Q4 + 1)), F(0))
        assert S2 == S and k == Q4 - P4 + 1, v['p']
        assert v['a'][2] == f'{k} 個' and v['a'][3] == f'P = {P4}、Q = {Q4}'
    return len(vs)


VERIFY = {'G1': verify_g1, 'G2': verify_g2, 'G3': verify_g3, 'G4': verify_g4,
          'G5': verify_g5, 'G6': verify_g6, 'G6a': verify_g6a}


# ══════════════════════════════════════════════════════════════════
# 2. 回帰テスト（元のNNOPの数値で公式解答と一致するか）
# ══════════════════════════════════════════════════════════════════
OFFICIAL = {
    'G1':  (['2', '48', '55'], {'N': 2027, 'D': 12}),
    'G2':  (['15.7', '25.12'], {'r': 6, 'a': 20}),
    'G3':  (['4.5%', '4%', '2%'], {'c1': '3', 'c2': '5', 'c3': '5.5'}),
    'G4':  (['8 : 3', '3 : 2', '2640 m'], {'v1': 160, 'v2': 60, 'v3': 140, 'k': 3, 'T': 80}),
    'G5':  (['5 通り', '5 通り', '15 通り'], {'n': 8}),
    'G6':  (['<span class="fr"><span class="fn">1</span><span class="fd">650</span></span> cm<sup>2</sup>',
             '43<span class="fr"><span class="fn">157</span><span class="fd">168</span></span> cm<sup>2</sup>'],
            {'N': 25, 'P2': 12, 'Q2': 55}),
    'G6a': (['<span class="fr"><span class="fn">8</span><span class="fd">105</span></span> cm<sup>2</sup>',
             '7<span class="fr"><span class="fn">97</span><span class="fd">105</span></span> cm<sup>2</sup>',
             '9 個', 'P = 7、Q = 15'],
            {'P3': 3, 'Q3': 10}),
}


def regression2(all_vs):
    for key, (ans, params) in V2.OFFICIAL2.items():
        hit = [v for v in all_vs[key]
               if all(str(v['p'].get(k)) == str(x) for k, x in params.items())]
        assert hit, f'{key}: 元の数値の候補が無い {params}'
        ok = [v for v in hit
              if all(a is None or a == b for a, b in zip(ans, v['a']))]
        assert ok, (f'{key}: 公式解答と一致しない\n  期待 {ans}\n  実際 {hit[0]["a"]}')
    return len(V2.OFFICIAL2)


def regression_of(all_vs, official):
    """元の数値を入れた候補をさがし、公式解答と突き合わせる。"""
    for key, (ans, params) in official.items():
        hit = [v for v in all_vs[key]
               if all(str(v['p'].get(k)) == str(x) for k, x in params.items())]
        assert hit, f'{key}: 元の数値の候補が無い {params}'
        ok = [v for v in hit
              if all(a is None or a == b for a, b in zip(ans, v['a']))]
        assert ok, (f'{key}: 公式解答と一致しない\n  期待 {ans}\n  実際 {hit[0]["a"]}')
    return len(official)


def regression(all_vs):
    for key, (ans, params) in OFFICIAL.items():
        hit = [v for v in all_vs[key]
               if all(str(v['p'].get(k)) == str(x) for k, x in params.items())]
        assert hit, f'{key}: 元の数値の候補が無い {params}'
        ok = [v for v in hit if v['a'] == ans]
        assert ok, (f'{key}: 公式解答と一致しない\n  期待 {ans}\n  実際 {hit[0]["a"]}')
    return len(OFFICIAL)


# ══════════════════════════════════════════════════════════════════
# 3. ビルド
# ══════════════════════════════════════════════════════════════════
def build():
    all_vs = {g['key']: ALL_VARIANTS[g['key']]() for g in ALL_GROUPS}
    verify = {**VERIFY, **V2.VERIFY2, **V3.VERIFY3, **V4.VERIFY4, **V5.VERIFY5, **V6.VERIFY6}

    print('― 独立検算 ―')
    for g in ALL_GROUPS:
        n = verify[g['key']](all_vs[g['key']])
        print(f'  {ROUND_NAME[g["round"]]:6} {g["key"]:4} {g["title"]:18} {n:4}通り OK')

    print('― 回帰テスト（公式解答との照合）―')
    print(f'  第1回 {regression(all_vs)} 大問すべて一致')
    print(f'  第2回 {regression2(all_vs)} 大問すべて一致')
    print(f'  第3回 {regression_of(all_vs, V3.OFFICIAL3)} 大問すべて一致')
    print(f'  夏期　 {regression_of(all_vs, V4.OFFICIAL4)} 大問すべて一致')
    print(f'  第4回 {regression_of(all_vs, V5.OFFICIAL5)} 大問すべて一致')
    print(f'  第5回 {regression_of(all_vs, V6.OFFICIAL6)} 大問すべて一致')

    # 図
    figs = {}
    for a in D.G2_ANGLES:
        figs[f'ogi:{a}'] = G.ogi_svg(a)
        figs[f'circle:{a}'] = G.circle_svg(a)
    figs['octagon'] = G.octagon_svg()
    figs['quad'] = G.quad_svg()
    figs['tri2'] = G.tri2_svg()
    figs['tri_front'] = G.tri_row_svg('front')
    figs['tri_back'] = G.tri_row_svg('back')
    figs['pond'] = G.pond_svg()
    figs['rect'] = G.rect_svg()
    figs['roll'] = G.roll_svg()
    for v in all_vs['N3']:
        figs[f'tri6:{v["p"]["L"]}'] = G.tri6_svg(v['p']['L'])
    for v in all_vs['N5']:
        figs[f'circ:{v["p"]["W"]}'] = G.circ_svg(v['p']['W'])
        figs[f'tri345:{v["p"]["pq"]}'] = G.tri345_svg(v['p']['p'], v['p']['q'])
    # 第4回
    for v in all_vs['M2']:
        figs[f'para:{v["p"]["mn"]}'] = G.para_svg(v['p']['m'], v['p']['n'])
    for v in all_vs['M3']:
        figs[f'rect3:{v["p"]["k"]}'] = G.rect3_svg(v['p']['k'])
    figs['meet:P'] = G.meet_svg('P')
    figs['meet:Q'] = G.meet_svg('Q')
    for v in all_vs['M5']:
        figs[f'ringL:{v["p"]["n1"]}'] = G.ring_svg(v['p']['n1'], True)
        for n in (v['p']['n2'], v['p']['n3']):
            figs[f'ring:{n}'] = G.ring_svg(n, False)
    # 第5回
    for v in all_vs['R5']:
        q = v['p']
        figs[f'dai:{q["W"]}x{q["H"]}x{q["e1"]}x{q["e2"]}'] = \
            G.dai_svg(q['W'], q['H'], q['e1'], q['e2'])
    for v in all_vs['R6']:
        figs[f'sieve:{v["p"]["N"]}'] = G.sieve_svg(v['p']['N'])

    # 図のキーがぜんぶ用意できているか（{…}を埋めてから照合する）
    for g in ALL_GROUPS:
        for key, where in ([(g.get('fig'), g['key'])] +
                           [(s.get('fig'), s['id']) for s in g['subs']]):
            if not key:
                continue
            for v in all_vs[g['key']]:
                k = key
                for name, val in v['p'].items():
                    k = k.replace('{' + name + '}', str(val))
                assert '{' not in k and k in figs, f'{where}: 図が無い {k}'

    # 内部用のキー（_chk / _pqr）は出力しない
    out_vs = {k: [{'p': v['p'], 'a': v['a']} for v in vs] for k, vs in all_vs.items()}
    groups = [{k: g[k] for k in g if k != 'vary'} for g in ALL_GROUPS]

    have = {g['round'] for g in ALL_GROUPS}
    rounds = [r for r in ROUND_ORDER if r in have]
    data = ('const ROUNDS='   + json.dumps(rounds) + ';\n'
            'const ROUNDNAME=' + json.dumps({str(k): v for k, v in ROUND_NAME.items()},
                                            ensure_ascii=False) + ';\n'
            'const FIELDS='   + json.dumps(D.FIELDS, ensure_ascii=False) + ';\n'
            'const FIELDNAME=' + json.dumps(dict(D.FIELDS), ensure_ascii=False) + ';\n'
            'const GROUPS='   + json.dumps(groups, ensure_ascii=False) + ';\n'
            'const VARIANTS=' + json.dumps(out_vs, ensure_ascii=False) + ';\n'
            'const WORK_MM=' + json.dumps(ALL_WORK, ensure_ascii=False) + ';\n'
            'const FIGS='     + json.dumps(figs, ensure_ascii=False) + ';')

    tpl = open(os.path.join(HERE, 'nnop_template.html'), encoding='utf-8').read()
    assert '/*__QDATA__*/' in tpl, 'テンプレートにプレースホルダが無い'
    html = tpl.replace('/*__QDATA__*/', data)

    for bad in ('{#', '{%', '{{'):
        assert bad not in html, f'Jinjaと衝突する記号が入っている: {bad}'

    dest = os.path.join(ROOT, 'templates', 'nnop.html')
    open(dest, 'w', encoding='utf-8').write(html)
    print(f'生成: {dest}  ({len(html)//1024} KB)')


if __name__ == '__main__':
    build()
