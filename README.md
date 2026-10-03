# autogradescoper

**Function-level autograding for Gradescope — in R, Python, and C++ (via Rcpp) — with no custom Docker image.**

You define an assignment as *functions + test cases*: students submit source
files containing specific functions; autogradescoper calls each function on
each test case, compares the output against your reference solution, enforces
per-case time limits, and produces Gradescope-native results with per-case
feedback. Correctness **and efficiency** are graded: a correct-but-quadratic
solution fails the cases you sized to kill it.

```yaml
# assignment.yaml — a complete assignment definition
version: 1
name: "HW3"
problems:
  - name: runningMedian
    lang: r                    # r | python | rcpp
    func: runningMedian
    digits: 6
    preload: preload.baseonly.R
    cases:
      - {args: args/case1.args, maxtime: 2}
      - {args: args/case2.args, maxtime: 20}   # kills O(n^2) submissions
```

## Why this tool

- **No custom Docker.** Works on Gradescope's default base image: your
  `setup.sh` apt-installs R and/or Python and pip-installs this package. Done.
- **Multi-language, one assignment.** R, Python, and Rcpp problems coexist in
  one config; a single submission can be graded in several languages
  (e.g., "implement it in both R and Python").
- **Time limits are first-class.** Each case has a `maxtime`; design large
  cases so the wrong data structure or algorithm cannot pass.
- **Authoring feedback loop built in.** `autogradescoper validate` self-tests
  your solution and grades your example answers — the same loop works for
  humans and for AI coding agents (see [AGENTS.md](AGENTS.md)).
- **Sandboxing preloads.** Restrict students to base R
  (`preload_baseonly.R`) or the Python standard library
  (`preload_stdlib_only.py`) for a level playing field.

## Quickstart

```bash
pip install autogradescoper       # or: pip install git+https://github.com/hyunminkang/autogradescoper.git

autogradescoper init hw1 --lang python --func myMean
cd hw1
#   1. edit PROBLEM.md (the spec), solution/myMean.py, args/*.args
#   2. add a correct-but-too-slow variant under examples/v1_slow/
autogradescoper validate .        # must pass before you ship
zip -r hw1_autograder.zip setup.sh run_autograder assignment.yaml solution/ args/ *.R *.py
# upload the zip on Gradescope: Assignment -> Configure Autograder
```

Grading locally (what Gradescope runs):

```bash
autogradescoper eval --config assignment.yaml \
  --solution-dir solution --submission-dir path/to/submission \
  --out-prefix /tmp/results --show-args --show-details
```

## Commands

| command | purpose |
|---|---|
| `eval` | grade a submission (the Gradescope entry point) |
| `validate` | author-side: solution self-test + grade `examples/` variants; writes `validation_report.md` |
| `init` | scaffold a new assignment directory |
| `migrate` | convert a legacy (v0, R-only) config to the current schema |

## Documentation

- [docs/quickstart.md](docs/quickstart.md) — end-to-end walkthrough
- [docs/config.md](docs/config.md) — assignment.yaml reference
- [docs/languages.md](docs/languages.md) — R / Python / Rcpp specifics, args file format, output formatting
- [docs/ai-authoring.md](docs/ai-authoring.md) — authoring problems with AI agents
- [docs/migration.md](docs/migration.md) — migrating from v0
- [AGENTS.md](AGENTS.md) — instructions for AI coding agents working in this repo or authoring assignments with it
- [skills/problem-author/](skills/problem-author/) — a drop-in skill for Claude Code / Cowork

## Examples

- `examples/mypexp/` — single R problem (numerical precision), with correct and
  incorrect example answers
- `examples/hw3_dual/` — one assignment grading the same two problems in
  **both R and Python**, with sandboxing preloads and performance-tiered time
  limits (from BIOSTAT 615, University of Michigan)

## v0.1 breaking change

The v0 commands (`eval_r_func_probset`, `eval_r_func_problem`,
`eval_r_func_args`) and the split config format were replaced by the single
`assignment.yaml` schema and the `eval` command. Convert old assignments with
`autogradescoper migrate <old_config.yaml>`; see
[docs/migration.md](docs/migration.md).

## License

MIT. Originally developed for BIOSTAT 615 (Statistical Computing / AI-assisted
Statistical Programming) at the University of Michigan.
