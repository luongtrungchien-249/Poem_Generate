"""Administrative commands; model-check never logs credentials."""

import argparse
import asyncio
import sys

from bootstrap.model_validation import validate_catalog, validate_remote_model
from bootstrap.settings import get_settings


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="ai-platform")
    parser.add_argument("command", choices=["model-check", "config-check", "worker"])
    args = parser.parse_args()
    try:
        settings = get_settings()
        if args.command == "worker":
            from entrypoints.worker.poem_jobs import main as worker_main

            asyncio.run(worker_main())
        elif args.command == "model-check":
            asyncio.run(validate_remote_model(settings))
            print(f"Model check OK: {settings.llm.default_provider}/{settings.llm.default_model}")
        else:
            validate_catalog(settings)
            print(f"Config OK: {settings.llm.default_provider}/{settings.llm.default_model}")
    except (ValueError, RuntimeError) as exc:
        print(str(exc))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
