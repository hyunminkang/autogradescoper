"""`autogradescoper validate` — the authoring feedback loop.

Runs, without any Gradescope involvement:

1. **Solution self-test**: the reference solution is graded as if it were a
   submission. It must score 100% — anything else is an authoring bug
   (nondeterminism, bad args file, formatting mismatch, or a solution that
   misses its own time limits).
2. **Example answers**: every directory under ``examples/`` is graded and
   reported. Name directories with their intent, e.g. ``v1_slow`` (expected
   to time out on large cases) or ``v2_incorrect`` (expected to fail some
   cases); the report shows exactly which cases passed and failed.

This command is the primary target for AI problem-authoring workflows: an
agent writes/modifies a problem, runs ``validate``, reads the report, and
iterates. Exit code 0 = solution self-test passed.
"""

from __future__ import annotations

import os
import tempfile
import time

from autogradescoper.core.config import load_assignment
from autogradescoper.core.grade import grade_assignment
from autogradescoper.core.io import create_custom_logger


def _summarize(results: dict) -> str:
    lines = []
    for t in results["tests"]:
        lines.append(f"| {t['name']} | {t['score']}/{t['max_score']} | {t['status']} |")
    return "\n".join(lines)


def run_validate(args) -> int:
    logger = create_custom_logger(__name__)
    adir = os.path.abspath(args.assignment_dir)
    config_path = args.config or os.path.join(adir, "assignment.yaml")
    report_path = args.report or os.path.join(adir, "validation_report.md")

    assignment = load_assignment(config_path)
    solution_dir = os.path.join(adir, "solution")
    report = [f"# Validation report: {assignment.name}",
              f"_generated {time.strftime('%Y-%m-%d %H:%M:%S')} by autogradescoper validate_", ""]
    ok = True
    cache: dict = {}

    with tempfile.TemporaryDirectory(prefix="agsval.") as tmp:
        # 1) solution self-test ------------------------------------------------
        logger.info("Step 1/2: solution self-test (must score 100%)")
        try:
            results = grade_assignment(
                assignment, solution_dir, solution_dir,
                os.path.join(tmp, "selftest"),
                show={"details": True}, solution_out_cache=cache)
            full = all(t["score"] == t["max_score"] for t in results["tests"])
            ok = ok and full
            report += ["## 1. Solution self-test",
                       "" if full else
                       "**FAILED** — the reference solution does not pass its own "
                       "test cases. Common causes: nondeterministic output, a case "
                       "exceeding its own `maxtime`, formatting instability at the "
                       "chosen `digits`.",
                       "", "| problem | score | status |", "|---|---|---|",
                       _summarize(results), ""]
            if not full:
                for t in results["tests"]:
                    if t["score"] != t["max_score"]:
                        report += [f"### Details: {t['name']}", "```",
                                   t["output"], "```", ""]
        except Exception as e:  # authoring errors (solution crashed, etc.)
            ok = False
            report += ["## 1. Solution self-test", "**ERROR**", "```", str(e), "```", ""]

        # 2) example answers ---------------------------------------------------
        examples_root = None
        for cand in ("examples", "example_answers"):
            if os.path.isdir(os.path.join(adir, cand)):
                examples_root = os.path.join(adir, cand)
                break
        report.append("## 2. Example answers")
        if examples_root is None:
            report += ["_No examples/ directory found. Recommended: add "
                       "`examples/v1_slow/` and `examples/v2_incorrect/` "
                       "variants so time limits and test coverage are exercised._", ""]
        else:
            logger.info("Step 2/2: grading example answers")
            for name in sorted(os.listdir(examples_root)):
                exdir = os.path.join(examples_root, name)
                if not os.path.isdir(exdir):
                    continue
                logger.info(f"  grading example: {name}")
                try:
                    results = grade_assignment(
                        assignment, solution_dir, exdir,
                        os.path.join(tmp, f"ex_{name}"), show={},
                        solution_out_cache=cache)
                    report += [f"### {name}", "",
                               "| problem | score | status |", "|---|---|---|",
                               _summarize(results), ""]
                    for t in results["tests"]:
                        cases = [ln for ln in t["output"].splitlines()
                                 if ln.startswith("Case ")]
                        if cases:
                            report += [f"`{t['name']}`: " + "; ".join(cases), ""]
                except Exception as e:
                    report += [f"### {name}", "**ERROR**", "```", str(e), "```", ""]

    verdict = "PASSED" if ok else "FAILED"
    report.insert(2, f"**Overall: {verdict}** (solution self-test)")
    with open(report_path, "w") as fh:
        fh.write("\n".join(report) + "\n")
    logger.info(f"Validation {verdict}; report written to {report_path}")
    return 0 if ok else 1
