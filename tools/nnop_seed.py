# -*- coding: utf-8 -*-
"""用紙に刷ってある「番号」から、そのテストをそのまま復元する。

ブラウザ側（tools/nnop_template.html）とまったく同じ手順を踏んでいる。
番号は「乱数のたね20bit ＋ 出題条件30bit」の計50bitを32進10文字にしたもの。

  python3 tools/nnop_seed.py 7K3M2-P5QX1            … 大問と正解を出す
  python3 tools/nnop_seed.py 7K3M2-P5QX1 --full     … 問題文も出す

**ブラウザ側を直したら、必ずここも合わせること。**
合っているかは、ブラウザのコンソールで同じ番号を入れて
大問の並びと正解が一致するかを見れば確かめられる。
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nnop_data as D          # noqa: E402
import nnop2_data as D2        # noqa: E402
import nnop3_data as D3        # noqa: E402
import nnop4_data as D4        # noqa: E402
import nnop5_data as D5        # noqa: E402
import nnop6_data as D6        # noqa: E402
import nnop7_data as D7        # noqa: E402

GROUPS = (D.GROUPS + D2.GROUPS2 + D3.GROUPS3 + D4.GROUPS4 + D5.GROUPS5 +
          D6.GROUPS6 + D7.GROUPS7)
VARIANTS = {**D.VARIANTS, **D2.VARIANTS2, **D3.VARIANTS3,
            **D4.VARIANTS4, **D5.VARIANTS5, **D6.VARIANTS6,
            **D7.VARIANTS7}
ROUND_NAME = {1: '第1回', 2: '第2回', 3: '第3回', 'N': '夏期そっくり', 4: '第4回',
              5: '第5回', 'Y1': '予想①'}
ROUND_ORDER = [1, 2, 3, 'N', 4, 5, 'Y1']
FIELDS = D.FIELDS

C32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ'
M32 = 0xFFFFFFFF


def mulberry32(seed):
    """JS:
         a = (a + 0x6D2B79F5) | 0;
         let t = Math.imul(a ^ (a >>> 15), 1 | a);
         t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
         return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    """
    a = seed & M32

    def rnd():
        nonlocal a
        a = (a + 0x6D2B79F5) & M32
        t = ((a ^ (a >> 15)) * (1 | a)) & M32
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & M32)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296
    return rnd


def read_code(txt):
    """番号 → (seed, bits)。まぎらわしい文字は読みかえる。"""
    t = re.sub(r'[^0-9A-Z]', '', str(txt).upper())
    t = t.replace('I', '1').replace('L', '1').replace('O', '0').replace('U', 'V')
    if len(t) != 10:
        raise ValueError(f'番号は32進10文字（{t!r} は {len(t)} 文字）')
    v = 0
    for c in t:
        k = C32.find(c)
        if k < 0:
            raise ValueError(f'使えない文字: {c}')
        v = v * 32 + k
    return v >> 30, v & ((1 << 30) - 1)


def make_code(seed, bits):
    v = (seed << 30) | bits
    out = ''
    for _ in range(10):
        out = C32[v % 32] + out
        v //= 32
    return out[:5] + '-' + out[5:]


def round_bit(i):
    """回のビット位置。6つ目までは bit24〜29、7つ目・8つ目は bit13・bit12。

    bit12/13 はもともと「問題数」の上位2ビットだったところ。問題数を1〜15に
    しぼったので空いた（紙に入る数は多くても10問ほど）。こうすると、
    **古い番号（問題数15以下・回は6つまで）はそのまま同じテストに戻る**。
    9つ目の回を足すときは、番号を32進11文字にするなどの作りかえが要る。
    """
    return 24 + i if i < 6 else 19 - i          # i=6→13, i=7→12


def unpack(bits):
    return {
        'lo': (bits & 15) * 10,
        'hi': ((bits >> 4) & 15) * 10,
        'cnt': (bits >> 8) & 15,
        'shuffle': bool((bits >> 14) & 1),
        'fields': {k for i, (k, _) in enumerate(FIELDS) if (bits >> 15) & (1 << i)},
        'rounds': {r for i, r in enumerate(ROUND_ORDER)
                   if (bits >> round_bit(i)) & 1},
    }


def cut_subs(g, lo, hi):
    last = -1
    for i, s in enumerate(g['subs']):
        if lo <= s['rate'] <= hi:
            last = i
    return None if last < 0 else g['subs'][:last + 1]


def build(code):
    """番号 → [(大問, 出す小問, 使ったパラメータ組, その番号)]"""
    seed, bits = read_code(code)
    st = unpack(bits)
    rnd = mulberry32((seed ^ 0x9E3779B9) & M32)

    elig = []
    for g in GROUPS:
        if g['field'] not in st['fields'] or g['round'] not in st['rounds']:
            continue
        subs = cut_subs(g, st['lo'], st['hi'])
        if subs:
            elig.append((g, subs))
    if not elig:
        return st, []

    chosen = list(elig)
    for i in range(len(chosen) - 1, 0, -1):          # JSと同じフィッシャー・イェーツ
        j = int(rnd() * (i + 1))
        chosen[i], chosen[j] = chosen[j], chosen[i]
    cnt = min(len(elig), max(1, st['cnt']))
    chosen = chosen[:cnt]
    if not st['shuffle']:
        chosen.sort(key=lambda x: GROUPS.index(x[0]))

    out = []
    for g, subs in chosen:
        vs = VARIANTS[g['key']]()
        idx = int(rnd() * len(vs))
        out.append((g, subs, vs[idx], idx))
    return st, out


def fill(tpl, p):
    return re.sub(r'\{(\w+)\}', lambda m: str(p.get(m.group(1), m.group(0))), str(tpl))


def plain(s):
    # 分数は a/b の形に戻す（タグを落とすだけだと 1/1260 が「11260」になる）
    # 帯分数は「整数＋分数のspan」なので、前の整数ごと拾う
    s = re.sub(r'(\d*)<span class="fr"><span class="fn">(.*?)</span>'
               r'<span class="fd">(.*?)</span></span>',
               lambda m: (m.group(1) + 'と' if m.group(1) else '')
                         + f'{m.group(2)}/{m.group(3)}', s)
    s = re.sub(r'<sup>(.*?)</sup>', r'^\1', s)
    return re.sub(r'<[^>]+>', '', s)


def main(argv=None):
    ap = argparse.ArgumentParser(description='番号からテストを復元する')
    ap.add_argument('code', help='用紙の右上の番号（例 7K3M2-P5QX1）')
    ap.add_argument('--full', action='store_true', help='問題文とヒントも出す')
    a = ap.parse_args(argv)

    st, picked = build(a.code)
    print(f'番号 {a.code.upper()}')
    print(f'条件: 正答率 {st["lo"]}〜{st["hi"]}% ／ 大問 {st["cnt"]}問 ／ '
          f'{"ランダム順" if st["shuffle"] else "番号順"}')
    print(f'  回: {"・".join(ROUND_NAME.get(r, str(r)) for r in ROUND_ORDER if r in st["rounds"])}')
    print(f'  分野: {"・".join(n for k, n in FIELDS if k in st["fields"])}')
    if not picked:
        print('※ 条件に合う大問がありません')
        return 1
    total = 0
    print()
    for i, (g, subs, v, idx) in enumerate(picked, 1):
        print(f'【{i}】{ROUND_NAME.get(g["round"], g["round"])}・{g["title"]}'
              f'　[{g["key"]} / 候補{idx}]')
        if a.full and g['intro']:
            print('   ' + plain(fill(g['intro'], v['p'])))
        used = 0
        for s in g['subs']:
            n = len(s['ans'])
            if s not in subs:
                used += n
                continue
            ans = ' / '.join(x for x in v['a'][used:used + n] if x) or '（空欄）'
            used += n
            total += s['score']
            print(f'   {s["label"] or "—":4} {s["score"]}点 正答率{s["rate"]:3}%  '
                  f'答 {plain(ans)}')
            if a.full:
                print('        問: ' + plain(fill(s['q'], v['p'])))
                print('        ヒ: ' + plain(fill(s['how'], v['p'])))
        print()
    print(f'満点 {total}点')
    return 0


if __name__ == '__main__':
    sys.exit(main())
