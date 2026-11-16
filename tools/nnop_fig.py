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
