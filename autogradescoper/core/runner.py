"""Run a harness command with a wall-clock limit; capture time/stdout/stderr.

Uses coreutils `timeout` (present in every Gradescope base image and any
Linux/macOS environment) so that runaway submissions are killed reliably,
including their child processes.
"""

from __future__ import annotations

import os
import subprocess
import time

TIMEOUT_EXIT_CODE = 124  # coreutils timeout convention


def run_command(cmd: list[str], stdout_path: str, maxtime: float | None = None,
                env: dict | None = None):
    """Run `cmd`, redirecting stdout to a file.

    `env`, if given, holds extra environment variables for the command.
    Returns (elapsed_seconds, exit_code, stderr_text).
    exit_code == TIMEOUT_EXIT_CODE indicates the time limit was hit.
    """
    if maxtime is not None:
        cmd = ["timeout", "--kill-after=5", f"{maxtime}s"] + cmd
    full_env = dict(os.environ, **env) if env else None
    start = time.time()
    with open(stdout_path, "w") as fout:
        proc = subprocess.run(cmd, stdout=fout, stderr=subprocess.PIPE, env=full_env)
    elapsed = time.time() - start
    stderr = proc.stderr.decode(errors="replace") if proc.stderr else ""
    return elapsed, proc.returncode, stderr
