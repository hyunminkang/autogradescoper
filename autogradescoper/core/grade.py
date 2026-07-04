"""Language-agnostic grading engine: case -> problem -> assignment.

The output of :func:`grade_assignment` is a Gradescope-compatible results
dictionary (https://gradescope-autograders.readthedocs.io/en/latest/specs/).
"""

from __future__ import annotations

import os

from autogradescoper.core.config import Assignment, Case, Problem
from autogradescoper.core.io import diff_texts, truncate
from autogradescoper.core.runner import TIMEOUT_EXIT_CODE, run_command
from autogradescoper.langs.base import get_backend

MAX_SHOW_CHARS = 500


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
    if solution_out_cache is not None:
        sol_out = solution_out_cache.get(cache_key)
    if sol_out is None:
        sol_prefix = f"{out_prefix}.sol"
        harness = backend.write_harness(
            problem.func, sol_prefix, solution_path, case.args,
            problem.digits, problem.format, [problem.preload_sol])
        elapsed, code, err = run_command(backend.command(harness),
                                         f"{sol_prefix}.stdout", maxtime=None)
        if code != 0:
            raise RuntimeError(
                f"SOLUTION failed on {os.path.basename(case.args)} "
                f"(exit {code}). This is an authoring error, not a submission "
                f"error.\n{truncate(err, 2000)}")
        with open(f"{sol_prefix}.out") as fh:
            sol_out = fh.read().strip()
        if solution_out_cache is not None:
            solution_out_cache[cache_key] = sol_out

    # --- submission side -----------------------------------------------------
    usr_prefix = f"{out_prefix}.usr"
    try:
        harness = backend.write_harness(
            problem.func, usr_prefix, submission_path, case.args,
            problem.digits, problem.format, [problem.preload])
    except ValueError as e:
        return {"status": "error", "elapsed": 0.0, "score": 0.0,
                "details": f"ERROR building test harness: {e}", "diffs": "", "errors": str(e)}

    elapsed, code, err = run_command(backend.command(harness),
                                     f"{usr_prefix}.stdout", maxtime=case.maxtime)

    result = {"elapsed": round(elapsed, 3), "diffs": "", "errors": ""}
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


def grade_problem(problem: Problem, solution_dir: str, submission_dir: str,
                  out_prefix: str, show: dict | None = None,
                  solution_out_cache: dict | None = None) -> dict:
    """Grade all cases of one problem; returns a Gradescope test entry."""
    show = show or {}
    backend = get_backend(problem.lang)
    solution_path = problem.solution_file or os.path.join(
        solution_dir, problem.submission_filename())
    submission_path = os.path.join(submission_dir, problem.submission_filename())

    if not os.path.exists(submission_path):
        return {"name": problem.name, "score": 0.0,
                "max_score": sum(c.maxscore for c in problem.cases),
                "output": (f"MISSING FILE: expected a submission named "
                           f"'{problem.submission_filename()}'."),
                "status": "failed"}

    total, chunks = 0.0, []
    elapsed_sum = 0.0
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
        chunk = f"Case {i}: {r['status']} ({r['score']}/{case.maxscore}) in {r['elapsed']}s"
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
    return {
        "name": f"{problem.name} ({problem.lang})",
        "score": total,
        "max_score": max_score,
        "output": (f"Score: {total}/{max_score} | total time: {elapsed_sum:.2f}s\n"
                   + "\n--------------------------------\n".join(chunks)),
        "status": "passed" if total == max_score else "failed",
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
    return {
        "score": score,
        "output": f"Total Score: {score}/{max_score}",
        "stdout_visibility": "hidden",
        "leaderboard": [{"name": "Score", "value": score}],
        "tests": tests,
    }
