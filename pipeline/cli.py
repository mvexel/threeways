from __future__ import annotations

import os
from pathlib import Path
from typing import Tuple

import click

try:  # Allow running as module or script
    from .import_osm import ImportConfig, run_import
except ImportError:  # pragma: no cover
    from import_osm import ImportConfig, run_import  # type: ignore


def _env_default(key: str, fallback: str | None = None) -> str | None:
    return os.environ.get(key, fallback)


def _default_flex_file() -> str:
    env_override = os.environ.get("PIPELINE_FLEX_FILE")
    if env_override:
        return env_override

    module_path = Path(__file__).resolve()
    for parent in module_path.parents:
        candidate = parent / "osm2pgsql" / "poi_age.lua"
        if candidate.exists():
            return str(candidate)

    cwd_candidate = Path.cwd() / "osm2pgsql" / "poi_age.lua"
    return str(cwd_candidate)


@click.group(help="CLI entrypoint for the threeways pipeline.")
@click.option(
    "--log-level",
    default=lambda: _env_default("PIPELINE_LOG_LEVEL", "INFO"),
    show_default="env PIPELINE_LOG_LEVEL or INFO",
    help="Minimum log level for Python logging (DEBUG, INFO, ...).",
)
def cli(log_level: str) -> None:
    import logging

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


@cli.command("import-osm", help="Load an .osm.pbf into PostGIS via osm2pgsql.")
@click.argument(
    "osm_file", type=click.Path(path_type=Path, exists=True, dir_okay=False)
)
@click.option(
    "--flex-file",
    "-f",
    type=click.Path(path_type=Path, exists=False, dir_okay=False),
    default=_default_flex_file,
    show_default="auto (env PIPELINE_FLEX_FILE or ./osm2pgsql/poi_age.lua)",
    help="osm2pgsql flex style to apply.",
)
@click.option(
    "--database",
    "-d",
    default=lambda: _env_default("PGDATABASE", "threeways"),
    show_default="env PGDATABASE or threeways",
    help="Target Postgres database.",
)
@click.option(
    "--username",
    "-U",
    default=lambda: _env_default("PGUSER", "postgres"),
    show_default="env PGUSER or postgres",
    help="Postgres role for the import.",
)
@click.option(
    "--password",
    "--pgpassword",
    default=lambda: _env_default("PGPASSWORD"),
    show_default="env PGPASSWORD",
    help="Optional password (or use .pgpass/ident).",
)
@click.option(
    "--host",
    "-h",
    default=lambda: _env_default("PGHOST", "localhost"),
    show_default="env PGHOST or localhost",
    help="Postgres host.",
)
@click.option(
    "--port",
    "-p",
    default=lambda: int(_env_default("PGPORT", "5432")),
    show_default="env PGPORT or 5432",
    type=int,
    help="Postgres port.",
)
@click.option(
    "--schema",
    "-s",
    default=lambda: _env_default("PGSCHEMA", "public"),
    show_default="env PGSCHEMA or public",
    help="Schema for imported tables.",
)
@click.option(
    "--cache",
    default=lambda: int(_env_default("OSM_CACHE", "1024")),
    show_default="env OSM_CACHE or 1024",
    type=int,
    help="Cache size in MB passed to osm2pgsql.",
)
@click.option(
    "--append",
    "append",
    is_flag=True,
    default=False,
    help="Append to existing tables instead of recreating them.",
)
@click.option(
    "--extra-flag",
    multiple=True,
    help="Additional raw flags forwarded to osm2pgsql (repeatable).",
)
def import_osm_command(
    osm_file: Path,
    flex_file: Path,
    database: str,
    username: str,
    password: str | None,
    host: str,
    port: int,
    schema: str,
    cache: int,
    append: bool,
    extra_flag: Tuple[str, ...],
) -> None:
    try:
        cfg = ImportConfig(
            osm_file=osm_file,
            flex_file=flex_file,
            database=database,
            username=username,
            password=password,
            host=host,
            port=port,
            schema=schema,
            cache=cache,
            append=append,
            extra_flags=extra_flag,
        )
    except FileNotFoundError as err:
        raise click.ClickException(str(err)) from err
    run_import(cfg)


@cli.command("refresh-metrics", help="Placeholder for H3/PostGIS metric refresh.")
def refresh_metrics_command() -> None:
    click.echo("TODO: implement metrics refresh command.")


@cli.command("build-tiles", help="Placeholder for tile generation/tippecanoe export.")
def build_tiles_command() -> None:
    click.echo("TODO: implement tile build command.")


if __name__ == "__main__":
    cli()
