try:
    from .main import main
except ImportError:  # pragma: no cover
    from main import main  # type: ignore


if __name__ == "__main__":
    main()
