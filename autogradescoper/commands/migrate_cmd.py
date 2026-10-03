"""`autogradescoper migrate` — convert a legacy (v0) config to the v1 schema.

Legacy layout (R-only):

- ``config.yaml``: list of ``{func, filename?, config, digits?, format?,
  preload_usr?, preload_sol?}``
- each per-problem ``config`` file: list of ``{args, maxtime?, maxscore?}``

v1 layout: a single ``assignment.yaml`` (see docs/config.md). Paths are
rewritten relative to the output file's directory, with the legacy
``/autograder/source/`` prefix stripped so the assignment directory becomes
relocatable.
"""

from __future__ import annotations

import os

from autogradescoper.core.io import load_file_to_dict, write_dict_to_file

_LEGACY_PREFIX = "/autograder/source/"


def _relocate(path: str | None, base_dir: str) -> str | None:
    if path is None:
        return None
    if path.startswith(_LEGACY_PREFIX):
        return path[len(_LEGACY_PREFIX):]
    if os.path.isabs(path):
        try:
            return os.path.relpath(path, base_dir)
        except ValueError:
            return path
    return path


def run_migrate(args) -> int:
    old = load_file_to_dict(args.old_config)
    if not isinstance(old, list):
        print("ERROR: this does not look like a legacy config "
              "(expected a YAML list of problems).")
        return 1

    old_dir = os.path.dirname(os.path.abspath(args.old_config))
    out_path = args.out or os.path.join(os.path.dirname(old_dir), "assignment.yaml")
    out_dir = os.path.dirname(os.path.abspath(out_path))

    problems = []
    for p in old:
        prob = {
            "name": p.get("filename", p["func"]),
            "lang": "r",
            "func": p["func"],
        }
        if p.get("filename") and p["filename"] != p["func"]:
            prob["file"] = p["filename"]
        if "digits" in p:
            prob["digits"] = p["digits"]
        if "format" in p:
            prob["format"] = p["format"]
        if p.get("preload_usr"):
            prob["preload"] = _relocate(p["preload_usr"], out_dir)
        if p.get("preload_sol"):
            prob["preload_sol"] = _relocate(p["preload_sol"], out_dir)

        # inline the per-problem case list
        case_cfg_path = p["config"]
        local_case_path = os.path.join(old_dir, os.path.basename(case_cfg_path))
        if not os.path.exists(local_case_path) and os.path.exists(case_cfg_path):
            local_case_path = case_cfg_path
        cases_raw = load_file_to_dict(local_case_path)
        cases = []
        for c in cases_raw:
            case = {"args": _relocate(c["args"], out_dir)}
            if "maxtime" in c:
                case["maxtime"] = c["maxtime"]
            if "maxscore" in c:
                case["maxscore"] = c["maxscore"]
            cases.append(case)
        prob["cases"] = cases
        problems.append(prob)

    out = {
        "version": 1,
        "name": os.path.basename(os.path.dirname(out_dir)) or "assignment",
        "defaults": {"digits": 8, "format": "g", "maxtime": 10},
        "problems": problems,
    }
    write_dict_to_file(out, out_path)
    print(f"Wrote {out_path} ({len(problems)} problem(s)).")
    print("Review the paths (they are now relative to the assignment.yaml "
          "location), then test with:")
    print(f"  autogradescoper validate {os.path.dirname(out_path) or '.'}")
    return 0
