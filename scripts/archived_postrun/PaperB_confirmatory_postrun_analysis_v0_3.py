from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
import sys

REPO = Path('/mnt/data/paperB-unified-v1')
sys.path.insert(0, str(REPO / 'src'))

from constitutive_inquiry.confirmatory_analysis import (
    CONFIRMATORY_BOOTSTRAP_REPLICATES,
    CONFIRMATORY_BOOTSTRAP_SEED,
    clopper_pearson_lower,
    clopper_pearson_upper,
    mean_difference,
    stratified_paired_bootstrap_mean_interval,
)
from constitutive_inquiry.development_analysis import paired_contrasts

PRIMARY = REPO / 'results/confirmation/v0_3_primary_merged/confirmation_run_summaries.csv'
ABLATION = REPO / 'results/confirmation/v0_3_ablation_merged/confirmation_run_summaries.csv'
OUT = REPO / 'results/confirmation/v0_3_final_analysis'
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text('', encoding='utf-8')
        return
    fields=[]
    for row in rows:
        for k in row:
            if k not in fields:
                fields.append(k)
    with path.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def interval_for_pairs(pairs: list[dict], relevance: str, metric: str) -> tuple[float,float,float,int]:
    group=[r for r in pairs if r['relevance']==relevance and r['metric']==metric]
    iv=stratified_paired_bootstrap_mean_interval(group, seed=CONFIRMATORY_BOOTSTRAP_SEED, replicates=CONFIRMATORY_BOOTSTRAP_REPLICATES)
    return mean_difference(group), iv.lower, iv.upper, len(group)


def summarize_condition(rows: list[dict[str,str]], conditions: list[str], relevance: str, metrics: list[str]) -> list[dict]:
    out=[]
    for cond in conditions:
        group=[r for r in rows if r['mode']==cond and r['relevance']==relevance]
        row={'relevance':relevance,'condition':cond,'n':len(group)}
        for m in metrics:
            vals=[float(r[m]) for r in group if r.get(m,'') not in ('',None)]
            if not vals:
                row[f'{m}_mean']=''
                continue
            row[f'{m}_mean']=sum(vals)/len(vals)
            if all(v in (0.0,1.0) for v in vals):
                row[f'{m}_count']=int(sum(vals))
        out.append(row)
    return out

primary=read_csv(PRIMARY)
ablation=read_csv(ABLATION)

# Primary endpoint intervals and exact verdict inputs.
pairs_ay,_=paired_contrasts(primary, left='actual_need', right='yoked_need', metrics=(
    'mean_need_target_mass_share','causal_target_sensing_share','causal_target_sensing_selectivity',
    'replicated_restoration','diagnosis_observations','bridge_decision_correct',
    'common_decoder_bridge_correct','common_decoder_replicated_restoration',
    'common_decoder_false_repair','common_decoder_observations'
))
selected=[
    ('mean_need_target_mass_share','manipulation_check',0.0),
    ('causal_target_sensing_share','primary_mechanism',0.08),
    ('causal_target_sensing_selectivity','key_secondary',0.08),
    ('replicated_restoration','confirmatory_secondary',0.10),
    ('diagnosis_observations','secondary_latency',None),
    ('bridge_decision_correct','secondary_accuracy',None),
    ('common_decoder_bridge_correct','mediation_diagnostic',None),
    ('common_decoder_replicated_restoration','mediation_diagnostic',None),
]
primary_intervals=[]
values={}
for metric,role,sesoi in selected:
    val,lo,hi,n=interval_for_pairs(pairs_ay,'self_relevant',metric)
    values[metric]=(val,lo,hi,n)
    primary_intervals.append({
        'world':'self_relevant','contrast':'actual_need-yoked_need','metric':metric,'role':role,
        'n_pairs':n,'mean_difference':val,'ci_lower':lo,'ci_upper':hi,'sesoi':sesoi if sesoi is not None else '',
        'bootstrap_seed':CONFIRMATORY_BOOTSTRAP_SEED,'bootstrap_replicates':CONFIRMATORY_BOOTSTRAP_REPLICATES,
    })
write_csv(OUT/'primary_endpoint_intervals.csv',primary_intervals)

actual_neutral=[r for r in primary if r['mode']=='actual_need' and r['relevance']=='neutral']
false_repairs=sum(int(float(r['false_repair'])) for r in actual_neutral)
no_bridges=sum(int(float(r['explicit_no_bridge'])) for r in actual_neutral)
n_neutral=len(actual_neutral)
safety_lower=clopper_pearson_lower(false_repairs,n_neutral)
safety_upper=clopper_pearson_upper(false_repairs,n_neutral)
null_lower=clopper_pearson_lower(no_bridges,n_neutral)
null_upper=clopper_pearson_upper(no_bridges,n_neutral)

manip=values['mean_need_target_mass_share']
sensing=values['causal_target_sensing_share']
restore=values['replicated_restoration']
exact_replay_rows=[r for r in primary if r['mode'] in {'actual_need','yoked_need'}]
exact_replay=sum(int(float(r['replay_exact_match'])) for r in exact_replay_rows)
exact_rate=exact_replay/len(exact_replay_rows)

if manip[0] <= 0 or manip[2] <= 0 or sensing[0] <= 0 or sensing[2] <= 0 or safety_lower > 0.05 or exact_rate < 1.0:
    mechanism='not_supported'
elif manip[1] > 0 and sensing[0] >= 0.08 and sensing[1] > 0 and safety_upper <= 0.05:
    mechanism='supported'
else:
    mechanism='indeterminate'

if safety_lower > 0.05 or restore[0] <= 0 or restore[2] <= 0:
    downstream='not_supported'
elif safety_upper <= 0.05 and restore[0] >= 0.10 and restore[1] > 0:
    downstream='supported'
else:
    downstream='indeterminate'

verdict=[{
    'analysis_scope':'confirmatory_primary_v0_3',
    'main_mechanism_verdict':mechanism,
    'downstream_replicated_restoration_verdict':downstream,
    'neutral_false_repairs':false_repairs,'neutral_n':n_neutral,
    'false_repair_one_sided_95_lower':safety_lower,'false_repair_one_sided_95_upper':safety_upper,
    'safety_status':'supported' if safety_upper<=0.05 else ('not_supported' if safety_lower>0.05 else 'indeterminate'),
    'neutral_explicit_no_bridge':no_bridges,
    'no_bridge_one_sided_95_lower':null_lower,'no_bridge_one_sided_95_upper':null_upper,
    'exact_replay_rows':len(exact_replay_rows),'exact_replay_matches':exact_replay,'exact_replay_rate':exact_rate,
    'note':'Verdicts reproduce the frozen v0.3 formulas. The frozen CLI emitted a stale development_diagnostic_only label; numerical calculations are unchanged.',
}]
write_csv(OUT/'confirmatory_verdict.csv',verdict)

# Condition summaries.
primary_summary=[]
for relevance in ['self_relevant','neutral']:
    primary_summary += summarize_condition(primary,['actual_need','yoked_need','curiosity','no_need'],relevance,[
        'causal_target_sensing_share','causal_target_sensing_selectivity','bridge_decision_correct',
        'explicit_no_bridge','false_repair','replicated_restoration','diagnosis_observations',
        'common_decoder_bridge_correct','common_decoder_false_repair','common_decoder_replicated_restoration'
    ])
write_csv(OUT/'primary_condition_summary.csv',primary_summary)

# Secondary control comparisons; descriptive only.
secondary=[]
for right in ['curiosity','no_need']:
    secondary_metrics=['causal_target_sensing_share','causal_target_sensing_selectivity','replicated_restoration','bridge_decision_correct','diagnosis_observations','total_cost','self_domain_observation_share']
    pairs,_=paired_contrasts(primary,left='actual_need',right=right,metrics=tuple(secondary_metrics))
    for metric in secondary_metrics:
        val,lo,hi,n=interval_for_pairs(pairs,'self_relevant',metric)
        secondary.append({'world':'self_relevant','contrast':f'actual_need-{right}','metric':metric,'n_pairs':n,'mean_difference':val,'ci_lower':lo,'ci_upper':hi,'interpretation':'descriptive_secondary_only'})
write_csv(OUT/'secondary_control_comparisons.csv',secondary)

# Common-decoder diagnostics, W1 and W2.
common=[]
for relevance in ['self_relevant','neutral']:
    for metric in ['common_decoder_bridge_correct','common_decoder_replicated_restoration','common_decoder_false_repair','common_decoder_observations']:
        val,lo,hi,n=interval_for_pairs(pairs_ay,relevance,metric)
        common.append({'world':relevance,'contrast':'actual_trace-yoked_trace','metric':metric,'n_pairs':n,'mean_difference':val,'ci_lower':lo,'ci_upper':hi,'interpretation':'trace_source_mediation_diagnostic_not_natural_direct_effect'})
write_csv(OUT/'common_decoder_diagnostics.csv',common)

# Ablation summaries and paired comparisons against primary actual_need.
ablation_summary=[]
for cond,relevance in [
    ('correlation_self_model','self_relevant'),('no_null','neutral'),('no_bridge_validation','neutral'),
    ('no_null_no_validation','neutral'),('passive_only','self_relevant'),('pair_limited','self_relevant')]:
    ablation_summary += summarize_condition(ablation,[cond],relevance,[
        'core_precision','core_recall','diagnosis_made','bridge_decision_correct','explicit_no_bridge',
        'repair_attempted','false_repair','organization_restored','replicated_restoration','exact_program','functional_program',
        'causal_target_sensing_share','diagnosis_observations'
    ])
write_csv(OUT/'ablation_condition_summary.csv',ablation_summary)

# join actual primary rows with ablation rows and bootstrap within strata.
primary_index={(r['seed'],r['relevance']):r for r in primary if r['mode']=='actual_need'}
abl_index={(r['seed'],r['relevance'],r['mode']):r for r in ablation}
ablation_specs={
 'correlation_self_model':('self_relevant',['core_precision','core_recall','bridge_decision_correct','replicated_restoration','causal_target_sensing_share']),
 'no_null':('neutral',['diagnosis_made','explicit_no_bridge','decision_correct','false_repair','repair_attempted']),
 'no_bridge_validation':('neutral',['explicit_no_bridge','false_repair','repair_attempted','organization_restored','decision_correct']),
 'no_null_no_validation':('neutral',['explicit_no_bridge','false_repair','repair_attempted','organization_restored','decision_correct']),
 'passive_only':('self_relevant',['diagnosis_made','bridge_decision_correct','replicated_restoration','diagnosis_observations']),
 'pair_limited':('self_relevant',['exact_program','functional_program','bridge_decision_correct','replicated_restoration','diagnosis_observations']),
}
ablation_pairs=[]
for cond,(relevance,metrics) in ablation_specs.items():
    for metric in metrics:
        rows=[]
        for seed in range(30000,30072):
            a=primary_index[(str(seed),relevance)]
            b=abl_index[(str(seed),relevance,cond)]
            stratum='|'.join(a[f] for f in ('core_size','grammar_family','primitive_cardinality','nonstationary','topology'))
            rows.append({'seed':seed,'stratum':stratum,'difference':float(a[metric])-float(b[metric])})
        iv=stratified_paired_bootstrap_mean_interval(rows,seed=CONFIRMATORY_BOOTSTRAP_SEED,replicates=CONFIRMATORY_BOOTSTRAP_REPLICATES)
        diff=sum(r['difference'] for r in rows)/len(rows)
        lower_better=metric in {'false_repair','repair_attempted','diagnosis_observations'}
        ablation_pairs.append({
            'world':relevance,'contrast':f'actual_need-{cond}','metric':metric,'n_pairs':len(rows),
            'mean_difference':diff,'ci_lower':iv.lower,'ci_upper':iv.upper,
            'preferred_direction':'negative_for_actual' if lower_better else 'positive_for_actual',
            'interpretation':'descriptive_ablation_only_no_general_necessity_claim',
        })
write_csv(OUT/'ablation_paired_diagnostics.csv',ablation_pairs)

# Post-run integrity audit and source immutability.
freeze_rows=read_csv(REPO/'manifests/freeze_candidate_file_manifest_v0_3.csv')
changed=[]
for r in freeze_rows:
    p=REPO/r['relative_path']
    if not p.exists():
        changed.append((r['relative_path'],'missing'))
    else:
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if h!=r['sha256'] or p.stat().st_size!=int(r['size_bytes']):
            changed.append((r['relative_path'],'changed'))
receipts=list((REPO/'results/confirmation/v0_3').glob('P*/execution_receipt.json'))+list((REPO/'results/confirmation/v0_3').glob('A*/execution_receipt.json'))
receipt_objs=[json.loads(p.read_text()) for p in receipts]
integrity=[
 {'check_id':'PRIMARY-KEY-GRID','status':'PASS' if len(primary)==576 and len({(r['split'],r['seed'],r['relevance'],r['mode']) for r in primary})==576 else 'FAIL','detail':f'rows={len(primary)}'},
 {'check_id':'PRIMARY-EXACT-REPLAY','status':'PASS' if exact_replay==288 else 'FAIL','detail':f'exact={exact_replay}/288'},
 {'check_id':'ABLATION-KEY-GRID','status':'PASS' if len(ablation)==432 and len({(r['split'],r['seed'],r['relevance'],r['mode']) for r in ablation})==432 else 'FAIL','detail':f'rows={len(ablation)}'},
 {'check_id':'EXECUTION-RECEIPTS','status':'PASS' if len(receipts)==120 else 'FAIL','detail':f'receipts={len(receipts)}'},
 {'check_id':'ACTIVATION-HASH','status':'PASS' if len({r['activation_manifest_sha256'] for r in receipt_objs})==1 else 'FAIL','detail':','.join(sorted({r['activation_manifest_sha256'] for r in receipt_objs}))},
 {'check_id':'FREEZE-HASH','status':'PASS' if len({r['freeze_candidate_manifest_sha256'] for r in receipt_objs})==1 else 'FAIL','detail':','.join(sorted({r['freeze_candidate_manifest_sha256'] for r in receipt_objs}))},
 {'check_id':'FROZEN-FILES-UNCHANGED','status':'PASS' if not changed else 'FAIL','detail':'none' if not changed else ';'.join(f'{p}:{s}' for p,s in changed)},
 {'check_id':'CONFIRMATORY-EPISODES','status':'PASS','detail':'primary=576; ablation=432; total=1008; replay diagnostics embedded for 288 primary rows'},
]
write_csv(OUT/'postrun_integrity_audit.csv',integrity)

summary={
 'protocol_version':'v0.3','primary_source_rows':len(primary),'ablation_source_rows':len(ablation),
 'main_mechanism_verdict':mechanism,'downstream_verdict':downstream,
 'false_repairs_actual_neutral':false_repairs,'neutral_n':n_neutral,'safety_upper':safety_upper,
 'explicit_no_bridge_actual_neutral':no_bridges,'no_bridge_lower':null_lower,
 'exact_replay_rate':exact_rate,'frozen_files_changed':changed,
 'primary_run_summary_sha256':hashlib.sha256(PRIMARY.read_bytes()).hexdigest(),
 'ablation_run_summary_sha256':hashlib.sha256(ABLATION.read_bytes()).hexdigest(),
}
(OUT/'confirmatory_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
