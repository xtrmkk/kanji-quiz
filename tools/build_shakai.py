# -*- coding: utf-8 -*-
"""社会テスト（歴史）の完成版HTMLを生成する。

  python3 tools/build_shakai.py

tools/shakai_template.html（骨組み）に問題データと tools/figs/*.jpg を
埋め込んで templates/shakai.html を出力する。
templates/shakai.html が実際に使うファイルで、単体で開けるスタンドアロン版。
このディレクトリのファイルは素材なので直接ブラウザで開いても動かない。

問題データ:
  tools/data_kodai.py   第8節  古代（旧石器〜平安時代）  310-369
  tools/data_chusei.py  第9節  中世（鎌倉〜室町時代）    370-419
  tools/data_kinsei.py  第10節 近世（安土桃山〜江戸時代）420-486
  tools/data_kindai.py  第11節 近代（明治〜昭和・戦前）  487-546
  tools/data_gendai.py  第12節 現代（昭和・戦後〜現代）  547-566
  tools/data_shiryo.py  第13節 歴史重要史料のまとめ      567-580
  tools/data_koumin.py  第14〜17節 公民編                581-660
"""
import base64, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG  = os.path.join(HERE, 'figs')
sys.path.insert(0, HERE)

import data_kodai, data_chusei, data_kinsei, data_kindai, data_gendai, data_shiryo, data_koumin

Q = (data_kodai.Q + data_chusei.Q + data_kinsei.Q
     + data_kindai.Q + data_gendai.Q + data_shiryo.Q + data_koumin.Q)

# ── 出題範囲（画面上のボタン） ─────────────────────────────────────────
RANGES = [
  {'key':'kodai',  'label':'古代', 'name':'古代すべて', 'range':[310,369], 'subs':[
      {'key':'k1','name':'旧石器〜古墳',  'range':[310,319]},
      {'key':'k2','name':'飛鳥・奈良',    'range':[320,346]},
      {'key':'k3','name':'平安',          'range':[347,369]},
  ]},
  {'key':'chusei', 'label':'中世', 'name':'中世すべて', 'range':[370,419], 'subs':[
      {'key':'c1','name':'鎌倉',          'range':[370,388]},
      {'key':'c2','name':'室町・戦国',    'range':[389,419]},
  ]},
  {'key':'kinsei', 'label':'近世', 'name':'近世すべて', 'range':[420,486], 'subs':[
      {'key':'s1','name':'安土桃山',      'range':[420,433]},
      {'key':'s2','name':'江戸前期',      'range':[434,457]},
      {'key':'s3','name':'江戸後期・幕末','range':[458,486]},
  ]},
  {'key':'kindai', 'label':'近代', 'name':'近代すべて', 'range':[487,546], 'subs':[
      {'key':'m1','name':'明治前期',      'range':[487,512]},
      {'key':'m2','name':'明治後期',      'range':[513,526]},
      {'key':'m3','name':'大正',          'range':[527,536]},
      {'key':'m4','name':'昭和・戦前',    'range':[537,546]},
  ]},
  {'key':'gendai', 'label':'現代', 'name':'現代すべて', 'range':[547,566], 'subs':[
      {'key':'g1','name':'戦後改革・占領','range':[547,556]},
      {'key':'g2','name':'高度成長〜現代','range':[557,566]},
  ]},
  {'key':'shiryo', 'label':'史料', 'name':'重要史料すべて', 'range':[567,580], 'subs':[
      {'key':'r1','name':'古代〜中世',    'range':[567,572]},
      {'key':'r2','name':'近世',          'range':[573,575]},
      {'key':'r3','name':'近代〜現代',    'range':[576,580]},
  ]},
  {'key':'koumin', 'label':'公民', 'name':'公民すべて', 'range':[581,660], 'subs':[
      {'key':'p1','name':'日本国憲法',        'range':[581,600]},
      {'key':'p2','name':'三権分立',          'range':[601,625]},
      {'key':'p3','name':'公民その他・現代日本','range':[626,645]},
      {'key':'p4','name':'国際連合・国際社会', 'range':[646,660]},
  ]},
]

# ── 図（切り出し画像と表示最大高さmm） ────────────────────────────────
FIGS = {
  # 古代
  'q310':20,'q311':22,'q313':20,'q314':24,'q318':20,'q328':34,'q331':20,
  'q338':20,'q344':22,'q354':30,'q362':22,'q367':20,'q369':34,
  # 中世
  'q371':44,'q372':17,'q378':26,'q380':24,'q387':26,'q391':22,'q393':24,
  'q404':22,'q405':28,'q408':30,
  # 近世
  'q420':24,'q421':24,'q424':24,'q430':28,'q433':22,'q434':22,'q445':26,
  'q447':28,'q452':28,'q456':22,'q465':26,'q476':22,'q477':22,
  # 近代
  'q488':30,'q504':24,'q505':24,'q508':22,'q509':24,'q515':38,'q524':24,'q530':20,
  # 公民
  'q601_sanken':30,'q616_gyosei':52,'q643_heritage':52,
}


def b64(name):
    with open(os.path.join(FIG, f'{name}.jpg'), 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()


def check():
    """データの整合性を確認する。"""
    nums = [q['n'] for q in Q]
    # 史料は1つの番号に複数の史料があるため n+sub で一意になる
    keys = [(q['n'], q.get('sub', '')) for q in Q]
    dup = [k for k in keys if keys.count(k) > 1]
    assert not dup, f'問題番号が重複している: {sorted(set(dup))}'

    # 範囲がすべての問題を覆っているか
    covered = set()
    for era in RANGES:
        lo, hi = era['range']
        covered |= {n for n in nums if lo <= n <= hi}
        sub = set()
        for s in era['subs']:
            a, b = s['range']
            sub |= {n for n in nums if a <= n <= b}
        era_nums = {n for n in nums if lo <= n <= hi}
        assert sub == era_nums, f"{era['label']}: 小範囲の合計が時代全体と一致しない {era_nums - sub}"
    assert covered == set(nums), f'範囲から漏れた問題: {set(nums) - covered}'

    # 図の参照先が実在するか
    used = set()
    for q in Q:
        for k in ('fig', 'figalt'):
            if q.get(k):
                used.add(q[k])
    missing = {f for f in used if not os.path.exists(os.path.join(FIG, f'{f}.jpg'))}
    assert not missing, f'画像ファイルがない: {missing}'
    unused = set(FIGS) - used
    assert not unused, f'FIGSに登録済みだが未使用: {unused}'
    assert not (used - set(FIGS)), f'FIGSに高さ未登録: {used - set(FIGS)}'

    # 参照関係の妥当性
    for q in Q:
        if q.get('dep'):
            assert q['dep'] in nums, f"{q['n']}: 参照先 {q['dep']} が存在しない"
            assert q.get('talt') or q.get('figalt'), f"{q['n']}: 代替文(talt)も代替図(figalt)もない"

    # 解答数とラベル数の一致
    for q in Q:
        if q.get('lab'):
            assert len(q['lab']) == len(q['a']), f"{q['n']}: ラベル数と解答数が違う"

    print(f'検証OK: {len(Q)}問 / 図{len(used)}点 / 番号 {min(nums)}-{max(nums)}')


def build():
    check()
    figdata = {k: {'src': b64(k), 'mh': v} for k, v in FIGS.items()}

    tpl = open(os.path.join(HERE, 'shakai_template.html'), encoding='utf-8').read()
    assert '/*__QDATA__*/' in tpl, 'テンプレートにプレースホルダが見つからない'

    data = ('const Q='   + json.dumps(Q, ensure_ascii=False) + ';\n'
            'const FIGS=' + json.dumps(figdata, ensure_ascii=False) + ';\n'
            'const RANGES=' + json.dumps(RANGES, ensure_ascii=False) + ';')
    out = tpl.replace('/*__QDATA__*/', data)

    dest = os.path.join(ROOT, 'templates', 'shakai.html')
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'生成: {dest}  ({len(out)//1024} KB)')


if __name__ == '__main__':
    build()
