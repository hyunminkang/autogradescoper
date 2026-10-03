# Quickstart

## 1. Install

```bash
pip install autogradescoper
```

Requirements: Python ≥ 3.9 + PyYAML (installed automatically). To grade R or
Rcpp problems you also need R (`Rscript`) on the machine.

## 2. Create an assignment

```bash
autogradescoper init hw1 --lang python --func myMean
cd hw1
```

Edit, in this order:

1. `PROBLEM.md` — the spec (inputs, outputs, edge cases, complexity story)
2. `solution/myMean.py` — the reference solution
3. `args/*.args` — test cases (`type:value` per line; see docs/languages.md)
4. `assignment.yaml` — case list with per-case `maxtime`
5. `examples/v1_slow/myMean.py` — a correct-but-too-slow trap

## 3. Validate (the loop you iterate)

```bash
autogradescoper validate .
cat validation_report.md
```

Required: solution self-test 100%; slow example times out on large cases;
incorrect example caught. Iterate on the solution/cases/limits until true.

## 4. Grade a submission locally

```bash
autogradescoper eval --config assignment.yaml \
  --solution-dir solution --submission-dir /path/to/student/files \
  --out-prefix /tmp/results --show-args --show-details
cat /tmp/results.json
```

## 5. Deploy to Gradescope (no custom Docker)

Zip the assignment directory and upload it as the autograder:

```bash
zip -r hw1_autograder.zip setup.sh run_autograder assignment.yaml solution/ args/ PROBLEM.md preload*
```

Gradescope runs `setup.sh` once at build time (apt + pip on the default base
image) and `run_autograder` per submission (which calls `autogradescoper eval`).

Student-visible feedback is controlled by the `--show-*` flags in
`run_autograder`: arguments, expected-vs-observed details, diffs, and error
messages are each opt-in.
