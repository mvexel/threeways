"""
Helpers for running osm2pgsql imports.

The actual CLI wiring lives in ``pipeline.cli``; this module only contains
pure Python functions so orchestration layers (Airflow, tests, etc.) can
call them directly.
"""

from __future__ import annotations

import logging
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

logger = logging.getLogger(__name__)


@dataclass
class ImportConfig:
    osm_file: Path
    flex_file: Path
    database: str
    username: str
    host: str
    port: int = 5432
    schema: str = "public"
    cache: int = 1024
    append: bool = False
    password: str | None = None
    extra_flags: Sequence[str] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.osm_file.exists():
            raise FileNotFoundError(f"OSM file not found: {self.osm_file}")
        if not self.flex_file.exists():
            raise FileNotFoundError(f"Flex file not found: {self.flex_file}")


def build_command(cfg: ImportConfig) -> List[str]:
    """
    Convert ImportConfig into the osm2pgsql command list.
    """
    command = [
        "osm2pgsql",
        "--output",
        "flex",
        "--database",
        cfg.database,
        "--username",
        cfg.username,
        "--host",
        cfg.host,
        "--port",
        str(cfg.port),
        "--schema",
        cfg.schema,
        "--cache",
        str(cfg.cache),
        "--style",
        str(cfg.flex_file),
        "--hstore",
        "--slim",
    ]

    command.append("--append" if cfg.append else "--create")
    command.extend(cfg.extra_flags)
    command.append(str(cfg.osm_file))
    return command


def run_import(cfg: ImportConfig) -> None:
    """
    Execute osm2pgsql with the provided configuration.

    Password authentication is handled via PGPASSWORD environment variable.
    If no password is provided, PostgreSQL will fall back to .pgpass file or
    peer/trust authentication methods configured in pg_hba.conf.
    """
    command = build_command(cfg)
    logger.info("Importing %s into %s (%s)", cfg.osm_file, cfg.database, cfg.schema)

    env = os.environ.copy()
    # Set PGPASSWORD if provided for non-interactive authentication
    if cfg.password:
        env["PGPASSWORD"] = cfg.password

    subprocess.run(command, check=True, env=env)
    logger.info("Import finished successfully")
