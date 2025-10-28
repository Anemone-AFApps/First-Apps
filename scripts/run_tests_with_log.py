#!/usr/bin/env python3
"""Run the backend test suite and persist a detailed log."""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments forwarded to pytest.",
    )
    return parser.parse_args()


def ensure_log_path() -> Path:
    logs_dir = Path("logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return logs_dir / f"pytest-{timestamp}.log"


def run_pytest(pytest_args: list[str], log_path: Path) -> int:
    command = [sys.executable, "-m", "pytest", *pytest_args]
    header_lines = [
        "=" * 80,
        f"Pytest invocation at {dt.datetime.now().isoformat()}",
        f"Command: {' '.join(command)}",
        "=" * 80,
        "",
    ]
    header = "\n".join(header_lines)

    print(header)
    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write(header)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log_file.write(line)
        return_code = process.wait()

        footer = (
            "\n".join(
                [
                    "",
                    "=" * 80,
                    f"Completed at {dt.datetime.now().isoformat()} with exit code {return_code}",
                    "=" * 80,
                ]
            )
            + "\n"
        )
        print(footer, end="")
        log_file.write(footer)
    return return_code


def main() -> int:
    args = parse_args()
    log_path = ensure_log_path()
    exit_code = run_pytest(args.pytest_args, log_path)
    print(f"Detailed log written to {log_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
