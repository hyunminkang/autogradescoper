"""autogradescoper command-line interface.

Commands:
  eval       Grade a submission against an assignment config (Gradescope entry point)
  validate   Author-side checks: solution self-test + example answers
  init       Scaffold a new assignment directory
  migrate    Convert a legacy (v0, R-only) config to the current schema
"""

from __future__ import annotations

import argparse
import sys

LEGACY_COMMANDS = {"eval_r_func_probset", "eval_r_func_problem", "eval_r_func_args"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autogradescoper",
        description=("Function-level autograding for Gradescope: define an "
                     "assignment as functions + test cases, in R, Python, or "
                     "C++ (via Rcpp), with no custom Docker image."))
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("eval", help="Grade a submission (Gradescope entry point)")
    p.add_argument("--config", default="/autograder/source/assignment.yaml",
                   help="Assignment config file (default: %(default)s)")
    p.add_argument("--solution-dir", default="/autograder/source/solution",
                   help="Directory with reference solutions (default: %(default)s)")
    p.add_argument("--submission-dir", default="/autograder/submission",
                   help="Directory with the student submission (default: %(default)s)")
    p.add_argument("--out-prefix", default="/autograder/results/results",
                   help="Prefix for output files; results JSON is written to "
                        "<out-prefix>.json (default: %(default)s)")
    p.add_argument("--show-args", action="store_true",
                   help="Show each case's arguments in student-visible output")
    p.add_argument("--show-details", action="store_true",
                   help="Show expected vs observed output to students")
    p.add_argument("--show-diffs", action="store_true",
                   help="Show unified diffs to students")
    p.add_argument("--show-errors", action="store_true",
                   help="Show runtime error messages to students")

    p = sub.add_parser("validate",
                       help="Author-side validation of an assignment directory")
    p.add_argument("assignment_dir",
                   help="Directory containing assignment.yaml, solution/, args/, "
                        "and optionally examples/<name>/")
    p.add_argument("--config", default=None,
                   help="Config path (default: <assignment_dir>/assignment.yaml)")
    p.add_argument("--report", default=None,
                   help="Write a markdown report here "
                        "(default: <assignment_dir>/validation_report.md)")

    p = sub.add_parser("init", help="Scaffold a new assignment directory")
    p.add_argument("assignment_dir", help="Directory to create")
    p.add_argument("--lang", choices=["r", "python", "rcpp"], default="r",
                   help="Language of the first problem (default: %(default)s)")
    p.add_argument("--func", default="myFunc",
                   help="Name of the first problem's function (default: %(default)s)")

    p = sub.add_parser("migrate",
                       help="Convert a legacy (v0) config.yaml to the current schema")
    p.add_argument("old_config", help="Path to the legacy config.yaml")
    p.add_argument("--out", default=None,
                   help="Output path (default: assignment.yaml next to the old config)")

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv

    if argv and argv[0] in LEGACY_COMMANDS:
        print(f"'{argv[0]}' was removed in v0.1 (legacy R-only interface).\n"
              f"Convert your config with:  autogradescoper migrate <config.yaml>\n"
              f"Then grade with:           autogradescoper eval --config assignment.yaml\n"
              f"See docs/migration.md for details.", file=sys.stderr)
        return 2

    args = build_parser().parse_args(argv)

    if args.command == "eval":
        from autogradescoper.commands.eval_cmd import run_eval
        return run_eval(args)
    if args.command == "validate":
        from autogradescoper.commands.validate_cmd import run_validate
        return run_validate(args)
    if args.command == "init":
        from autogradescoper.commands.init_cmd import run_init
        return run_init(args)
    if args.command == "migrate":
        from autogradescoper.commands.migrate_cmd import run_migrate
        return run_migrate(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
