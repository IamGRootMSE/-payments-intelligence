let DATA = [];
let DIAG;
let dims;
const state={filters:{country:'All',merchant_segment:'All',device:'All',payment_method:'All'}};
const $=s=>document.querySelector(s);
const fmtMoney=n=>n>=1e6?'$'+(n/1e6).toFixed(2)+'M':n>=1e3?'$'+(n/1e3).toFixed(1)+'K':'$'+n.toFixed(0);
const fmtPct=n=>(n*100).toFixed(1)+'%'; const fmtBps=n=>(n>0?'+':'')+Math.round(n)+' bps';

function setupFilters(){
  const cfg=[['countryFilter','country'],['segmentFilter','merchant_segment'],['deviceFilter','device'],['methodFilter','payment_method']];
  cfg.forEach(([id,key])=>{const el=$('#'+id);['All',...dims[key]].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;el.appendChild(o)});el.addEventListener('change',()=>{state.filters[key]=el.value;render()})});
  $('#resetFilters').addEventListener('click',()=>{cfg.forEach(([id,key])=>{$('#'+id).value='All';state.filters[key]='All'});render()});
}
function filtered(){return DATA.filter(r=>Object.entries(state.filters).every(([k,v])=>v==='All'||r[k]===v))}
function monthly(){const m={};filtered().forEach(r=>{if(!m[r.month])m[r.month]={month:r.month,attempts:0,successes:0,attempted_volume_usd:0,successful_amount_usd:0,refunds:0,disputes:0,platform_revenue_usd:0};const x=m[r.month];Object.keys(x).filter(k=>k!=='month').forEach(k=>x[k]+=r[k])});return Object.values(m).sort((a,b)=>a.month.localeCompare(b.month)).map(x=>({...x,success_rate:x.successes/x.attempts,refund_rate:x.refunds/Math.max(x.successes,1),dispute_rate:x.disputes/Math.max(x.successes,1)}))}
function total(rows){const t={attempts:0,successes:0,attempted_volume_usd:0,successful_amount_usd:0,refunds:0,disputes:0,platform_revenue_usd:0};rows.forEach(r=>Object.keys(t).forEach(k=>t[k]+=r[k]));return {...t,success_rate:t.successes/t.attempts,refund_rate:t.refunds/t.successes,dispute_rate:t.disputes/t.successes}}
function render(){const rows=monthly(),t=total(rows),latest=rows.at(-1),prev=rows.at(-2);const kpis=[['Successful volume',fmtMoney(t.successful_amount_usd),'Selected period'],['Success rate',fmtPct(t.success_rate),`${Math.round(t.successes).toLocaleString()} successful attempts`],['Platform revenue',fmtMoney(t.platform_revenue_usd),'Fictional 1.9% assumption'],['Refund rate',fmtPct(t.refund_rate),'Of successful payments'],['Dispute rate',fmtPct(t.dispute_rate),'Of successful payments']];$('#kpiGrid').innerHTML=kpis.map(([a,b,c])=>`<div class="kpi"><span>${a}</span><strong>${b}</strong><small>${c}</small></div>`).join('');if(latest&&prev){const bps=(latest.success_rate-prev.success_rate)*10000;$('#trendDelta').textContent=`${fmtBps(bps)} vs prior month`;$('#trendDelta').className='delta '+(bps<0?'negative':'positive')}drawLine('#successChart',rows.map(x=>({label:x.month.slice(5),value:x.success_rate*100})),v=>v.toFixed(1)+'%');drawLine('#volumeChart',rows.map(x=>({label:x.month.slice(5),value:x.successful_amount_usd})),fmtMoney)}
function drawLine(sel,pts,formatter){const el=$(sel);const W=620,H=220,p={l:48,r:16,t:18,b:34};const vals=pts.map(x=>x.value),min=Math.min(...vals),max=Math.max(...vals),pad=(max-min||1)*.18,lo=min-pad,hi=max+pad;const x=i=>p.l+i*(W-p.l-p.r)/Math.max(pts.length-1,1),y=v=>p.t+(hi-v)*(H-p.t-p.b)/(hi-lo),path=pts.map((d,i)=>(i?'L':'M')+x(i).toFixed(1)+','+y(d.value).toFixed(1)).join(' '),ticks=[0,.5,1].map(q=>lo+(hi-lo)*q);el.innerHTML=`<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><defs><linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#635bff" stop-opacity=".18"/><stop offset="100%" stop-color="#635bff" stop-opacity="0"/></linearGradient></defs>${ticks.map(v=>`<line class="gridline" x1="${p.l}" x2="${W-p.r}" y1="${y(v)}" y2="${y(v)}"/><text class="axis-label" x="0" y="${y(v)+3}">${formatter(v)}</text>`).join('')}<path class="chart-area" d="${path} L ${x(pts.length-1)},${H-p.b} L ${x(0)},${H-p.b} Z"/><path class="chart-line" d="${path}"/>${pts.map((d,i)=>`<circle class="chart-dot" cx="${x(i)}" cy="${y(d.value)}" r="4"/><text class="axis-label" x="${x(i)-7}" y="${H-10}">${d.label}</text>`).join('')}</svg>`}
function renderDiagnosis(){const d=DIAG;$('#findingTitle').textContent=`${d.focus} deteriorated from June onward.`;$('#findingBody').textContent=`The event-level Python build shows success falling from ${fmtPct(d.baseline_success_rate)} to ${fmtPct(d.incident_success_rate)} across ${d.incident_attempts.toLocaleString()} incident-period attempts.`;$('#diagBps').textContent=fmtBps(d.delta_bps);$('#diagVolume').textContent=fmtMoney(d.estimated_recoverable_successful_volume_usd);$('#issuerBaseline').textContent=fmtPct(d.issuer_decline_share_baseline);$('#issuerIncident').textContent=fmtPct(d.issuer_decline_share_incident);$('#barBaseline').style.width=(d.issuer_decline_share_baseline*100)+'%';$('#barIncident').style.width=(d.issuer_decline_share_incident*100)+'%'}
async function initialize() {
  try {
    const response = await fetch('data.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    DATA = payload.monthly;
    DIAG = payload.diagnosis;
    dims = Object.fromEntries(Object.keys(state.filters).map(key =>
      [key, [...new Set(DATA.map(row => row[key]))].sort()]));
    setupFilters();
    render();
    renderDiagnosis();
    $('#dataStatus').hidden = true;
  } catch (error) {
    $('#dataStatus').textContent = 'Dashboard data could not be loaded. Please reload the page or serve the docs folder over HTTP.';
    $('#dataStatus').setAttribute('role', 'alert');
    console.error('Unable to load dashboard data:', error);
  }
}
initialize();
