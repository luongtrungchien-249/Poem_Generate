"""Reproducible 40/200 poetry eval, with safe artifacts and paired comparisons.

python evals/baseline.py --size 40 --prepare-only
python evals/baseline.py --size 40 --profile fixed
python evals/baseline.py --summarize evals/ket_qua/baseline_775b225.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import statistics
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from evals.do_that import _ctx, _DemLuotGoi, _yeu_cau  # noqa: E402

from adapters.observability.cost import CostCalculator  # noqa: E402
from adapters.persistence.corpus import duong_dan_mac_dinh  # noqa: E402
from adapters.persistence.corpus.chi_muc_dong import tep_dung_san_mac_dinh  # noqa: E402
from adapters.rate_limit.memory import InMemoryRateLimiter  # noqa: E402
from application.poetry.sinh_tho import CanLamRo, sinh_bai_tho  # noqa: E402
from application.poetry.tools import PoetryTools  # noqa: E402
from bootstrap.container import build_container, close_container  # noqa: E402
from bootstrap.model_validation import validate_catalog, validate_remote_model  # noqa: E402
from bootstrap.settings import get_settings  # noqa: E402
from domain.common.errors import BudgetExceeded  # noqa: E402
from domain.common.result import Err  # noqa: E402


class Meter(_DemLuotGoi):
    def __init__(self, inner, max_calls):
        super().__init__(inner)
        self.max_calls = max_calls
        self.errors = {}

    async def reply(self, messages, tools, ctx, model=None):
        if self.luot_reply >= self.max_calls:
            return Err(
                BudgetExceeded(
                    scope_name=ctx.scope.thread_id, limit=self.max_calls, current=self.luot_reply
                )
            )
        result = await super().reply(messages, tools, ctx, model)
        if isinstance(result, Err):
            error = type(result.error).__name__
            self.errors[error] = self.errors.get(error, 0) + 1
        return result

    async def cheap(self, messages, route, ctx):
        from domain.common.result import Ok

        self.luot_cheap += 1
        result = await self.reply(messages, (), ctx)
        return Ok(result.value.text) if not isinstance(result, Err) else result


def percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def summarize(rows):
    count = len(rows)
    passed = [row for row in rows if row.get("thanh_cong")]
    cost = sum(row.get("chi_phi_usd", 0) for row in rows)
    durations = [row.get("giay", 0) for row in rows]
    return {
        "count": count,
        "passed": len(passed),
        "pass_rate": len(passed) / count if count else None,
        "first_pass_rate": sum(row.get("so_luot") == 0 for row in passed) / count
        if count
        else None,
        "cost_usd": cost,
        "cost_per_1000": cost * 1000 / count if count else None,
        "cost_per_pass": cost / len(passed) if passed else None,
        "reply_mean": statistics.mean(row.get("luot_reply", 0) for row in rows) if rows else None,
        "input_tokens": sum(row.get("token_vao", 0) for row in rows),
        "output_tokens": sum(row.get("token_ra", 0) for row in rows),
        "cached_tokens": sum(row.get("token_cache", 0) for row in rows),
        "retry_429": sum(
            row.get("retry_counts", {}).get("429", row.get("lan_thu_lai_429", 0)) for row in rows
        ),
        "timeouts": sum(
            row.get("error_type") in ("TimeoutError", "UpstreamTimeout") for row in rows
        ),
        "p50_seconds": percentile(durations, 0.5),
        "p95_seconds": percentile(durations, 0.95),
        "by_length": {
            str(length): summarize([row for row in rows if row.get("so_dong_yc") == length])
            for length in sorted({row.get("so_dong_yc") for row in rows})
        }
        if len({row.get("so_dong_yc") for row in rows}) > 1
        else {},
    }


def write_summary(path, rows, manifest):
    summary = {"manifest": manifest, "metrics": summarize(rows)}
    path.with_suffix(".summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    metrics = summary["metrics"]
    lines = [
        "# Poetry evaluation",
        "",
        f"Completed: {len(rows)}/{manifest.get('expected_count', len(rows))}",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    lines += [f"| {key} | {value} |" for key, value in metrics.items() if key != "by_length"]
    lines += [
        "",
        "Costs exclude provider attempts without usage. Historical runs can also omit cheap usage. Prices are configured paid-tier estimates.",
        "",
        "## By length",
        "",
        "| Lines | Pass rate | Cost per pass | P95 seconds |",
        "|---|---:|---:|---:|",
    ]
    for length, group in metrics["by_length"].items():
        lines.append(
            f"| {length} | {group['pass_rate']} | {group['cost_per_pass']} | {group['p95_seconds']} |"
        )
    path.with_suffix(".summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def source_hash():
    digest = hashlib.sha256()
    for file in sorted((ROOT / "src").rglob("*.py")):
        digest.update(file.relative_to(ROOT).as_posix().encode())
        digest.update(file.read_bytes())
    return digest.hexdigest()


def corpus_hash():
    path = next((path for path in duong_dan_mac_dinh(ROOT) if path.exists()), None)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path else None


def file_hash(path):
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compare(control, treatment):
    left = [
        json.loads(line)
        for line in control.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    right = [
        json.loads(line)
        for line in treatment.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    def ids(rows):
        return [(row.get("id_de"), row.get("chu_de"), row.get("so_dong_yc")) for row in rows]

    if not left or ids(left) != ids(right):
        raise ValueError("A/B requires identical ordered questions and completed sample sizes")
    for field in ("model", "provider", "dataset_sha256"):
        if {row.get(field) for row in left} != {row.get(field) for row in right}:
            raise ValueError(f"A/B mismatch: {field}")
    for rows, path in ((left, control), (right, treatment)):
        manifest_path = path.with_suffix(".manifest.json")
        if not manifest_path.exists():
            raise ValueError(
                "A/B requires manifests; historical runs cannot be paired with live runs"
            )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("mode") != "live" or len(rows) != manifest.get("expected_count"):
            raise ValueError("A/B requires complete live runs")
    control_manifest = json.loads(control.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    treatment_manifest = json.loads(
        treatment.with_suffix(".manifest.json").read_text(encoding="utf-8")
    )
    for field in (
        "models_sha256",
        "corpus_sha256",
        "anti_copy_sha256",
        "rule_sha256",
        "runner_sha256",
        "concurrency",
        "max_calls_per_poem",
        "timeout_seconds",
        "candidate_ceiling",
        "repair_rounds",
        "seed",
    ):
        if control_manifest.get(field) != treatment_manifest.get(field):
            raise ValueError(f"A/B configuration mismatch: {field}")
    lm, rm = summarize(left), summarize(right)
    result = {"control": lm, "treatment": rm, "passed_control_only": 0, "passed_treatment_only": 0}
    result["passed_control_only"] = sum(
        a.get("thanh_cong") and not b.get("thanh_cong") for a, b in zip(left, right, strict=True)
    )
    result["passed_treatment_only"] = sum(
        b.get("thanh_cong") and not a.get("thanh_cong") for a, b in zip(left, right, strict=True)
    )
    return result


async def run(args):
    if args.summarize:
        rows = [
            json.loads(line)
            for line in args.summarize.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_summary(
            args.out,
            rows,
            {
                "kind": "historical",
                "expected_count": len(rows),
                "source": args.summarize.resolve().relative_to(ROOT).as_posix(),
            },
        )
        return 0
    if args.compare:
        result = compare(*args.compare)
        args.out.with_suffix(".comparison.json").parent.mkdir(parents=True, exist_ok=True)
        args.out.with_suffix(".comparison.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        return 0
    dataset = ROOT / "evals/datasets/de_danh_gia.jsonl"
    questions = [
        json.loads(line)
        for line in dataset.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ][: args.size]
    settings = get_settings()
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"
    manifest = {
        "created_at": datetime.now(UTC).isoformat(),
        "commit": commit,
        "source_sha256": source_hash(),
        "dataset_sha256": hashlib.sha256(dataset.read_bytes()).hexdigest(),
        "models_sha256": hashlib.sha256(settings.models_catalog_path.read_bytes()).hexdigest(),
        "corpus_sha256": corpus_hash(),
        "anti_copy_sha256": file_hash(tep_dung_san_mac_dinh(ROOT)),
        "rule_sha256": file_hash(ROOT / "src/application/rule.py"),
        "runner_sha256": file_hash(Path(__file__)),
        "provider": settings.llm.default_provider,
        "model": settings.llm.default_model,
        "expected_count": args.size,
        "profile": args.profile,
        "candidate_ceiling": 32,
        "concurrency": settings.llm.so_song_song,
        "repair_rounds": 3,
        "max_calls_per_poem": args.max_calls,
        "timeout_seconds": args.timeout,
        "seed": None,
        "mode": "prepared" if args.prepare_only else "live",
    }
    path = args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not args.prepare_only:
        raise ValueError("Output exists; select a new --out path")
    path.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if args.prepare_only:
        print(
            f"Prepared {args.size} questions; no model calls: {path.with_suffix('.manifest.json')}"
        )
        return 0
    if settings.llm.default_provider == "mock":
        raise ValueError("Live baseline cannot use mock")
    validate_catalog(settings)
    await validate_remote_model(settings)
    container = build_container(settings)
    if type(container.default_llm).__name__ == "MockLLMClient":
        await close_container(container)
        raise ValueError("Live baseline cannot use fallback mock")
    cost = CostCalculator(str(settings.models_catalog_path))
    rows = []
    # Eval budgets are per poem, not production tenant quotas. All calls still
    # pass through Meter; tools cannot start unmetered recursive generation.
    eval_limiter = InMemoryRateLimiter(so_lan_goi_model_moi_ngay=1_000_000)
    with path.open("x", encoding="utf-8") as output:
        for index, question in enumerate(questions):
            meter = Meter(container.chat_llm, args.max_calls)
            retries_before = dict(container.chat_llm.retry_counts)
            started = time.monotonic()
            row = {
                "id_de": question["id"],
                "chu_de": question["chu_de"],
                "so_dong_yc": question["so_dong"],
                "thanh_cong": False,
                "so_luot": 0,
                **{
                    key: manifest[key]
                    for key in ("model", "provider", "dataset_sha256", "profile", "source_sha256")
                },
            }
            try:
                async with asyncio.timeout(args.timeout):
                    result = await sinh_bai_tho(
                        _yeu_cau(question["chu_de"], question["so_dong"]),
                        llm=meter,
                        tools=PoetryTools(container.tools),
                        rate_limiter=eval_limiter,
                        ctx=_ctx(index),
                        corpus=container.poem_corpus,
                        verifier=container.poem_verifier,
                        default_model=container.default_model,
                        timeout_sec=args.timeout,
                        so_song_song=settings.llm.so_song_song,
                        adaptive_candidates=args.profile == "adaptive",
                        line_framing=args.profile == "line",
                    )
                if isinstance(result, Err):
                    row["error_type"] = type(result.error).__name__
                    row["so_luot"] = getattr(result.error, "so_luot_da_sua", 0)
                elif isinstance(result.value, CanLamRo):
                    row["error_type"] = "CanLamRo"
                else:
                    poem = result.value
                    row.update(
                        thanh_cong=True,
                        so_luot=poem.so_luot,
                        bai_tho=poem.text,
                        bo_sinh=poem.bo_sinh,
                        duong_di=list(poem.duong_di),
                    )
            except TimeoutError:
                row["error_type"] = "TimeoutError"
            except Exception as exc:
                row["error_type"] = type(exc).__name__
            row.update(
                giay=time.monotonic() - started,
                luot_reply=meter.luot_reply,
                luot_cheap=meter.luot_cheap,
                token_vao=meter.token_vao,
                token_ra=meter.token_ra,
                token_cache=meter.token_cache,
                errors=meter.errors,
                retry_counts={
                    key: value - retries_before.get(key, 0)
                    for key, value in container.chat_llm.retry_counts.items()
                },
                chi_phi_usd=cost.calculate_cost(
                    container.default_model,
                    meter.token_vao + meter.token_cache,
                    meter.token_ra,
                    meter.token_cache,
                ),
            )
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
            output.flush()
            rows.append(row)
            write_summary(path, rows, manifest)
            print(
                f"{index + 1}/{len(questions)}: pass={row['thanh_cong']} calls={meter.luot_reply}",
                flush=True,
            )
    await close_container(container)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, choices=[40, 200], default=40)
    parser.add_argument("--profile", choices=["fixed", "adaptive", "line"], default="fixed")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--max-calls", type=int, default=80)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT
        / "evals/ket_qua"
        / f"run_{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%f')}.jsonl",
    )
    parser.add_argument("--summarize", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path, metavar=("CONTROL", "TREATMENT"))
    args = parser.parse_args()
    if args.max_calls < 1 or args.timeout <= 0:
        parser.error("Budgets must be positive")
    try:
        return asyncio.run(run(args))
    except (ValueError, RuntimeError) as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
