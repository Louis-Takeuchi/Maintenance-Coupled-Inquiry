from __future__ import annotations
import csv, sys
from pathlib import Path
from multiprocessing import Pool

REPO=Path('/mnt/data/paperB-unified-v1')
sys.path.insert(0,str(REPO/'src'))
from constitutive_inquiry.confirmatory_analysis import stratified_paired_bootstrap_mean_interval, CONFIRMATORY_BOOTSTRAP_SEED, CONFIRMATORY_BOOTSTRAP_REPLICATES


def read_csv(p):
    with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def worker(task):
    cond,relevance,metric,rows=task
    iv=stratified_paired_bootstrap_mean_interval(rows,seed=CONFIRMATORY_BOOTSTRAP_SEED,replicates=CONFIRMATORY_BOOTSTRAP_REPLICATES)
    diff=sum(float(r['difference']) for r in rows)/len(rows)
    lower_better=metric in {'false_repair','repair_attempted','diagnosis_observations'}
    return {
      'world':relevance,'contrast':f'actual_need-{cond}','metric':metric,'n_pairs':len(rows),
      'mean_difference':diff,'ci_lower':iv.lower,'ci_upper':iv.upper,
      'preferred_direction':'negative_for_actual' if lower_better else 'positive_for_actual',
      'interpretation':'descriptive_ablation_only_no_general_necessity_claim',
      'bootstrap_seed':CONFIRMATORY_BOOTSTRAP_SEED,'bootstrap_replicates':CONFIRMATORY_BOOTSTRAP_REPLICATES,
    }

if __name__=='__main__':
    primary=read_csv(REPO/'results/confirmation/v0_3_primary_merged/confirmation_run_summaries.csv')
    ablation=read_csv(REPO/'results/confirmation/v0_3_ablation_merged/confirmation_run_summaries.csv')
    pidx={(r['seed'],r['relevance']):r for r in primary if r['mode']=='actual_need'}
    aidx={(r['seed'],r['relevance'],r['mode']):r for r in ablation}
    specs={
     'correlation_self_model':('self_relevant',['core_precision','core_recall','bridge_decision_correct','replicated_restoration','causal_target_sensing_share']),
     'no_null':('neutral',['diagnosis_made','explicit_no_bridge','decision_correct','false_repair','repair_attempted']),
     'no_bridge_validation':('neutral',['explicit_no_bridge','false_repair','repair_attempted','organization_restored','decision_correct']),
     'no_null_no_validation':('neutral',['explicit_no_bridge','false_repair','repair_attempted','organization_restored','decision_correct']),
     'passive_only':('self_relevant',['diagnosis_made','bridge_decision_correct','replicated_restoration','diagnosis_observations']),
     'pair_limited':('self_relevant',['exact_program','functional_program','bridge_decision_correct','replicated_restoration','diagnosis_observations']),
    }
    tasks=[]
    for cond,(rel,metrics) in specs.items():
      for metric in metrics:
        rows=[]
        for seed in range(30000,30072):
          a=pidx[(str(seed),rel)]; b=aidx[(str(seed),rel,cond)]
          st='|'.join(a[f] for f in ('core_size','grammar_family','primitive_cardinality','nonstationary','topology'))
          rows.append({'seed':seed,'stratum':st,'difference':float(a[metric])-float(b[metric])})
        tasks.append((cond,rel,metric,rows))
    with Pool(processes=5) as pool:
      out=pool.map(worker,tasks)
    out.sort(key=lambda r:(r['contrast'],r['metric']))
    path=REPO/'results/confirmation/v0_3_final_analysis/ablation_paired_diagnostics.csv'
    with open(path,'w',newline='',encoding='utf-8') as f:
      w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    print('wrote',len(out),'rows to',path)
