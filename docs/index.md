# autogradescoper

Function-level autograding for Gradescope — R, Python, and C++ (via Rcpp) —
with no custom Docker image.

Define an assignment as **functions + test cases**; students submit source
files defining those functions; the tool grades correctness *and efficiency*
(per-case time limits) and produces Gradescope-native results.

- New here? Start with the [Quickstart](quickstart.md).
- Full config reference: [assignment.yaml](config.md)
- Language details (args files, formatting, sandboxing): [Languages](languages.md)
- Authoring with AI agents: [AI authoring](ai-authoring.md)
- Coming from the v0 R-only interface: [Migration](migration.md)
