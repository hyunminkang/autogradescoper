---
name: autogradescoper-problem-author
description: Author, test, and validate autograded programming problems (R, Python, or Rcpp) for Gradescope using autogradescoper. Use when the user asks to create a homework/exam programming problem, add test cases, design an autograded assignment, or debug why an autograder mis-scores submissions.
---

# Authoring autograded problems with autogradescoper

You are helping an instructor create a **function-level autograded problem**:
students submit a source file defining a specific function; the grader runs it
on test cases, compares output to the reference solution, and enforces
per-case time limits (so efficiency is graded, not just correctness).

## Workflow

1. **Clarify the pedagogy before writing anything.** Ask (or infer from
   context) three things: (a) what concept must the student demonstrate?
   (b) which naive-but-correct approach should FAIL, and why? (c) what inputs
   make that naive approach fail while the intended one passes with ≥5×
   time margin?

2. **Write the spec** (PROBLEM.md): exact signature, input domains, output
   format, edge cases, tie-breaking (always byte-wise/C-locale order), time
   limits. Determinism rule: if inputs must be large, have the function
   generate them from `(n, seed)` with an explicitly spec'd generator (e.g.,
   the LCG `x <- (69069*x + 1) mod 2^32`, exact in doubles) so args files
   stay tiny and language-neutral.

3. **Scaffold and implement**:
   ```bash
   autogradescoper init <dir> --lang <r|python|rcpp> --func <name>
   ```
   Write `solution/<func>.<ext>`, the `args/*.args` cases (one argument per
   line, `type:value`; types: numeric, int, str, df, json, eval, asis, and
   rds for R), and `assignment.yaml` (cases + maxtime per case; `digits` for
   numeric tolerance via formatting; `exact: true` for string outputs).
   Add sandboxing if desired: `preload: preload_baseonly.R` (base R only) or
   `preload: preload_stdlib_only.py` (Python stdlib only).

4. **Write the traps** — this is what makes the problem good:
   - `examples/v1_slow/`: correct but wrong complexity (must TIME OUT on the
     large cases);
   - `examples/v2_incorrect/`: plausible bug (must FAIL ≥1 case).

5. **Close the loop** — run and READ the report, then iterate:
   ```bash
   autogradescoper validate <dir>
   cat <dir>/validation_report.md
   ```
   Required: solution 100%; v1_slow times out on performance cases only;
   v2_incorrect caught. Never fix a failure by weakening a time limit or
   deleting a case — fix the design.

6. **Ship**: the assignment directory (setup.sh, run_autograder,
   assignment.yaml, solution/, args/, preloads) zipped is the Gradescope
   autograder. `run_autograder` calls `autogradescoper eval`.

## Quality bar for test cases

- Every edge case in the spec has a case (empty-ish inputs, ties, boundaries).
- At least one case per distinct failure mode you can imagine an AI or a
  student producing (off-by-one, wrong tie-break, unstable formula).
- Performance cases: intended solution ≤ 20% of maxtime; naive ≥ 300%.
- Args files small (< 1 KB); big inputs are generated, not shipped.

## Debugging mis-scores

- Reproduce locally: `autogradescoper eval --config assignment.yaml
  --solution-dir solution --submission-dir <the submission> --out-prefix /tmp/r
  --show-details --show-errors`, then read `/tmp/r.json` and the per-case
  `.out` / `.stdout` / `.harness.*` files — the harness is a plain script you
  can run by hand.
- Formatting mismatches: lower `digits`, or set `exact: true` only for
  genuinely exact outputs.
- Rcpp: budget compile time (~15 s) into every case's maxtime.
