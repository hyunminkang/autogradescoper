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
    timelimit: wall       # wall: maxtime limits the whole run (default);
                          # function: maxtime limits the student's function
                          # call alone (see "Timing the student's function")
    wallcap: 3            # timelimit: function -- the whole run is stopped
                          # at wallcap x maxtime
    leaderboard: null     # optional Gradescope leaderboard column, e.g.
                          # "hw3 R time (s)" (see "Leaderboard" below)
    cases:                # inline cases, and/or ...
      - args: args/case1.args
        maxtime: 2        # seconds; enforced with coreutils `timeout`
        maxscore: 1       # points for this case (default 1)
    cases_file: null      # ... a YAML file containing a list of cases

leaderboard_total: null   # optional leaderboard column with the sum of all
                          # problems' leaderboard times, e.g. "Total time (s)"
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

## Leaderboard

Gradescope shows `results.json`'s `leaderboard` entries as sortable columns once
the leaderboard is enabled in the assignment settings (students pick a
pseudonym). autogradescoper always writes a `Score` column, and adds:

- one column per problem with a `leaderboard:` name: the problem's time summed
  over its cases, `order: asc` (lower ranks higher). A case that does not pass
  counts as its `maxtime`, so a fast but wrong submission cannot top the board;
  a missing file counts as the sum of all `maxtime`s;
- a `leaderboard_total` column, if named: the sum of those problem times.

The leaderboard uses the student's function time when the given code reports it (below), the
wall time of each case otherwise.

## Timing the student's function

By default `maxtime` limits the **whole run** of a case: interpreter start-up, preload, loading the
submission and the given code, building the arguments (reading files, simulating data), the call
and writing the output. With `timelimit: function`, `maxtime` limits **the student's function call
alone**:

- The harness creates a timer **before** the preload and the submission are loaded: `.agsTimed`
  in R (a locked global binding), `__ags_timed__` in the given Python module. It captures the clock
  and the writer, so redefining `proc.time`/`writeLines` or patching `time.perf_counter` later
  has no effect.
- The given entry point wraps the student's call, including any conversion of the result, so no
  work can be deferred past the timed window:

```r
timedCall <- function(f) if (exists(".agsTimed")) .agsTimed(f) else f()   # plain call outside the autograder
beta <- timedCall(function() as.numeric(studentFunction(X, y)))
```

```python
def _timed_call(f):
    timed = globals().get("__ags_timed__")      # set by the harness; absent outside the autograder
    return timed(f) if timed is not None else f()

beta = _timed_call(lambda: np.asarray(student_function(X, y), dtype=float))
```

- The timer writes the seconds to a file whose randomly named path the grader passes in
  `AUTOGRADESCOPER_TIMING_FILE`; the harness reads it and removes it from the environment before the
  submission is loaded, so submission code cannot find the file to write a fake time.
- A case is a timeout when the reported function time exceeds `maxtime`. The whole run is still
  killed at `wallcap` x `maxtime` (default 3), so even a faked time cannot rescue a hopelessly slow
  submission. If no time is reported (the given code was bypassed, or the run crashed), the whole
  run is timed against `maxtime`, as with `timelimit: wall`.
- Each case's feedback shows "your function X s (reference Y s)".

These safeguards stop casual tampering (redefining the clock, patching the time module, writing
the report file). Code running in the same interpreter can always defeat in-process measures with
deliberate effort (for example rebinding functions inside R's base environment), so treat the
reported time as a fair-play measure, as with the preloads.

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
