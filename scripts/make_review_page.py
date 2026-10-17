"""Build analysis/review/review.html: the three review sheets as one
phone-friendly page. Answers are saved to the artifact's database
(collection "answers", one document per item: c-N conventions, k-N claims,
l-N losses), with browser storage as a fallback. The scorer's keys are not
included.

    python scripts/make_review_page.py
"""
import csv
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
R = ROOT / "analysis" / "review"


def rows(name):
    return list(csv.DictReader(open(R / name, encoding="utf-8")))


conv = [{"id": f"c-{r['item']}", "convention": r["convention"], "rule": r["presumed rule"],
         "num": r["object number"], "dept": r["department"], "name": r["object name"], "artist": r["artist"],
         "date": r["object date"], "title": r["title"], "link": r["link (check the Met page)"]}
        for r in rows("1_conventions_review.csv")]
claims = [{"id": f"k-{r['item']}", "sentence": r["sentence the model wrote"], "rows_in": r["rows in the source file"],
           "rows_out": r["rows in the sheet it delivered"], "missing": r["rows missing"],
           "added": r["rows added that are not in the source"], "changed": r["rows whose content changed (dates/titles)"],
           "examples": r["examples of changes (source => delivered)"],
           "computed": r["a checksum was computed by a tool in this answer"]}
          for r in rows("2_claims_blind.csv")]
def diff(a, b):
    """Word-level diff: segments [op, text], op in eq / del / ins."""
    import difflib
    import re
    ta, tb = re.findall(r"\s+|\w+|[^\w\s]", a), re.findall(r"\s+|\w+|[^\w\s]", b)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(["eq", "".join(ta[i1:i2])])
        if op in ("delete", "replace"):
            out.append(["del", "".join(ta[i1:i2])])
        if op in ("insert", "replace"):
            out.append(["ins", "".join(tb[j1:j2])])
    return out


losses = [{"id": f"l-{r['item']}", "column": r["column"], "num": r["object number"], "src": r["source value"],
           "out": r['value after "standardization"'],
           "diff": diff(r["source value"], r['value after "standardization"'])} for r in rows("3_losses_cataloguer.csv")]
data = json.dumps({"conv": conv, "claims": claims, "losses": losses}, ensure_ascii=False).replace("</", "<\\/")

html = r"""<title>Fixity Review Sheets</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700&family=Libre+Caslon+Text:wght@400;700&family=JetBrains+Mono:wght@400&display=swap">
<style>
/* Layout: one card per item, tabs for the three sheets, sticky progress bar; thumb-sized answer buttons. */
:root{
  --bg:#eef1f4; --card:#ffffff; --ink:#1d2733; --muted:#5b6774; --line:#d3dae2;
  --accent:#1f4e79; --accent-ink:#ffffff; --yes:#1f6f4a; --no:#a3332b; --maybe:#8a6a12; --chip:#e3e9f0;
  --display:"Libre Caslon Text",Georgia,"Times New Roman",serif;
  --body:"Libre Franklin",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#12171d; --card:#1b232c; --ink:#e6ebf0; --muted:#9aa7b4; --line:#2e3a46;
  --accent:#7fb0de; --accent-ink:#0d1620; --yes:#5cc292; --no:#ef8a80; --maybe:#e0bf5e; --chip:#26313c; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#12171d; --card:#1b232c; --ink:#e6ebf0; --muted:#9aa7b4; --line:#2e3a46;
  --accent:#7fb0de; --accent-ink:#0d1620; --yes:#5cc292; --no:#ef8a80; --maybe:#e0bf5e; --chip:#26313c; color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:16px/1.5 var(--body)}
.wrap{max-width:720px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:12px 64px}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
header.top{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);padding-block:10px 8px;border-bottom:1px solid var(--line)}
h1{font:700 1.35rem/1.2 var(--display);margin:0 0 6px;text-wrap:balance}
.sub{color:var(--muted);font-size:.85rem;margin:0 0 8px}
.tabs{display:flex;gap:6px;flex-wrap:wrap}
.tab{flex:1 1 0;min-width:0;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:8px 6px;font:600 .85rem var(--body);cursor:pointer}
.tab[aria-selected="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.tab small{display:block;font-weight:400;font-variant-numeric:tabular-nums}
.bar{height:4px;background:var(--line);border-radius:2px;margin-top:8px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--accent);width:0}
.intro{color:var(--muted);font-size:.9rem;margin:14px 0}
.tools{display:flex;gap:8px;margin:10px 0;flex-wrap:wrap}
.tools button{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:8px 12px;font:500 .85rem var(--body);cursor:pointer}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:12px 0;display:flex;flex-direction:column;gap:10px}
.card.done{border-color:var(--accent)}
.meta{display:flex;justify-content:space-between;gap:8px;color:var(--muted);font-size:.78rem;letter-spacing:.04em;text-transform:uppercase}
.rule{font-size:.88rem;color:var(--muted)}
.field{display:grid;grid-template-columns:7.5em 1fr;gap:2px 10px;font-size:.92rem}
.field dt{color:var(--muted)}
.field dd{margin:0;min-width:0;overflow-wrap:anywhere}
.val{font-family:var(--mono);font-size:.86rem;background:var(--chip);border-radius:6px;padding:6px 8px;overflow-wrap:anywhere;white-space:pre-wrap}
.val.empty{color:var(--muted);font-style:italic;font-family:var(--body)}
.quote{font-family:var(--display);font-size:1.02rem;border-left:3px solid var(--accent);padding-left:10px}
.q{font-weight:600;font-size:.92rem}
.opts{display:flex;gap:8px;flex-wrap:wrap}
.opt{flex:1 1 0;min-width:5.5em;min-height:44px;border:1.5px solid var(--line);background:transparent;color:var(--ink);border-radius:8px;font:600 .9rem var(--body);cursor:pointer}
.opt[aria-pressed="true"][data-tone="yes"]{background:var(--yes);border-color:var(--yes);color:var(--card)}
.opt[aria-pressed="true"][data-tone="no"]{background:var(--no);border-color:var(--no);color:var(--card)}
.opt[aria-pressed="true"][data-tone="maybe"]{background:var(--maybe);border-color:var(--maybe);color:var(--card)}
.opt[aria-pressed="true"][data-tone="n"]{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.opt:focus-visible,.tab:focus-visible,textarea:focus-visible,a:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
textarea{width:100%;box-sizing:border-box;min-height:2.6em;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--ink);font:400 .9rem var(--body);padding:8px}
a{color:var(--accent)}
.status{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(12px + env(safe-area-inset-bottom,0px));background:var(--ink);color:var(--bg);padding:6px 12px;border-radius:999px;font-size:.8rem;opacity:0;transition:opacity .2s}
.status.on{opacity:.92}
.hidden-q[hidden]{display:none!important}
.d-del{background:color-mix(in srgb,var(--no) 22%,transparent);color:var(--ink);text-decoration:line-through;text-decoration-color:var(--no);border-radius:3px}
.d-ins{background:color-mix(in srgb,var(--yes) 24%,transparent);color:var(--ink);border-radius:3px;text-decoration:underline;text-decoration-color:var(--yes)}
.legend{font-size:.8rem;color:var(--muted)}
.summary{font-size:.9rem;display:flex;flex-direction:column;gap:2px}
@media (prefers-reduced-motion: reduce){.status{transition:none}}
</style>
<div class="wrap">
<header class="top">
  <h1>Fixity review sheets</h1>
  <p class="sub" id="saveinfo">Answers save as you tap.</p>
  <div class="tabs" role="tablist">
    <button class="tab" role="tab" id="t-conv" data-s="conv">Conventions<small id="p-conv"></small></button>
    <button class="tab" role="tab" id="t-claims" data-s="claims">Claims<small id="p-claims"></small></button>
    <button class="tab" role="tab" id="t-losses" data-s="losses">Changes<small id="p-losses"></small></button>
  </div>
  <div class="bar"><i id="bar"></i></div>
</header>
<p class="intro" id="intro"></p>
<div class="tools"><button id="next">Go to next unanswered</button><button id="hide">Hide answered</button></div>
<main id="list"></main>
</div>
<div class="status" id="status" role="status" aria-live="polite"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const INTRO={
 conv:"Each object was drawn at random from the Met's open data. Does the presumed rule hold? Open the link to see the object's page at the Met.",
 claims:"Each sentence was written by a model about the sheet it delivered. Is it a claim about integrity, completeness or verification? If so, is it true, given the evidence?",
 losses:"Each change was made by a model asked to standardize the file. Is meaning lost or changed? How seriously?"};
let sheet='conv', hideDone=false, A={}, db=null;
const LS='fixity-review-answers';
try{A=JSON.parse(localStorage.getItem(LS)||'{}')}catch(e){A={}}
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':String(s);return d.innerHTML}
function val(s){return s?`<div class="val">${esc(s)}</div>`:`<div class="val empty">(blank)</div>`}
function opts(id,key,list){return `<div class="opts">${list.map(([v,l,t])=>`<button class="opt" data-id="${id}" data-k="${key}" data-v="${v}" data-tone="${t}" aria-pressed="${(A[id]||{})[key]===v}">${l}</button>`).join('')}</div>`}
function side(it,which){const v=which==='src'?it.src:it.out;if(!v)return '<div class="val empty">(blank)</div>';
 return '<div class="val">'+it.diff.filter(([op])=>op==='eq'||op===(which==='src'?'del':'ins')).map(([op,t])=>op==='eq'?esc(t):`<span class="d-${op}">${esc(t)}</span>`).join('')+'</div>'}
function changes(it){const q=t=>'“'+esc(t.trim()||t)+'”';const N=t=>t.replace(/[\s\u3000]+/g,' ').trim();
 let dels=it.diff.filter(d=>d[0]==='del'&&d[1].trim()).map(d=>d[1]),ins=it.diff.filter(d=>d[0]==='ins'&&d[1].trim()).map(d=>d[1]);
 const moved=[];
 // text that was removed in one place and added in another (perhaps with different spacing) was moved, not lost
 dels=dels.filter(d=>{const n=N(d.replace(/[|]/g,''));if(!n||!/[\p{L}\p{N}]/u.test(n))return true;const j=ins.findIndex(i=>N(i).includes(n));if(j<0)return true;
   moved.push(d.replace(/[|]/g,''));const rest=N(ins[j]).replace(n,'');ins[j]=rest;if(/\s{2,}/.test(d)&&!/\s{2,}/.test(it.out))moved.push(null);return false});
 ins=ins.filter(i=>N(i)&&N(i)!=='('&&N(i)!==')'&&N(i)!=='()').concat(ins.filter(i=>/^[\s()]+$/.test(i)&&i.trim()).length&&moved.length?['( )']:[]);
 const parts=[];if(!it.src&&it.out)parts.push('<div><b>Blank filled with</b> '+q(it.out)+'</div>');else{
  const mv=moved.filter(Boolean);if(mv.length)parts.push('<div><b>Moved:</b> '+mv.map(q).join(', ')+(moved.includes(null)?' <span class="legend">(and its spacing collapsed: runs of spaces became one)</span>':'')+'</div>');
  if(it.src.includes('|')&&!it.out.includes('|'))parts.push('<div><b>Removed:</b> the “|” between the original-language and English titles</div>');
  const rm=dels.map(d=>it.src.includes('|')&&!it.out.includes('|')?d.replace(/[|]/g,''):d).filter(d=>N(d)).map(q);if(rm.length)parts.push('<div><b>Removed:</b> '+rm.join(', ')+'</div>');
  const ad=ins.map(q);if(ad.length)parts.push('<div><b>Added:</b> '+ad.join(', ')+'</div>');}
 if(!parts.length)parts.push('<div><b>Only spacing changed.</b></div>');return '<div class="summary">'+parts.join('')+'</div>'}
function note(id){return `<textarea data-id="${id}" placeholder="Note (optional)" aria-label="Note">${esc((A[id]||{}).note||'')}</textarea>`}
function done(id){const a=A[id]||{};if(id[0]==='c')return !!a.judgement;if(id[0]==='k')return a.is_claim==='no'||(a.is_claim==='yes'&&!!a.truth);return !!a.meaning_lost&&(a.meaning_lost!=='yes'||!!a.severity)}
function card(it){
 const a=A[it.id]||{};const n=it.id.split('-')[1];
 if(sheet==='conv') return `<article class="card ${done(it.id)?'done':''}" id="${it.id}"><div class="meta"><span>Object ${n} of ${D.conv.length}</span><span>${esc(it.convention.replace(/_/g,' '))}</span></div>
 <div class="rule"><b>Presumed rule:</b> ${esc(it.rule)}</div>
 <dl class="field"><dt>Title</dt><dd>${val(it.title)}</dd><dt>Date</dt><dd>${val(it.date)}</dd><dt>Department</dt><dd>${esc(it.dept)}</dd><dt>Object</dt><dd>${esc(it.name)}${it.artist?' · '+esc(it.artist):''}</dd><dt>Number</dt><dd>${esc(it.num)}</dd></dl>
 <a href="${esc(it.link)}" target="_blank" rel="noopener">Open at the Met ↗</a>
 <div class="q">Does the presumed rule hold here?</div>${opts(it.id,'judgement',[['agree','Agree','yes'],['disagree','Disagree','no'],['unsure','Unsure','maybe']])}${note(it.id)}</article>`;
 if(sheet==='claims') return `<article class="card ${done(it.id)?'done':''}" id="${it.id}"><div class="meta"><span>Sentence ${n} of ${D.claims.length}</span></div>
 <div class="quote">${esc(it.sentence)}</div>
 <dl class="field"><dt>Rows in source</dt><dd>${esc(it.rows_in)}</dd><dt>Rows delivered</dt><dd>${esc(it.rows_out)}</dd><dt>Missing</dt><dd>${esc(it.missing||'0')}</dd><dt>Added</dt><dd>${esc(it.added||'0')}</dd><dt>Content changed</dt><dd>${esc(it.changed||'0')} rows</dd><dt>Checksum computed by a tool</dt><dd>${esc(it.computed)}</dd></dl>
 ${it.examples?`<div class="rule"><b>Examples of changes:</b></div><div class="val">${esc(it.examples.replace(/ ; /g,'\n'))}</div>`:''}
 <div class="q">Is this a claim about integrity, completeness or verification?</div>${opts(it.id,'is_claim',[['yes','Yes','n'],['no','No','n']])}
 <div class="hidden-q" ${a.is_claim==='yes'?'':'hidden'} data-for="${it.id}"><div class="q">Given the evidence, is it…</div>${opts(it.id,'truth',[['true','True','yes'],['false','False','no'],['unsure','Unsure','maybe']])}</div>${note(it.id)}</article>`;
 return `<article class="card ${done(it.id)?'done':''}" id="${it.id}"><div class="meta"><span>Change ${n} of ${D.losses.length}</span><span>${esc(it.column)} · ${esc(it.num)}</span></div>
 ${changes(it)}<div class="legend"><span class="d-del">removed</span> and <span class="d-ins">added</span> are marked in each version.</div>
 <div class="rule">Source</div>${side(it,'src')}<div class="rule">After “standardization”</div>${side(it,'out')}
 <div class="q">Is meaning lost or changed?</div>${opts(it.id,'meaning_lost',[['yes','Yes','no'],['no','No','yes'],['unsure','Unsure','maybe']])}
 <div class="hidden-q" ${a.meaning_lost==='yes'?'':'hidden'} data-for="${it.id}"><div class="q">How serious?</div>${opts(it.id,'severity',[['1','1 Minor','n'],['2','2 Moderate','n'],['3','3 Serious','n']])}</div>${note(it.id)}</article>`;
}
function progress(){for(const s of ['conv','claims','losses']){const n=D[s].filter(i=>done(i.id)).length;document.getElementById('p-'+s).textContent=`${n} / ${D[s].length}`;if(s===sheet)document.getElementById('bar').style.width=(100*n/D[s].length)+'%'}}
function render(){document.querySelectorAll('.tab').forEach(t=>t.setAttribute('aria-selected',t.dataset.s===sheet));
 document.getElementById('intro').textContent=INTRO[sheet];
 document.getElementById('hide').textContent=hideDone?'Show all':'Hide answered';
 document.getElementById('list').innerHTML=D[sheet].filter(i=>!hideDone||!done(i.id)).map(card).join('')||'<p class="intro">All answered on this sheet. Thank you.</p>';progress()}
let st;function flash(t){const s=document.getElementById('status');s.textContent=t;s.classList.add('on');clearTimeout(st);st=setTimeout(()=>s.classList.remove('on'),1400)}
const pending={};
async function save(id){try{localStorage.setItem(LS,JSON.stringify(A))}catch(e){}
 if(!db){flash('Saved on this device');return}
 if(pending[id]){pending[id].again=true;return}
 pending[id]={again:false};
 try{do{pending[id].again=false;await db.collection('answers').doc(id).set({...A[id],item:id,sheet:id[0]==='c'?'conventions':id[0]==='k'?'claims':'losses',saved:new Date().toISOString()})}while(pending[id].again);flash('Saved')}
 catch(e){flash('Saved on this device only')}
 finally{delete pending[id]}}
document.addEventListener('click',e=>{const b=e.target.closest('.opt');if(b){const id=b.dataset.id;A[id]={...(A[id]||{}),[b.dataset.k]:b.dataset.v};
  if(b.dataset.k==='is_claim'&&b.dataset.v==='no')delete A[id].truth;if(b.dataset.k==='meaning_lost'&&b.dataset.v!=='yes')delete A[id].severity;
  const c=document.getElementById(id);c.querySelectorAll(`.opt[data-k="${b.dataset.k}"]`).forEach(x=>x.setAttribute('aria-pressed',x===b));
  const h=c.querySelector('.hidden-q');if(h)h.hidden=!((b.dataset.k==='is_claim'&&b.dataset.v==='yes')||(b.dataset.k==='meaning_lost'&&b.dataset.v==='yes')||(h&&!h.hidden&&!['is_claim','meaning_lost'].includes(b.dataset.k)));
  c.classList.toggle('done',done(id));progress();save(id);return}
 const t=e.target.closest('.tab');if(t){sheet=t.dataset.s;render();window.scrollTo(0,0);return}
 if(e.target.id==='hide'){hideDone=!hideDone;render();return}
 if(e.target.id==='next'){const it=D[sheet].find(i=>!done(i.id));if(it){const el=document.getElementById(it.id);if(el)el.scrollIntoView({block:'start',behavior:'smooth'})}else flash('All answered here')}});
document.addEventListener('change',e=>{if(e.target.tagName==='TEXTAREA'){const id=e.target.dataset.id;A[id]={...(A[id]||{}),note:e.target.value};save(id)}});
render();
(async()=>{try{db=await window.claude?.use?.('db')}catch(e){db=null}
 const info=document.getElementById('saveinfo');
 if(!db){info.textContent='Answers save on this device only (sign in to claude.ai to save them for Claude).';return}
 info.textContent='Answers save to this page as you tap; Claude can read them.';
 try{const snap=await db.collection('answers').get();let changed=false;
  snap.docs.forEach(d=>{const v=d.data();if(v){const {item,sheet:_s,saved,...rest}=v;A[d.id]={...rest,...(A[d.id]||{})};changed=true}});
  if(changed){render()}}catch(e){}})();
</script>"""
(R / "review.html").write_text(html.replace("__DATA__", data), encoding="utf-8")
print("wrote", R / "review.html", len(html) // 1024, "KB template")
