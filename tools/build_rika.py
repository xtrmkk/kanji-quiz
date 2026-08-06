# -*- coding: utf-8 -*-
"""理科テストの完成版HTMLを生成する。

  python3 tools/build_rika.py

tools/rika_template.html（骨組み）に問題データと tools/figs_rika/*.jpg を
埋め込んで quiz_rika.html を出力する。
出力ファイルが実際に使うもので、単体で開けるスタンドアロン版。
このディレクトリのファイルは素材なので直接ブラウザで開いても動かない。

素材:
  tools/data_rika.json    問題720問（旧 gen_quiz.py の Q を抽出したもの）
  tools/figs_rika/*.jpg   図286点（旧 quiz_final.html の base64 を抽出・軽量化）
  tools/rika_wide.json    幅広で表示する図のキー
  tools/rika_narrow.json  小さく表示する図のキー
  tools/rika_evap.txt     蒸発とふっとうの比較表（問題中に埋め込む表）
"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG  = os.path.join(HERE, 'figs_rika')

Q      = json.load(open(os.path.join(HERE, 'data_rika.json'), encoding='utf-8'))
WIDE   = set(json.load(open(os.path.join(HERE, 'rika_wide.json'), encoding='utf-8')))
NARROW = set(json.load(open(os.path.join(HERE, 'rika_narrow.json'), encoding='utf-8')))

# ── 節の定義（見出し・色） ────────────────────────────────────────────
SEC = {
  "s1":  ("第1節","水の状態変化・あたたまり方","#E1F5EE","#0F6E56"),
  "s2":  ("第2節","酸素・二酸化炭素・燃え方","#FAECE7","#993C1D"),
  "s3":  ("第3節","溶解度・水溶液","#E3F2FD","#1565C0"),
  "s4":  ("第4節","天体","#F3E5F5","#7B1FA2"),
  "s5":  ("第5節","地層・岩石","#E8F5E9","#2E7D32"),
  "s6":  ("第6節","気象","#FFF8E1","#F57F17"),
  "s7":  ("第7節","力学","#FBE9E7","#BF360C"),
  "s8":  ("第8節","電磁気","#E8EAF6","#283593"),
  "s9":  ("第9節","光・音","#E0F2F1","#004D40"),
  "s10": ("第10節","人体","#FCE4EC","#880E4F"),
  "s11": ("第11節","動物","#E8F5E9","#1B5E20"),
  "s12": ("第12節","植物","#F9FBE7","#558B2F"),
  "s13": ("第13節","実験器具","#FFFDE7","#E65100"),
  "s14": ("第14節","環境問題","#E0F7FA","#006064"),
  "s15": ("発展化学","化学分野のプラス知識","#EDE7F6","#4527A0"),
  "s16": ("発展地学","地学分野のプラス知識","#FFF3E0","#BF360C"),
  "s17": ("発展物理","物理分野のプラス知識","#E8EAF6","#1A237E"),
  "s18": ("発展生物","生物分野のプラス知識","#F1F8E9","#33691E"),
}

# ── 出題範囲のまとまり（画面上のボタン） ──────────────────────────────
GROUPS = [
  {'key':'chem', 'label':'化学',  'secs':['s1','s2','s3','s15']},
  {'key':'earth','label':'地学',  'secs':['s4','s5','s6','s16']},
  {'key':'phys', 'label':'物理',  'secs':['s7','s8','s9','s17']},
  {'key':'bio',  'label':'生物',  'secs':['s10','s11','s12','s18']},
  {'key':'misc', 'label':'その他','secs':['s13','s14']},
]

# 図の表示最大高さ(mm)。幅広指定は本文の下に全幅、それ以外は右に回り込ませる。
MH_WIDE, MH_DEFAULT, MH_NARROW = 44, 32, 24


def fig_meta(key):
    path = os.path.join(FIG, f'{key}.jpg')
    with open(path, 'rb') as f:
        src = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()
    wide = key in WIDE
    mh = MH_WIDE if wide else (MH_NARROW if key in NARROW else MH_DEFAULT)
    return {'src': src, 'mh': mh, 'wide': wide}


def check():
    ids = [q['id'] for q in Q]
    assert len(ids) == len(set(ids)), '問題IDが重複している'

    # 節がすべて定義済みか、範囲ボタンで網羅されているか
    secs = {q['s'] for q in Q}
    assert secs <= set(SEC), f'未定義の節: {secs - set(SEC)}'
    covered = {s for g in GROUPS for s in g['secs']}
    assert secs <= covered, f'範囲ボタンから漏れた節: {secs - covered}'
    assert covered <= set(SEC), f'存在しない節を参照: {covered - set(SEC)}'

    # 図の実在確認
    used = {q[k] for q in Q for k in ('fig', 'ref_fig') if q.get(k)}
    missing = {k for k in used if not os.path.exists(os.path.join(FIG, f'{k}.jpg'))}
    assert not missing, f'画像ファイルがない: {sorted(missing)[:5]}'

    print(f'検証OK: {len(Q)}問 / 図{len(used)}点 / 節{len(secs)}個 / ID {min(ids)}-{max(ids)}')
    return used


def build():
    used = check()
    figs = {k: fig_meta(k) for k in sorted(used)}
    evap = open(os.path.join(HERE, 'rika_evap.txt'), encoding='utf-8').read()
    evap = evap.split('"""')[1]

    tpl = open(os.path.join(HERE, 'rika_template.html'), encoding='utf-8').read()
    assert '/*__QDATA__*/' in tpl, 'テンプレートにプレースホルダが見つからない'

    data = ('const Q='      + json.dumps(Q, ensure_ascii=False) + ';\n'
            'const FIGS='   + json.dumps(figs, ensure_ascii=False) + ';\n'
            'const SEC='    + json.dumps(SEC, ensure_ascii=False) + ';\n'
            'const GROUPS=' + json.dumps(GROUPS, ensure_ascii=False) + ';\n'
            'const EVAP_TABLE=' + json.dumps(evap, ensure_ascii=False) + ';')
    out = tpl.replace('/*__QDATA__*/', data)

    dest = os.path.join(ROOT, 'templates', 'rika.html')
    open(dest, 'w', encoding='utf-8').write(out)
    print(f'生成: {dest}  ({len(out)//1024//1024} MB)')


if __name__ == '__main__':
    build()
