/* ── 印刷の記録・採点・出題のかたより（社会・理科で共通）──────────────
   build_shakai.py / build_rika.py がテンプレートの / *__HIST__* / に差しこむ。

   ・テストを作るたびに番号（例 S-7KQ2M）を決めて、用紙に番号と印刷日を刷る。
   ・印刷したときだけ「出した」とみなし、出した問題の並びをこの端末のブラウザに残す
     （localStorage の <科目>.tests）。解答を表示したまま印刷したときは残さない。
   ・操作画面で、印刷したテストを選んで「まちがえた問題」をタップして採点を保存する。
   ・次にテストを作るとき
       正解した問題 …… 直近 N 枚（既定10枚）のうちに正解していたら出さない
       採点待ちの問題 … 直近 N 枚に出ていて、まだ採点していなければ出さない
       まちがえた問題 … 最後に解いたときまちがえていたら、出やすくする
                        （重み 3＋3×まちがえた回数、上限15。ふつうの問題は1）
     出さない問題を除くと足りないときは、古いものから戻して数をそろえ、画面に注意を出す。
   ・番号を選べば、その回とまったく同じ問題・同じ順番でもう一度出せる（この端末だけ）。
   ・別の端末へは「書き出す」「読みこむ」で記録ごと持っていける。

   テンプレート側が用意するもの（makeHist に渡す）
     subj     'shakai' / 'rika'（localStorage のキーの頭）
     name     '社会' / '理科'
     prefix   'S' / 'R'（番号の頭）
     color    操作画面の色
     keyOf(q)        問題の記録用キー（文字列）
     labelOf(q, i)   採点画面に出す番号（用紙に刷ってある番号と同じもの）
     replay(list, title, code)   この並びでテストを作り直す
*/
function makeHist(o){
  const TKEY = o.subj + '.tests', OKEY = o.subj + '.opt';
  const C32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
  const BYKEY = new Map(Q.map(q => [o.keyOf(q), q]));
  let opt = { n: 10, wrong: true };
  let CUR = null;          // 画面に出ているテスト {code, title, ids}
  let gradeSel = null;     // 採点中の記録の番号
  let gradeWrong = new Set();

  /* ── 保存 ── */
  function load(){
    try { const v = JSON.parse(localStorage.getItem(TKEY) || '[]'); return Array.isArray(v) ? v : []; }
    catch(e){ return []; }
  }
  function save(h){ try { localStorage.setItem(TKEY, JSON.stringify(h.slice(0, 300))); } catch(e){} }
  function loadOpt(){
    try { const v = JSON.parse(localStorage.getItem(OKEY) || 'null'); if(v) opt = Object.assign(opt, v); } catch(e){}
  }
  function saveOpt(){ try { localStorage.setItem(OKEY, JSON.stringify(opt)); } catch(e){} }

  /* ── 日付・番号 ── */
  const WD = '日月火水木金土';
  function today(){
    const d = new Date();
    const p = x => String(x).padStart(2, '0');
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
  }
  function jpDate(s){
    const [y, m, d] = s.split('-').map(Number);
    return `${y}年${m}月${d}日（${WD[new Date(y, m - 1, d).getDay()]}）`;
  }
  function shortDate(s){ const [, m, d] = s.split('-').map(Number); return m + '/' + d; }
  function newCode(){
    const used = new Set(load().map(r => r.code));
    for(;;){
      let c = '';
      for(let i = 0; i < 5; i++) c += C32[Math.floor(Math.random() * 32)];
      c = o.prefix + '-' + c;
      if(!used.has(c)) return c;
    }
  }
  function normCode(t){
    t = String(t).toUpperCase().replace(/[^0-9A-Z]/g, '')
                 .replace(/I|L/g, '1').replace(/O/g, '0').replace(/U/g, 'V');
    if(t.length === 5) t = o.prefix + t;
    return t.length === 6 ? t[0] + '-' + t.slice(1) : null;
  }

  /* ── 問題ごとの状態 ──
     新しい記録から順に見て、その問題がいちばん最近出た記録で決める。 */
  function status(){
    const h = load(), st = new Map();
    h.forEach((r, i) => {
      const ws = r.w ? new Set(r.w) : null;
      r.ids.forEach(k => {
        let s = st.get(k);
        if(!s){
          s = { idx: i, last: ws ? (ws.has(k) ? 'x' : 'o') : 'p', wrongs: 0 };
          st.set(k, s);
        }
        if(ws && ws.has(k)) s.wrongs++;
      });
    });
    return st;
  }
  function held(s){ return s && opt.n > 0 && s.idx < opt.n && (s.last === 'o' || s.last === 'p'); }
  function weight(s){
    if(!s || s.last !== 'x' || !opt.wrong) return 1;
    return Math.min(15, 3 + 3 * s.wrongs);
  }

  /* ── 抽選 ── 重みつきで cnt 問を選ぶ（選んだ順がそのまま出題順のもとになる） */
  let lastWarn = '';
  /* unit(q) は「q を出すなら一緒に出す問題」（参照先＋q）。既定は q だけ。
     まとまりごとに選び、問題数をこえるまとまりは飛ばして次をさがす。 */
  function pick(P, cnt, unit){
    unit = unit || (q => [q]);
    const st = status();
    const ok = [], hold = [];
    P.forEach(q => {
      const s = st.get(o.keyOf(q));
      if(held(s)) hold.push({ q, s }); else ok.push({ q, w: weight(s) });
    });
    ok.forEach(x => { x.r = Math.pow(Math.random(), 1 / x.w); });
    ok.sort((a, b) => b.r - a.r);
    hold.sort((a, b) => b.s.idx - a.s.idx || Math.random() - .5);   // 古いものから
    const list = [], seen = new Set();
    const take = (arr, force) => {
      let n = 0;
      for(const x of arr){
        if(list.length >= cnt) break;
        const u = unit(x.q).filter(q => !seen.has(o.keyOf(q)));
        if(!u.length || (!force && list.length + u.length > cnt)) continue;
        u.forEach(q => { seen.add(o.keyOf(q)); list.push(q); });
        n += u.length;
      }
      return n;
    };
    take(ok, false);
    lastWarn = '';
    if(list.length < cnt){
      // 足りない分は、出さないはずの問題のうち古いものから戻す
      const n = take(hold, false) + (list.length < cnt ? take(ok.concat(hold), true) : 0);
      if(n) lastWarn = `この範囲で出せる問題が足りないため、直近${opt.n}枚に出た問題を${n}問まぜています。`;
      for(let i = list.length - 1; i > 0; i--){
        const j = Math.floor(Math.random() * (i + 1)); [list[i], list[j]] = [list[j], list[i]];
      }
    }
    return list;
  }

  /* ── 用紙に番号と日付を刷る ── */
  function begin(list, title, code){
    CUR = { code: code || newCode(), title, ids: list.map(o.keyOf) };
    stamp();
    const wb = document.getElementById('histWarn');
    wb.textContent = code ? `番号 ${code} のテストを、前と同じ問題・同じ順番で出しています。` : lastWarn;
    wb.style.display = wb.textContent ? 'block' : 'none';
    lastWarn = '';
  }
  function stamp(){
    if(!CUR) return;
    document.getElementById('shCode').textContent = '番号 ' + CUR.code;
    document.getElementById('shDate').textContent = '印刷日　' + jpDate(today());
  }
  /** 2枚目以降の見出し */
  function head2(title, nth){
    const h = document.createElement('div'); h.className = 'sh-head2';
    const a = document.createElement('span'); a.className = 'sh-pg';
    a.textContent = title + '（' + nth + '枚目）　名前＿＿＿＿＿＿＿＿　印刷日 ' + jpDate(today());
    const b = document.createElement('span'); b.className = 'sh-code';
    b.textContent = CUR ? '番号 ' + CUR.code : '';
    h.append(a, b);
    return h;
  }

  /* ── 印刷したら記録する ── */
  function mark(){
    stamp();
    if(!CUR || o.ansShown()) return;          // 解答つきの印刷（答え合わせ用）は記録しない
    const h = load();
    if(h.some(r => r.code === CUR.code)) return;  // 同じテストの刷り直し
    h.unshift({ code: CUR.code, d: today(), title: CUR.title, ids: CUR.ids, w: null });
    save(h);
    draw();
  }
  function print(){ mark(); window.print(); }
  window.addEventListener('beforeprint', mark);

  /* ── 操作画面 ── */
  function seg(id, items, cur, fn){
    return `<div class="seg" id="${id}">` + items.map(([v, t]) =>
      `<button class="seg-btn${v === cur ? ' on' : ''}" onclick="HIST.${fn}(${JSON.stringify(v)})">${t}</button>`
    ).join('') + '</div>';
  }
  function draw(){
    const host = document.getElementById('histCard');
    if(!host) return;
    const h = load(), st = status();
    let nHold = 0, nWrong = 0;
    st.forEach(s => { if(held(s)) nHold++; if(s.last === 'x') nWrong++; });
    const nGraded = h.filter(r => r.w).length;

    let html = `<div class="card"><div class="card-h">出題のかたより（印刷・採点の記録から）</div>`
      + `<div class="frow"><span class="flabel hl">正解した問題</span>`
      + seg('hN', [[10, '10枚は出さない'], [5, '5枚'], [20, '20枚'], [0, '気にしない']], opt.n, 'setN') + `</div>`
      + `<div class="frow"><span class="flabel hl">まちがえた問題</span>`
      + seg('hW', [[true, '出やすくする'], [false, 'ふつう']], opt.wrong, 'setWrong') + `</div>`
      + `<div class="hinfo">`;
    if(!h.length){
      html += 'まだ記録はありません。印刷したテストがここに記録され、採点すると次の出題に反映されます。';
    }else{
      html += `記録 ${h.length}枚（採点ずみ ${nGraded}・採点待ち ${h.length - nGraded}）`
        + `<br>いま出さない問題 <b>${nHold}</b>問　／　まちがえたままの問題 <b class="xr">${nWrong}</b>問`;
    }
    html += `<div class="hlinks">`
      + (h.length ? `<button class="lnk" onclick="HIST.exportJson()">記録を書き出す</button>` : '')
      + `<button class="lnk" onclick="document.getElementById('histFile').click()">記録を読みこむ</button>`
      // 「記録を消す」は子どもが押さないよう画面に出さない（HIST.clearAll() は残してある）
      + `<input type="file" id="histFile" accept=".json,application/json" style="display:none" onchange="HIST.importJson(this)">`
      + `</div></div></div>`;

    // 採点・前と同じテスト
    html += `<div class="card"><div class="card-h">採点する・前と同じテストを出す</div>`;
    if(!h.length){
      html += `<div class="hinfo">印刷したテストがまだありません。</div></div>`;
      host.innerHTML = html;
      return;
    }
    html += `<div class="row"><label>番号</label>`
      + `<input id="hCodeIn" class="hcode" placeholder="${o.prefix}-XXXXX" onkeydown="if(event.key==='Enter')HIST.find()">`
      + `<button class="hbtn" onclick="HIST.find()">さがす</button></div>`
      + `<div class="hlist">`
      + h.slice(0, 12).map(r => {
          const tag = r.w ? `<span class="htag ok">${r.ids.length - r.w.length}/${r.ids.length}</span>`
                          : `<span class="htag pend">採点待ち</span>`;
          return `<button class="hrow${r.code === gradeSel ? ' on' : ''}" onclick="HIST.choose('${r.code}')">`
            + `<span class="hc">${r.code}</span><span class="hd">${shortDate(r.d)}</span>`
            + `<span class="ht">${esc(r.title.replace(/^(社会|理科)テスト\s*/, ''))}</span>${tag}</button>`;
        }).join('')
      + (h.length > 12 ? `<div class="hinfo">ほか${h.length - 12}枚（番号でさがせます）</div>` : '')
      + `</div>`;

    const r = h.find(x => x.code === gradeSel);
    if(r){
      html += `<div class="gbox"><div class="gtitle">${r.code}　${jpDate(r.d)}　${esc(r.title)}</div>`
        + `<div class="hinfo">まちがえた問題をタップして ✗ にしてください（ほかは ○ になります）。</div>`
        + `<div class="ggrid">`
        + r.ids.map((k, i) => {
            const q = BYKEY.get(k);
            const lab = q ? o.labelOf(q, i) : k;
            return `<button class="gq${gradeWrong.has(k) ? ' x' : ''}" onclick="HIST.flip('${esc(k)}')">${lab}</button>`;
          }).join('')
        + `</div><div class="gsum">○ ${r.ids.length - gradeWrong.size}　✗ ${gradeWrong.size}　（${r.ids.length}問中）</div>`
        + `<div class="gbtns"><button class="hbtn main" onclick="HIST.saveGrade()">採点を保存する</button>`
        + `<button class="hbtn" onclick="HIST.redo('${r.code}')">このテストをもう一度出す</button>`
        + (r.w ? `<button class="lnk" onclick="HIST.unGrade()">採点を取り消す</button>` : '')
        + `</div></div>`;
    }
    html += `</div>`;
    host.innerHTML = html;
  }

  function choose(code){
    if(gradeSel === code){ gradeSel = null; draw(); return; }
    const r = load().find(x => x.code === code);
    if(!r) return;
    gradeSel = code;
    gradeWrong = new Set(r.w || []);
    draw();
  }
  function find(){
    const el = document.getElementById('hCodeIn');
    const c = normCode(el.value);
    if(!c || !load().some(r => r.code === c)){
      el.classList.add('bad');
      el.value = el.value + (el.value.includes('（') ? '' : '（この端末に記録がありません）');
      setTimeout(() => { el.classList.remove('bad'); el.value = ''; }, 1600);
      return;
    }
    gradeSel = null;
    choose(c);
  }
  function flip(k){ if(gradeWrong.has(k)) gradeWrong.delete(k); else gradeWrong.add(k); draw(); }
  function saveGrade(){
    const h = load(), r = h.find(x => x.code === gradeSel);
    if(!r) return;
    r.w = r.ids.filter(k => gradeWrong.has(k));
    r.gd = today();
    save(h);
    gradeSel = null;
    draw();
    o.refresh && o.refresh();
  }
  function unGrade(){
    const h = load(), r = h.find(x => x.code === gradeSel);
    if(!r) return;
    r.w = null; delete r.gd;
    save(h); gradeWrong = new Set(); draw();
  }
  function redo(code){
    const r = load().find(x => x.code === code);
    if(!r) return;
    const list = r.ids.map(k => BYKEY.get(k)).filter(Boolean);
    if(!list.length) return;
    o.replay(list, r.title, r.code);
  }
  function setN(n){ opt.n = n; saveOpt(); draw(); }
  function setWrong(v){ opt.wrong = v; saveOpt(); draw(); }
  function clearAll(){
    if(!confirm(o.name + 'テストの印刷・採点の記録をすべて消します。もとに戻せません。よろしいですか？')) return;
    try { localStorage.removeItem(TKEY); } catch(e){}
    gradeSel = null; draw();
  }
  function exportJson(){
    const blob = new Blob([JSON.stringify({ subj: o.subj, tests: load() }, null, 1)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = o.name + 'テスト_記録_' + today() + '.json';
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  function importJson(inp){
    const f = inp.files && inp.files[0];
    if(!f) return;
    f.text().then(t => {
      let v;
      try { v = JSON.parse(t); } catch(e){ alert('読みこめませんでした（JSONではありません）'); return; }
      if(!v || v.subj !== o.subj || !Array.isArray(v.tests)){ alert(o.name + 'テストの記録ではありません'); return; }
      const h = load(), at = new Map(h.map(r => [r.code, r]));
      let add = 0, upd = 0;
      v.tests.forEach(r => {
        if(!r || !r.code || !Array.isArray(r.ids)) return;
        const m = at.get(r.code);
        if(!m){ h.push(r); at.set(r.code, r); add++; }
        else if(r.w && (!m.w || (r.gd || '') > (m.gd || ''))){ m.w = r.w; m.gd = r.gd; upd++; }
      });
      h.sort((a, b) => (b.d || '').localeCompare(a.d || ''));
      save(h); draw();
      alert(`読みこみました（新しい記録 ${add}枚・採点の更新 ${upd}枚）`);
    });
    inp.value = '';
  }

  /* ── 見た目 ── */
  const css = `
.flabel.hl{min-width:96px}
.hinfo{font-size:12.5px;color:#718096;line-height:1.7;margin-top:10px}
.hinfo b{color:#2d3748}.hinfo b.xr{color:#c53030}
.hlinks{display:flex;gap:14px;flex-wrap:wrap;margin-top:4px}
.lnk{background:none;border:none;color:${o.color};cursor:pointer;font-size:12.5px;padding:0;
  text-decoration:underline;font-family:inherit}
.hcode{flex:1;min-width:0;padding:9px 12px;border:1.5px solid #e2e8f0;border-radius:9px;font-size:15px;
  font-family:"SF Mono",Menlo,monospace;letter-spacing:.08em;text-transform:uppercase}
.hcode.bad{border-color:#d32f2f;background:#fdeeee;text-transform:none;letter-spacing:0;font-family:inherit;font-size:13px}
.hbtn{padding:9px 16px;border:1.5px solid ${o.color};background:#fff;color:${o.color};border-radius:9px;
  font-size:14px;font-weight:600;font-family:inherit;cursor:pointer;white-space:nowrap}
.hbtn.main{background:${o.color};color:#fff}
.hlist{display:flex;flex-direction:column;gap:5px;margin-top:12px}
.hrow{display:flex;align-items:center;gap:10px;padding:8px 11px;border:1.5px solid #edf0f4;border-radius:9px;
  background:#fafbfc;cursor:pointer;font-family:inherit;font-size:13px;color:#2d3748;text-align:left}
.hrow.on{border-color:${o.color};background:#fff}
.hc{font-family:"SF Mono",Menlo,monospace;font-weight:700;letter-spacing:.05em}
.hd{color:#718096;min-width:38px}
.ht{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#4a5568}
.htag{font-size:11.5px;padding:2px 8px;border-radius:99px;white-space:nowrap}
.htag.pend{background:#fff4e5;color:#b7791f}.htag.ok{background:#e6f6ec;color:#2f855a}
.gbox{margin-top:12px;padding:12px;border:1.5px solid ${o.color};border-radius:11px;background:#fff}
.gtitle{font-size:13.5px;font-weight:700;color:#2d3748}
.ggrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(58px,1fr));gap:6px;margin-top:10px}
.gq{padding:8px 2px;border:1.5px solid #cbd5e0;border-radius:8px;background:#fff;font-size:13px;
  font-family:inherit;cursor:pointer;color:#2d3748}
.gq.x{background:#fde8e8;border-color:#e53e3e;color:#c53030;font-weight:700}
.gq.x::before{content:'✗ '}
.gsum{font-size:13px;color:#4a5568;margin-top:10px}
.gbtns{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:10px}
#histWarn{display:none;max-width:192mm;margin:0 auto 10px;padding:9px 13px;border-radius:9px;
  background:#fff8e6;color:#8a5a00;font-size:13px}
.sh-left{display:flex;flex-direction:column;gap:2px}
.sh-date{font-size:10px;color:#222}
.sh-code{font-size:13px;font-weight:700;letter-spacing:.1em;color:#000;margin-left:10px;
  font-family:"SF Mono",Menlo,monospace;white-space:nowrap;border:2px solid #000;border-radius:4px;
  padding:2px 8px;line-height:1.1}
.sh-code:empty{display:none}
.sh-head2{display:flex;justify-content:space-between;align-items:center;
  border-bottom:1.5px solid #111;padding-bottom:4px;margin-bottom:8px}
.sh-pg{font-size:10px;color:#333}
@media print{#histWarn{display:none!important}}
`;
  const stEl = document.createElement('style'); stEl.textContent = css;
  document.head.appendChild(stEl);

  loadOpt();
  return { pick, begin, head2, print, draw, choose, find, flip, saveGrade, unGrade, redo,
           setN, setWrong, clearAll, exportJson, importJson,
           code: () => CUR && CUR.code };
}
