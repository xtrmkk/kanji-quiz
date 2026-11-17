# -*- coding: utf-8 -*-
"""NNOPランダムテストの図をSVGで作る。

数値で変わるのは「おうぎ形」と「円」の2枚だけ（しかも角aの5通り）。
正八角形と正三角形は固定。
"""
import math

# 線や文字の太さ（印刷したときに潰れない最小限）
LW, LW2, FS = 1.3, 1.0, 11
SHADE = '#c9cdd4'


def _p(x, y, cx, cy):
    return f'{cx + x:.2f},{cy - y:.2f}'


# ══════════════════════════════════════════════════════════════════
# おうぎ形（中心角90°・半径6・●の角a）
# ══════════════════════════════════════════════════════════════════
def ogi_svg(a_deg: int, R=108, pad=16) -> str:
    cx, cy = pad, pad + R                      # 中心は左下
    W, H = R + pad * 2, R + pad * 2
    ar, br = math.radians(a_deg), math.radians(90 - a_deg)
    Q = (R * math.cos(ar), R * math.sin(ar))   # 下側の半径の先
    P = (R * math.cos(br), R * math.sin(br))   # 上側の半径の先
    pt = lambda x, y: _p(x, y, cx, cy)

    shade = (f'M {pt(0, P[1])} L {pt(*P)} '
             f'A {R} {R} 0 0 1 {pt(*Q)} '
             f'L {pt(0, Q[1])} Z')
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append(f'<path d="{shade}" fill="{SHADE}" stroke="none"/>')
    # おうぎ形の外形
    s.append(f'<path d="M {pt(0,0)} L {pt(R,0)} A {R} {R} 0 0 0 {pt(0,R)} Z" '
             f'fill="none" stroke="#111" stroke-width="{LW}"/>')
    # 半径2本
    for X in (P, Q):
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{cx+X[0]:.2f}" y2="{cy-X[1]:.2f}" '
                 f'stroke="#111" stroke-width="{LW2}"/>')
    # 縦の半径に垂直な弦2本
    for X in (P, Q):
        s.append(f'<line x1="{cx}" y1="{cy-X[1]:.2f}" x2="{cx+X[0]:.2f}" y2="{cy-X[1]:.2f}" '
                 f'stroke="#111" stroke-width="{LW2}"/>')
    # 直角の印（弦と縦の半径）
    for X in (P, Q):
        d = 7
        s.append(f'<path d="M {pt(0, X[1]-d)} L {pt(d, X[1]-d)} L {pt(d, X[1])}" '
                 f'fill="none" stroke="#111" stroke-width="0.8"/>')
    # ●（角a）2か所
    for ang, base in ((ar/2, 0), (math.radians(90) - ar/2, 1)):
        rr = 30 if base else 34
        s.append(f'<path d="M {pt(rr,0) if not base else pt(0,rr)} '
                 f'A {rr} {rr} 0 0 {0 if not base else 1} '
                 f'{pt(rr*math.cos(ar), rr*math.sin(ar)) if not base else pt(rr*math.cos(br), rr*math.sin(br))}" '
                 f'fill="none" stroke="#111" stroke-width="0.8"/>')
        s.append(f'<circle cx="{cx + rr*0.72*math.cos(ang):.2f}" '
                 f'cy="{cy - rr*0.72*math.sin(ang):.2f}" r="2.1" fill="#111"/>')
    s.append('</svg>')
    return ''.join(s)


# ══════════════════════════════════════════════════════════════════
# 円（半径6・直径4本＋弦4本・○の角a）
# ══════════════════════════════════════════════════════════════════
def circle_svg(a_deg: int, R=100, pad=16) -> str:
    cx = cy = R + pad
    W = H = (R + pad) * 2
    ar, br = math.radians(a_deg), math.radians(90 - a_deg)
    y1, x1 = R * math.sin(ar), R * math.cos(ar)        # 内側の弦
    y2, x2 = R * math.sin(br), R * math.cos(br)        # 外側の弦
    pt = lambda x, y: _p(x, y, cx, cy)

    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    # 塗り1：一番上の弦より上
    s.append(f'<path d="M {pt(-x2, y2)} L {pt(x2, y2)} A {R} {R} 0 0 0 {pt(-x2, y2)} Z" '
             f'fill="{SHADE}" stroke="none"/>')
    # 塗り2：横の直径のすぐ下の帯
    s.append(f'<path d="M {pt(-R,0)} L {pt(R,0)} A {R} {R} 0 0 1 {pt(x1,-y1)} '
             f'L {pt(-x1,-y1)} A {R} {R} 0 0 1 {pt(-R,0)} Z" '
             f'fill="{SHADE}" stroke="none"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#111" stroke-width="{LW}"/>')
    # 直径4本（縦・横・横からa°・横から90-a°）
    for ang in (math.pi/2, 0.0, ar, br):
        dx, dy = R*math.cos(ang), R*math.sin(ang)
        s.append(f'<line x1="{cx-dx:.2f}" y1="{cy+dy:.2f}" x2="{cx+dx:.2f}" y2="{cy-dy:.2f}" '
                 f'stroke="#111" stroke-width="{LW2}"/>')
    # 弦4本
    for yy, xx in ((y1, x1), (-y1, x1), (y2, x2), (-y2, x2)):
        s.append(f'<line x1="{cx-xx:.2f}" y1="{cy-yy:.2f}" x2="{cx+xx:.2f}" y2="{cy-yy:.2f}" '
                 f'stroke="#111" stroke-width="{LW2}"/>')
    # 直角の印（縦の直径と弦）
    for yy in (y1, -y1, y2, -y2):
        d = 7
        sg = 1 if yy > 0 else -1
        s.append(f'<path d="M {pt(0, yy-sg*d)} L {pt(d, yy-sg*d)} L {pt(d, yy)}" '
                 f'fill="none" stroke="#111" stroke-width="0.8"/>')
    # ○（角a）2か所：縦の直径と急な直径／横の直径とゆるやかな直径
    for lo, hi in ((br, math.pi/2), (0.0, ar)):
        rr = 26 if lo == 0.0 else 32
        s.append(f'<path d="M {pt(rr*math.cos(lo), rr*math.sin(lo))} '
                 f'A {rr} {rr} 0 0 0 {pt(rr*math.cos(hi), rr*math.sin(hi))}" '
                 f'fill="none" stroke="#111" stroke-width="0.8"/>')
        mid = (lo + hi) / 2
        s.append(f'<circle cx="{cx + rr*0.74*math.cos(mid):.2f}" '
                 f'cy="{cy - rr*0.74*math.sin(mid):.2f}" r="2.3" '
                 f'fill="#fff" stroke="#111" stroke-width="0.9"/>')
    s.append(f'<text x="{cx+7}" y="{cy+13}" font-size="{FS}">O</text>')
    s.append('</svg>')
    return ''.join(s)


# ══════════════════════════════════════════════════════════════════
# 正八角形（固定）
# ══════════════════════════════════════════════════════════════════
def octagon_svg(n=8, R=92, pad=22) -> str:
    cx = cy = R + pad
    W = H = (R + pad) * 2
    # A を左上に置き、反時計回りに A,B,C,…
    start = 90 + 180 / n
    names = 'ABCDEFGH'
    V = []
    for i in range(n):
        th = math.radians(start + 360 * i / n)
        V.append((R * math.cos(th), R * math.sin(th)))
    pt = lambda x, y: _p(x, y, cx, cy)
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append('<polygon points="' + ' '.join(pt(*v) for v in V) +
             f'" fill="none" stroke="#111" stroke-width="{LW}"/>')
    for i, v in enumerate(V):
        lx, ly = v[0] * 1.17, v[1] * 1.17
        s.append(f'<text x="{cx+lx:.1f}" y="{cy-ly+4:.1f}" font-size="{FS}" '
                 f'text-anchor="middle">{names[i]}</text>')
    # P は反時計回り（A→B）、Q は時計回り（A→H）。矢印のそばにラベルを置く
    def arc_mid(i, j, f):
        th = math.radians(start + 360 * (i + j) / 2 / n)
        return (R * f * math.cos(th), R * f * math.sin(th))
    pm = arc_mid(0, 1, 1.30)
    qm = arc_mid(0, -1, 1.30)
    s.append(f'<path d="M {pt(V[0][0]*1.16, V[0][1]*1.16)} '
             f'A {R*1.16} {R*1.16} 0 0 0 {pt(V[1][0]*1.16, V[1][1]*1.16)}" '
             f'fill="none" stroke="#111" stroke-width="0.9" marker-end="url(#ah)"/>')
    s.append(f'<path d="M {pt(V[0][0]*1.16, V[0][1]*1.16)} '
             f'A {R*1.16} {R*1.16} 0 0 1 {pt(V[-1][0]*1.16, V[-1][1]*1.16)}" '
             f'fill="none" stroke="#111" stroke-width="0.9" marker-end="url(#ah)"/>')
    s.append(f'<text x="{cx+pm[0]:.1f}" y="{cy-pm[1]+4:.1f}" font-size="{FS}" '
             f'text-anchor="middle">P</text>')
    s.append(f'<text x="{cx+qm[0]:.1f}" y="{cy-qm[1]+4:.1f}" font-size="{FS}" '
             f'text-anchor="middle">Q</text>')
    s.insert(1, '<defs><marker id="ah" viewBox="0 0 8 8" refX="6" refY="4" '
                'markerWidth="5" markerHeight="5" orient="auto">'
                '<path d="M0,0 L8,4 L0,8 z" fill="#111"/></marker></defs>')
    s.append('</svg>')
    return ''.join(s)


# ══════════════════════════════════════════════════════════════════
# 正三角形の分割（固定：1〜3番目を並べる）
# ══════════════════════════════════════════════════════════════════
def _tri_one(idx, L, R, small, big, S=86, pad=14):
    """1枚分。左の辺をL等分、右の辺をR等分し、頂点に近い点どうしを結ぶ。"""
    h = S * math.sqrt(3) / 2
    ox, oy = pad, pad + h + 12
    T = (S / 2, h)
    BL, BR = (0.0, 0.0), (S, 0.0)
    pt = lambda p: f'{ox + p[0]:.2f},{oy - p[1]:.2f}'
    lerp = lambda a, b, t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    PL = lerp(T, BL, 1 / L)
    PR = lerp(T, BR, 1 / R)
    s = [f'<svg viewBox="0 0 {S+pad*2} {h+pad*2+12}" xmlns="http://www.w3.org/2000/svg" class="tri-svg">']
    s.append(f'<text x="{ox+S/2:.1f}" y="10" font-size="10" text-anchor="middle">{idx}番目</text>')
    s.append(f'<polygon points="{pt(T)} {pt(BR)} {pt(BL)}" fill="none" '
             f'stroke="#111" stroke-width="{LW}"/>')
    s.append(f'<line x1="{ox+PL[0]:.2f}" y1="{oy-PL[1]:.2f}" x2="{ox+PR[0]:.2f}" '
             f'y2="{oy-PR[1]:.2f}" stroke="#111" stroke-width="{LW2}"/>')
    # 等分点は内側だけ打つ。1等分のときだけ、分ける点が向こうの頂点そのものになる
    for (side, k) in ((BL, L), (BR, R)):
        idxs = range(1, k) if k > 1 else [1]
        for i in idxs:
            q = lerp(T, side, i / k)
            s.append(f'<circle cx="{ox+q[0]:.2f}" cy="{oy-q[1]:.2f}" r="1.8" fill="#111"/>')
    s.append(f'<circle cx="{ox+T[0]:.2f}" cy="{oy-T[1]:.2f}" r="2.6" fill="#fff" '
             f'stroke="#111" stroke-width="1"/>')
    mid = ((T[0] + PL[0] + PR[0]) / 3, (T[1] + PL[1] + PR[1]) / 3)
    s.append(f'<text x="{ox+mid[0]:.1f}" y="{oy-mid[1]+4:.1f}" font-size="{FS}" '
             f'text-anchor="middle">{small}</text>')
    s.append(f'<text x="{ox+S/2:.1f}" y="{oy-h*0.22+4:.1f}" font-size="{FS}" '
             f'text-anchor="middle">{big}</text>')
    s.append('</svg>')
    return ''.join(s)


def tri_row_svg(rule: str) -> str:
    """rule='front' … 左n等分・右(n+1)等分 / rule='back' … 左(2n-1)・右(2n+1)"""
    small, big = ('ア', 'イ') if rule == 'front' else ('ウ', 'エ')
    out = []
    for n in (1, 2, 3):
        L, R = (n, n + 1) if rule == 'front' else (2 * n - 1, 2 * n + 1)
        out.append(_tri_one(n, L, R, small, big))
    return '<div class="tri-row">' + ''.join(out) + '</div>'


# ══════════════════════════════════════════════════════════════════
# 第2回の図（どちらも「図は正確とは限りません」なので形は固定）
# ══════════════════════════════════════════════════════════════════
def _cross(p1, p2, p3, p4):
    """線分 p1p2 と p3p4 の交点。"""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def quad_svg(W=250, H=200, pad=20):
    """四角形ABCDと対角線AC・BD、交点O（第2回・大問2）"""
    sx = lambda u: pad + u * (W - 2 * pad)
    sy = lambda v: H - pad - v * (H - 2 * pad)
    A, Bp, C, Dp = (0.26, 0.96), (0.02, 0.06), (0.95, 0.06), (0.80, 0.68)
    O = _cross(A, C, Bp, Dp)
    P = lambda p: f'{sx(p[0]):.1f},{sy(p[1]):.1f}'
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append(f'<polygon points="{P(A)} {P(Dp)} {P(C)} {P(Bp)}" fill="none" '
             f'stroke="#111" stroke-width="{LW}"/>')
    for a, b in ((A, C), (Bp, Dp)):
        s.append(f'<line x1="{sx(a[0]):.1f}" y1="{sy(a[1]):.1f}" '
                 f'x2="{sx(b[0]):.1f}" y2="{sy(b[1]):.1f}" stroke="#111" stroke-width="{LW2}"/>')
    for name, p, dx, dy in (('A', A, 0, -9), ('B', Bp, -9, 10), ('C', C, 9, 10),
                            ('D', Dp, 10, -2), ('O', O, 7, 10)):
        s.append(f'<text x="{sx(p[0])+dx:.1f}" y="{sy(p[1])+dy:.1f}" '
                 f'font-size="{FS}" text-anchor="middle">{name}</text>')
    s.append('</svg>')
    return ''.join(s)


def tri2_svg(W=300, H=235, pad=22):
    """三角形ABCと直角三角形DBCの重ね合わせ（第2回・大問4）"""
    sx = lambda u: pad + u * (W - 2 * pad)
    sy = lambda v: H - pad - v * (H - 2 * pad)
    Bp, C = (0.02, 0.05), (0.86, 0.05)
    Dp = (0.86, 0.97)
    A = (0.22, 0.46)
    Fp = (A[0], Bp[1])
    E = _cross(A, C, Bp, Dp)
    P = lambda p: f'{sx(p[0]):.1f},{sy(p[1]):.1f}'
    ln = lambda a, b, w=LW2, extra='': (
        f'<line x1="{sx(a[0]):.1f}" y1="{sy(a[1]):.1f}" x2="{sx(b[0]):.1f}" '
        f'y2="{sy(b[1]):.1f}" stroke="#111" stroke-width="{w}" {extra}/>')
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append(f'<polygon points="{P(A)} {P(Bp)} {P(C)}" fill="none" stroke="#111" '
             f'stroke-width="{LW}"/>')
    s.append(f'<polygon points="{P(Dp)} {P(Bp)} {P(C)}" fill="none" stroke="#111" '
             f'stroke-width="{LW}"/>')
    s.append(ln(A, Fp, 0.9, 'stroke-dasharray="3,2.5"'))
    # 直角の印（FとC）
    d = 8
    for base, sgn in ((Fp, 1), (C, -1)):
        x, y = sx(base[0]), sy(base[1])
        s.append(f'<path d="M {x+sgn*d:.1f},{y:.1f} L {x+sgn*d:.1f},{y-d:.1f} '
                 f'L {x:.1f},{y-d:.1f}" fill="none" stroke="#111" stroke-width="0.8"/>')
    for name, p, dx, dy in (('A', A, -10, -1), ('B', Bp, -8, 11), ('C', C, 10, 11),
                            ('D', Dp, 9, -2), ('E', E, 2, -6), ('F', Fp, 0, 12)):
        s.append(f'<text x="{sx(p[0])+dx:.1f}" y="{sy(p[1])+dy:.1f}" '
                 f'font-size="{FS}" text-anchor="middle">{name}</text>')
    s.append('</svg>')
    return ''.join(s)


# ══════════════════════════════════════════════════════════════════
# 第3回の図
# ══════════════════════════════════════════════════════════════════
def pond_svg(W=200, H=215, R=68):
    """円形の池と出発地点P、時計回りの矢印（第3回・大問2）"""
    cx, cy = W / 2, H - R - 16
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#111" '
             f'stroke-width="{LW}"/>')
    px, py = cx, cy - R
    s.append(f'<circle cx="{px}" cy="{py}" r="2.6" fill="#111"/>')
    s.append(f'<text x="{px-8}" y="{py-2}" font-size="{FS}" text-anchor="end">地点P</text>')
    # A・B・Cの印（Pの真上に縦に並べる）
    for i, nm in enumerate('ABC'):
        s.append(f'<text x="{px-14}" y="{py-40+i*13}" font-size="{FS}" '
                 f'text-anchor="middle">{nm}</text>')
    s.append(f'<line x1="{px-6}" y1="{py-52}" x2="{px-6}" y2="{py-4}" '
             f'stroke="#111" stroke-width="0.9"/>')
    # 時計回りの矢印
    s.append(f'<path d="M {px+10},{py-30} q 34,-6 44,22" fill="none" stroke="#111" '
             f'stroke-width="1.1"/>')
    s.append(f'<path d="M {px+52},{py-14} l 3,10 l -9,-4 z" fill="#111"/>')
    s.append('</svg>')
    return ''.join(s)


def rect_svg(W=250, H=180, pad=18):
    """長方形ABCDと四角形EBFD（第3回・大問3）"""
    x0, y0 = pad + 10, pad
    x1, y1 = W - pad - 14, H - pad - 12
    A, Dp, C, Bp = (x0, y0), (x1, y0), (x1, y1), (x0, y1)
    E = (x0 + (x1 - x0) * 0.80, y0)
    Fp = (x1, y0 + (y1 - y0) * 0.30)
    P = lambda p: f'{p[0]:.1f},{p[1]:.1f}'
    ln = lambda a, b, w=LW2: (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" '
                              f'y2="{b[1]:.1f}" stroke="#111" stroke-width="{w}"/>')
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append(f'<polygon points="{P(A)} {P(Dp)} {P(C)} {P(Bp)}" fill="none" '
             f'stroke="#111" stroke-width="{LW}"/>')
    for a, b in ((Bp, E), (Bp, Fp), (Bp, Dp)):
        s.append(ln(Bp, b, 0.95 if b is Dp else LW2))
    for name, p, dx, dy in (('A', A, -8, -3), ('D', Dp, 9, -3), ('C', C, 9, 12),
                            ('B', Bp, -8, 13), ('E', E, -2, -4), ('F', Fp, 10, 4)):
        s.append(f'<text x="{p[0]+dx:.1f}" y="{p[1]+dy:.1f}" font-size="{FS}" '
                 f'text-anchor="middle">{name}</text>')
    s.append('</svg>')
    return ''.join(s)


def roll_svg(W=210, H=190, side=96):
    """正方形の上にのった正三角形と、転がる向きの矢印（第3回・大問5）"""
    x0 = (W - side) / 2
    y1 = H - 16
    y0 = y1 - side
    h = side / 2 * math.sqrt(3) / 2 * 2 / 2 * 2      # 正三角形の高さ（1辺 side/2）
    t = side / 2
    h = t * math.sqrt(3) / 2
    A, C = (x0, y0), (x0 + t, y0)
    Bp = (x0 + t / 2, y0 - h)
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append(f'<rect x="{x0}" y="{y0}" width="{side}" height="{side}" fill="none" '
             f'stroke="#111" stroke-width="{LW}"/>')
    s.append(f'<polygon points="{A[0]:.1f},{A[1]:.1f} {Bp[0]:.1f},{Bp[1]:.1f} '
             f'{C[0]:.1f},{C[1]:.1f}" fill="none" stroke="#111" stroke-width="{LW}"/>')
    for name, p, dx, dy in (('A', A, -9, 4), ('B', Bp, -1, -5), ('C', C, 10, 4)):
        s.append(f'<text x="{p[0]+dx:.1f}" y="{p[1]+dy:.1f}" font-size="{FS}" '
                 f'text-anchor="middle">{name}</text>')
    ax = x0 + t + 6
    s.append(f'<path d="M {ax},{y0-h-6} q 26,-9 40,8" fill="none" stroke="#111" '
             f'stroke-width="1.1"/>')
    s.append(f'<path d="M {ax+40},{y0-h+2} l 1.5,-10 l -8,5 z" fill="#111"/>')
    s.append('</svg>')
    return ''.join(s)


# ══════════════════════════════════════════════════════════════════
# 夏期そっくりテストの図
# ══════════════════════════════════════════════════════════════════
def tri6_svg(L=8, W=520, pad=26):
    """直角三角形ABCを6つに分けた図（そっくり・大問3）。●はすべて同じ長さ。"""
    th = math.radians(15)
    cx = L / math.tan(th)
    sc = (W - pad * 2 - 26) / cx
    H = int(L * sc) + pad * 2 + 10
    X = lambda u: pad + 20 + u * sc
    Y = lambda u: H - pad - u * sc
    A, B, C = (0, L), (0, 0), (cx, 0)
    U1, V1 = (L / 2, L * math.sqrt(3) / 2), (L, 0)
    U2 = (L + L * math.sqrt(3) / 2, L / 2)
    V2 = (L + L * math.sqrt(3), 0)
    Wp = (L, L - L * math.tan(th))
    P = lambda p: f'{X(p[0]):.1f},{Y(p[1]):.1f}'
    ln = lambda a, b, w=LW2: (f'<line x1="{X(a[0]):.1f}" y1="{Y(a[1]):.1f}" '
                              f'x2="{X(b[0]):.1f}" y2="{Y(b[1]):.1f}" '
                              f'stroke="#111" stroke-width="{w}"/>')
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    s.append(f'<polygon points="{P(A)} {P(B)} {P(C)}" fill="none" stroke="#111" '
             f'stroke-width="{LW}"/>')
    for a, b in ((B, U1), (U1, V1), (V1, Wp), (V1, U2), (U2, V2)):
        s.append(ln(a, b))
    # 直角の印（BとV1）
    for base in (B, V1):
        x, y = X(base[0]), Y(base[1])
        s.append(f'<path d="M {x+8:.1f},{y:.1f} L {x+8:.1f},{y-8:.1f} '
                 f'L {x:.1f},{y-8:.1f}" fill="none" stroke="#111" stroke-width="0.8"/>')
    # ●（長さが等しい辺の印）
    for a, b in ((A, B), (B, U1), (U1, V1), (B, V1), (V1, U2), (U2, V2), (V2, C)):
        mx, my = (X(a[0]) + X(b[0])) / 2, (Y(a[1]) + Y(b[1])) / 2
        s.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="2.8" fill="#111"/>')
    # 記号
    lab = ((('ア'), (A, B, U1)), (('イ'), (B, U1, V1)), (('ウ'), (U1, Wp, V1)),
           (('エ'), (Wp, V1, U2)), (('オ'), (V1, U2, V2)), (('カ'), (U2, V2, C)))
    for name, tri in lab:
        gx = sum(X(p[0]) for p in tri) / 3
        gy = sum(Y(p[1]) for p in tri) / 3
        s.append(f'<text x="{gx:.1f}" y="{gy+4:.1f}" font-size="{FS}" '
                 f'text-anchor="middle">{name}</text>')
    for name, p, dx, dy in (('A', A, -4, -6), ('B', B, -6, 14), ('C', C, 10, 12)):
        s.append(f'<text x="{X(p[0])+dx:.1f}" y="{Y(p[1])+dy:.1f}" font-size="{FS}" '
                 f'text-anchor="middle">{name}</text>')
    # 8cm（ABの長さ）
    s.append(f'<text x="{X(0)-14:.1f}" y="{(Y(0)+Y(L))/2+4:.1f}" font-size="{FS}" '
             f'text-anchor="middle">{L}cm</text>')
    s.append('</svg>')
    return ''.join(s)


def circ_svg(Wmm=12, W=300, H=276, pad=16):
    """PQを直径とする円とD・E・F・G（そっくり・大問5 図2）。HI＝Wmm cm。"""
    h, i = 60.0, 85.0                      # OH, OI（図は正確でなくてよい）
    d, f = i, h                            # DH＝OI、FI＝OH
    R = math.hypot(h, d)
    sc = min(W - pad * 2 - 26, H - pad * 2) / (2 * R)
    cx, cy = W / 2, H / 2
    X = lambda u: cx + u * sc
    Y = lambda u: cy - u * sc
    Dp, E, Fp, G = (-h, d), (-h, -d), (i, f), (i, -f)
    Pp, Q = (-R, 0), (R, 0)
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    # 斜線部分（弓形2つ）
    for sgn, xv in ((-1, -h), (1, i)):
        yy = math.sqrt(max(R * R - xv * xv, 0))
        big = 0
        if sgn < 0:
            dd = (f'M {X(xv):.1f},{Y(yy):.1f} A {R*sc:.1f} {R*sc:.1f} 0 {big} 0 '
                  f'{X(xv):.1f},{Y(-yy):.1f} Z')
        else:
            dd = (f'M {X(xv):.1f},{Y(yy):.1f} A {R*sc:.1f} {R*sc:.1f} 0 {big} 1 '
                  f'{X(xv):.1f},{Y(-yy):.1f} Z')
        s.append(f'<path d="{dd}" fill="{SHADE}" stroke="none"/>')
    s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R*sc:.1f}" fill="none" '
             f'stroke="#111" stroke-width="{LW}"/>')
    ln = lambda a, b, w=LW2, extra='': (
        f'<line x1="{X(a[0]):.1f}" y1="{Y(a[1]):.1f}" x2="{X(b[0]):.1f}" '
        f'y2="{Y(b[1]):.1f}" stroke="#111" stroke-width="{w}" {extra}/>')
    s.append(ln(Pp, Q, LW))
    s.append(ln(Dp, E, LW))
    s.append(ln(Fp, G, LW))
    s.append(ln(Dp, G, 0.85, 'stroke-dasharray="4,3"'))
    s.append(ln(E, Fp, 0.85, 'stroke-dasharray="4,3"'))
    # 直角の印（2本の点線の交点）と直角の印（HとI）
    mx = (i - h) / 2
    px, py = X(mx), Y(0)
    t = 9.0 / math.sqrt(2)
    s.append(f'<path d="M {px-t:.1f},{py-t:.1f} L {px:.1f},{py-2*t:.1f} '
             f'L {px+t:.1f},{py-t:.1f} L {px:.1f},{py:.1f} Z" '
             f'fill="none" stroke="#111" stroke-width="0.8"/>')
    for xv, sgn in ((-h, 1), (i, -1)):
        x, y = X(xv), Y(0)
        s.append(f'<path d="M {x+sgn*9:.1f},{y:.1f} L {x+sgn*9:.1f},{y-9:.1f} '
                 f'L {x:.1f},{y-9:.1f}" fill="none" stroke="#111" stroke-width="0.8"/>')
    s.append(f'<circle cx="{X(0):.1f}" cy="{Y(0):.1f}" r="2.4" fill="#111"/>')
    for name, p, dx, dy in (('P', Pp, -10, 4), ('Q', Q, 10, 4), ('O', (0, 0), -4, 14),
                            ('H', (-h, 0), -9, -5), ('I', (i, 0), 9, -5),
                            ('D', Dp, -4, -6), ('E', E, -4, 15),
                            ('F', Fp, 7, -5), ('G', G, 7, 14)):
        s.append(f'<text x="{X(p[0])+dx:.1f}" y="{Y(p[1])+dy:.1f}" font-size="{FS}" '
                 f'text-anchor="middle">{name}</text>')
    # HI の寸法線
    yd = Y(0) + 30
    s.append(f'<line x1="{X(-h):.1f}" y1="{yd:.1f}" x2="{X(i):.1f}" y2="{yd:.1f}" '
             f'stroke="#111" stroke-width="0.8"/>')
    for xv, sgn in ((-h, 1), (i, -1)):
        s.append(f'<path d="M {X(xv):.1f},{yd:.1f} l {sgn*7},-3 l 0,6 z" fill="#111"/>')
    s.append(f'<rect x="{(X(-h)+X(i))/2-17:.1f}" y="{yd-8:.1f}" width="34" height="14" '
             f'fill="#fff"/>')
    s.append(f'<text x="{(X(-h)+X(i))/2:.1f}" y="{yd+4:.1f}" font-size="{FS}" '
             f'text-anchor="middle">{Wmm}cm</text>')
    s.append('</svg>')
    return ''.join(s)


def tri345_svg(p=3, q=4, W=210, H=140, pad=18):
    """合同な直角三角形2枚（そっくり・大問5 図1）"""
    sc = (W - pad * 2) / (p + q)
    sc = min(sc, (H - pad * 2) / max(p, q))
    x0 = pad + p * sc
    y0 = H - pad
    X = lambda u: x0 + u * sc
    Y = lambda u: y0 - u * sc
    A, B, C = (-p, q), (0, 0), (q, p)
    P1, Q1 = (-p, 0), (q, 0)
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    pts = lambda *ps: ' '.join(f'{X(a[0]):.1f},{Y(a[1]):.1f}' for a in ps)
    s.append(f'<polygon points="{pts(P1, A, B)}" fill="none" stroke="#111" '
             f'stroke-width="{LW}"/>')
    s.append(f'<polygon points="{pts(Q1, C, B)}" fill="none" stroke="#111" '
             f'stroke-width="{LW}"/>')
    s.append(f'<line x1="{X(A[0]):.1f}" y1="{Y(A[1]):.1f}" x2="{X(C[0]):.1f}" '
             f'y2="{Y(C[1]):.1f}" stroke="#111" stroke-width="0.85" '
             f'stroke-dasharray="4,3"/>')
    for base, sgn in ((P1, 1), (Q1, -1)):
        x, y = X(base[0]), Y(base[1])
        s.append(f'<path d="M {x+sgn*8:.1f},{y:.1f} L {x+sgn*8:.1f},{y-8:.1f} '
                 f'L {x:.1f},{y-8:.1f}" fill="none" stroke="#111" stroke-width="0.8"/>')
    for name, pt, dx, dy in (('A', A, -8, -3), ('B', B, 0, 14), ('C', C, 9, -3)):
        s.append(f'<text x="{X(pt[0])+dx:.1f}" y="{Y(pt[1])+dy:.1f}" font-size="{FS}" '
                 f'text-anchor="middle">{name}</text>')
    s.append('</svg>')
    return ''.join(s)


# ══════════════════════════════════════════════════════════════════
# 第4回 M2：平行四辺形ABCD（AF:FD＝m:n、G＝AC∩FB、H＝EC∩FB、EはAB上）
# ══════════════════════════════════════════════════════════════════
def _ix(p1, p2, p3, p4):
    """直線p1p2と直線p3p4の交点。"""
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def para_svg(m: int, n: int, W=250, H=118, sx=52, pad=20) -> str:
    """平行四辺形ABCD。AD上のFをAF:FD＝m:nにとり、AC・FB・ECを引く。"""
    A = (pad, pad)
    D = (pad + W, pad)
    B = (pad + sx, pad + H)
    C = (pad + sx + W, pad + H)
    F = (A[0] + (D[0] - A[0]) * m / (m + n), A[1])
    G = _ix(A, C, F, B)
    u = m / (m + n)                          # FBを F→B に進んだ割合（H の位置）
    H_ = (F[0] + u * (B[0] - F[0]), F[1] + u * (B[1] - F[1]))
    E = _ix(C, H_, A, B)
    Wp, Hp = W + sx + pad * 2, H + pad * 2 + 6

    def ln(p, q, w=LW2):
        return (f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" '
                f'stroke="#111" stroke-width="{w}"/>')

    def tx(p, t, dx, dy):
        return (f'<text x="{p[0]+dx:.2f}" y="{p[1]+dy:.2f}" font-size="{FS}" '
                f'text-anchor="middle" fill="#111">{t}</text>')

    o = [f'<svg viewBox="0 0 {Wp} {Hp}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    for p, q in ((A, D), (D, C), (C, B), (B, A)):
        o.append(ln(p, q, LW))
    o += [ln(A, C), ln(F, B), ln(E, C)]
    o.append(tx(A, 'A', -9, 2))
    o.append(tx(D, 'D', 9, 2))
    o.append(tx(F, 'F', 0, -5))
    o.append(tx(B, 'B', -4, 12))
    o.append(tx(C, 'C', 9, 4))
    o.append(tx(E, 'E', -10, 3))
    o.append(tx(G, 'G', -3, -5))
    o.append(tx(H_, 'H', -9, 2))
    o.append('</svg>')
    return ''.join(o)


# ══════════════════════════════════════════════════════════════════
# 第4回 M3：長方形PQRSを対角線PRとジグザグで3k+1個の三角形に分ける
# ══════════════════════════════════════════════════════════════════
KANA = list('アイウエオカキクケコサシスセソタチツテト')


def rect3_parts(k: int):
    """対角線上の点の位置a[]、辺QR上の点x[]、三角形（頂点名のタプル）の並びを返す。"""
    from fractions import Fraction as F
    t = F(1, 4 * k)
    a = [F(1, 2 * k)]
    x = []
    for _ in range(k - 1):
        x.append((x[-1] if x else F(0)) + 2 * t / (1 - a[-1]))
        a.append(a[-1] + 2 * t / (1 - x[-1]))
    tris = [('P', 'B0', 'V1')]
    for i in range(1, k):
        tris.append((f'B{i-1}', f'B{i}', f'V{i}'))
        tris.append((f'V{i}', f'B{i}', f'V{i+1}'))
    tris.append((f'B{k-1}', f'B{k}', f'V{k}'))
    tris.append((f'V{k}', f'B{k}', 'S'))
    for j in range(k - 1, 0, -1):
        tris.append((f'V{j}', f'V{j+1}', 'S'))
    tris.append(('P', 'V1', 'S'))
    return a, x, tris


def rect3_svg(k: int, W=330, H=150, pad=20) -> str:
    a, x, tris = rect3_parts(k)
    P, S = (pad, pad), (pad + W, pad)
    Q, R = (pad, pad + H), (pad + W, pad + H)
    pts = {'P': P, 'S': S, 'B0': Q, f'B{k}': R}
    for i, ai in enumerate(a, 1):
        pts[f'V{i}'] = (pad + W * float(ai), pad + H * float(ai))
    for i, xi in enumerate(x, 1):
        pts[f'B{i}'] = (pad + W * float(xi), pad + H)
    Wp, Hp = W + pad * 2, H + pad * 2

    def ln(p, q, w=LW2):
        return (f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" '
                f'stroke="#111" stroke-width="{w}"/>')

    o = [f'<svg viewBox="0 0 {Wp} {Hp}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    o.append(f'<rect x="{pad}" y="{pad}" width="{W}" height="{H}" fill="none" '
             f'stroke="#111" stroke-width="{LW}"/>')
    o.append(ln(P, R))
    for i in range(1, k + 1):
        o.append(ln(S, pts[f'V{i}']))
    o.append(ln(Q, pts['V1']))
    for i in range(1, k):
        o.append(ln(pts[f'V{i}'], pts[f'B{i}']))
        o.append(ln(pts[f'B{i}'], pts[f'V{i+1}']))
    for idx, tri in enumerate(tris):
        cx = sum(pts[v][0] for v in tri) / 3
        cy = sum(pts[v][1] for v in tri) / 3
        o.append(f'<text x="{cx:.2f}" y="{cy+4:.2f}" font-size="{FS}" '
                 f'text-anchor="middle" fill="#111">{KANA[idx]}</text>')
    for nm, p, dx, dy in (('P', P, -9, 0), ('S', S, 9, 0),
                          ('Q', Q, -9, 10), ('R', R, 9, 10)):
        o.append(f'<text x="{p[0]+dx:.2f}" y="{p[1]+dy:.2f}" font-size="{FS}" '
                 f'text-anchor="middle" fill="#111">{nm}</text>')
    o.append('</svg>')
    return ''.join(o)


# ══════════════════════════════════════════════════════════════════
# 第4回 M4：円周上を反対方向に進む2点（出発点は上）
# ══════════════════════════════════════════════════════════════════
def meet_svg(start='P', R=72, pad=30) -> str:
    cx, cy = R + pad, R + pad + 6
    W, H = (R + pad) * 2, (R + pad) * 2 + 6
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#111" '
             f'stroke-width="{LW}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy-R}" r="2.6" fill="#111"/>')
    o.append(f'<text x="{cx}" y="{cy-R-8}" font-size="{FS}" text-anchor="middle" '
             f'fill="#111">{start}</text>')
    # 上端から左右へ出る矢印（右＝時計回りのA、左＝反時計回りのB）
    for sgn, nm in ((1, 'A'), (-1, 'B')):
        x0, x1 = cx + sgn * 12, cx + sgn * 40
        y = cy - R - 2
        o.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#111" '
                 f'stroke-width="{LW2}"/>')
        o.append(f'<path d="M {x1} {y} L {x1-sgn*6} {y-3.5} L {x1-sgn*6} {y+3.5} Z" '
                 f'fill="#111"/>')
        o.append(f'<text x="{x1+sgn*9}" y="{y+4}" font-size="{FS}" '
                 f'text-anchor="middle" fill="#111">{nm}</text>')
    o.append('</svg>')
    return ''.join(o)


# ══════════════════════════════════════════════════════════════════
# 第4回 M5：円形に並べたカードの位置（上に1、時計回りにA、B、…）
# ══════════════════════════════════════════════════════════════════
def ring_svg(n: int, labeled: bool, R=66, r=13, pad=18) -> str:
    cx, cy = R + r + pad, R + r + pad
    W = H = (R + r + pad) * 2
    o = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" class="fig-svg">']
    for i in range(n):
        th = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + R * math.cos(th), cy + R * math.sin(th)
        o.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="#fff" '
                 f'stroke="#111" stroke-width="{LW2}"/>')
        t = '1' if i == 0 else (chr(ord('A') + i - 1) if labeled else '')
        if t:
            o.append(f'<text x="{x:.2f}" y="{y+4:.2f}" font-size="{FS}" '
                     f'text-anchor="middle" fill="#111">{t}</text>')
    o.append('</svg>')
    return ''.join(o)


# ══════════════════════════════════════════════════════════════════
# 第5回の図
# ══════════════════════════════════════════════════════════════════
def dai_svg(W: int, H: int, e1: int, e2: int, u=11.0, pad=16) -> str:
    """台紙（図1）と、2枚の長方形をはりつけた例（図2）を1枚に並べる。

    図2は左上に 横e1×たてe2、右下に 横e2×たてe1 を置いた「直角向き」の例。
    重なり（ぬりつぶし）は (e1+e2-W)×(e1+e2-H)。
    """
    bw, bh = W * u, H * u                       # 台紙の大きさ(px)
    lab = 22                                    # 寸法の文字ぶんの余白
    gap = 34
    x1 = pad + lab                              # 図1の左上
    y1 = pad + lab
    x2 = x1 + bw + gap + lab + 10               # 図2の左上
    y2 = y1
    Wpx = x2 + bw + lab + pad
    Hpx = y1 + bh + lab + pad
    o = [f'<svg viewBox="0 0 {Wpx:.0f} {Hpx:.0f}" xmlns="http://www.w3.org/2000/svg" '
         f'class="fig-svg">']
    box = (lambda x, y, w, h, lw: f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                                  f'height="{h:.1f}" fill="none" stroke="#111" '
                                  f'stroke-width="{lw}"/>')
    txt = (lambda x, y, t, an='middle': f'<text x="{x:.1f}" y="{y:.1f}" font-size="{FS}" '
                                        f'text-anchor="{an}">{t}</text>')

    # ── 図1 ───────────────────────────────────────────────
    o.append(box(x1, y1, bw, bh, LW))
    o.append(txt(x1 + bw / 2, y1 - 6, f'{W}cm'))
    o.append(txt(x1 - 6, y1 + bh / 2 + 4, f'{H}cm', 'end'))
    o.append(txt(x1 + bw / 2, y1 + bh + lab - 4, '図1'))

    # ── 図2 ───────────────────────────────────────────────
    ow, oh = (e1 + e2 - W) * u, (e1 + e2 - H) * u      # 重なり
    ox = x2 + (W - e2) * u                              # 右下の長方形の左端
    oy = y2 + (H - e1) * u
    o.append(f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{ow:.1f}" height="{oh:.1f}" '
             f'fill="{SHADE}" stroke="none"/>')
    o.append(box(x2, y2, bw, bh, LW))                     # 台紙
    o.append(box(x2, y2, e1 * u, e2 * u, LW2))            # 左上（横e1×たてe2）
    o.append(box(x2 + (W - e2) * u, y2 + (H - e1) * u,
                 e2 * u, e1 * u, LW2))                    # 右下（横e2×たてe1）
    for name, px, py, dx, dy in (('A', x2, y2, -8, -4), ('D', x2 + bw, y2, 9, -4),
                                 ('B', x2, y2 + bh, -8, 13),
                                 ('C', x2 + bw, y2 + bh, 9, 13)):
        o.append(txt(px + dx, py + dy, name))
    o.append(txt(x2 + e1 * u / 2, y2 - 6, f'{e1}cm'))             # 上辺
    o.append(txt(x2 - 6, y2 + e2 * u / 2 + 4, f'{e2}cm', 'end'))  # 左辺
    o.append(txt(x2 + bw + 6, y2 + (H - e1 / 2) * u + 4, f'{e1}cm', 'start'))  # 右辺
    o.append(txt(x2 + (W - e2 / 2) * u, y2 + bh + 13, f'{e2}cm'))  # 下辺
    o.append(txt(x2 + bw / 2, y2 + bh + lab - 4, '図2'))
    o.append('</svg>')
    return ''.join(o)


def sieve_svg(N: int, cols=6, show=8, cw=54.0, ch=17.0, pad=4) -> str:
    """1からNまでを横cols個ずつ並べた表（最初のshow行＋…＋最終行）。"""
    rows = N // cols
    lw = cw + 14                                   # 行ラベルの列は少し広い
    nrow = 1 + show + 1 + 1                        # 見出し・本体・点々・最終行
    Wpx, Hpx = lw + cw * cols + pad * 2, ch * nrow + pad * 2
    o = [f'<svg viewBox="0 0 {Wpx:.0f} {Hpx:.0f}" xmlns="http://www.w3.org/2000/svg" '
         f'class="fig-svg">']
    cx = lambda j: pad + lw + cw * j
    cy = lambda i: pad + ch * i
    txt = (lambda x, y, t: f'<text x="{x:.1f}" y="{y:.1f}" font-size="{FS}" '
                           f'text-anchor="middle">{t}</text>')
    # 枠
    o.append(f'<rect x="{pad}" y="{pad}" width="{lw + cw * cols:.1f}" '
             f'height="{ch * nrow:.1f}" fill="none" stroke="#111" stroke-width="{LW}"/>')
    for i in range(1, nrow):
        o.append(f'<line x1="{pad}" y1="{cy(i):.1f}" x2="{pad + lw + cw * cols:.1f}" '
                 f'y2="{cy(i):.1f}" stroke="#111" stroke-width="{LW2}"/>')
    for j in range(cols + 1):
        x = pad + lw if j == 0 else cx(j)
        o.append(f'<line x1="{x:.1f}" y1="{pad}" x2="{x:.1f}" '
                 f'y2="{pad + ch * nrow:.1f}" stroke="#111" stroke-width="{LW2}"/>')
    # 見出し
    for j in range(cols):
        o.append(txt(cx(j) + cw / 2, cy(0) + ch - 4, f'{chr(ord("A") + j)} 列'))
    # 本体
    for i in range(show):
        o.append(txt(pad + lw / 2, cy(i + 1) + ch - 4, f'{i + 1} 行目'))
        for j in range(cols):
            o.append(txt(cx(j) + cw / 2, cy(i + 1) + ch - 4, str(i * cols + j + 1)))
    o.append(txt(pad + lw / 2, cy(show + 1) + ch - 5, '・'))
    for j in range(cols):
        o.append(txt(cx(j) + cw / 2, cy(show + 1) + ch - 5, '・'))
    o.append(txt(pad + lw / 2, cy(show + 2) + ch - 4, f'{rows} 行目'))
    for j in range(cols):
        o.append(txt(cx(j) + cw / 2, cy(show + 2) + ch - 4, str(N - cols + j + 1)))
    o.append('</svg>')
    return ''.join(o)
