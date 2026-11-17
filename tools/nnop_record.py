# -*- coding: utf-8 -*-
"""採点の記録（採点/記録.json）をまとめて見る。

  python3 tools/nnop_record.py              … 全体のまとめ
  python3 tools/nnop_record.py op3-2-1      … その設問の履歴だけ
  python3 tools/nnop_record.py --repeat     … 2回以上間違えた設問だけ

**答案を採点するときは、必ず先にこれを走らせて「前も間違えていないか」を見ること。**
記録ファイルは .gitignore 済み（息子さんの成績なので公開リポジトリに上げない）。
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PATH = os.path.join(ROOT, '採点', '記録.json')


def load():
    if not os.path.exists(PATH):
        sys.exit(f'記録がまだ無い: {PATH}')
    with open(PATH, encoding='utf-8') as f:
        return json.load(f)


def rows(data):
    for t in data['回']:
        for r in t['結果']:
            yield t, r


def main(argv=None):
    ap = argparse.ArgumentParser(description='採点の記録をまとめる')
    ap.add_argument('sub', nargs='?', help='設問id（例 op3-2-1）')
    ap.add_argument('--repeat', action='store_true', help='2回以上間違えた設問だけ')
    a = ap.parse_args(argv)
    data = load()

    if a.sub:
        print(f'=== {a.sub} の履歴 ===')
        hit = False
        for t, r in rows(data):
            if r['id'] != a.sub:
                continue
            hit = True
            print(f"  {t['日付']}  {r['正誤']}  答 {r['答']} ／ 正解 {r['正解']}"
                  f"{'　' + r['メモ'] if r.get('メモ') else ''}")
        if not hit:
            print('  まだ出ていない')
        return 0

    print(f'=== これまでのテスト（{len(data["回"])}回）===')
    for t in data['回']:
        pct = round(t['得点'] / t['満点'] * 100, 1)
        code = t.get('番号') or '（番号なし）'
        print(f"  {t['日付']}  {t['得点']:3}/{t['満点']:3}点 ({pct:5}%)  番号 {code}")

    st = collections.OrderedDict()
    for t, r in rows(data):
        d = st.setdefault(r['id'], {'出題': 0, '誤': 0, '名': f"{r['大問']}{r['小問']}",
                                    '率': r['全体正答率'], '日': []})
        d['出題'] += 1
        if r['正誤'] != '○':
            d['誤'] += 1
            d['日'].append(t['日付'])

    bad = [(k, v) for k, v in st.items() if v['誤'] >= (2 if a.repeat else 1)]
    bad.sort(key=lambda x: (-x[1]['誤'], -x[1]['率']))
    print(f'\n=== 間違えた設問{"（2回以上）" if a.repeat else ""} ===')
    if not bad:
        print('  なし')
    for k, v in bad:
        mark = '★くり返し' if v['誤'] >= 2 else ''
        print(f"  {k:10} {v['名']:22} {v['誤']}/{v['出題']}回ミス "
              f"（全体正答率{v['率']}%）{mark}")
        if v['誤'] >= 2:
            print(f"      間違えた日: {'、'.join(v['日'])}")

    tot = sum(v['出題'] for v in st.values())
    ng = sum(v['誤'] for v in st.values())
    print(f'\n小問 {tot}問中 {ng}問ミス')
    return 0


if __name__ == '__main__':
    sys.exit(main())
