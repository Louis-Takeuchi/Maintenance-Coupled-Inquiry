from __future__ import annotations

from statistics import mean

from .agent import StepRecord
from .environment import WorldSpec, intervention_space_size


def summarize_run(records: list[StepRecord], spec: WorldSpec, budget: int) -> dict:
    if not records:
        raise ValueError("records must not be empty")
    final = records[-1]
    diagnoses = [row for row in records if row.diagnosis_made]
    first = diagnoses[0] if diagnoses else None
    repairs = [row for row in records if row.repair_attempted]
    replications = [row for row in records if row.replication_attempted]
    final_core = {int(x) for x in final.predicted_core.split(",") if x}
    true_core = set(spec.core_indices)
    precision = len(final_core & true_core) / len(final_core) if final_core else 0.0
    recall = len(final_core & true_core) / len(true_core)
    repair_correct = any(row.repair_correct for row in repairs)
    replication_success = any(row.replication_success for row in replications)
    explicit_null = int(first is not None and first.diagnosis_kind == "no_bridge")
    false_null = int(spec.relevance == "self_relevant" and explicit_null)
    false_repair = int(spec.relevance == "neutral" and bool(repairs))
    exact_program = int(first is not None and first.mechanism_correct and first.exact_program)
    functional_program = int(first is not None and first.mechanism_correct and first.functional_program)
    restored = int(repair_correct and final.internal_min_core >= 0.55)
    replicated = int(restored and (replication_success or not replications))
    decision_correct = int((spec.relevance == "self_relevant" and restored) or (spec.relevance == "neutral" and not repairs))
    restoration_row = next((row for row in records if row.repair_correct), None)
    diagnosis_observations = (first.observation_index + 1) if first else budget + 1
    restoration_observations = (restoration_row.observation_index + 1) if restoration_row else budget + 1
    return {
        "split": final.split,
        "seed": final.seed,
        "relevance": spec.relevance,
        "mode": final.mode,
        "core_indices": ",".join(map(str, spec.core_indices)),
        "core_size": spec.core_size,
        "topology": spec.topology,
        "causal_mechanism": spec.causal_mechanism,
        "nuisance_mechanism": spec.nuisance_mechanism,
        "true_program": ">".join(spec.intervention_program),
        "program_length": spec.program_length,
        "grammar_family": spec.grammar_family,
        "role_program": ">".join(spec.role_program),
        "label_permuted": int(spec.label_permuted),
        "primitive_cardinality": len(spec.available_primitives),
        "active_roles": ">".join(spec.active_roles),
        "nonstationary": int(spec.nonstationary),
        "steps_survived": len(records),
        "alive_at_end": int(final.alive),
        "completion_rate": len(records) / budget,
        "core_precision": precision,
        "core_recall": recall,
        "exact_program": exact_program,
        "functional_program": functional_program,
        "max_sequence_length_tested": max(row.intervention_length for row in records),
        "unique_sequences_evaluated": final.unique_sequences_evaluated,
        "search_space_fraction": final.unique_sequences_evaluated / intervention_space_size(primitive_count=len(spec.available_primitives)),
        "diagnosis_made": int(first is not None),
        "diagnosis_observations": diagnosis_observations,
        "restoration_observations": restoration_observations,
        "diagnosis_kind_bridge": int(first is not None and first.diagnosis_kind == "bridge"),
        "explicit_no_bridge": explicit_null,
        "false_null": false_null,
        "mechanism_correct": int(first is not None and first.mechanism_correct),
        "bridge_decision_correct": int(first is not None and first.bridge_correct),
        "suppression": first.suppression if first else 0.0,
        "bridge_effect": first.bridge_effect if first else 0.0,
        "evidence_rows": first.evidence_rows if first else 0,
        "tested_scope_declared": int(bool(first and first.tested_scope)),
        "validation_attempted": int(any(row.validation_attempted for row in records)),
        "validation_passed": int(any(row.validation_passed for row in records)),
        "validation_effect": max((row.validation_effect for row in records), default=0.0),
        "repair_attempted": int(bool(repairs)),
        "repair_attempt_count": len(repairs),
        "false_repair": false_repair,
        "repair_correct": int(repair_correct),
        "organization_restored": restored,
        "replication_attempted": int(bool(replications)),
        "replication_success": int(replication_success),
        "replicated_restoration": replicated,
        "failed_repairs": final.failed_repairs,
        "appropriate_abstention": int(spec.relevance == "neutral" and not repairs),
        "scientific_null_result": int(spec.relevance == "neutral" and explicit_null and not repairs),
        "decision_correct": decision_correct,
        "final_min_core": final.internal_min_core,
        "final_mean_core": final.internal_mean_core,
        "total_cost": final.total_cost,
        "crossworld_successes": final.crossworld_successes,
        "crossworld_templates": final.crossworld_templates,
        "macro_reuse": int(final.macro_reuse),
        "relational_alignment_cost": final.relational_alignment_cost,
        "memory_energy": final.memory_energy,
        "memory_strategy": final.memory_strategy,
        "alignment_entropy": final.alignment_entropy,
        "alignment_support": final.alignment_support,
        "mapping_trust": final.mapping_trust,
        "memory_proposal_tested": int(final.memory_proposal_tested),
        "memory_changed_action": int(final.memory_changed_action),
        "wrong_memory_detected_before_repair": int(final.wrong_memory_detected_before_repair),
        "local_beam_reserved": int(final.local_beam_reserved),
        "quarantined_count": final.quarantined_count,
    }


def aggregate(rows: list[dict]) -> list[dict]:
    keys = sorted({(
        row["split"], row["relevance"], row["mode"], row["core_size"], row["program_length"],
        row.get("grammar_family", ""), row.get("label_permuted", 0), row.get("nonstationary", 0),
    ) for row in rows})
    excluded = {
        "split", "seed", "relevance", "mode", "core_indices", "core_size", "topology",
        "causal_mechanism", "nuisance_mechanism", "true_program", "program_length",
        "grammar_family", "role_program", "label_permuted", "active_roles", "memory_strategy", "nonstationary",
    }
    output: list[dict] = []
    for split, relevance, mode, core_size, program_length, grammar_family, label_permuted, nonstationary in keys:
        group = [row for row in rows if (
            row["split"], row["relevance"], row["mode"], row["core_size"], row["program_length"],
            row.get("grammar_family", ""), row.get("label_permuted", 0), row.get("nonstationary", 0),
        ) == (split, relevance, mode, core_size, program_length, grammar_family, label_permuted, nonstationary)]
        item = {
            "split": split, "relevance": relevance, "mode": mode, "core_size": core_size,
            "program_length": program_length, "grammar_family": grammar_family,
            "label_permuted": label_permuted, "nonstationary": nonstationary, "runs": len(group),
        }
        for field in group[0]:
            if field in excluded:
                continue
            item[field] = mean(float(row[field]) for row in group)
        output.append(item)
    return output
