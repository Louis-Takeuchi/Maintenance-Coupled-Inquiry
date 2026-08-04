from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROTOCOL_VERSION = "v0.3"
APPROVAL_TOKEN = "EXECUTE_PAPER_B_CONFIRMATION_V0_3"


class ConfirmationLocked(RuntimeError):
    """Raised when confirmatory execution has not been explicitly activated."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def validate_activation(pre_run_path: Path, activation_path: Path) -> dict[str, Any]:
    """Validate the explicit human activation manifest.

    The repository intentionally ships without an activation manifest. Merely
    preparing or hashing the confirmatory plan cannot start an outcome episode.
    """

    if not pre_run_path.exists():
        raise ConfirmationLocked(f"pre-run manifest missing: {pre_run_path}")
    if not activation_path.exists():
        raise ConfirmationLocked(
            "confirmation is locked: no activation manifest exists; "
            "Phase U1.5 preparation does not authorize outcome execution"
        )

    pre_run = read_json(pre_run_path)
    activation = read_json(activation_path)
    if pre_run.get("status") != "LOCKED_NOT_ACTIVATED":
        raise ConfirmationLocked("pre-run manifest is not in the expected locked state")
    if activation.get("status") != "ACTIVATED_BY_EXPLICIT_USER_APPROVAL":
        raise ConfirmationLocked("activation status is invalid")
    if activation.get("approval_token") != APPROVAL_TOKEN:
        raise ConfirmationLocked("activation approval token is invalid")
    if activation.get("protocol_version") != PROTOCOL_VERSION:
        raise ConfirmationLocked("activation protocol version mismatch")
    expected_hash = pre_run.get("freeze_candidate_manifest_sha256")
    if not expected_hash or activation.get("freeze_candidate_manifest_sha256") != expected_hash:
        raise ConfirmationLocked("activation is not anchored to the frozen candidate manifest")
    if activation.get("pre_run_manifest_sha256") != sha256_file(pre_run_path):
        raise ConfirmationLocked("activation is not anchored to the current pre-run manifest")
    return activation
