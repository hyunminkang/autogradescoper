# AGENTS.md — instructions for AI coding agents

This file guides AI agents (Claude Code, Codex, OpenCode, Antigravity, ...)
working **in this repository** or **authoring assignments with this tool**.

## What this tool is

autogradescoper grades *functions*: a student submits `<file>.<R|py|cpp>`
defining `<func>`; the grader calls `<func>` on each test case's arguments,
captures a deterministic text rendering of the return value, and compares it
with the reference solution's rendering. Time limits make efficiency part of
correctness. Everything is configured by one `assignment.yaml`
(see docs/config.md).

## The authoring loop (follow this exactly)

When asked to create or modify an assignment/problem:

1. **Write the spec first** in `PROBLEM.md`: precise inputs, outputs, edge
   cases, tie-breaking rules, and the complexity story — which naive approach
   must the time limits rule out? If the spec is ambiguous, the grader will
   be ambiguous. Ask the user before guessing.
2. **Scaffold**: `autogradescoper init <dir> --lang <r|python|rcpp> --func <name>`
   (or edit an existing directory with the same layout).
3. **Write the reference solution** in `solution/`. Determinism is mandatory:
   no RNG without a fixed algorithmic generator (an LCG spec'd in the problem
   works well and is language-neutral), no dict-iteration-order dependence,
   no time/locale dependence. Specify tie-breaking explicitly (use byte-wise /
   C-locale ordering; in R, `order(..., method="radix")`).
4. **Design test cases** in `args/` (format: docs/languages.md#args-files):
   - small correctness cases, including every edge case in the spec;
   - at least one **large performance case** sized so the intended solution
     passes comfortably (≥5× margin) and the naive one cannot finish;
   - keep args files tiny — for large inputs, have the function *generate*
     its input from parameters (n, seed) using a spec'd generator.
5. **Write the traps**: put a correct-but-too-slow implementation in
   `examples/v1_slow/` and, if useful, a subtly wrong one in
   `examples/v2_incorrect/`.
6. **Validate**: run `autogradescoper validate <dir>` and **read
   `validation_report.md`**. Required outcome:
   - solution self-test: 100%;
   - `v1_slow`: passes small cases, **times out on the performance cases**
     (if it passes everything, your limits or sizes are wrong);
   - `v2_incorrect`: fails at least one case (if it passes, add a case that
     catches it).
7. **Iterate** on 3–6 until the report matches the intent. Do not weaken a
   time limit to make a slow example pass — that inverts the design.

## Repository conventions (when modifying the tool itself)

- Language support lives in `autogradescoper/langs/`; each backend only
  generates a harness script and a run command. Grading logic in
  `autogradescoper/core/` must stay language-agnostic.
- A submission is always compared against the same-language solution, so
  output formatting only needs to be deterministic *within* a language.
- No mandatory dependencies beyond PyYAML at runtime; the tool must work on
  Gradescope's default image after `setup.sh` (no custom Docker).
- Test without Gradescope: `autogradescoper validate` on `examples/*` is the
  integration test. Python examples run anywhere; R examples need Rscript.

## Things that commonly go wrong (check these first)

- **Solution self-test fails at N digits**: output formatting is unstable at
  the chosen `digits` (e.g., a value near a rounding boundary computed two
  ways). Reduce `digits` for that problem or make the case less marginal.
- **All cases error instantly in R**: the preload jail (`preload_baseonly.R`)
  blocks `library()`; the solution itself must be base-only too.
- **Python "module not found" for numpy**: the stdlib jail
  (`preload_stdlib_only.py`) is doing its job; the problem intends standard
  library only.
- **Rcpp cases time out**: compilation happens inside the first harness run;
  give every rcpp case `maxtime` ≥ compile time + run time (typically +15 s),
  or note the compile cost in PROBLEM.md.
- **Nondeterministic list/dict output**: sort keys explicitly; JSON rendering
  sorts dict keys in Python but R list order is preserved — emit sorted.
