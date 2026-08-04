from __future__ import annotations

import math

from .environment import N_INTERNAL, Observation


class SelfModelLearner:
    def __init__(self, strategy: str = "causal") -> None:
        self.strategy = strategy
        self.states: list[tuple[float | None, ...]] = []
        self.pulse_vectors: dict[int, list[tuple[float, ...]]] = {i: [] for i in range(N_INTERNAL)}
        self.probe_counts = [0] * N_INTERNAL
        self.baseline = [0.925] * N_INTERNAL
        self.last_seen = [0.925] * N_INTERNAL
        self.last_seen_at = [-1] * N_INTERNAL
        self.centrality = [0.0] * N_INTERNAL
        self.core_probabilities = [0.35] * N_INTERNAL

    def update(self, observation: Observation) -> None:
        self.states.append(observation.internal_after)
        for i in observation.observed_indices:
            value = observation.internal_after[i]
            if value is not None:
                self.last_seen[i] = value
                self.last_seen_at[i] = observation.index
        if len(self.states) <= 12:
            for i in range(N_INTERNAL):
                values = [state[i] for state in self.states if state[i] is not None]
                if values:
                    self.baseline[i] = sum(values) / len(values)
        if observation.pulse_index >= 0:
            j = observation.pulse_index
            self.probe_counts[j] += 1
            vector = []
            for k in range(N_INTERNAL):
                before, after = observation.internal_before[k], observation.internal_after[k]
                if k == j or before is None or after is None:
                    vector.append(0.0)
                else:
                    vector.append(max(0.0, float(before) - float(after)))
            self.pulse_vectors[j].append(tuple(vector))
        if self.strategy == "causal" and observation.pulse_index >= 0:
            self._recompute()
        elif self.strategy == "correlation" and observation.index % 4 == 0:
            self._recompute()

    def _recompute(self) -> None:
        if len(self.states) < 5:
            return
        if self.strategy == "correlation":
            complete = [state for state in self.states if all(v is not None for v in state)]
            if len(complete) < 5:
                return
            global_series = [sum(float(v) for v in state) / N_INTERNAL for state in complete]
            scores = [abs(_correlation([float(s[i]) for s in complete], global_series)) for i in range(N_INTERNAL)]
        else:
            scores = [self._causal_score(i) for i in range(N_INTERNAL)]
        self.centrality = scores
        lo, hi = min(scores), max(scores)
        if hi - lo < 1e-9:
            self.core_probabilities = [0.35] * N_INTERNAL
            return
        predicted = set(self.predicted_core_from_scores(scores))
        midpoint = _cluster_midpoint(scores, predicted)
        scale = max(1e-4, 0.10 * (hi - lo))
        probabilities = [1 / (1 + math.exp(-(s - midpoint) / scale)) for s in scores]
        for i, count in enumerate(self.probe_counts):
            if count == 0 and self.strategy != "correlation":
                probabilities[i] = max(probabilities[i], 0.35)
        self.core_probabilities = probabilities

    def _causal_score(self, index: int) -> float:
        own = self.pulse_vectors[index]
        if not own:
            return 0.0
        background = [v for other, rows in self.pulse_vectors.items() if other != index for v in rows]
        own_mean = [sum(v[k] for v in own) / len(own) for k in range(N_INTERNAL)]
        bg_mean = [sum(v[k] for v in background) / len(background) for k in range(N_INTERNAL)] if background else [0.0] * N_INTERNAL
        return sum(max(0.0, own_mean[k] - bg_mean[k] - 0.0025) for k in range(N_INTERNAL) if k != index)

    def probe_priority(self) -> int:
        min_count = min(self.probe_counts)
        candidates = [i for i, count in enumerate(self.probe_counts) if count == min_count]
        return min(candidates, key=lambda i: abs(self.core_probabilities[i] - 0.5))

    def sensing_priority(self, needs: list[float], count: int = 8, topology_aware: bool = True) -> tuple[int, ...]:
        predicted = set(self.predicted_core())
        current = len(self.states)
        max_cent = max(self.centrality) if self.centrality else 0.0
        ranked = sorted(
            range(N_INTERNAL),
            key=lambda i: (
                0.38 * needs[i]
                + 0.24 * (1.0 if i in predicted else self.core_probabilities[i])
                + 0.20 * min(1.0, max(0, current - self.last_seen_at[i]) / 10.0)
                + (0.18 * (1.0 - self.centrality[i] / max_cent) if topology_aware and i in predicted and max_cent > 0 else 0.0)
            ),
            reverse=True,
        )
        return tuple(sorted(ranked[:count]))

    def need_vector(self) -> list[float]:
        return [
            self.core_probabilities[i] * max(0.0, self.baseline[i] - self.last_seen[i]) / 0.30
            for i in range(N_INTERNAL)
        ]

    def predicted_core(self) -> tuple[int, ...]:
        return self.predicted_core_from_scores(self.centrality)

    @staticmethod
    def predicted_core_from_scores(scores: list[float]) -> tuple[int, ...]:
        order = sorted(range(N_INTERNAL), key=lambda i: scores[i], reverse=True)
        if max(scores) - min(scores) < 1e-9:
            return tuple(order[: max(1, N_INTERNAL // 4)])
        best_k, best = 1, float("inf")
        n = len(scores)
        for k in range(1, n - 1):
            high = [scores[i] for i in order[:k]]
            low = [scores[i] for i in order[k:]]
            mh, ml = sum(high) / len(high), sum(low) / len(low)
            sse = sum((v - mh) ** 2 for v in high) + sum((v - ml) ** 2 for v in low)
            variance = max(1e-9, sse / n)
            bic = n * math.log(variance) + 4.0 * math.log(n) + (1.2 if k == 1 else 0.0)
            if bic < best:
                best, best_k = bic, k
        return tuple(sorted(order[:best_k]))


def _cluster_midpoint(scores: list[float], predicted: set[int]) -> float:
    high = [scores[i] for i in predicted]
    low = [scores[i] for i in range(len(scores)) if i not in predicted]
    return (min(high) + max(low)) / 2 if high and low else (max(scores) + min(scores)) / 2


def _correlation(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs)
    dy = sum((y - my) ** 2 for y in ys)
    return 0.0 if dx <= 1e-12 or dy <= 1e-12 else num / math.sqrt(dx * dy)
