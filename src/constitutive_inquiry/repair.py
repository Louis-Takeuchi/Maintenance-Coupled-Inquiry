from __future__ import annotations

from typing import Sequence

from .environment import N_INTERNAL


def select_need_blind_restore_operator(
    world,
    target_index: int,
    self_probabilities: Sequence[float],
) -> str:
    """Select a restore operator without receiving need or policy identity."""

    if len(self_probabilities) != N_INTERNAL:
        raise ValueError(f"expected {N_INTERNAL} self probabilities")
    priority = [
        0.68 * float(index == target_index) + 0.32 * float(self_probabilities[index])
        for index in range(N_INTERNAL)
    ]
    best_operator = next(iter(world.restore_targets))
    best_score = float("-inf")
    for operator in world.restore_targets:
        probe = world.probe_restore(operator)
        score = sum(delta * weight for delta, weight in zip(probe.delta, priority))
        if score > best_score:
            best_operator, best_score = operator, score
    return best_operator
