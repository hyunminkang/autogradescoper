# hw3_dual — one assignment, two languages

Grades the same two problems (hash-based top-frequent-items; two-heap running
median) in BOTH R and Python, with sandboxing preloads and performance-tiered
time limits. From BIOSTAT 615 (U. Michigan), Topic 4: data structures.

- Inputs are generated inside the functions from a spec'd LCG, so the same
  tiny .args files drive both languages.
- YAML anchors (`&topfreq_cases` / `*topfreq_cases`) keep the R and Python
  case lists identical.
- `examples/v1_slow/` holds correct-but-too-slow implementations in both
  languages; `autogradescoper validate .` shows them timing out on the large
  cases (running the R half requires Rscript).
