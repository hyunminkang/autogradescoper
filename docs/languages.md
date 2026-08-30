# Language backends

A backend generates a small harness script per test case and runs it. The
harness: executes preloads → loads the submission (or solution) → parses the
args file → calls the function → writes the result to a text file. Grading
compares that text against the solution's. Because comparison is always
same-language, formatting only needs to be deterministic within a language.

## Args files

One argument per line, `type:value`:

| type | meaning | R | Python |
|---|---|---|---|
| `numeric` | scalar or comma/space-separated vector | `c(...)` double | float or list of floats |
| `int` | integer scalar/vector | `c(...)` | int or list of ints |
| `bool` | logical scalar/vector (`TRUE`/`FALSE`, `T`/`F`, `1`/`0`) | `c(TRUE, ...)` | bool or list of bools |
| `str` | whitespace-separated string(s) | character vector | str or list of str |
| `df` | path to a table with header row | `read.table(header=TRUE)` | dict of columns (lists) |
| `json` | path to a JSON file | `jsonlite::fromJSON` | `json.load` |
| `eval` | language-native expression | evaluated in a function | `eval()` |
| `asis` | language-native literal | inserted verbatim | inserted verbatim |
| `rds` | path to an .rds file | `readRDS` | *(R family only)* |

With `--show-args`, each argument value shown to students is truncated to
120 characters (cut at a token boundary), followed by
`... [truncated; N values in total]` — so very long input vectors do not
flood the feedback while students still see the input size.

`eval`/`asis` values are language-specific — problems using them are tied to
one language. For cross-language problems, prefer `numeric`/`int`/`str` and
have the function generate large inputs from `(n, seed)` with a spec'd
generator (see the hw3_dual example).

**Tip for large inputs**: never ship megabyte args files. Specify a
deterministic generator in the problem statement (e.g., the LCG
`x <- (69069*x + 1) mod 2^32`, exact in double precision) and pass only its
parameters.

## Output formatting

| return value | rendered as |
|---|---|
| NULL / None | `NA` |
| numeric scalar/vector | one value per line, C-style `%.<digits><format>` |
| character / str / list of str | one per line, verbatim |
| logical / bool | `TRUE` / `FALSE` |
| R list / Python dict | JSON (Python: sorted keys) |
| R data.frame | TSV with header |

Choose `digits` so the correct answer is *stable* at that precision; grading
is byte equality of the rendered text, not epsilon comparison.

## R (`lang: r`)

- Submission: `<file>.R` defining `<func>`.
- Runs with `Rscript --vanilla`.
- Sandboxing: `preload_baseonly.R` (ships with the package assets; copy it
  into your assignment) detaches non-base packages and disables
  `library()`/`require()` and `::` via `source()` inspection.
- `setup.sh`: `apt-get install -y r-base` — no custom Docker.

## Python (`lang: python`)

- Submission: `<file>.py` defining `<func>`.
- Runs with `python3`; the module is imported by path.
- Sandboxing: `preload_stdlib_only.py` installs an import hook that blocks
  numpy/scipy/pandas/... before the submission is imported. This is a
  fairness mechanism, not a security boundary (Gradescope's container is the
  security boundary).
- `setup.sh`: python3 is present on the default image; the venv is created by
  the template.

## C++ via Rcpp (`lang: rcpp`)

- Submission: `<file>.cpp` with an exported function:

```cpp
#include <Rcpp.h>
// [[Rcpp::export]]
double myFunc(Rcpp::NumericVector x) { ... }
```

- The harness runs `Rcpp::sourceCpp()` — compilation happens on first run,
  inside the case's time limit. **Budget maxtime accordingly** (compile is
  typically 5–20 s on Gradescope hardware): give every rcpp case
  `maxtime: <compile + run + margin>`, and consider a trivial "warm-up" case
  with a generous limit as case 1.
- `setup.sh`: `apt-get install -y r-base r-base-dev build-essential` plus
  `install.packages("Rcpp")` (see templates/setup_rcpp.sh).
- Compile errors surface as `error` status with the compiler message in
  stderr (students see it with `--show-errors`).

## Adding a new language

Implement `LanguageBackend` (two methods: `write_harness`, `command`) in
`autogradescoper/langs/`, register it in `get_backend`, and add a setup.sh
template. ~150 lines; see `python_lang.py` for the pattern.
