# Migrating from v0 (the R-only interface)

v0.1 replaces the three `eval_r_func_*` commands and the split config format
with a single `assignment.yaml` and the `eval` command. R behavior is
unchanged: same args files, same preloads, same formatting rules, same
Gradescope results shape.

## Automatic conversion

```bash
autogradescoper migrate path/to/gradescope/config/config.yaml \
    --out path/to/gradescope/assignment.yaml
```

This inlines the per-problem case files, rewrites `/autograder/source/...`
paths as relative paths, and emits the v1 schema. Then:

```bash
autogradescoper validate path/to/gradescope   # needs solution/ and args/ present
```

## Update run_autograder

```bash
# before (v0)
autogradescoper eval_r_func_probset --config /autograder/source/config/config.yaml \
  --solution-dir /autograder/source/solution --submission-dir /autograder/submission \
  --out-prefix /autograder/results/results --show-args --show-details

# after (v0.1)
autogradescoper eval --config /autograder/source/assignment.yaml \
  --solution-dir /autograder/source/solution --submission-dir /autograder/submission \
  --out-prefix /autograder/results/results --show-args --show-details
```

`setup.sh` needs no changes for R assignments (pin the package version if you
want reproducible builds: `pip install autogradescoper==0.1.*`).

## Mapping of v0 config keys

| v0 | v1 |
|---|---|
| top-level list of `{func, filename, config, digits, format, preload_usr, preload_sol}` | `problems:` list |
| `filename` | `file` (only when ≠ `func`) |
| `config:` (per-problem YAML of `{args, maxtime, maxscore}`) | inlined `cases:` (or `cases_file:`) |
| `preload_usr` | `preload` |
| `preload_sol` | `preload_sol` |
| `--skip-solution` JSON self-scoring mode | not carried over (open an issue if you used it) |

## Behavior changes to be aware of

- Relative paths in the config are now resolved against the config file's
  directory (previously everything was absolute `/autograder/...`). Absolute
  paths still work.
- Diffs shown to students are unified diffs (previously `diff` default format).
- The results JSON per-problem `name` now includes the language, e.g.
  `myPearsonCor (r)`.
