"""Run a harness command with a wall-clock limit; capture time/stdout/stderr.

Uses coreutils `timeout` (present in every Gradescope base image and any
Linux/macOS environment) so that runaway submissions are killed reliably,
including their child processes. The command also runs in its own session, and
everything left in that session is killed when the command ends, so a
background process started by a submission cannot keep running into later
cases; stderr is captured through a file, so such a process cannot stall the
grader either.
"""

from __future__ import annotations

import os
import signal
import subprocess
import time

TIMEOUT_EXIT_CODE = 124  # coreutils timeout convention
KILL_AFTER = 5           # seconds `timeout` waits after SIGTERM before SIGKILL
# The longest a timed run can take past its limit: KILL_AFTER plus the hard stop below.
RUN_OVERHEAD = KILL_AFTER + 5


def _kill_session(pid: int) -> None:
    """SIGKILL every process left in the session led by `pid` (no-op if none)."""
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def run_command(cmd: list[str], stdout_path: str, maxtime: float | None = None,
                env: dict | None = None):
    """Run `cmd`, redirecting stdout to a file.

    `env`, if given, holds extra environment variables for the command.
    Returns (elapsed_seconds, exit_code, stderr_text).
    exit_code == TIMEOUT_EXIT_CODE indicates the time limit was hit.
    """
    if maxtime is not None:
        cmd = ["timeout", f"--kill-after={KILL_AFTER}", f"{maxtime}s"] + cmd
    full_env = dict(os.environ, **env) if env else None
    # Hard stop on the grader's side, in case something outlives `timeout`.
    hard_limit = None if maxtime is None else maxtime + RUN_OVERHEAD
    # stderr goes to a file, not a pipe: a background process that inherits it cannot make the
    # grader wait for the pipe to close.
    stderr_path = f"{stdout_path}.stderr"
    start = time.time()
    with open(stdout_path, "w") as fout, open(stderr_path, "wb") as ferr:
        proc = subprocess.Popen(cmd, stdout=fout, stderr=ferr, env=full_env,
                                start_new_session=True)
        try:
            code = proc.wait(timeout=hard_limit)
        except subprocess.TimeoutExpired:
            _kill_session(proc.pid)
            proc.wait()
            code = TIMEOUT_EXIT_CODE
        finally:                                # leftover background processes; also on Ctrl-C
            _kill_session(proc.pid)
    elapsed = time.time() - start
    with open(stderr_path, "rb") as fh:
        stderr = fh.read().decode(errors="replace")
    os.remove(stderr_path)
    return elapsed, code, stderr
