"""Allow the package to run with ``python -m echo``."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())