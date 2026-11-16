# -*- coding: utf-8 -*-
"""NNOP第2回・算数の公式解答を、一般化した式で再現できるか確かめる。

OP2 の実装に入る前の足場。ここで式が合えば、あとは数値を振るだけになる。
"""
from fractions import Fraction as F
from math import gcd
import itertools

ok = lambda name, got, want: print(f'  {name:28} {str(got):22} 期待 {want}  {"OK" if str(got)==str(want) else "★不一致"}')

print('【大問1】操作P(2.5倍)・Q(3/5倍)・R(2/3倍)')
MUL = {'P': F(5, 2), 'Q': F(3, 5), 'R': F(2, 3)}
def apply(x, seq):
    v = F(x)
    for c in seq:
        v *= MUL[c]
    return v
r1 = apply(2027, 'RRPRPQ')
ok('(1) [2027→R R P R P Q]', f'{r1.numerator//r1.denominator} {r1.numerator%r1.denominator}/{r1.denominator}', '2252 2/9')
# (2) 6回・P,Q,Rどれも1回以上・結果が200より大きく400より小さい
cand = [''.join(s) for s in itertools.product('PQR', repeat=6)
        if all(c in s for c in 'PQR') and 200 < apply(200, s) < 400]
# かけ算なので順番は関係なく、回数の組み合わせで決まる
counts = sorted({tuple(sorted(s)) for s in cand})
print(f'  (2) 条件を満たす並びは {len(cand)} 通り（回数の組み合わせでは {len(counts)} 通り）')
print(f'      例: 200 → ' + ' → '.join('PQRPRR'), '=', apply(200, 'PQRPRR'))
ok('(2) 公式例が条件を満たすか', 200 < apply(200, 'PQRPRR') < 400, 'True')

print('\n【大問2】三角形ABC=175, DBC=126, ACD=35 → AOD')
def aod(S1, S2, S3):           # S1=ABC, S2=DBC, S3=ACD
    return F(S3 * (S1 + S3 - S2), S1 + S3)
ok('三角形AODの面積', aod(175, 126, 35), 14)

print('\n【大問3】A:16%180g, B:4%180g, C:水180g')
def beaker(ca, cb, w, g=180):
    sa, sb = F(ca, 100) * g, F(cb, 100) * g
    # Bの濃さが変わらない ⇔ Cから戻す食塩水の濃さ = Bの濃さ
    # (ca+cb)/100*x / (w+2x) = cb/100
    x = F(cb * w, ca - cb)
    cC = F(sa * 0 + (F(ca, 100) + F(cb, 100)) * x, w + 2 * x) * 100
    return sa, sb, cC, x
sa, sb, cC, x = beaker(16, 4, 180)
ok('(1) Aの食塩', f'{float(sa)}g', '28.8g')
ok('(1) Bの食塩', f'{float(sb)}g', '7.2g')
ok('(2) 最後のCの濃さ', (f'{cC.numerator}%' if cC.denominator==1 else f'{float(cC)}%'), '4%')
ok('(3) x', x, 60)

print('\n【大問4】AF:DC=3:7, 三角形ABE:DCE=3:19')
def op4(a, b, p, q):
    """AF:DC=a:b, [ABE]:[DCE]=p:q → (AE:EC, BF:FC)"""
    # [EBC]=u: (p+u):(u+q) = a:b  →  u = (b*p - a*q)/(a - b) ... 整理すると
    u = F(b * p - a * q, a - b)
    ae_ec = (p, u)                         # [ABE]:[EBC]
    g = gcd(int(p * u.denominator), int(u.numerator))
    s = F(p, p + u)                        # AE:AC
    # 座標で F の位置を出す（B=0, C=1, A の高さ a, D の高さ b）
    t = F(a * (1 - s), b)                  # BD上の E の位置
    f = (t - s) / (1 - s)                  # F の位置（B からの割合）
    return (p / u, f / (1 - f))
r, bf = op4(3, 7, 3, 19)
ok('AE:EC', f'{r.numerator} : {r.denominator}', '1 : 3')
ok('BF:FC', f'{bf.numerator} : {bf.denominator}', '2 : 19')

print('\n【大問5】太朗120/60, 次朗180/45, すれ違い12分40秒')
def op5(a1, b1, a2, b2, tmeet):
    T1, T2 = F(1, a1) + F(1, b1), F(1, a2) + F(1, b2)
    g = gcd(T1.numerator * T2.denominator, T2.numerator * T1.denominator)
    m = T1.denominator * T2.denominator // gcd(T1.denominator, T2.denominator)
    i1, i2 = int(T1 * m), int(T2 * m); g = gcd(i1, i2)
    ratio = (i1 // g, i2 // g)
    # 同時に家を出て tmeet 分後にすれ違う（次朗が折り返した後）
    # a1*t = D + (D/a2)*b2... → D*(1 + b2/a2) = a1*t + b2*t
    D = F((a1 + b2) * tmeet, 1 + F(b2, a2))
    post = D * T1 / (T1 + T2)              # 家から郵便局まで
    return ratio, D, post
ratio, D, post = op5(120, 60, 180, 45, F(38, 3))
ok('(1) 往復時間の比', f'{ratio[0]} : {ratio[1]}', '9 : 10')
ok('(2) 家〜公園', f'{D} m', '1672 m')
ok('(3) 家〜郵便局', f'{post} m', '792 m')

print('\n【大問6】<P> = P を 7 で割った余り')
M = 7
br = lambda n: n % M
ok('(1)① <1+2+…+100>', br(5050), 3)
ok('(1)② <<1895>+…+<1898>>', br(sum(br(n) for n in (1895, 1896, 1897, 1898))), 5)
ok('(1)③ <<2027>×<2027>×<2027>>', br(br(2027) ** 3), 1)
ok('(2) <[3,7]>', br(br(3) * 7), 0)
smallest = min(p for p in range(1000, 10000) if br(br(p) * 2027) == 3)
ok('(3) 最小の4桁P', smallest, 1000)
cnt = sum(1 for p in range(1000, 10000) if br(pow(br(p), 2027, M)) == 4)
ok('(4) 条件を満たす4桁Pの個数', f'{cnt} 個', '1286 個')
