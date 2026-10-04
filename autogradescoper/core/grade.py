"""Language-agnostic grading engine: case -> problem -> assignment.

The output of :func:`grade_assignment` is a Gradescope-compatible results
dictionary (https://gradescope-autograders.readthedocs.io/en/latest/specs/).
"""

from __future__ import annotations

import os
import shutil

from autogradescoper.core.config import Assignment, Case, Problem
from autogradescoper.core.io import diff_texts, truncate
from autogradescoper.core.runner import TIMEOUT_EXIT_CODE, run_command
from autogradescoper.langs.base import get_backend

MAX_SHOW_CHARS = 500

# Given code (an `entry:` file) may report the time of the student's function alone by writing
# a number of seconds to the file named in this environment variable; the leaderboard and the
# per-case feedback use it instead of the wall time of the whole case (interpreter start-up,
# data simulation and output formatting included).
TIMING_ENV = "AUTOGRADESCOPER_TIMING_FILE"


def _run_with_timing(cmd: list[str], out_prefix: str, maxtime: float | None):
    """run_command plus the optional function time reported through TIMING_ENV."""
    timing_path = f"{out_prefix}.timing"
    if os.path.exists(timing_path):
        os.remove(timing_path)
    elapsed, code, err = run_command(cmd, f"{out_prefix}.stdout", maxtime=maxtime,
                                     env={TIMING_ENV: os.path.abspath(timing_path)})
    func_time = None
    try:
        with open(timing_path) as fh:
            func_time = float(fh.read().split()[0])
    except (OSError, ValueError, IndexError):
        pass
    return elapsed, code, err, func_time


def grade_case(problem: Problem, case: Case, solution_path: str,
               submission_path: str, out_prefix: str,
               solution_out_cache: dict | None = None) -> dict:
    """Grade one test case; returns a result dict.

    status: pass | incorrect | timeout | error
    """
    backend = get_backend(problem.lang)

    # --- solution side (cached across submissions during `validate`) --------
    cache_key = (solution_path, case.args)
    sol_out = None
    sol_time = None
    if solution_out_cache is not None:
        sol_out = solution_out_cache.get(cache_key)
        sol_time = solution_out_cache.get(("time",) + cache_key)
    if sol_out is None:
        sol_prefix = f"{out_prefix}.sol"
        harness = backend.write_harness(
            problem.func, sol_prefix, solution_path, case.args,
            problem.digits, problem.format, [problem.preload_sol],
            entry_path=problem.entry)
        elapsed, code, err, sol_time = _run_with_timing(backend.command(harness),
                                                        sol_prefix, maxtime=None)
        if code != 0:
            raise RuntimeError(
                f"SOLUTION failed on {os.path.basename(case.args)} "
                f"(exit {code}). This is an authoring error, not a submission "
                f"error.\n{truncate(err, 2000)}")
        with open(f"{sol_prefix}.out") as fh:
            sol_out = fh.read().strip()
        if solution_out_cache is not None:
            solution_out_cache[cache_key] = sol_out
            solution_out_cache[("time",) + cache_key] = sol_time

    # --- submission side -----------------------------------------------------
    usr_prefix = f"{out_prefix}.usr"
    try:
        harness = backend.write_harness(
            problem.func, usr_prefix, submission_path, case.args,
            problem.digits, problem.format, [problem.preload],
            entry_path=problem.entry)
    except ValueError as e:
        return {"status": "error", "elapsed": 0.0, "score": 0.0,
                "details": f"ERROR building test harness: {e}", "diffs": "", "errors": str(e)}

    elapsed, code, err, func_time = _run_with_timing(backend.command(harness), usr_prefix,
                                                     maxtime=case.maxtime)

    result = {"elapsed": round(elapsed, 3), "diffs": "", "errors": "",
              "func_time": func_time, "sol_func_time": sol_time}
    if code == TIMEOUT_EXIT_CODE or elapsed >= case.maxtime:
        result.update(status="timeout", score=0.0, details=(
            f"TIMEOUT: terminated at {elapsed:.2f}s "
            f"(limit: {case.maxtime}s)."))
    elif code != 0:
        result.update(status="error", score=0.0,
                      details=f"ERROR: the code exited with code {code}.",
                      errors=truncate(err, MAX_SHOW_CHARS))
    else:
        try:
            with open(f"{usr_prefix}.out") as fh:
                usr_out = fh.read().strip()
        except FileNotFoundError:
            usr_out = ""
        if usr_out == sol_out:
            result.update(status="pass", score=case.maxscore,
                          details="PASS: output matches the expected output.")
        else:
            result.update(status="incorrect", score=0.0,
                          details=("INCORRECT output.\n"
                                   f"Expected: {truncate(sol_out, MAX_SHOW_CHARS)}\n"
                                   f"Observed: {truncate(usr_out, MAX_SHOW_CHARS)}"),
                          diffs=diff_texts(sol_out, usr_out, MAX_SHOW_CHARS))
    return result


def find_submission_file(submission_dir: str, expected: str):
    """Locate the student's file for a problem, tolerating filename case.

    Returns (path, note). An exact match wins. Otherwise the submission
    directory is scanned for a file whose name matches `expected`
    case-insensitively (e.g. `foo.r` for `foo.R`, `Foo.py` for `foo.py`);
    a unique match is used, and `note` records the substitution so the
    student sees it in the feedback. If nothing matches, `path` is None and
    `note` lists the files that were submitted, to make the mismatch obvious.
    """
    try:
        entries = sorted(os.listdir(submission_dir))
    except OSError:
        return None, ""
    # Compare against the real directory entries (not os.path.exists) so the
    # behavior is identical on case-insensitive (macOS) and case-sensitive
    # (Linux / Gradescope) filesystems.
    if expected in entries:
        return os.path.join(submission_dir, expected), ""
    matches = [e for e in entries if e.lower() == expected.lower()
               and os.path.isfile(os.path.join(submission_dir, e))]
    if len(matches) == 1:
        return (os.path.join(submission_dir, matches[0]),
                f" (submitted as '{matches[0]}'; matched case-insensitively — "
                f"please name it '{expected}' next time)")
    files = [e for e in entries if os.path.isfile(os.path.join(submission_dir, e))
             and not e.startswith(".")]
    listing = ", ".join(files[:20]) + (" ..." if len(files) > 20 else "")
    return None, f" Files found in your submission: {listing or '(none)'}."


def grade_problem(problem: Problem, solution_dir: str, submission_dir: str,
                  out_prefix: str, show: dict | None = None,
                  solution_out_cache: dict | None = None) -> dict:
    """Grade all cases of one problem; returns a Gradescope test entry."""
    show = show or {}
    backend = get_backend(problem.lang)
    solution_path = problem.solution_file or os.path.join(
        solution_dir, problem.submission_filename())
    submission_path, note = find_submission_file(
        submission_dir, problem.submission_filename())

    if submission_path is None:
        return {"name": problem.name, "score": 0.0,
                "max_score": sum(c.maxscore for c in problem.cases),
                "output": (f"MISSING FILE: expected a submission named "
                           f"'{problem.submission_filename()}'." + note),
                "status": "failed",
                "_leaderboard_time": sum(c.maxtime for c in problem.cases)}
    if note:
        # A case-insensitive match (e.g. 'foo.PY'): grade a copy under the
        # expected name so every language backend sees the suffix it expects
        # (Python's import machinery selects its loader by exact suffix).
        normalized = f"{out_prefix}.{problem.submission_filename()}"
        os.makedirs(os.path.dirname(os.path.abspath(normalized)), exist_ok=True)
        shutil.copyfile(submission_path, normalized)
        submission_path = normalized

    total, chunks = 0.0, []
    elapsed_sum = 0.0
    lb_time = 0.0       # leaderboard time: a case that does not pass counts as its maxtime
    for i, case in enumerate(problem.cases, 1):
        try:
            r = grade_case(problem, case, solution_path, submission_path,
                           f"{out_prefix}.{i}", solution_out_cache)
        except RuntimeError as e:
            # Solution-side failure: an authoring/infrastructure error.
            # Score 0 for the case but keep grading; surface the cause in the
            # (instructor-visible) results rather than crashing the run.
            r = {"status": "error", "score": 0.0, "elapsed": 0.0,
                 "details": str(e), "diffs": "", "errors": str(e)}
        total += r["score"]
        elapsed_sum += r["elapsed"]
        ft = r.get("func_time")
        lb_time += (ft if ft is not None else r["elapsed"]) if r["status"] == "pass" else case.maxtime
        chunk = f"Case {i}: {r['status']} ({r['score']}/{case.maxscore}) in {r['elapsed']}s"
        if ft is not None:
            chunk += f"; your function {ft:.3f}s"
            if r.get("sol_func_time") is not None:
                chunk += f" (reference {r['sol_func_time']:.3f}s)"
        if show.get("args"):
            chunk += "\n" + backend.describe_args(case.args)
        if show.get("details") and r["details"]:
            chunk += "\n" + r["details"]
        if show.get("diffs") and r["diffs"]:
            chunk += "\n" + r["diffs"]
        if show.get("errors") and r["errors"]:
            chunk += "\n" + r["errors"]
        chunks.append(chunk)

    max_score = sum(c.maxscore for c in problem.cases)
    lb_note = (f" | leaderboard time: {lb_time:.3f}s (a case that does not pass counts as "
               f"its time limit)" if problem.leaderboard else "")
    return {
        "name": f"{problem.name} ({problem.lang})",
        "score": total,
        "max_score": max_score,
        "output": (f"Score: {total}/{max_score} | total time: {elapsed_sum:.2f}s" + lb_note
                   + (f"\nNOTE: file{note}" if note else "") + "\n"
                   + "\n--------------------------------\n".join(chunks)),
        "status": "passed" if total == max_score else "failed",
        "_leaderboard_time": lb_time,
    }


def grade_assignment(assignment: Assignment, solution_dir: str,
                     submission_dir: str, out_prefix: str,
                     show: dict | None = None,
                     solution_out_cache: dict | None = None) -> dict:
    """Grade the whole assignment; returns the Gradescope results dict."""
    os.makedirs(os.path.dirname(os.path.abspath(out_prefix)), exist_ok=True)
    tests = []
    for problem in assignment.problems:
        tests.append(grade_problem(
            problem, solution_dir, submission_dir,
            f"{out_prefix}.{problem.file}", show, solution_out_cache))

    score = sum(t["score"] for t in tests)
    max_score = sum(t["max_score"] for t in tests)
    leaderboard = [{"name": "Score", "value": score}]
    lb_total = 0.0
    for problem, t in zip(assignment.problems, tests):
        lb_time = t.pop("_leaderboard_time", None)   # private key: not part of Gradescope's format
        if problem.leaderboard and lb_time is not None:
            leaderboard.append({"name": problem.leaderboard, "value": round(lb_time, 3),
                                "order": "asc"})
            lb_total += lb_time
    if assignment.leaderboard_total:
        leaderboard.append({"name": assignment.leaderboard_total, "value": round(lb_total, 3),
                            "order": "asc"})
    return {
        "score": score,
        "output": f"Total Score: {score}/{max_score}",
        "stdout_visibility": "hidden",
        "leaderboard": leaderboard,
        "tests": tests,
    }
