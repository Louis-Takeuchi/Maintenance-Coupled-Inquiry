from __future__ import annotations

import argparse
from pathlib import Path

from constitutive_inquiry.chunking import merge_unified_chunks


def _csv_values(text: str) -> list[str] | None:
    values = [value.strip() for value in text.split(",") if value.strip()]
    return values or None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge Paper B unified execution chunks with key audit.")
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--split", default="development")
    parser.add_argument("--expected-seeds", default="")
    parser.add_argument("--expected-relevances", default="")
    parser.add_argument("--expected-conditions", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seed_values = _csv_values(args.expected_seeds)
    audit = merge_unified_chunks(
        [Path(value) for value in args.inputs],
        Path(args.output),
        split=args.split,
        expected_seeds=[int(value) for value in seed_values] if seed_values else None,
        expected_relevances=_csv_values(args.expected_relevances),
        expected_conditions=_csv_values(args.expected_conditions),
    )
    print(f"merged chunks: {audit}")


if __name__ == "__main__":
    main()
