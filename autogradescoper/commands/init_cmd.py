"""`autogradescoper init` — scaffold a self-contained assignment directory."""

from __future__ import annotations

import os
import shutil

_TEMPLATES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "templates")

_STARTERS = {
    "r": ("R", """\
## {func}.R -- reference solution
{func} <- function(x) {{
  sum(x) / length(x)   ## replace with the real solution
}}
"""),
    "python": ("py", """\
## {func}.py -- reference solution
def {func}(x):
    if isinstance(x, (int, float)):
        x = [x]
    return sum(x) / len(x)   # replace with the real solution
"""),
    "rcpp": ("cpp", """\
// {func}.cpp -- reference solution (compiled via Rcpp::sourceCpp)
#include <Rcpp.h>
using namespace Rcpp;

// [[Rcpp::export]]
double {func}(NumericVector x) {{
  return mean(x);   // replace with the real solution
}}
"""),
}

_CONFIG = """\
version: 1
name: "{name}"
defaults:
  digits: 8
  format: g
  maxtime: 10
problems:
  - name: {func}
    lang: {lang}
    func: {func}
    cases:
      - args: args/{func}.1.args
        maxtime: 2
      - args: args/{func}.2.args
        maxtime: 2
"""

_ARGS1 = "numeric:1,2,3,4,5\n"
_ARGS2 = "numeric:0.5\n"

_PROBLEM_MD = """\
# {name}

<!-- Problem statement for students. If you use an AI agent to author this
     assignment, keep this spec precise: inputs, outputs, edge cases, and
     complexity/time-limit expectations. See AGENTS.md in the repo root. -->

Write a function `{func}` that ...

## Requirements
- Input: ...
- Output: ...
- Time limit: ... (which naive approach should this rule out?)

## Authoring checklist
- [ ] `solution/{func}.{ext}` implements the reference solution
- [ ] args/ contains small correctness cases AND large performance cases
- [ ] `examples/v1_slow/` contains a correct-but-too-slow implementation
- [ ] `autogradescoper validate .` passes
"""


def run_init(args) -> int:
    adir = os.path.abspath(args.assignment_dir)
    if os.path.exists(adir) and os.listdir(adir):
        print(f"ERROR: {adir} already exists and is not empty.")
        return 1

    ext, starter = _STARTERS[args.lang]
    name = os.path.basename(adir)

    for sub in ("solution", "args", "examples/v1_slow"):
        os.makedirs(os.path.join(adir, sub), exist_ok=True)

    with open(os.path.join(adir, "assignment.yaml"), "w") as fh:
        fh.write(_CONFIG.format(name=name, func=args.func, lang=args.lang))
    with open(os.path.join(adir, "solution", f"{args.func}.{ext}"), "w") as fh:
        fh.write(starter.format(func=args.func))
    with open(os.path.join(adir, "args", f"{args.func}.1.args"), "w") as fh:
        fh.write(_ARGS1)
    with open(os.path.join(adir, "args", f"{args.func}.2.args"), "w") as fh:
        fh.write(_ARGS2)
    with open(os.path.join(adir, "PROBLEM.md"), "w") as fh:
        fh.write(_PROBLEM_MD.format(name=name, func=args.func, ext=ext))

    # Gradescope wrapper scripts
    for tpl in ("run_autograder", f"setup_{args.lang}.sh"):
        src = os.path.join(_TEMPLATES, tpl)
        if os.path.exists(src):
            dst = os.path.join(adir, "setup.sh" if tpl.startswith("setup") else tpl)
            shutil.copy(src, dst)
            os.chmod(dst, 0o755)

    print(f"Scaffolded assignment in {adir}")
    print("Next steps:")
    print("  1. Edit PROBLEM.md (the spec), solution/, and args/")
    print("  2. Add a correct-but-too-slow variant under examples/v1_slow/")
    print(f"  3. Run: autogradescoper validate {args.assignment_dir}")
    print("  4. Zip this directory as the Gradescope autograder "
          "(setup.sh + run_autograder + assignment.yaml + solution/ + args/)")
    return 0
