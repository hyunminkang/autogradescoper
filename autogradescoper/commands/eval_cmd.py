"""`autogradescoper eval` — grade a submission (the Gradescope entry point)."""

from __future__ import annotations

from autogradescoper.core.config import load_assignment
from autogradescoper.core.grade import grade_assignment
from autogradescoper.core.io import create_custom_logger, write_dict_to_file


def run_eval(args) -> int:
    logger = create_custom_logger(__name__)
    assignment = load_assignment(args.config)
    logger.info(f"Grading assignment '{assignment.name}' "
                f"({len(assignment.problems)} problem(s))")

    show = {"args": args.show_args, "details": args.show_details,
            "diffs": args.show_diffs, "errors": args.show_errors}
    results = grade_assignment(assignment, args.solution_dir,
                               args.submission_dir, args.out_prefix, show)

    out_json = f"{args.out_prefix}.json"
    write_dict_to_file(results, out_json)
    logger.info(f"Score: {results['output']}")
    logger.info(f"Results written to {out_json}")
    return 0
