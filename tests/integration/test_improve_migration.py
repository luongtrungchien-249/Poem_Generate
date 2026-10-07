"""Migration tests do not touch the developer's DATABASE_URL."""

import subprocess
import sys
from pathlib import Path

from sqlalchemy import inspect

from adapters.persistence.sql.engine import tao_engine


async def test_upgrade_and_metadata_parity(isolated_sql_dsn):
    root = Path(__file__).resolve().parents[2]
    dsn = isolated_sql_dsn
    for command in ("upgrade", "check"):
        args = [sys.executable, "-m", "alembic", "-x", f"dsn={dsn}", command]
        if command == "upgrade":
            args.append("head")
        result = subprocess.run(args, cwd=root, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
    engine = tao_engine(dsn)
    try:
        async with engine.connect() as connection:
            tables = await connection.run_sync(lambda conn: inspect(conn).get_table_names())
            assert {"poem_jobs", "poem_job_gate"} <= set(tables)
    finally:
        await engine.dispose()
