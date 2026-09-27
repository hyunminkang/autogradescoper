"""Assignment configuration: schema, loading, validation, path resolution.

An assignment is described by a single YAML (or JSON) file:

.. code-block:: yaml

    version: 1
    name: "HW3"                    # optional display name
    defaults:                      # optional; applied to every problem
      lang: r
      digits: 8
      format: g
      maxtime: 10
    problems:
      - name: topFreqItems         # display name (default: func)
        lang: r                    # r | rcpp | python
        func: topFreqItems         # function to call
        file: topFreqItems         # submission file stem (default: func);
                                   # extension is implied by lang (.R/.cpp/.py)
        exact: false               # exact string match (skip numeric formatting note)
        digits: 6                  # significant digits when formatting outputs
        format: g                  # C-style format: g, f, e, d, s
        preload: preload.R         # sourced before the SUBMISSION (sandboxing)
        preload_sol: null          # sourced before the SOLUTION
        solution_file: null        # override solution path (default:
                                   # <solution_dir>/<file>.<ext>)
        entry: null                # optional GIVEN-CODE file, shipped with the
                                   # assignment, loaded AFTER the submission /
                                   # solution; `func` is then taken from it. Keeps
                                   # entry points and helpers out of student files.
        cases:                     # inline test cases ...
          - args: args/case1.args
            maxtime: 2
            maxscore: 1
        cases_file: null           # ... or a separate YAML list of cases

All relative paths are resolved against the directory containing the config
file, so an assignment directory is self-contained and relocatable (no
hard-coded /autograder paths required).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from autogradescoper.core.io import load_file_to_dict

SUPPORTED_LANGS = ("r", "rcpp", "python")
LANG_EXTENSIONS = {"r": "R", "rcpp": "cpp", "python": "py"}


class ConfigError(ValueError):
    """Raised when an assignment configuration is invalid."""


@dataclass
class Case:
    args: str
    maxtime: float = 10.0
    maxscore: float = 1.0


@dataclass
class Problem:
    func: str
    lang: str = "r"
    name: str = ""
    file: str = ""
    digits: int = 8
    format: str = "g"
    exact: bool = False
    preload: str | None = None
    preload_sol: str | None = None
    solution_file: str | None = None
    entry: str | None = None
    cases: list[Case] = field(default_factory=list)

    @property
    def extension(self) -> str:
        return LANG_EXTENSIONS[self.lang]

    def submission_filename(self) -> str:
        return f"{self.file}.{self.extension}"


@dataclass
class Assignment:
    name: str
    problems: list[Problem]
    base_dir: str


def _resolve(base_dir: str, path: str | None) -> str | None:
    if path is None:
        return None
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base_dir, path))


def load_assignment(config_path: str) -> Assignment:
    """Load and validate an assignment config; resolve all relative paths."""
    raw = load_file_to_dict(config_path)
    base_dir = os.path.dirname(os.path.abspath(config_path))

    if isinstance(raw, list):
        raise ConfigError(
            "This looks like a legacy (v0) config, which is a YAML list. "
            "Convert it with: autogradescoper migrate <old_config.yaml>"
        )
    if not isinstance(raw, dict) or "problems" not in raw:
        raise ConfigError("Config must be a mapping with a 'problems' list.")

    defaults = raw.get("defaults", {}) or {}
    problems: list[Problem] = []

    for i, p in enumerate(raw["problems"]):
        if "func" not in p:
            raise ConfigError(f"problems[{i}]: 'func' is required.")
        lang = str(p.get("lang", defaults.get("lang", "r"))).lower()
        if lang not in SUPPORTED_LANGS:
            raise ConfigError(
                f"problems[{i}] ({p['func']}): unsupported lang '{lang}'. "
                f"Supported: {', '.join(SUPPORTED_LANGS)}"
            )

        cases_raw = list(p.get("cases", []) or [])
        cases_file = p.get("cases_file")
        if cases_file:
            cases_raw += load_file_to_dict(_resolve(base_dir, cases_file)) or []
        if not cases_raw:
            raise ConfigError(f"problems[{i}] ({p['func']}): no test cases defined.")

        cases = []
        for j, c in enumerate(cases_raw):
            if "args" not in c:
                raise ConfigError(f"problems[{i}] ({p['func']}) case {j}: 'args' is required.")
            args_path = _resolve(base_dir, c["args"])
            if not os.path.exists(args_path):
                raise ConfigError(
                    f"problems[{i}] ({p['func']}) case {j}: args file not found: {args_path}"
                )
            cases.append(Case(
                args=args_path,
                maxtime=float(c.get("maxtime", defaults.get("maxtime", 10))),
                maxscore=float(c.get("maxscore", 1)),
            ))

        entry_path = _resolve(base_dir, p.get("entry", defaults.get("entry")))
        if entry_path and not os.path.isfile(entry_path):
            raise ConfigError(f"problems[{i}] ({p['func']}): entry file not found: {entry_path}")
        problems.append(Problem(
            func=p["func"],
            lang=lang,
            name=p.get("name", p["func"]),
            file=p.get("file", p["func"]),
            digits=int(p.get("digits", defaults.get("digits", 8))),
            format=str(p.get("format", defaults.get("format", "g"))),
            exact=bool(p.get("exact", defaults.get("exact", False))),
            preload=_resolve(base_dir, p.get("preload", defaults.get("preload"))),
            preload_sol=_resolve(base_dir, p.get("preload_sol", defaults.get("preload_sol"))),
            solution_file=_resolve(base_dir, p.get("solution_file")),
            entry=entry_path,
            cases=cases,
        ))

    return Assignment(
        name=raw.get("name", os.path.basename(base_dir)),
        problems=problems,
        base_dir=base_dir,
    )
