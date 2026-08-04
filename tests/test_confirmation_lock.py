from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from constitutive_inquiry.confirmation_lock import (
    APPROVAL_TOKEN,
    ConfirmationLocked,
    validate_activation,
)


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_confirmation_requires_activation_manifest(tmp_path: Path):
    pre = tmp_path / "pre.json"
    _write_json(pre, {"status": "LOCKED_NOT_ACTIVATED", "freeze_candidate_manifest_sha256": "abc"})
    with pytest.raises(ConfirmationLocked):
        validate_activation(pre, tmp_path / "missing.json")


def test_confirmation_rejects_unanchored_activation(tmp_path: Path):
    pre = tmp_path / "pre.json"
    activation = tmp_path / "activation.json"
    _write_json(pre, {"status": "LOCKED_NOT_ACTIVATED", "freeze_candidate_manifest_sha256": "abc"})
    _write_json(
        activation,
        {
            "status": "ACTIVATED_BY_EXPLICIT_USER_APPROVAL",
            "approval_token": APPROVAL_TOKEN,
            "protocol_version": "v0.3",
            "freeze_candidate_manifest_sha256": "wrong",
            "pre_run_manifest_sha256": hashlib.sha256(pre.read_bytes()).hexdigest(),
        },
    )
    with pytest.raises(ConfirmationLocked):
        validate_activation(pre, activation)


def test_confirmation_accepts_fully_anchored_activation(tmp_path: Path):
    pre = tmp_path / "pre.json"
    activation = tmp_path / "activation.json"
    _write_json(pre, {"status": "LOCKED_NOT_ACTIVATED", "freeze_candidate_manifest_sha256": "abc"})
    _write_json(
        activation,
        {
            "status": "ACTIVATED_BY_EXPLICIT_USER_APPROVAL",
            "approval_token": APPROVAL_TOKEN,
            "protocol_version": "v0.3",
            "freeze_candidate_manifest_sha256": "abc",
            "pre_run_manifest_sha256": hashlib.sha256(pre.read_bytes()).hexdigest(),
        },
    )
    assert validate_activation(pre, activation)["approval_token"] == APPROVAL_TOKEN
