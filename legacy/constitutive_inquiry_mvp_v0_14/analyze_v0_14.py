from __future__ import annotations

import csv
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'results' / 'confirmation'
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)
DRAWS = 20_000
RNG_SEED = 14_140_014

MODES = [
    'confidence_gated_relational_generation',
    'ungated_relational_generation',
    'reset_actual_generation',
    'sparse_reset_generation',
    'posterior_no_quarantine_generation',
    'quarantine_no_local_reservation_generation',
    'frozen_correct_memory_generation',
    'adversarial_wrong_memory_generation',
    'oracle_family_generation',
    'no_null_confidence_gated_generation',
]


def load() -> pd.DataFrame:
    frames = []
    for mode in MODES:
        path = INPUT / f'{mode}_run_summaries.csv'
        if not path.exists():
            raise FileNotFoundError(path)
        frame = pd.read_csv(path)
        if len(frame) != 80:
            raise ValueError(f'{path}: expected 80 rows, got {len(frame)}')
        frames.append(frame)
    df = pd.concat(frames, ignore_index=True)
    if df.duplicated(['mode', 'seed', 'relevance']).any():
        raise ValueError('duplicate mode-seed-relevance rows')
    expected = set(range(18000, 18040))
    for mode in MODES:
        if set(df.loc[df['mode'] == mode, 'seed']) != expected:
            raise ValueError(f'incomplete seeds for {mode}')
    return df.sort_values(['mode', 'seed', 'relevance']).reset_index(drop=True)


def paired(df: pd.DataFrame, mode_a: str, mode_b: str, relevance: str, metric: str) -> tuple[float, float, float]:
    a = df[(df['mode'] == mode_a) & (df['relevance'] == relevance)].set_index('seed')[metric].sort_index()
    b = df[(df['mode'] == mode_b) & (df['relevance'] == relevance)].set_index('seed')[metric].sort_index()
    common = a.index.intersection(b.index)
    diff = a.loc[common].to_numpy(float) - b.loc[common].to_numpy(float)
    rng = np.random.default_rng(RNG_SEED + sum(map(ord, mode_a + mode_b + metric + relevance)))
    idx = rng.integers(0, len(diff), size=(DRAWS, len(diff)))
    boot = diff[idx].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(diff.mean()), float(lo), float(hi)


def rate_interval(values: np.ndarray) -> tuple[float, float, float]:
    """Wilson 95% score interval, as frozen in the confirmation plan."""
    values = np.asarray(values, dtype=float)
    n = len(values)
    if n == 0:
        return float('nan'), float('nan'), float('nan')
    p = float(values.mean())
    z = 1.959963984540054
    denominator = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denominator
    half = z * ((p * (1.0 - p) / n + z * z / (4.0 * n * n)) ** 0.5) / denominator
    return p, max(0.0, center - half), min(1.0, center + half)


def relative_reduction(df: pd.DataFrame, mode_a: str, mode_b: str) -> tuple[float, float, float]:
    a = df[(df['mode'] == mode_a) & (df['relevance'] == 'self_relevant')].set_index('seed')['unique_sequences_evaluated'].sort_index()
    b = df[(df['mode'] == mode_b) & (df['relevance'] == 'self_relevant')].set_index('seed')['unique_sequences_evaluated'].sort_index()
    common = a.index.intersection(b.index)
    av, bv = a.loc[common].to_numpy(float), b.loc[common].to_numpy(float)
    rng = np.random.default_rng(RNG_SEED + 991)
    idx = rng.integers(0, len(common), size=(DRAWS, len(common)))
    boot = 1.0 - av[idx].mean(axis=1) / bv[idx].mean(axis=1)
    point = 1.0 - av.mean() / bv.mean()
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(point), float(lo), float(hi)


def main() -> None:
    df = load()
    df.to_csv(OUT / 'confirmation_run_summaries.csv', index=False)

    metrics = []
    for mode in MODES:
        for relevance in ('self_relevant', 'neutral'):
            g = df[(df['mode'] == mode) & (df['relevance'] == relevance)]
            metrics.append({
                'mode': mode,
                'relevance': relevance,
                'runs': len(g),
                'organization_restored': g.organization_restored.mean(),
                'false_repair': g.false_repair.mean(),
                'explicit_no_bridge': g.explicit_no_bridge.mean(),
                'unique_sequences_evaluated': g.unique_sequences_evaluated.mean(),
                'memory_proposal_tested': g.memory_proposal_tested.mean(),
                'memory_changed_action': g.memory_changed_action.mean(),
                'wrong_memory_detected_before_repair': g.wrong_memory_detected_before_repair.mean(),
                'mapping_trust': g.mapping_trust.mean(),
                'alignment_entropy': g.alignment_entropy.mean(),
            })
    pd.DataFrame(metrics).to_csv(OUT / 'confirmation_aggregate_metrics.csv', index=False)

    contrasts = []
    for a, b, rel, metric, label in [
        ('confidence_gated_relational_generation', 'reset_actual_generation', 'self_relevant', 'organization_restored', 'main_minus_full_reset_restoration'),
        ('confidence_gated_relational_generation', 'sparse_reset_generation', 'self_relevant', 'organization_restored', 'main_minus_sparse_reset_restoration'),
        ('confidence_gated_relational_generation', 'ungated_relational_generation', 'self_relevant', 'organization_restored', 'main_minus_ungated_restoration'),
        ('confidence_gated_relational_generation', 'quarantine_no_local_reservation_generation', 'self_relevant', 'organization_restored', 'main_minus_no_local_reservation_restoration'),
        ('confidence_gated_relational_generation', 'frozen_correct_memory_generation', 'self_relevant', 'organization_restored', 'main_minus_frozen_memory_restoration'),
        ('confidence_gated_relational_generation', 'reset_actual_generation', 'self_relevant', 'unique_sequences_evaluated', 'main_minus_full_reset_sequences'),
        ('confidence_gated_relational_generation', 'sparse_reset_generation', 'self_relevant', 'unique_sequences_evaluated', 'main_minus_sparse_reset_sequences'),
        ('confidence_gated_relational_generation', 'no_null_confidence_gated_generation', 'neutral', 'false_repair', 'main_minus_forced_positive_false_repair'),
    ]:
        point, lo, hi = paired(df, a, b, rel, metric)
        contrasts.append({'contrast': label, 'mode_a': a, 'mode_b': b, 'relevance': rel, 'metric': metric, 'difference': point, 'ci_low': lo, 'ci_high': hi})
    for b, label in [('reset_actual_generation', 'main_relative_sequence_reduction_vs_full_reset'), ('sparse_reset_generation', 'main_relative_sequence_reduction_vs_sparse_reset')]:
        point, lo, hi = relative_reduction(df, 'confidence_gated_relational_generation', b)
        contrasts.append({'contrast': label, 'mode_a': 'confidence_gated_relational_generation', 'mode_b': b, 'relevance': 'self_relevant', 'metric': 'relative_sequence_reduction', 'difference': point, 'ci_low': lo, 'ci_high': hi})
    pd.DataFrame(contrasts).to_csv(OUT / 'key_evaluation_contrasts.csv', index=False)

    main_self = df[(df['mode'] == 'confidence_gated_relational_generation') & (df['relevance'] == 'self_relevant')]
    main_neutral = df[(df['mode'] == 'confidence_gated_relational_generation') & (df['relevance'] == 'neutral')]
    reset_self = df[(df['mode'] == 'reset_actual_generation') & (df['relevance'] == 'self_relevant')]
    sparse_self = df[(df['mode'] == 'sparse_reset_generation') & (df['relevance'] == 'self_relevant')]
    adversarial_self = df[(df['mode'] == 'adversarial_wrong_memory_generation') & (df['relevance'] == 'self_relevant')]

    targets = []
    def add(name, value, lo, hi, criterion, met):
        targets.append({'target': name, 'value': value, 'ci_low': lo, 'ci_high': hi, 'criterion': criterion, 'met': met})

    d, lo, hi = paired(df, 'confidence_gated_relational_generation', 'reset_actual_generation', 'self_relevant', 'organization_restored')
    add('restoration_noninferior_to_full_reset', d, lo, hi, 'difference >= -0.05', int(d >= -0.05))
    d2, lo2, hi2 = paired(df, 'confidence_gated_relational_generation', 'sparse_reset_generation', 'self_relevant', 'organization_restored')
    add('restoration_noninferior_to_sparse_reset', d2, lo2, hi2, 'difference >= -0.05', int(d2 >= -0.05))
    p, plo, phi = rate_interval(main_neutral.false_repair.to_numpy())
    add('neutral_false_repair', p, plo, phi, '< 0.05', int(p < 0.05))
    r, rlo, rhi = relative_reduction(df, 'confidence_gated_relational_generation', 'reset_actual_generation')
    add('sequence_reduction_vs_full_reset', r, rlo, rhi, '>= 0.15', int(r >= 0.15))
    rs, rslo, rshi = relative_reduction(df, 'confidence_gated_relational_generation', 'sparse_reset_generation')
    add('sequence_reduction_vs_sparse_reset', rs, rslo, rshi, '>= 0.05', int(rs >= 0.05))
    p, plo, phi = rate_interval(main_self.memory_proposal_tested.to_numpy())
    add('memory_proposal_execution_rate', p, plo, phi, '>= 0.20', int(p >= 0.20))
    memory_not_ignored = int((rs >= 0.05) and (p >= 0.20))
    add('memory_not_merely_ignored', memory_not_ignored, float('nan'), float('nan'), 'sequence reduction vs sparse >=0.05 and execution >=0.20', memory_not_ignored)
    affected = adversarial_self[adversarial_self.memory_changed_action == 1]
    if len(affected):
        p, plo, phi = rate_interval(affected.wrong_memory_detected_before_repair.to_numpy())
        add('adversarial_wrong_memory_detected_before_repair', p, plo, phi, '>= 0.80', int(p >= 0.80))
    else:
        add('adversarial_wrong_memory_detected_before_repair', float('nan'), float('nan'), float('nan'), '>= 0.80; not evaluable when memory never changes action', 0)
    quarter = max(1, len(adversarial_self) // 4)
    adversarial_sorted = adversarial_self.sort_values('seed')
    adv_improvement = adversarial_sorted.tail(quarter).organization_restored.mean() - adversarial_sorted.head(quarter).organization_restored.mean()
    add('adversarial_final_minus_first_quarter_restoration', adv_improvement, float('nan'), float('nan'), '>= 0.20', int(adv_improvement >= 0.20))
    five = main_self[main_self.primitive_cardinality == 5].organization_restored.mean()
    seven = main_self[main_self.primitive_cardinality == 7].organization_restored.mean()
    add('five_seven_operation_stability', abs(five - seven), float('nan'), float('nan'), '<= 0.10', int(abs(five - seven) <= 0.10))
    stationary = main_self[main_self.nonstationary == 0].organization_restored.mean()
    shifted = main_self[main_self.nonstationary == 1].organization_restored.mean()
    add('nonstationary_minus_stationary_restoration', shifted - stationary, float('nan'), float('nan'), '>= -0.10', int(shifted - stationary >= -0.10))
    pd.DataFrame(targets).to_csv(OUT / 'primary_target_results.csv', index=False)

    failures = df[((df.relevance == 'self_relevant') & (df.organization_restored == 0)) | ((df.relevance == 'neutral') & (df.false_repair == 1))].copy()
    failures.to_csv(OUT / 'failure_cases.csv', index=False)

    transfer = df.groupby(['mode', 'relevance', 'primitive_cardinality', 'nonstationary'], as_index=False).agg(
        runs=('seed', 'size'),
        organization_restored=('organization_restored', 'mean'),
        false_repair=('false_repair', 'mean'),
        unique_sequences_evaluated=('unique_sequences_evaluated', 'mean'),
        memory_changed_action=('memory_changed_action', 'mean'),
    )
    transfer.to_csv(OUT / 'transfer_by_cardinality_and_stationarity.csv', index=False)

    # Counterfactual summary: sparse calibration isolates the contribution of memory.
    counterfactual = pd.DataFrame([
        {
            'comparison': 'principal_vs_full_reset',
            'restoration_a': main_self.organization_restored.mean(),
            'restoration_b': reset_self.organization_restored.mean(),
            'mean_sequences_a': main_self.unique_sequences_evaluated.mean(),
            'mean_sequences_b': reset_self.unique_sequences_evaluated.mean(),
            'interpretation': 'combines sparse calibration and memory gating',
        },
        {
            'comparison': 'principal_vs_sparse_reset',
            'restoration_a': main_self.organization_restored.mean(),
            'restoration_b': sparse_self.organization_restored.mean(),
            'mean_sequences_a': main_self.unique_sequences_evaluated.mean(),
            'mean_sequences_b': sparse_self.unique_sequences_evaluated.mean(),
            'interpretation': 'isolates memory contribution under matched sparse calibration',
        },
    ])
    counterfactual.to_csv(OUT / 'memory_counterfactual_summary.csv', index=False)

    text = []
    text.append(f'Confirmation runs: {len(df)}')
    text.append(f'Main restoration: {main_self.organization_restored.mean():.3f}')
    text.append(f'Full reset restoration: {reset_self.organization_restored.mean():.3f}')
    text.append(f'Sparse reset restoration: {sparse_self.organization_restored.mean():.3f}')
    text.append(f'Main mean sequences: {main_self.unique_sequences_evaluated.mean():.3f}')
    text.append(f'Full reset mean sequences: {reset_self.unique_sequences_evaluated.mean():.3f}')
    text.append(f'Sparse reset mean sequences: {sparse_self.unique_sequences_evaluated.mean():.3f}')
    text.append(f'Main neutral false repair: {main_neutral.false_repair.mean():.3f}')
    text.append(f'Main memory changed action: {main_self.memory_changed_action.mean():.3f}')
    text.append(f'Adversarial memory changed action: {adversarial_self.memory_changed_action.mean():.3f}')
    (OUT / 'analysis_output_v0_14.txt').write_text('\n'.join(text) + '\n', encoding='utf-8')
    print('\n'.join(text))


if __name__ == '__main__':
    main()
