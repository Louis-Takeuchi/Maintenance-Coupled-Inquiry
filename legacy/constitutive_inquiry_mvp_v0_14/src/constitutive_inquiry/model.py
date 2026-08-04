from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from statistics import mean

from .environment import MECHANISMS, N_INTERNAL, Observation, PRIMITIVES, isolating_bits, trigger


@dataclass(frozen=True)
class Diagnosis:
    kind: str
    mechanism: str
    target_index: int
    intervention: tuple[str, ...]
    mechanism_confidence: float
    suppression: float
    bridge_effect: float
    evidence_rows: int
    tested_scope: str


class InquiryModel:
    def __init__(self, allow_null: bool = True) -> None:
        self.allow_null = allow_null
        self.observations: list[Observation] = []
        self.external_stats: dict[tuple[str, tuple[str, ...]], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
        self.accepted: Diagnosis | None = None
        self.failed_repairs = 0
        self.rejected_bridges: set[tuple[str, tuple[str, ...]]] = set()

    def update(self, observation: Observation) -> None:
        self.observations.append(observation)
        if observation.domain == "self":
            for mechanism in MECHANISMS:
                if observation.bits == isolating_bits(mechanism):
                    key = (mechanism, observation.intervention)
                    stats = self.external_stats[key]
                    stats[0] += observation.external_intensity
                    stats[1] += observation.external_intensity ** 2
                    stats[2] += 1.0
                    break
        cap = observation.retained_capacity
        if len(self.observations) > cap:
            self.observations = self.observations[-cap:]

    def mechanism_rates(self) -> dict[str, float]:
        output = {}
        for mechanism in MECHANISMS:
            total, _, count = self.external_stats.get((mechanism, ()), [0.0, 0.0, 0.0])
            output[mechanism] = total / count if count else 0.0
        return output

    def active_mechanisms(self, count: int = 2) -> tuple[str, ...]:
        rates = self.mechanism_rates()
        return tuple(m for m, _ in sorted(rates.items(), key=lambda row: row[1], reverse=True)[:count])

    def candidate_suppression(self, mechanism: str, intervention: tuple[str, ...]) -> tuple[float, int, int]:
        base_total, _, base_count = self.external_stats.get((mechanism, ()), [0.0, 0.0, 0.0])
        treated_total, _, treated_count = self.external_stats.get((mechanism, intervention), [0.0, 0.0, 0.0])
        if not base_count or not treated_count:
            return 0.0, int(base_count), int(treated_count)
        return base_total / base_count - treated_total / treated_count, int(base_count), int(treated_count)

    def tested_sequences(self, mechanism: str, length: int | None = None) -> list[tuple[str, ...]]:
        rows = [seq for m, seq in self.external_stats if m == mechanism and seq]
        if length is not None:
            rows = [seq for seq in rows if len(seq) == length]
        return list(dict.fromkeys(rows))

    def primitive_rank_maps(self, mechanism: str, primitives: tuple[str, ...] | None = None) -> tuple[dict[str, int], dict[int, str]]:
        rows: list[tuple[float, str]] = []
        for primitive in (primitives or PRIMITIVES):
            suppression, _, count = self.candidate_suppression(mechanism, (primitive,))
            # Stable tie-breaking is required for reproducible label-invariant memory.
            rows.append((suppression if count else -1.0, primitive))
        rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
        primitive_to_rank = {primitive: rank for rank, (_, primitive) in enumerate(rows, start=1)}
        rank_to_primitive = {rank: primitive for primitive, rank in primitive_to_rank.items()}
        return primitive_to_rank, rank_to_primitive


    def relational_matrix(
        self,
        mechanism: str,
        primitives: tuple[str, ...],
    ) -> dict[tuple[str, str], float]:
        """Estimate directed pair interaction beyond ambiguous singleton effects."""
        singles = {
            p: self.candidate_suppression(mechanism, (p,))[0]
            for p in primitives
        }
        output: dict[tuple[str, str], float] = {}
        for a in primitives:
            for b in primitives:
                pair, _, count = self.candidate_suppression(mechanism, (a, b))
                if count <= 0:
                    output[(a, b)] = float("nan")
                else:
                    output[(a, b)] = pair - 0.18 * (singles[a] + singles[b])
        return output

    def relational_coverage(self, mechanism: str, primitives: tuple[str, ...]) -> float:
        matrix = self.relational_matrix(mechanism, primitives)
        observed = sum(value == value for value in matrix.values())
        return observed / max(1, len(matrix))

    def ranked_sequences(self, mechanism: str, length: int | None = None) -> list[tuple[str, ...]]:
        rows = []
        for seq in self.tested_sequences(mechanism, length):
            suppression, _, n = self.candidate_suppression(mechanism, seq)
            risk = self._mean_risk(mechanism, seq)
            score = suppression + 0.018 * min(n, 3) - 0.16 * risk - 0.004 * len(seq)
            rows.append((seq, score, suppression, n))
        rows.sort(key=lambda row: (row[1], row[2], row[3], row[0]), reverse=True)
        return [row[0] for row in rows]

    def _mean_risk(self, mechanism: str, intervention: tuple[str, ...]) -> float:
        values = [
            row.intervention_risk for row in self.observations
            if row.domain == "self" and row.bits == isolating_bits(mechanism) and row.intervention == intervention
        ]
        return mean(values) if values else 0.0

    def weighted_loss(self, observation: Observation, self_prob: list[float]) -> float | None:
        values: list[tuple[float, float]] = []
        for i in observation.observed_indices:
            before, after = observation.internal_before[i], observation.internal_after[i]
            if before is None or after is None:
                continue
            values.append((max(0.02, self_prob[i]), float(before) - float(after)))
        if not values:
            return None
        # Topology-aware evidence preserves endpoint effects instead of averaging them away.
        values.sort(key=lambda row: row[0] * row[1], reverse=True)
        selected = values[: max(2, min(4, len(values)))]
        denom = sum(weight for weight, _ in selected)
        return sum(weight * loss for weight, loss in selected) / denom if denom else None

    def bridge_evidence(self, mechanism: str, intervention: tuple[str, ...], self_prob: list[float]) -> tuple[float, int, int]:
        untreated: list[float] = []
        treated: list[float] = []
        bits = isolating_bits(mechanism)
        for row in self.observations:
            if row.domain != "self" or row.bits != bits:
                continue
            loss = self.weighted_loss(row, self_prob)
            if loss is None:
                continue
            if not row.intervention:
                untreated.append(loss)
            elif row.intervention == intervention:
                treated.append(loss)
        if not untreated or not treated:
            return 0.0, len(untreated), len(treated)
        return mean(untreated) - mean(treated), len(untreated), len(treated)

    def target_scores(self, mechanism: str, intervention: tuple[str, ...]) -> list[float]:
        bits = isolating_bits(mechanism)
        scores = [0.0] * N_INTERNAL
        for i in range(N_INTERNAL):
            untreated: list[float] = []
            treated: list[float] = []
            for row in self.observations:
                if row.domain != "self" or row.bits != bits:
                    continue
                before, after = row.internal_before[i], row.internal_after[i]
                if before is None or after is None:
                    continue
                loss = float(before) - float(after)
                if not row.intervention:
                    untreated.append(loss)
                elif row.intervention == intervention:
                    treated.append(loss)
            if untreated and treated:
                scores[i] = mean(untreated) - mean(treated)
        return scores

    def diagnose(
        self,
        self_prob: list[float],
        candidates: dict[str, tuple[str, ...]],
        force_positive: bool = False,
        observational: bool = False,
    ) -> Diagnosis | None:
        if self.accepted is not None:
            return self.accepted
        ordered = sorted(self.mechanism_rates(), key=self.mechanism_rates().get, reverse=True)[:2]
        if observational:
            for mechanism in ordered:
                effect, n0, n1 = self._observational_effect(mechanism, self_prob)
                if effect >= 0.020 and n0 + n1 >= 16:
                    result = Diagnosis(
                        "bridge", mechanism, max(range(N_INTERNAL), key=lambda i: self_prob[i]), (),
                        self.mechanism_rates()[mechanism], 0.0, effect, n0 + n1,
                        f"observational:{mechanism}:control={n0}:trigger={n1}",
                    )
                    self.accepted = result
                    return result
            return None

        positives: list[Diagnosis] = []
        nulls: list[Diagnosis] = []
        for mechanism in ordered:
            intervention = candidates.get(mechanism, ())
            if not intervention:
                continue
            suppression, n_base, n_treated = self.candidate_suppression(mechanism, intervention)
            effect, n_off, n_on = self.bridge_evidence(mechanism, intervention, self_prob)
            target_scores = self.target_scores(mechanism, intervention)
            target = max(range(N_INTERNAL), key=lambda i: 0.82 * target_scores[i] + 0.18 * self_prob[i])
            scope = (
                f"mechanism={mechanism};sequence={'>'.join(intervention)};"
                f"external={n_base}/{n_treated};bridge={n_off}/{n_on};"
                f"target={target};effect={effect:.4f};suppression={suppression:.3f}"
            )
            if suppression >= 0.64 and n_treated >= 3 and n_off >= 10 and n_on >= 10:
                if (mechanism, intervention) in self.rejected_bridges:
                    if self.allow_null:
                        nulls.append(Diagnosis(
                            "no_bridge", mechanism, -1, intervention, self.mechanism_rates()[mechanism],
                            suppression, effect, n_base + n_treated + n_off + n_on, scope + ";validation=rejected",
                        ))
                elif effect >= 0.0040 or force_positive:
                    positives.append(Diagnosis(
                        "bridge", mechanism, target, intervention, self.mechanism_rates()[mechanism],
                        suppression, effect, n_base + n_treated + n_off + n_on, scope,
                    ))
                elif self.allow_null and effect <= 0.0015:
                    nulls.append(Diagnosis(
                        "no_bridge", mechanism, -1, intervention, self.mechanism_rates()[mechanism],
                        suppression, effect, n_base + n_treated + n_off + n_on, scope,
                    ))
        if positives:
            self.accepted = max(positives, key=lambda d: (d.bridge_effect, d.suppression))
            return self.accepted
        if self.allow_null and len(nulls) >= 2:
            self.accepted = max(nulls, key=lambda d: (d.suppression, d.evidence_rows))
            return self.accepted
        return None

    def register_validation_failure(self, diagnosis: Diagnosis) -> None:
        self.rejected_bridges.add((diagnosis.mechanism, diagnosis.intervention))
        self.accepted = None

    def register_repair_outcome(self, diagnosis: Diagnosis, success: bool, improvement: float) -> None:
        if success or improvement >= 0.035:
            return
        self.failed_repairs += 1
        self.accepted = None

    def _observational_effect(self, mechanism: str, self_prob: list[float]) -> tuple[float, int, int]:
        triggered: list[float] = []
        controls: list[float] = []
        for row in self.observations:
            if row.domain != "self" or row.intervention:
                continue
            loss = self.weighted_loss(row, self_prob)
            if loss is None:
                continue
            (triggered if trigger(mechanism, row.bits) else controls).append(loss)
        if not triggered or not controls:
            return 0.0, len(controls), len(triggered)
        return mean(triggered) - mean(controls), len(controls), len(triggered)
