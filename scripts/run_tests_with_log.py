#!/usr/bin/env python3
"""Run the backend test suite and persist a detailed log."""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
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


def update_latest_log(latest_log: Path, source_log: Path) -> None:
    """Copy the generated log to a deterministic location for version control."""
    latest_log.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_log, latest_log)


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

        outcome = "SUCCESS" if return_code == 0 else "FAILURE"
        footer = (
            "\n".join(
                [
                    "",
                    "=" * 80,
                    f"Completed at {dt.datetime.now().isoformat()} with exit code {return_code}",
                    f"Overall result: {outcome}",
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
    latest_log_path = log_path.with_name("pytest-latest.log")
    update_latest_log(latest_log_path, log_path)
    print(f"Latest log mirrored to {latest_log_path}")
    print(f"Detailed log written to {log_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
