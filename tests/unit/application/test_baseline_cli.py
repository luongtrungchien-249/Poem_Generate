import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("size", [40, 200])
def test_prepare_manifest_without_model_calls(tmp_path, size):
    root = Path(__file__).resolve().parents[3]
    output = tmp_path / "prepared.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "evals/baseline.py",
            "--size",
            str(size),
            "--prepare-only",
            "--out",
            str(output),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads(output.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    assert manifest["expected_count"] == size and manifest["mode"] == "prepared"
    assert manifest["corpus_sha256"] and manifest["source_sha256"]
    assert not output.exists()
    assert "api_key" not in str(manifest).lower()


def test_historical_summary_keeps_raw_input_unchanged(tmp_path):
    root = Path(__file__).resolve().parents[3]
    raw = root / "evals/ket_qua/baseline_775b225.jsonl"
    before = raw.read_bytes()
    output = tmp_path / "historical.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "evals/baseline.py",
            "--summarize",
            "evals/ket_qua/baseline_775b225.jsonl",
            "--out",
            str(output),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    summary = json.loads(output.with_suffix(".summary.json").read_text(encoding="utf-8"))
    assert summary["manifest"]["kind"] == "historical"
    assert summary["metrics"]["count"] == 200
    assert raw.read_bytes() == before
