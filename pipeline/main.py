from __future__ import annotations

try:  # Allow running as module or script
    from .cli import cli
except ImportError:  # pragma: no cover
    from cli import cli  # type: ignore


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
