"""Python backend.

The generated harness executes preloads (which may install an import jail —
see assets/preload_stdlib_only.py), imports the submission module from its
file path, parses the ``.args`` file into Python values, calls the function,
and writes the result with deterministic formatting to ``<out_prefix>.out``.

Output formatting rules (internally consistent; compared only against the
Python solution's output produced by this same harness):

- ``None``                          -> ``NA``
- float/int scalar                  -> C-style format (e.g. ``%.8g``)
- str scalar                        -> as-is
- list/tuple of scalars             -> one element per line
- dict / nested structures          -> JSON with sorted keys, floats formatted
"""

from __future__ import annotations

import os

from autogradescoper.langs.base import (LanguageBackend, format_arg_value,
                                        parse_bool_token)

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

_HARNESS_TEMPLATE = '''\
import importlib.util
import json
import sys

DIGITS = {digits}
FORMAT = "{out_format}"

def _fmt_scalar(v):
    if v is None:
        return "NA"
    if isinstance(v, bool):
        return "TRUE" if v else "FALSE"
    if isinstance(v, float):
        if v != v:
            return "NA"
        return ("%." + str(DIGITS) + FORMAT) % v
    if isinstance(v, int):
        return str(v) if FORMAT == "d" else ("%." + str(DIGITS) + "g") % v
    return str(v)

def _jsonable(v):
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, dict):
        return {{str(k): _jsonable(x) for k, x in sorted(v.items(), key=lambda kv: str(kv[0]))}}
    if isinstance(v, float):
        return _fmt_scalar(v)
    return v

def write_result(rst, path):
    with open(path, "w") as fh:
        if rst is None:
            fh.write("NA\\n")
        elif isinstance(rst, dict):
            json.dump(_jsonable(rst), fh, indent=1)
            fh.write("\\n")
        elif isinstance(rst, (list, tuple)):
            if any(isinstance(x, (list, tuple, dict)) for x in rst):
                json.dump(_jsonable(rst), fh, indent=1)
                fh.write("\\n")
            else:
                fh.write("\\n".join(_fmt_scalar(x) for x in rst))
                fh.write("\\n")
        else:
            fh.write(_fmt_scalar(rst) + "\\n")

def _load_json(path):
    with open(path) as fh:
        return json.load(fh)

def _load_df(path):
    import csv
    with open(path) as fh:
        sample = fh.read(4096); fh.seek(0)
        delim = "\\t" if "\\t" in sample else (" " if "," not in sample else ",")
        rows = list(csv.DictReader(fh, delimiter=delim, skipinitialspace=True))
    cols = {{}}
    for k in (rows[0].keys() if rows else []):
        vals = [r[k] for r in rows]
        try:
            cols[k] = [float(v) for v in vals]
        except (TypeError, ValueError):
            cols[k] = vals
    return cols

# ---- timer for the student's function call (see TIMING_ENV in core/grade.py) ------
# Created before any submission code runs: it removes the report file's name from the
# environment and captures the clock and open(), so patching time.perf_counter or os.environ
# later has no effect. It is handed to the given entry module as __ags_timed__ and otherwise
# lives only in a local variable of _ags_main().
def _ags_make_timed():
    import os as _os
    import time as _time
    path = _os.environ.pop("AUTOGRADESCOPER_TIMING_FILE", None)
    clock = _time.perf_counter
    _open = open
    def timed(f):
        t0 = clock()
        r = f()
        dt = clock() - t0
        if path:
            with _open(path, "w") as fh:
                fh.write("%.6f\\n" % dt)
        return r
    return timed

# ---- preloads (may install an import jail) --------------------------------
for _pre in {preloads!r}:
    if _pre:
        with open(_pre) as _fh:
            exec(compile(_fh.read(), _pre, "exec"), {{"__name__": "__preload__"}})


def _ags_main(_ags_timed):
    # ---- load the target module ------------------------------------------------
    _spec = importlib.util.spec_from_file_location("_submission", {source_path!r})
    _mod = importlib.util.module_from_spec(_spec)
    _entry = {entry_path!r}
    if not _entry:   # legacy layout: the graded entry point lives in the submission file itself
        _mod.__ags_timed__ = _ags_timed
    _spec.loader.exec_module(_mod)
    # register the submission under its file name so that a given-code entry file
    # can `import <stem>` regardless of the working directory
    sys.modules.setdefault({submission_name!r}, _mod)
    if _entry:
        _espec = importlib.util.spec_from_file_location("_entry", _entry)
        _emod = importlib.util.module_from_spec(_espec)
        _emod.__ags_timed__ = _ags_timed
        _espec.loader.exec_module(_emod)
        _func = getattr(_emod, {func!r})
    else:
        _func = getattr(_mod, {func!r})

    # ---- arguments --------------------------------------------------------------
    _args = []
{arg_lines}

    # ---- run and write ----------------------------------------------------------
    _rst = _func(*_args)
    write_result(_rst, {out_path!r})


_ags_main(_ags_make_timed())
'''


def _parse_arg_lines(args_path: str):
    with open(args_path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            typ, _, value = line.partition(":")
            yield typ.strip(), value.strip()


def _py_arg_stmt(typ: str, value: str) -> str:
    if typ in ("numeric", "int"):
        cast = "int" if typ == "int" else "float"
        vals = value.replace(",", " ").split()
        if len(vals) == 1:
            return f"_args.append({cast}({vals[0]}))"
        return f"_args.append([{cast}(v) for v in {vals!r}])"
    if typ == "bool":
        vals = [parse_bool_token(v) for v in value.replace(",", " ").split()]
        return f"_args.append({vals[0]!r})" if len(vals) == 1 else f"_args.append({vals!r})"
    if typ == "str":
        vals = value.split()
        return f"_args.append({vals[0]!r})" if len(vals) == 1 else f"_args.append({vals!r})"
    if typ == "df":
        return f"_args.append(_load_df({value!r}))"
    if typ == "json":
        return f"_args.append(_load_json({value!r}))"
    if typ == "eval":
        return f"_args.append(eval(compile({value!r}, '<args>', 'eval')))"
    if typ == "asis":
        return f"_args.append({value})"
    if typ == "rds":
        raise ValueError("'rds' arguments are R-only; use 'json' or 'df' for python problems")
    raise ValueError(f"Unknown argument type '{typ}'")


class PythonBackend(LanguageBackend):
    extension = "py"

    def write_harness(self, func, out_prefix, source_path, args_path,
                      digits, out_format, preload_paths, entry_path=None):
        harness_path = f"{out_prefix}.harness.py"
        arg_lines = []
        for typ, value in _parse_arg_lines(args_path):
            arg_lines.append(_py_arg_stmt(typ, value))
        if not arg_lines:
            raise ValueError(f"No arguments found in {args_path}")

        with open(harness_path, "w") as fh:
            fh.write(_HARNESS_TEMPLATE.format(
                digits=digits,
                out_format=out_format,
                preloads=[p for p in preload_paths if p],
                source_path=os.path.abspath(source_path),
                submission_name=os.path.splitext(os.path.basename(source_path))[0],
                entry_path=os.path.abspath(entry_path) if entry_path else None,
                func=func,
                arg_lines="\n".join("    " + line for line in arg_lines),
                out_path=f"{out_prefix}.out",
            ))
        return harness_path

    def command(self, harness_path):
        return ["python3", harness_path]

    def describe_args(self, args_path):
        descs = []
        for i, (typ, value) in enumerate(_parse_arg_lines(args_path), 1):
            descs.append(f"arg{i} ({typ}) = {format_arg_value(typ, value)}")
        return f"{len(descs)} argument(s):\n" + "\n".join(descs)
