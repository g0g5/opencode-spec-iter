#!/usr/bin/env python3
"""Backward-compatible installer entrypoint."""

from spec_iter.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
