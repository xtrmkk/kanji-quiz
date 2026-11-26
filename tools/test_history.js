/* ── 印刷の記録・採点・復習の予定（社会・理科で共通）──────────────────
   build_shakai.py / build_rika.py がテンプレートの / *__HIST__* / に差しこむ。

   ・テストを作るたびに番号（例 S-7KQ2M）を決めて、用紙に番号と印刷日を刷る。
   ・印刷したときだけ「出した」とみなし、出した問題の並びをこの端末のブラウザに残す
     （localStorage の <科目>.tests）。解答を表示したままの印刷と、解き直し用紙は残さない。
   ・操作画面で、印刷したテストを選んで1問ずつ ○ → ✗ → △ とタップして採点を保存する。
       △ は「正解だけど自信がない・小問の一部がちがう」。予定の上では ✗ と同じあつかい。
   ・問題ごとに「次に出す日」を決める（ライトナー方式。日付は印刷日＝解いた日で数える）
       ✗・△ ……… 箱0にもどし、翌日に出す
       ○ ………… 箱を1つ上げ、箱1→3日後、箱2→7日後、箱3→14日後、箱4→28日後、箱5→56日後
       箱3以上（日を空けて2回以上つづけて正解）を「定着」とよぶ
       採点待ち …… 採点するまで出さない。ただし印刷から7日たっても採点がなければ無視する
   ・新しいテストは次の順で埋める（参照先といっしょに出す問題は、まとまりごと）
       1. 復習日が来た問題（✗・△ が先、次に予定日の古い順）… 問題数の7割まで
       2. まだ一度も出ていない問題（ランダム）
       3. 復習日が来た問題の残り
       4. まだ復習日の来ていない問題（予定日の近い順）・採点待ちの問題 … 画面に注意を出す
     できたテストの並びはランダム（番号順の指定ならテンプレート側が並べ直す）。
   ・採点した用紙から、✗・△ の問題だけの「解き直し用紙」を作れる。
   ・番号を選べば、その回とまったく同じ問題・同じ順番でもう一度出せる（この端末だけ）。
   ・別の端末へは「書き出す」「読みこむ」で記録ごと持っていける。

   テンプレート側が用意するもの（makeHist に渡す）
     subj     'shakai' / 'rika'（localStorage のキーの頭）
     name     '社会' / '理科'
     prefix   'S' / 'R'（番号の頭）
     color    操作画面の色
     keyOf(q)        問題の記録用キー（文字列）
     labelOf(q, i)   採点画面に出す番号（用紙に刷ってある番号と同じもの）
     ansShown()      いま解答を表示しているか
     sections        節の一覧 [{key, name, keys:[問題キー…]}]（節ごとの状況の表に使う）
     pickSection(key) 節の行をタップしたとき、その節を出題範囲にする
     replay(list, title, code, redo)   この並びでテストを作り直す（redo=解き直し用紙）
*/
function makeHist(o){
  const TKEY = o.subj + '.tests', OKEY = o.subj + '.opt';
  const C32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';
  const BYKEY = new Map(Q.map(q => [o.keyOf(q), q]));
  const IV = [1, 3, 7, 14, 28, 56];   // 箱ごとの次の出題までの日数
  const SOLID = 3;                    // この箱から「定着」
  const PEND_DAYS = 7;                // 採点待ちを待つ日数
  const DUE_SHARE = 0.7;              // 復習の問題でうめる割合の上限
  let opt = { mode: 'plan' };         // plan=復習の予定どおり／random=ランダム
  let CUR = null;          // 画面に出ているテスト {code, title, ids, redo}
  let gradeSel = null;     // 採点中の記録の番号
  let gradeMark = new Map();   // 問題キー -> 'x' | 't'

  /* ── 保存 ── */
  function load(){
    try { const v = JSON.parse(localStorage.getItem(TKEY) || '[]'); return Array.isArray(v) ? v : []; }
    catch(e){ return []; }
  }
  function save(h){ try { localStorage.setItem(TKEY, JSON.stringify(h.slice(0, 400))); } catch(e){} }
  function loadOpt(){
    try {
      const v = JSON.parse(localStorage.getItem(OKEY) || 'null');
      if(v && (v.mode === 'plan' || v.mode === 'random')) opt.mode = v.mode;
    } catch(e){}
  }
  function saveOpt(){ try { localStorage.setItem(OKEY, JSON.stringify(opt)); } catch(e){} }

  /* ── 日付・番号 ── */
  const WD = '日月火水木金土';
  const p2 = x => String(x).padStart(2, '0');
  const ymd = d => d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate());
  function today(){ return ymd(new Date()); }
  function addDays(s, n){
    const [y, m, d] = s.split('-').map(Number);
    return ymd(new Date(y, m - 1, d + n));
  }
  function daysBetween(a, b){
    const f = s => { const [y, m, d] = s.split('-').map(Number); return Date.UTC(y, m - 1, d); };
    return Math.round((f(b) - f(a)) / 86400000);
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
     古い記録から順に見て、箱と次に出す日を更新していく。
     s = {box, due, seen（採点ずみで解いた回数）, last('o'|'x'|'t'), pend（採点待ち）} */
  function status(){
    const td = today(), st = new Map();
    load().slice().reverse().forEach(r => {
      if(!r.w && daysBetween(r.d, td) > PEND_DAYS) return;   // 採点されないまま古くなった用紙
      const ws = new Set(r.w || []), ts = new Set(r.t || []);
      r.ids.forEach(k => {
        const s = st.get(k) || { box: 0, due: null, seen: 0, last: null, pend: false };
        if(!r.w){ s.pend = true; st.set(k, s); return; }
        s.pend = false; s.seen++;
        if(ws.has(k) || ts.has(k)){
          s.box = 0; s.last = ws.has(k) ? 'x' : 't';
        }else{
          s.box = Math.min(s.box + 1, IV.length - 1); s.last = 'o';
        }
        s.due = addDays(r.d, IV[s.box]);
        st.set(k, s);
      });
    });
    return st;
  }
  /** 'new' まだ | 'pend' 採点待ち | 'due' 今日の復習 | 'learn' 練習中 | 'solid' 定着 */
  function kind(s, td){
    if(!s || (!s.seen && !s.pend)) return 'new';
    if(s.pend) return 'pend';
    if(s.due <= td) return 'due';
    return s.box >= SOLID ? 'solid' : 'learn';
  }

  /* ── 抽選 ──
     unit(q) は「q を出すなら一緒に出す問題」（参照先＋q）。既定は q だけ。
     まとまりごとに選び、問題数をこえるまとまりは飛ばして次をさがす。 */
  let lastWarn = '';
  const shuffle = a => { for(let i = a.length - 1; i > 0; i--){
    const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  function pick(P, cnt, unit){
    unit = unit || (q => [q]);
    const st = status(), td = today();
    const list = [], seen = new Set();
    const take = (arr, upto) => {
      let n = 0;
      for(const q of arr){
        if(list.length >= upto) break;
        const u = unit(q).filter(x => !seen.has(o.keyOf(x)));
        if(!u.length || list.length + u.length > cnt) continue;
        u.forEach(x => { seen.add(o.keyOf(x)); list.push(x); });
        n += u.length;
      }
      return n;
    };
    lastWarn = '';
    if(opt.mode === 'random'){
      take(shuffle(P.slice()), cnt);
      return shuffle(list);
    }
    const due = [], neu = [], later = [], pend = [];
    P.forEach(q => {
      const s = st.get(o.keyOf(q)), k = kind(s, td);
      if(k === 'new') neu.push(q);
      else if(k === 'pend') pend.push(q);
      else if(k === 'due') due.push({ q, s, r: Math.random() });
      else later.push({ q, s, r: Math.random() });
    });
    const bad = s => (s.last === 'o' ? 1 : 0);
    due.sort((a, b) => bad(a.s) - bad(b.s) || a.s.due.localeCompare(b.s.due) || a.r - b.r);
    later.sort((a, b) => a.s.due.localeCompare(b.s.due) || a.r - b.r);
    const dueQ = due.map(x => x.q);
    take(dueQ, Math.ceil(cnt * DUE_SHARE));
    take(shuffle(neu), cnt);
    take(dueQ, cnt);
    const n = take(later.map(x => x.q), cnt) + take(shuffle(pend), cnt);
    if(n) lastWarn = `この範囲で今日出すべき問題が足りないため、まだ復習日の来ていない問題を${n}問まぜています。`
                   + '範囲をひろげると、新しい問題が入ります。';
    return shuffle(list);
  }

  /* ── 用紙に番号と日付を刷る ── */
  function begin(list, title, code, redo){
    CUR = { code: code || newCode(), title, ids: list.map(o.keyOf), redo: !!redo };
    stamp();
    const wb = document.getElementById('histWarn');
    wb.textContent = redo ? `番号 ${code} の解き直し用紙です。印刷しても記録には入りません。`
                          + '答えを見て確かめたら、解答を隠してもう一度、何も見ずに答えさせてください。'
                   : code ? `番号 ${code} のテストを、前と同じ問題・同じ順番で出しています。` : lastWarn;
    wb.style.display = wb.textContent ? 'block' : 'none';
    lastWarn = '';
  }
  function codeText(){ return CUR ? (CUR.redo ? '解き直し ' : '番号 ') + CUR.code : ''; }
  function stamp(){
    if(!CUR) return;
    document.getElementById('shCode').textContent = codeText();
    document.getElementById('shDate').textContent = '印刷日　' + jpDate(today());
  }
  /** 2枚目以降の見出し */
  function head2(title, nth){
    const h = document.createElement('div'); h.className = 'sh-head2';
    const a = document.createElement('span'); a.className = 'sh-pg';
    a.textContent = title + '（' + nth + '枚目）　名前＿＿＿＿＿＿＿＿　印刷日 ' + jpDate(today());
    const b = document.createElement('span'); b.className = 'sh-code';
    b.textContent = codeText();
    h.append(a, b);
    return h;
  }

  /* ── 印刷したら記録する ── */
  function mark(){
    stamp();
    if(!CUR || CUR.redo || o.ansShown()) return;   // 解き直し・答え合わせ用の印刷は記録しない
    const h = load();
    if(h.some(r => r.code === CUR.code)) return;   // 同じテストの刷り直し
    h.unshift({ code: CUR.code, d: today(), title: CUR.title, ids: CUR.ids, w: null });
    save(h);
    draw();
  }
  function print(){ mark(); window.print(); }
  window.addEventListener('beforeprint', mark);

  /* ── 操作画面 ── */
  function seg(items, cur, fn){
    return `<div class="seg">` + items.map(([v, t]) =>
      `<button class="seg-btn${v === cur ? ' on' : ''}" onclick="HIST.${fn}(${JSON.stringify(v)})">${t}</button>`
    ).join('') + '</div>';
  }
  const KN = { new: 'まだ', due: '今日の復習', learn: '練習中', solid: '定着', pend: '採点待ち' };
  function draw(){
    const host = document.getElementById('histCard');
    if(!host) return;
    const h = load(), st = status(), td = today();
    const nPend = h.filter(r => !r.w && daysBetween(r.d, td) <= PEND_DAYS).length;

    // ── 節ごとの状況 ──
    const tot = { new: 0, due: 0, learn: 0, solid: 0, pend: 0 };
    const rows = (o.sections || []).map(sec => {
      const c = { new: 0, due: 0, learn: 0, solid: 0, pend: 0 };
      sec.keys.forEach(k => { const t = kind(st.get(k), td); c[t]++; tot[t]++; });
      return { sec, c, n: sec.keys.length };
    });
    let html = `<div class="card"><div class="card-h">復習の予定（印刷・採点の記録から）</div>`
      + `<div class="frow"><span class="flabel hl">出し方</span>`
      + seg([['plan', '復習の予定どおり'], ['random', 'ランダム']], opt.mode, 'setMode') + `</div>`
      + `<div class="hinfo">`
      + (opt.mode === 'plan'
          ? '✗・△ の問題は翌日、○ の問題は 3日→7日→14日→28日後 と間をのばして出します。'
            + '今日の復習（最大7割）のあと、まだ出ていない問題で埋めます。'
          : '記録を使わず、範囲からランダムに出します（記録は残ります）。')
      + `</div>`;
    if(h.length){
      html += `<div class="hsum">`
        + `<span class="k due">今日の復習 <b>${tot.due}</b></span>`
        + `<span class="k learn">練習中 <b>${tot.learn}</b></span>`
        + `<span class="k solid">定着 <b>${tot.solid}</b></span>`
        + `<span class="k new">まだ <b>${tot.new}</b></span>`
        + (tot.pend ? `<span class="k pend">採点待ち <b>${tot.pend}</b></span>` : '')
        + `</div>`;
      if(nPend) html += `<div class="hwarn">採点待ちの用紙が ${nPend}枚あります。採点すると次の出題に反映されます。</div>`;
      html += `<details class="secs"><summary>節ごとの状況を見る（タップするとその節を出題範囲にします）</summary>`
        + `<div class="stab">`
        + rows.map(({ sec, c, n }) => {
            const seg = t => c[t] ? `<i class="b ${t}" style="width:${c[t] / n * 100}%"></i>` : '';
            return `<button class="srow" onclick="HIST.pickSection('${sec.key}')">`
              + `<span class="sn">${esc(sec.name)}</span>`
              + `<span class="bar">${seg('solid')}${seg('learn')}${seg('due')}${seg('pend')}</span>`
              + `<span class="sc">${c.due ? `<em>復習${c.due}</em>` : ''}定着${c.solid}/${n}</span></button>`;
          }).join('')
        + `</div><div class="legend"><i class="b solid"></i>定着 <i class="b learn"></i>練習中 `
        + `<i class="b due"></i>今日の復習 <i class="b pend"></i>採点待ち <i class="b new"></i>まだ</div></details>`;
    }else{
      html += `<div class="hinfo">まだ記録はありません。印刷したテストがここに記録され、採点すると次の出題に反映されます。</div>`;
    }
    html += `<div class="hlinks">`
      + (h.length ? `<button class="lnk" onclick="HIST.exportJson()">記録を書き出す</button>` : '')
      + `<button class="lnk" onclick="document.getElementById('histFile').click()">記録を読みこむ</button>`
      // 「記録を消す」は子どもが押さないよう画面に出さない（HIST.clearAll() は残してある）
      + `<input type="file" id="histFile" accept=".json,application/json" style="display:none" onchange="HIST.importJson(this)">`
      + `</div></div>`;

    // ── 採点・解き直し・前と同じテスト ──
    html += `<div class="card"><div class="card-h">採点する・解き直す・前と同じテストを出す</div>`;
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
          const nb = (r.w ? r.w.length : 0) + (r.t ? r.t.length : 0);
          const tag = r.w ? `<span class="htag ok">○${r.ids.length - nb}/${r.ids.length}</span>`
                          : `<span class="htag pend">採点待ち</span>`;
          return `<button class="hrow${r.code === gradeSel ? ' on' : ''}" onclick="HIST.choose('${r.code}')">`
            + `<span class="hc">${r.code}</span><span class="hd">${shortDate(r.d)}</span>`
            + `<span class="ht">${esc(r.title.replace(/^(社会|理科)テスト\s*/, ''))}</span>${tag}</button>`;
        }).join('')
      + (h.length > 12 ? `<div class="hinfo">ほか${h.length - 12}枚（番号でさがせます）</div>` : '')
      + `</div>`;

    const r = h.find(x => x.code === gradeSel);
    if(r){
      let nx = 0, nt = 0;
      gradeMark.forEach(v => { if(v === 'x') nx++; else nt++; });
      html += `<div class="gbox"><div class="gtitle">${r.code}　${jpDate(r.d)}　${esc(r.title)}</div>`
        + `<div class="hinfo">タップするたびに ○ → ✗ → △ と変わります。`
        + `△ は「正解だけど自信がない・一部まちがい」で、✗ と同じく翌日もう一度出ます。</div>`
        + `<div class="ggrid">`
        + r.ids.map((k, i) => {
            const q = BYKEY.get(k);
            const lab = q ? o.labelOf(q, i) : k;
            const m = gradeMark.get(k) || '';
            return `<button class="gq ${m}" onclick="HIST.flip('${esc(k)}')">${lab}</button>`;
          }).join('')
        + `</div><div class="gsum">○ ${r.ids.length - nx - nt}　✗ ${nx}　△ ${nt}　（${r.ids.length}問中）</div>`
        + `<div class="gbtns"><button class="hbtn main" onclick="HIST.saveGrade()">採点を保存する</button>`
        + (r.w && (r.w.length || (r.t || []).length)
            ? `<button class="hbtn" onclick="HIST.redoWrong('${r.code}')">✗・△ の解き直し用紙を作る</button>` : '')
        + `<button class="hbtn" onclick="HIST.redo('${r.code}')">このテストをもう一度出す</button></div>`
        + `<div class="gbtns">`
        + (r.w ? `<button class="lnk" onclick="HIST.unGrade()">採点を取り消す</button>` : '')
        + (!r.w ? `<button class="lnk" onclick="HIST.drop()">この用紙は解かなかった（記録から外す）</button>` : '')
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
    gradeMark = new Map();
    (r.w || []).forEach(k => gradeMark.set(k, 'x'));
    (r.t || []).forEach(k => gradeMark.set(k, 't'));
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
  function flip(k){
    const m = gradeMark.get(k);
    if(!m) gradeMark.set(k, 'x'); else if(m === 'x') gradeMark.set(k, 't'); else gradeMark.delete(k);
    draw();
  }
  function saveGrade(){
    const h = load(), r = h.find(x => x.code === gradeSel);
    if(!r) return;
    r.w = r.ids.filter(k => gradeMark.get(k) === 'x');
    r.t = r.ids.filter(k => gradeMark.get(k) === 't');
    r.gd = today();
    save(h);
    draw();      // 解き直し用紙のボタンを出すため、選んだまま描き直す
  }
  function unGrade(){
    const h = load(), r = h.find(x => x.code === gradeSel);
    if(!r) return;
    r.w = null; delete r.t; delete r.gd;
    save(h); gradeMark = new Map(); draw();
  }
  function drop(){
    const h = load(), i = h.findIndex(x => x.code === gradeSel);
    if(i < 0 || h[i].w) return;
    if(!confirm(`番号 ${h[i].code} の用紙を、解かなかったものとして記録から外します。よろしいですか？`)) return;
    h.splice(i, 1); save(h); gradeSel = null; draw();
  }
  function redo(code){
    const r = load().find(x => x.code === code);
    if(!r) return;
    const list = r.ids.map(k => BYKEY.get(k)).filter(Boolean);
    if(list.length) o.replay(list, r.title, r.code, false);
  }
  function redoWrong(code){
    const r = load().find(x => x.code === code);
    if(!r || !r.w) return;
    const bad = new Set([...(r.w || []), ...(r.t || [])]);
    const list = r.ids.filter(k => bad.has(k)).map(k => BYKEY.get(k)).filter(Boolean);
    if(list.length) o.replay(list, r.title.replace(/^(社会|理科)テスト/, '$1テスト 解き直し'), r.code, true);
  }
  function setMode(m){ opt.mode = m; saveOpt(); draw(); }
  function pickSection(key){ o.pickSection && o.pickSection(key); draw(); }
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
        else if(r.w && (!m.w || (r.gd || '') > (m.gd || ''))){ m.w = r.w; m.t = r.t || []; m.gd = r.gd; upd++; }
      });
      h.sort((a, b) => (b.d || '').localeCompare(a.d || ''));
      save(h); draw();
      alert(`読みこみました（新しい記録 ${add}枚・採点の更新 ${upd}枚）`);
    });
    inp.value = '';
  }

  /* ── 見た目 ── */
  const css = `
.flabel.hl{min-width:60px}
.hinfo{font-size:12.5px;color:#718096;line-height:1.7;margin-top:10px}
.hinfo b{color:#2d3748}
.hwarn{font-size:12.5px;color:#8a5a00;background:#fff8e6;border-radius:8px;padding:7px 10px;margin-top:10px}
.hsum{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}
.hsum .k{font-size:12.5px;padding:4px 10px;border-radius:99px;background:#f1f3f6;color:#4a5568}
.hsum .k b{font-size:14px;margin-left:2px}
.hsum .k.due{background:#fde8e8;color:#c53030}
.hsum .k.solid{background:#e6f6ec;color:#2f855a}
.hsum .k.learn{background:#e8f0fe;color:#2b5fb4}
.hsum .k.pend{background:#fff4e5;color:#b7791f}
.secs{margin-top:12px}
.secs summary{font-size:12.5px;color:${o.color};cursor:pointer}
.stab{display:flex;flex-direction:column;gap:3px;margin-top:8px}
.srow{display:grid;grid-template-columns:minmax(0,12.5em) minmax(40px,1fr) auto;gap:8px;align-items:center;padding:5px 6px;
  border:none;background:none;border-radius:6px;cursor:pointer;font-family:inherit;text-align:left}
.srow:hover{background:#f5f7fa}
.sn{font-size:12px;color:#2d3748;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar{display:flex;height:10px;border-radius:5px;overflow:hidden;background:#e9ecf1}
.sc{font-size:11.5px;color:#718096;white-space:nowrap}
.sc em{font-style:normal;color:#c53030;margin-right:6px}
i.b{display:inline-block;height:100%}
i.b.solid{background:#48bb78}i.b.learn{background:#7aa7ee}i.b.due{background:#f56565}
i.b.pend{background:#f6c26b}i.b.new{background:#e9ecf1}
.legend{font-size:11px;color:#718096;margin-top:6px}
.legend i.b{width:10px;height:10px;border-radius:2px;vertical-align:-1px;margin-left:6px}
.hlinks{display:flex;gap:14px;flex-wrap:wrap;margin-top:12px}
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
.gq.t{background:#fff4e5;border-color:#dd8a1e;color:#b7791f;font-weight:700}
.gq.t::before{content:'△ '}
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
  return { pick, begin, head2, print, draw, choose, find, flip, saveGrade, unGrade, drop,
           redo, redoWrong, setMode, pickSection, clearAll, exportJson, importJson,
           status, code: () => CUR && CUR.code };
}
