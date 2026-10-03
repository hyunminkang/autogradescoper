# assignment.yaml reference

One file describes one assignment. All relative paths are resolved against
the directory containing the config file, so the assignment directory is
self-contained and relocatable.

```yaml
version: 1                # schema version (required going forward)
name: "HW3"               # display name (optional)

defaults:                 # optional; inherited by every problem
  lang: r
  digits: 8
  format: g
  maxtime: 10
  preload: preload.baseonly.R

problems:
  - name: runningMedian   # display name (default: func)
    lang: r               # r | python | rcpp
    func: runningMedian   # function the submission must define
    file: runningMedian   # submission file stem (default: func).
                          # Extension is implied by lang: .R / .py / .cpp
    digits: 6             # significant digits used when writing outputs
    format: g             # C-style numeric format: g, f, e, d, s
    exact: false          # informational; string outputs compare exactly anyway
    preload: jail.R       # sourced/executed BEFORE the submission (sandboxing)
    preload_sol: null     # sourced/executed before the solution
    entry: null           # optional given-code file loaded AFTER the submission;
                          # `func` is taken from it (keeps entry points, data
                          # readers and simulators out of student files)
    solution_file: null   # override the solution path
                          # (default: <solution-dir>/<file>.<ext>)
    cases:                # inline cases, and/or ...
      - args: args/case1.args
        maxtime: 2        # seconds; enforced with coreutils `timeout`
        maxscore: 1       # points for this case (default 1)
    cases_file: null      # ... a YAML file containing a list of cases
```

## Semantics

- **Scoring**: each case scores `maxscore` on pass, 0 otherwise. A problem's
  score is the sum over cases. The Gradescope results JSON contains one test
  entry per problem with per-case lines in its output.
- **Comparison**: the submission's rendered output must equal the solution's
  rendered output byte-for-byte *after* deterministic formatting
  (see [languages.md](languages.md#output-formatting)). Numeric tolerance is
  controlled by rendering at `digits` significant digits — not by epsilon
  comparison — so choose `digits` such that the correct answer is stable.
- **Statuses**: `pass`, `incorrect`, `timeout`, `error` (submission crashed),
  plus `MISSING FILE` at the problem level if the expected file is absent.
  Filename matching tolerates case: `foo.r` or `Foo.R` is accepted for an
  expected `foo.R` (a note in the feedback asks for the exact name next
  time). When nothing matches, the `MISSING FILE` message lists the files
  that were actually submitted.
- **Multi-language assignments**: list the same conceptual problem twice with
  different `lang`/`func` values. YAML anchors keep case lists in sync:

```yaml
    cases: &shared_cases
      - {args: args/c1.args, maxtime: 2}
  - name: running_median
    lang: python
    func: running_median
    cases: *shared_cases
```

## Directory layout convention

```
hw3/
├── assignment.yaml
├── setup.sh              # apt-get + pip install (Gradescope build step)
├── run_autograder        # calls `autogradescoper eval`
├── solution/             # reference solutions, one file per problem
├── args/                 # test case argument files
├── preload*.{R,py}       # optional sandboxing preloads
└── examples/             # optional; graded by `validate`
    ├── v1_slow/          #   correct but too slow (must time out)
    └── v2_incorrect/     #   subtly wrong (must be caught)
```
