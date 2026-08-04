from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from itertools import permutations
import json
import math
from pathlib import Path
import random
from typing import TYPE_CHECKING

from .environment import MECHANISMS

if TYPE_CHECKING:
    from .agent import StepRecord
    from .environment import UnlabeledSelfWorld
    from .model import InquiryModel

CanonicalTemplate = tuple[int, ...]


@dataclass(frozen=True)
class AlignmentHypothesis:
    primitive_to_role: dict[str, int]
    role_to_primitive: dict[int, str]
    fit_cost: float
    validation_cost: float
    posterior: float

    @property
    def support(self) -> float:
        # Independent held-out support. Values near one indicate that the mapping
        # reconstructs pair relations that were not used to fit it.
        return math.exp(-max(0.0, self.validation_cost) / 0.010)


def _finite(value: float) -> bool:
    return value == value and math.isfinite(value)


@dataclass
class CrossWorldMemory:
    """Maintenance-limited relational memory of intervention structures.

    The relational variant stores a directed operation-interaction prototype and
    intervention programs expressed in canonical graph-node identities. Primitive
    labels and scalar singleton ranks are not part of the representation.

    The scalar variant is retained only as a v0.12-style control.
    """

    strategy: str = "relational"  # relational | scalar
    template_weights: Counter[CanonicalTemplate] = field(default_factory=Counter)
    macro_weights: Counter[CanonicalTemplate] = field(default_factory=Counter)
    transition_weights: Counter[tuple[int, int]] = field(default_factory=Counter)
    prototype_matrix: list[list[float]] = field(default_factory=list)
    prototype_counts: list[list[float]] = field(default_factory=list)
    prototype_size: int = 6
    successes: int = 0
    failures: int = 0
    worlds_seen: int = 0
    energy: float = 1.0
    revision_enabled: bool = True
    shuffled: bool = False
    negative_transfer: bool = False
    last_alignment_cost: float = 0.0
    last_alignment_entropy: float = 0.0
    last_alignment_support: float = 0.0
    quarantined_pairs: set[str] = field(default_factory=set)
    family_distrust: Counter[str] = field(default_factory=Counter)
    _alignment_cache: dict[tuple, tuple[dict[str, int], dict[int, str], float]] = field(default_factory=dict, repr=False)
    _posterior_cache: dict[tuple, tuple[AlignmentHypothesis, ...]] = field(default_factory=dict, repr=False)

    # Compatibility aliases used by existing metrics and traces.
    @property
    def template_counts(self) -> Counter[CanonicalTemplate]:
        return self.template_weights

    @property
    def macro_counts(self) -> Counter[CanonicalTemplate]:
        return self.macro_weights

    @property
    def transition_counts(self) -> Counter[tuple[int, int]]:
        return self.transition_weights

    def clone(self) -> "CrossWorldMemory":
        return CrossWorldMemory.from_dict(self.to_dict())

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy,
            "template_weights": {">".join(map(str, k)): float(v) for k, v in self.template_weights.items()},
            "macro_weights": {">".join(map(str, k)): float(v) for k, v in self.macro_weights.items()},
            "transition_weights": {f"{a}>{b}": float(v) for (a, b), v in self.transition_weights.items()},
            "prototype_matrix": self.prototype_matrix,
            "prototype_counts": self.prototype_counts,
            "prototype_size": self.prototype_size,
            "successes": self.successes,
            "failures": self.failures,
            "worlds_seen": self.worlds_seen,
            "energy": self.energy,
            "revision_enabled": self.revision_enabled,
            "shuffled": self.shuffled,
            "negative_transfer": self.negative_transfer,
            "last_alignment_cost": self.last_alignment_cost,
            "last_alignment_entropy": self.last_alignment_entropy,
            "last_alignment_support": self.last_alignment_support,
            "quarantined_pairs": sorted(self.quarantined_pairs),
            "family_distrust": dict(self.family_distrust),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "CrossWorldMemory":
        out = cls(
            strategy=str(payload.get("strategy", "relational")),
            prototype_size=int(payload.get("prototype_size", 6)),
            revision_enabled=bool(payload.get("revision_enabled", True)),
        )
        out.template_weights = Counter({
            tuple(map(int, k.split(">"))): float(v)
            for k, v in payload.get("template_weights", payload.get("template_counts", {})).items()
        })
        out.macro_weights = Counter({
            tuple(map(int, k.split(">"))): float(v)
            for k, v in payload.get("macro_weights", payload.get("macro_counts", {})).items()
        })
        out.transition_weights = Counter({
            tuple(map(int, k.split(">"))): float(v)
            for k, v in payload.get("transition_weights", payload.get("transition_counts", {})).items()
        })
        out.prototype_matrix = [[float(x) for x in row] for row in payload.get("prototype_matrix", [])]
        out.prototype_counts = [[float(x) for x in row] for row in payload.get("prototype_counts", [])]
        out.successes = int(payload.get("successes", 0))
        out.failures = int(payload.get("failures", 0))
        out.worlds_seen = int(payload.get("worlds_seen", 0))
        out.energy = float(payload.get("energy", 1.0))
        out.shuffled = bool(payload.get("shuffled", False))
        out.negative_transfer = bool(payload.get("negative_transfer", False))
        out.last_alignment_cost = float(payload.get("last_alignment_cost", 0.0))
        out.last_alignment_entropy = float(payload.get("last_alignment_entropy", 0.0))
        out.last_alignment_support = float(payload.get("last_alignment_support", 0.0))
        out.quarantined_pairs = set(payload.get("quarantined_pairs", []))
        out.family_distrust = Counter({str(k): float(v) for k, v in payload.get("family_distrust", {}).items()})
        return out

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "CrossWorldMemory":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def scalar_copy(self) -> "CrossWorldMemory":
        out = self.clone()
        out.strategy = "scalar"
        out.prototype_matrix = []
        out.prototype_counts = []
        return out

    def shuffled_copy(self, seed: int) -> "CrossWorldMemory":
        rng = random.Random(seed + 13_130_131)
        perm = list(range(self.prototype_size))
        rng.shuffle(perm)
        out = self.clone()
        # Deliberately scramble remembered templates while retaining the graph prototype.
        out.template_weights = Counter({tuple(perm[i] for i in t): w for t, w in self.template_weights.items()})
        out.macro_weights = Counter({tuple(perm[i] for i in t): w for t, w in self.macro_weights.items()})
        out.transition_weights = Counter({(perm[a], perm[b]): w for (a, b), w in self.transition_weights.items()})
        out.shuffled = True
        return out

    def negative_copy(self, seed: int) -> "CrossWorldMemory":
        out = self.shuffled_copy(seed)
        out.negative_transfer = True
        out.revision_enabled = True
        # Start with a strong but wrong prior so revision/forgetting is testable.
        out.template_weights = Counter({k: 2.5 * v for k, v in out.template_weights.items()})
        out.macro_weights = Counter({k: 2.5 * v for k, v in out.macro_weights.items()})
        out.energy = 1.0
        return out

    @property
    def confidence(self) -> float:
        evidence = self.successes / max(4.0, 0.55 * max(1, self.worlds_seen))
        return max(0.0, min(1.0, evidence * self.energy))

    def maintain(self, success: bool | None = None) -> None:
        """Apply stipulated memory decay and optional evidence-dependent refresh."""
        self.worlds_seen += 1
        decay = 0.985 if success else 0.965
        self.energy = max(0.0, self.energy * decay - 0.008)
        for counter in (self.template_weights, self.macro_weights, self.transition_weights):
            for key in list(counter):
                counter[key] *= decay
                if counter[key] < 0.05:
                    del counter[key]
        if success:
            self.energy = min(1.0, self.energy + 0.18)
        self._alignment_cache.clear()
        self._posterior_cache.clear()

    def _graph(self, model: "InquiryModel", mechanism: str, primitives: tuple[str, ...]) -> list[list[float]]:
        matrix = model.relational_matrix(mechanism, primitives)
        return [[matrix[(a, b)] for b in primitives] for a in primitives]

    @staticmethod
    def _node_fingerprint(matrix: list[list[float]], i: int) -> tuple:
        n = len(matrix)
        outgoing = sorted(round(matrix[i][j], 4) for j in range(n) if _finite(matrix[i][j]))
        incoming = sorted(round(matrix[j][i], 4) for j in range(n) if _finite(matrix[j][i]))
        out_mean = sum(outgoing) / len(outgoing) if outgoing else -9.0
        in_mean = sum(incoming) / len(incoming) if incoming else -9.0
        diag = matrix[i][i] if _finite(matrix[i][i]) else -9.0
        return (round(out_mean, 4), round(in_mean, 4), round(diag, 4), tuple(outgoing), tuple(incoming))

    def _initialize_prototype(
        self,
        model: "InquiryModel",
        mechanism: str,
        primitives: tuple[str, ...],
    ) -> tuple[dict[str, int], dict[int, str], float]:
        graph = self._graph(model, mechanism, primitives)
        if len(primitives) < self.prototype_size:
            return {}, {}, float("inf")
        # Canonicalize the first graph by structural fingerprints, not labels.
        order = sorted(range(len(primitives)), key=lambda i: self._node_fingerprint(graph, i))[: self.prototype_size]
        self.prototype_matrix = [[graph[i][j] for j in order] for i in order]
        self.prototype_counts = [[1.0 if _finite(self.prototype_matrix[i][j]) else 0.0 for j in range(self.prototype_size)] for i in range(self.prototype_size)]
        p2r = {primitives[idx]: role for role, idx in enumerate(order)}
        r2p = {role: primitive for primitive, role in p2r.items()}
        return p2r, r2p, 0.0

    def alignment_mechanism(
        self,
        model: "InquiryModel",
        requested: str,
        primitives: tuple[str, ...],
    ) -> str:
        if self.strategy != "relational":
            return requested
        rows = [(model.relational_coverage(m, primitives), m) for m in MECHANISMS]
        best_coverage, best = max(rows)
        requested_coverage = model.relational_coverage(requested, primitives)
        return best if best_coverage > requested_coverage + 1e-9 else requested

    def align(
        self,
        model: "InquiryModel",
        mechanism: str,
        primitives: tuple[str, ...],
        initialize: bool = False,
    ) -> tuple[dict[str, int], dict[int, str], float]:
        mechanism = self.alignment_mechanism(model, mechanism, primitives)
        cache_key = (
            self.strategy, mechanism, primitives, initialize,
            len(self.template_weights), round(self.energy, 4),
        )
        if cache_key in self._alignment_cache:
            return self._alignment_cache[cache_key]
        if self.strategy == "scalar":
            p2rank, rank2p = model.primitive_rank_maps(mechanism, primitives)
            p2r = {p: rank - 1 for p, rank in p2rank.items() if rank <= self.prototype_size}
            r2p = {r: p for p, r in p2r.items()}
            result = (p2r, r2p, 0.0)
            self.last_alignment_cost = 0.0
            self._alignment_cache[cache_key] = result
            return result
        if not self.prototype_matrix:
            if initialize:
                result = self._initialize_prototype(model, mechanism, primitives)
                self.last_alignment_cost = result[2]
                self._alignment_cache.clear()
                return result
            result = ({}, {}, float("inf"))
            self.last_alignment_cost = result[2]
            self._alignment_cache[cache_key] = result
            return result
        current = self._graph(model, mechanism, primitives)
        k = self.prototype_size
        n = len(primitives)
        best_cost = float("inf")
        best_p2r: dict[str, int] = {}
        if n >= k:
            # Assign each canonical role to one current primitive; extra primitives are decoys.
            for assignment in permutations(range(n), k):
                cost = 0.0
                count = 0
                for r1 in range(k):
                    for r2 in range(k):
                        a = self.prototype_matrix[r1][r2]
                        b = current[assignment[r1]][assignment[r2]]
                        if _finite(a) and _finite(b):
                            cost += (a - b) ** 2
                            count += 1
                cost = cost / max(1, count)
                if cost < best_cost:
                    best_cost = cost
                    best_p2r = {primitives[assignment[r]]: r for r in range(k)}
        else:
            # One irrelevant canonical role may be absent. Align current primitives to a
            # subset of canonical graph nodes.
            for roles in permutations(range(k), n):
                cost = 0.0
                count = 0
                for i in range(n):
                    for j in range(n):
                        a = self.prototype_matrix[roles[i]][roles[j]]
                        b = current[i][j]
                        if _finite(a) and _finite(b):
                            cost += (a - b) ** 2
                            count += 1
                cost = cost / max(1, count)
                if cost < best_cost:
                    best_cost = cost
                    best_p2r = {primitives[i]: roles[i] for i in range(n)}
        result = (best_p2r, {r: p for p, r in best_p2r.items()}, best_cost)
        self.last_alignment_cost = best_cost
        self._alignment_cache[cache_key] = result
        return result

    @staticmethod
    def _pair_is_fit(role_a: int, role_b: int) -> bool:
        """Deterministic split for mapping fit versus independent validation."""
        return ((role_a * 7 + role_b * 11 + role_a * role_b) % 4) != 0

    def alignment_posterior(
        self,
        model: "InquiryModel",
        mechanism: str,
        primitives: tuple[str, ...],
        top_k: int = 6,
    ) -> tuple[AlignmentHypothesis, ...]:
        """Return a posterior over graph alignments instead of one best mapping.

        Mapping scores are fit on one deterministic subset of ordered role pairs and
        validated on disjoint observed pairs. Missing relations remain missing rather
        than being imputed from the prototype.
        """
        mechanism = self.alignment_mechanism(model, mechanism, primitives)
        cache_key = (
            "posterior", self.strategy, mechanism, primitives, top_k,
            len(self.template_weights), round(self.energy, 4),
        )
        if cache_key in self._posterior_cache:
            return self._posterior_cache[cache_key]
        if self.strategy == "scalar":
            p2r, r2p, cost = self.align(model, mechanism, primitives)
            result = (AlignmentHypothesis(p2r, r2p, cost, cost, 1.0),) if p2r else ()
            self._posterior_cache[cache_key] = result
            return result
        if not self.prototype_matrix:
            return ()

        current = self._graph(model, mechanism, primitives)
        k = self.prototype_size
        n = len(primitives)
        candidates: list[tuple[float, float, dict[str, int]]] = []

        def score_mapping(mapping: dict[str, int]) -> tuple[float, float]:
            index = {p: i for i, p in enumerate(primitives)}
            fit_sum = valid_sum = 0.0
            fit_n = valid_n = 0
            items = list(mapping.items())
            for pa, ra in items:
                for pb, rb in items:
                    a = self.prototype_matrix[ra][rb]
                    b = current[index[pa]][index[pb]]
                    if not (_finite(a) and _finite(b)):
                        continue
                    err = (a - b) ** 2
                    if self._pair_is_fit(ra, rb):
                        fit_sum += err
                        fit_n += 1
                    else:
                        valid_sum += err
                        valid_n += 1
            return fit_sum / max(1, fit_n), valid_sum / max(1, valid_n)

        if n >= k:
            for assignment in permutations(range(n), k):
                mapping = {primitives[assignment[r]]: r for r in range(k)}
                fit, valid = score_mapping(mapping)
                candidates.append((fit, valid, mapping))
        else:
            for roles in permutations(range(k), n):
                mapping = {primitives[i]: roles[i] for i in range(n)}
                fit, valid = score_mapping(mapping)
                candidates.append((fit, valid, mapping))
        if not candidates:
            return ()
        candidates.sort(key=lambda row: (row[0], row[1], sorted(row[2].items())))
        shortlisted = candidates[: max(top_k * 4, top_k)]
        # Temperature is deliberately conservative: ambiguous decoy alignments retain
        # posterior mass instead of collapsing to a single arbitrary permutation.
        min_fit = shortlisted[0][0]
        raw = [math.exp(-max(0.0, fit - min_fit) / 0.0025) for fit, _, _ in shortlisted]
        denom = sum(raw) or 1.0
        rows = []
        for (fit, valid, p2r), weight in zip(shortlisted, raw):
            rows.append(AlignmentHypothesis(p2r, {r: p for p, r in p2r.items()}, fit, valid, weight / denom))
        rows.sort(key=lambda h: (h.posterior, -h.validation_cost), reverse=True)
        rows = rows[:top_k]
        norm = sum(row.posterior for row in rows) or 1.0
        rows = [AlignmentHypothesis(row.primitive_to_role, row.role_to_primitive, row.fit_cost, row.validation_cost, row.posterior / norm) for row in rows]
        entropy = -sum(row.posterior * math.log(max(row.posterior, 1e-12)) for row in rows)
        self.last_alignment_entropy = entropy / max(1e-12, math.log(max(2, len(rows)))) if len(rows) > 1 else 0.0
        self.last_alignment_support = rows[0].support if rows else 0.0
        self.last_alignment_cost = rows[0].fit_cost if rows else float("inf")
        result = tuple(rows)
        self._posterior_cache[cache_key] = result
        return result

    def mapping_trust(
        self,
        model: "InquiryModel",
        mechanism: str,
        primitives: tuple[str, ...],
    ) -> float:
        posterior = self.alignment_posterior(model, mechanism, primitives)
        if not posterior:
            return 0.0
        best = posterior[0]
        # v0.13 failed because a low-cost top-1 mapping was treated as certain even
        # when many alternatives fit almost equally well. Trust therefore includes
        # posterior concentration, not just the leading mapping's fit and support.
        concentration = max(0.0, 1.0 - self.last_alignment_entropy)
        return max(0.0, min(1.0, best.posterior * best.support * self.energy * concentration))

    @staticmethod
    def _quarantine_key(template: CanonicalTemplate, family: str) -> str:
        return f"{family}|{'>' .join(map(str, template))}"

    def quarantine(self, template: CanonicalTemplate, family: str) -> None:
        self.quarantined_pairs.add(self._quarantine_key(template, family))
        self.family_distrust[family] += 1.0

    def is_quarantined(self, template: CanonicalTemplate, family: str) -> bool:
        return self._quarantine_key(template, family) in self.quarantined_pairs

    def restore_from(self, checkpoint: "CrossWorldMemory", preserve_quarantine: bool = True) -> None:
        quarantine = set(self.quarantined_pairs)
        distrust = Counter(self.family_distrust)
        restored = CrossWorldMemory.from_dict(checkpoint.to_dict())
        self.__dict__.update(restored.__dict__)
        if preserve_quarantine:
            self.quarantined_pairs |= quarantine
            self.family_distrust.update(distrust)
        self._alignment_cache.clear()
        self._posterior_cache.clear()

    def _update_prototype(
        self,
        model: "InquiryModel",
        mechanism: str,
        primitives: tuple[str, ...],
        p2r: dict[str, int],
    ) -> None:
        if self.strategy != "relational" or not self.prototype_matrix:
            return
        graph = self._graph(model, mechanism, primitives)
        index = {p: i for i, p in enumerate(primitives)}
        for pa, ra in p2r.items():
            for pb, rb in p2r.items():
                value = graph[index[pa]][index[pb]]
                if not _finite(value):
                    continue
                count = self.prototype_counts[ra][rb]
                old = self.prototype_matrix[ra][rb]
                self.prototype_matrix[ra][rb] = value if not _finite(old) else (old * count + value) / (count + 1.0)
                self.prototype_counts[ra][rb] = count + 1.0
        self._alignment_cache.clear()

    def _successful_sequence(
        self,
        world: "UnlabeledSelfWorld",
        model: "InquiryModel",
        records: list["StepRecord"],
    ) -> tuple[str, ...]:
        measured: list[tuple[int, float, tuple[str, ...]]] = []
        for sequence in model.tested_sequences(world.spec.causal_mechanism):
            suppression, _, treated = model.candidate_suppression(world.spec.causal_mechanism, sequence)
            if treated >= 1 and suppression >= 0.70 and world.intervention_is_functional(world.spec.causal_mechanism, sequence):
                measured.append((len(sequence), -suppression, sequence))
        if measured:
            measured.sort()
            return measured[0][2]
        successful = next((row for row in records if row.repair_correct and row.proposed_intervention), None)
        return tuple(successful.proposed_intervention.split(">")) if successful else ()

    def register_outcome(
        self,
        world: "UnlabeledSelfWorld",
        model: "InquiryModel",
        records: list["StepRecord"],
        allow_learning: bool = True,
    ) -> bool:
        success = any(row.repair_correct for row in records)
        self.maintain(success)
        mechanism = world.spec.causal_mechanism
        primitives = world.available_primitives
        calibration_mechanism = self.alignment_mechanism(model, mechanism, primitives)
        if success and allow_learning:
            sequence = self._successful_sequence(world, model, records)
            p2r, _, _ = self.align(model, calibration_mechanism, primitives, initialize=not self.prototype_matrix)
            if sequence and all(p in p2r for p in sequence):
                template = tuple(p2r[p] for p in sequence)
                # Online structure revision is permitted only when the current-world
                # relation graph is substantially observed. Sparse confidence-gated
                # evaluation worlds may use and validate memory, but must not rewrite
                # the prototype from an ambiguous top-1 alignment.
                coverage = model.relational_coverage(calibration_mechanism, primitives)
                if coverage >= 0.90 or not self.prototype_matrix:
                    self.template_weights[template] += 1.0
                    for length in (2, 3):
                        for start in range(0, len(template) - length + 1):
                            self.macro_weights[template[start : start + length]] += 1.0
                    for a, b in zip(template, template[1:]):
                        self.transition_weights[(a, b)] += 1.0
                    self._update_prototype(model, calibration_mechanism, primitives, p2r)
                self.successes += 1
                return True
        if not success:
            self.failures += 1
            if self.revision_enabled:
                proposed = next((row.proposed_intervention for row in reversed(records) if row.proposed_intervention), "")
                sequence = tuple(proposed.split(">")) if proposed else ()
                p2r, _, _ = self.align(model, calibration_mechanism, primitives)
                if sequence and all(p in p2r for p in sequence):
                    template = tuple(p2r[p] for p in sequence)
                    self.template_weights[template] *= 0.28
                    for length in (2, 3):
                        for start in range(0, len(template) - length + 1):
                            macro = template[start : start + length]
                            self.macro_weights[macro] *= 0.50
                    for pair in zip(template, template[1:]):
                        self.transition_weights[pair] *= 0.55
                    self.energy = max(0.0, self.energy - 0.12)
        return False

    def proposals(
        self,
        model: "InquiryModel",
        mechanism: str,
        depth: int,
        primitives: tuple[str, ...],
        include_macros: bool = True,
        limit: int = 8,
    ) -> list[tuple[str, ...]]:
        if self.successes <= 0 or self.energy < 0.12:
            return []
        _, r2p, cost = self.align(model, mechanism, primitives)
        if not r2p or cost > 0.035:
            return []
        sources: Counter[CanonicalTemplate] = Counter()
        for template, weight in self.template_weights.items():
            if len(template) == depth:
                sources[template] += 2.0 * weight
            elif len(template) > depth:
                sources[template[:depth]] += weight
        if include_macros:
            for macro, weight in self.macro_weights.items():
                if len(macro) == depth:
                    sources[macro] += 3.0 * weight
        # Compose a longer intervention from remembered prefixes and learned directed
        # transitions. This is the mechanism used for held-out grammar composition.
        if depth >= 3:
            prefixes: Counter[CanonicalTemplate] = Counter()
            for template, weight in self.template_weights.items():
                if len(template) >= depth - 1:
                    prefixes[template[: depth - 1]] += weight
            for macro, weight in self.macro_weights.items():
                if len(macro) == depth - 1:
                    prefixes[macro] += 1.5 * weight
            for prefix, weight in prefixes.items():
                if not prefix:
                    continue
                for role in r2p:
                    transition = self.transition_weights[(prefix[-1], role)]
                    if transition > 0.05:
                        sources[prefix + (role,)] += 0.8 * weight + 2.2 * transition
        rows: list[tuple[float, tuple[str, ...]]] = []
        for template, weight in sources.items():
            if any(role not in r2p for role in template):
                continue
            sequence = tuple(r2p[role] for role in template)
            transition = sum(self.transition_weights[(a, b)] for a, b in zip(template, template[1:]))
            score = self.energy * (weight + 0.30 * transition) - 0.08 * len(template) - 2.0 * cost
            rows.append((score, sequence))
        rows.sort(key=lambda row: (row[0], row[1]), reverse=True)
        output: list[tuple[str, ...]] = []
        for _, sequence in rows:
            if sequence not in output:
                output.append(sequence)
            if len(output) >= limit:
                break
        return output

    def posterior_proposals(
        self,
        model: "InquiryModel",
        mechanism: str,
        depth: int,
        primitives: tuple[str, ...],
        family: str,
        include_macros: bool = True,
        limit: int = 8,
    ) -> list[tuple[tuple[str, ...], float, CanonicalTemplate]]:
        """Project remembered canonical programs through multiple alignments.

        The returned confidence combines alignment posterior, independent held-out
        graph support, memory energy, and template weight. Quarantined template-family
        pairs are excluded.
        """
        if self.successes <= 0 or self.energy < 0.12:
            return []
        hypotheses = self.alignment_posterior(model, mechanism, primitives)
        if not hypotheses:
            return []
        sources: Counter[CanonicalTemplate] = Counter()
        for template, weight in self.template_weights.items():
            if len(template) == depth:
                sources[template] += 2.0 * weight
            elif len(template) > depth:
                sources[template[:depth]] += weight
        if include_macros:
            for macro, weight in self.macro_weights.items():
                if len(macro) == depth:
                    sources[macro] += 3.0 * weight
        if depth >= 3:
            prefixes: Counter[CanonicalTemplate] = Counter()
            for template, weight in self.template_weights.items():
                if len(template) >= depth - 1:
                    prefixes[template[: depth - 1]] += weight
            for macro, weight in self.macro_weights.items():
                if len(macro) == depth - 1:
                    prefixes[macro] += 1.5 * weight
            roles = range(self.prototype_size)
            for prefix, weight in prefixes.items():
                if not prefix:
                    continue
                for role in roles:
                    transition = self.transition_weights[(prefix[-1], role)]
                    if transition > 0.05:
                        sources[prefix + (role,)] += 0.8 * weight + 2.2 * transition

        total_source = sum(max(0.0, value) for value in sources.values()) or 1.0
        projected: dict[tuple[str, ...], tuple[float, CanonicalTemplate]] = {}
        for template, weight in sources.items():
            if self.is_quarantined(template, family):
                continue
            for hypothesis in hypotheses:
                if any(role not in hypothesis.role_to_primitive for role in template):
                    continue
                sequence = tuple(hypothesis.role_to_primitive[role] for role in template)
                transition = sum(self.transition_weights[(a, b)] for a, b in zip(template, template[1:]))
                memory_mass = max(0.0, weight + 0.30 * transition) / total_source
                confidence = (
                    hypothesis.posterior
                    * hypothesis.support
                    * self.energy
                    * min(1.0, 2.5 * memory_mass)
                    * max(0.15, 1.0 - 0.18 * self.family_distrust[family])
                )
                previous = projected.get(sequence)
                if previous is None:
                    projected[sequence] = (confidence, template)
                else:
                    # Posterior mass from distinct alignments may support the same
                    # concrete sequence. Sum that mass rather than selecting one map.
                    projected[sequence] = (previous[0] + confidence, previous[1])
        rows = [(sequence, confidence, template) for sequence, (confidence, template) in projected.items()]
        rows.sort(key=lambda row: (row[1], row[0]), reverse=True)
        return rows[:limit]

    def transition_prior(
        self,
        model: "InquiryModel",
        mechanism: str,
        sequence: tuple[str, ...],
        primitives: tuple[str, ...],
    ) -> float:
        p2r, _, cost = self.align(model, mechanism, primitives)
        if any(p not in p2r for p in sequence) or cost > 0.035:
            return 0.0
        roles = tuple(p2r[p] for p in sequence)
        total = sum(self.transition_weights.values())
        if total <= 0:
            return 0.0
        return self.energy * sum(self.transition_weights[pair] / total for pair in zip(roles, roles[1:]))

    def is_macro_reuse(
        self,
        model: "InquiryModel",
        mechanism: str,
        sequence: tuple[str, ...],
        primitives: tuple[str, ...],
    ) -> bool:
        p2r, _, cost = self.align(model, mechanism, primitives)
        if any(p not in p2r for p in sequence) or cost > 0.035:
            return False
        roles = tuple(p2r[p] for p in sequence)
        return any(
            weight > 0.10 and len(macro) <= len(roles)
            and any(roles[i : i + len(macro)] == macro for i in range(len(roles) - len(macro) + 1))
            for macro, weight in self.macro_weights.items()
        )
