#!/usr/bin/env python3
"""Build a self-contained curator handoff from the proposed cleanup plan."""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / 'skills/curate-tcia-wordpress-metadata/references/external-resource-cleanup-plan-2026-10-16.json'
OUTPUT = ROOT / 'docs/curation/external-resource-cleanup/index.html'


def esc(value):
    return html.escape(str(value), quote=True)


def links(records):
    return ', '.join(f'<a href="{esc(r["url"])}">{esc(r["short_title"])}</a>' for r in records) or 'No visible public use'


def build():
    plan = json.loads(PLAN.read_text())
    assert len(plan['crosswalk']) == plan['summary']['registered_labels']
    assert len(plan['assignments']) == plan['summary']['legacy_assignments_to_review']
    canonical = ''.join(f'<tr><th scope="row">{esc(r["label"])}</th><td>{esc(r["meaning"])}</td></tr>' for r in plan['canonical_categories'])
    steps = ''.join(f'<li>{esc(s)}</li>' for s in plan['workflow'])
    crosswalk = ''.join(f'<tr><th scope="row">{esc(r["old_label"])}</th><td>{r["public_dataset_count"]}</td><td>{esc(" + ".join(r["proposed_labels"]) or "Leave empty / retire placeholder")}</td><td>{esc(r["action"])}<p>{esc(r["instructions"])}</p></td><td>{links(r["affected_datasets"])}</td></tr>' for r in plan['crosswalk'])
    assignments = ''.join(f'<tr data-review="{str(r["status"] == "needs curator decision").lower()}"><th scope="row"><a href="{esc(r["dataset_url"])}">{esc(r["dataset"])}</a><small>{esc(r["dataset_type"])}</small></th><td>{esc(r["old_label"])}</td><td>{esc(" + ".join(r["proposed_labels"]))}</td><td>{esc(r["status"])}<p>{esc(r["instructions"])}</p></td></tr>' for r in plan['assignments'])
    limits = ''.join(f'<li>{esc(s)}</li>' for s in plan['limitations'])
    sources = ''.join(f'<li><a href="{esc(r["url"])}">{esc(r["endpoint"])} page {r["page"]}</a> — {esc(r["retrieved_at_utc"])}<small>SHA-256: {esc(r["sha256"])}</small></li>' for r in plan['sources'])
    logo = base64.b64encode((ROOT/'skills/curate-tcia-wordpress-metadata/assets/tcia-logo-light.svg').read_bytes()).decode()
    embedded = json.dumps(plan,ensure_ascii=False).replace('</','<\\/')
    body = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TCIA external resource label cleanup</title><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%23042b5b'/%3E%3Ccircle cx='16' cy='16' r='8' fill='none' stroke='%235bc6ff' stroke-width='3'/%3E%3C/svg%3E">
<style>
:root{--navy:#042b5b;--blue:#155c9d;--line:#d5dfeb}*{box-sizing:border-box}body{margin:0;background:#f4f7fb;color:#222;font:16px/1.55 system-ui,sans-serif}a{color:var(--blue);text-underline-offset:3px}header{background:var(--navy);color:white;padding:28px max(24px,calc((100% - 1220px)/2))}header img{width:220px;height:auto}header a{color:#caeaff}h1{font-size:clamp(28px,4vw,42px);line-height:1.15;margin:24px 0 12px}main{max-width:1268px;margin:auto;padding:24px}h2{color:var(--navy);margin-top:36px}h3{color:var(--navy)}.notice{padding:18px;border:1px solid #d9a62d;background:#fff8e3;border-radius:8px}.stats{font-weight:700;color:var(--navy)}.actions{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}button{padding:12px 16px;border:1px solid var(--navy);border-radius:6px;color:white;background:var(--navy);font:inherit;cursor:pointer}:focus-visible{outline:3px solid #8d44ce;outline-offset:3px}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:8px;background:white}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid var(--line);overflow-wrap:anywhere}thead th{background:#eaf3fc;color:var(--navy)}tbody th{min-width:155px;color:var(--navy)}td p{margin:8px 0 0}small{display:block;font-size:12px;font-weight:400;color:#555;overflow-wrap:anywhere}li{margin:10px 0}.canonical{max-width:950px}code{font-family:ui-monospace,monospace}.filter{display:block;margin:16px 0}.filter input{width:18px;height:18px;vertical-align:middle}footer{margin-top:36px;color:#666;font-size:13px}@media(max-width:600px){main{padding:14px}header{padding:22px 14px}.table-wrap table{min-width:760px}.canonical table{min-width:550px}}@media print{body{background:white;font-size:10pt}header{padding:12px;background:white;color:#222}header img,.actions,.filter,nav{display:none}.table-wrap{overflow:visible;border:0}table{font-size:9pt}thead{display:table-header-group}tr{break-inside:avoid}h2{break-after:avoid}a{color:#222;text-decoration:none}.notice{border:1px solid #aaa}}
</style></head><body><header><img alt="The Cancer Imaging Archive" src="data:image/svg+xml;base64,__LOGO__"><h1>External resource label cleanup</h1><p>Curator handoff • reviewed October 16, 2026</p><nav><a href="../../labels/">Open the label catalog</a></nav></header><main>
<p class="notice"><strong>Proposal for review.</strong> No WordPress edits have been applied. The worklist recommends replacements using existing labels. The resource-link/content checks below remain part of the curator's work.</p>
<p class="stats">34 registered labels → 6 proposed broad categories · 47 legacy assignments across 34 datasets · 7 options with no visible public use</p>
<p>Scope: the WordPress <code>external_resources</code> field and its <code>/api/v2/supporting-data</code> registry. The normalized query API also calls the array <code>external_resource_labels</code>. This is separate from download category, data type, and file type.</p>
<div class="actions"><button id="worklist-export" type="button">Download curator worklist (.csv)</button><button id="crosswalk-export" type="button">Download full crosswalk (.csv)</button></div>
<h2>Use these six existing labels</h2><p>Keep the detailed organ, method, assay, format, and measurement wording in each resource's title or description. Multiple categories are appropriate only when the linked resources support each one.</p><div class="table-wrap canonical"><table><thead><tr><th>Proposed label</th><th>Meaning for this cleanup</th></tr></thead><tbody>__CANONICAL__</tbody></table></div>
<h2>Instructions for curators</h2><ol>__STEPS__</ol>
<h2>Dataset worklist</h2><p>41 assignments have straightforward broad-category recommendations. Six assignments need a content-dependent choice. Even straightforward replacements require confirming the current link and preserving its description.</p><label class="filter"><input id="review-only" type="checkbox"> Show only content-dependent choices</label><div class="table-wrap"><table><thead><tr><th>Dataset</th><th>Current label</th><th>Proposed label(s)</th><th>Decision and instructions</th></tr></thead><tbody id="assignments">__ASSIGNMENTS__</tbody></table></div>
<h2>Complete 34-label crosswalk</h2><p>Zero means no visible public dataset uses the exact label at this review date. Check hidden/unpublished references in WordPress before retiring an option.</p><div class="table-wrap"><table><thead><tr><th>Current label</th><th>Public datasets</th><th>Proposed label(s)</th><th>Action and instructions</th><th>Affected datasets</th></tr></thead><tbody>__CROSSWALK__</tbody></table></div>
<h2>Species references</h2><p>Human: <a href="https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C14225">C14225</a>; Mouse: <a href="https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C14238">C14238</a>; Canine (Dog): <a href="https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C14201">C14201</a>. All verified active in NCIt 26.09d on October 16.</p><p>Physical Phantom can use the broader Imaging Phantom reference <a href="https://evsexplore.semantics.cancer.gov/evsexplore/concept/ncit/C17892">C17892</a>. No faithful NCIt mapping for Computational Phantom was verified; retain it as an unlinked TCIA classification. Phantom classifications are not biological species. The generic Phantom option was absent from the current public species registry.</p>
<h2>Evidence and limits</h2><ul>__LIMITS__</ul><details><summary>Public source responses and hashes</summary><ul>__SOURCES__</ul></details><footer>Official TCIA logo and palette retained from the curator catalog. Layout and category recommendations are implementation/curation proposals.</footer></main>
<script id="plan-data" type="application/json">__PLAN__</script><script>
const plan=JSON.parse(document.getElementById('plan-data').textContent);
document.getElementById('review-only').addEventListener('change',event=>{document.querySelectorAll('#assignments tr').forEach(row=>row.hidden=event.target.checked&&row.dataset.review!=='true');});
function cell(value){let text=String(value??'');if(/^[\\s\\uFEFF]*[=+@-]/.test(text))text="'"+text;return '"'+text.replace(/"/g,'""')+'"';}
function download(name,rows){const csv='\\uFEFF'+rows.map(row=>row.map(cell).join(',')).join('\\r\\n')+'\\r\\n';const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
document.getElementById('worklist-export').addEventListener('click',()=>download('tcia-external-resource-curator-worklist.csv',[['Dataset','Dataset type','Dataset URL','Current label','Proposed labels','Decision status','Instructions'],...plan.assignments.map(r=>[r.dataset,r.dataset_type,r.dataset_url,r.old_label,r.proposed_labels.join(' | '),r.status,r.instructions])]));
document.getElementById('crosswalk-export').addEventListener('click',()=>download('tcia-external-resource-crosswalk.csv',[['Current label','WordPress option ID','Public dataset count','Proposed labels','Decision status','Action','Instructions','Dataset names','Dataset URLs'],...plan.crosswalk.map(r=>[r.old_label,r.wordpress_option_id,r.public_dataset_count,r.proposed_labels.join(' | '),r.status,r.action,r.instructions,r.affected_datasets.map(d=>d.short_title).join(' | '),r.affected_datasets.map(d=>d.url).join(' | ')])]));
</script></body></html>'''
    for token,value in {'__LOGO__':logo,'__CANONICAL__':canonical,'__STEPS__':steps,'__ASSIGNMENTS__':assignments,'__CROSSWALK__':crosswalk,'__LIMITS__':limits,'__SOURCES__':sources,'__PLAN__':embedded}.items():
        assert body.count(token)==1
        body=body.replace(token,value)
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(body)
    print(f'Wrote {OUTPUT}')


if __name__=='__main__':
    build()
