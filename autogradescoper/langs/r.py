"""R and Rcpp backends.

The generated harness sources preloads, loads the target source file
(``source()`` for R, ``Rcpp::sourceCpp()`` for C++), builds the arguments
from the ``.args`` file, calls the function, and writes the result to
``<out_prefix>.out`` with deterministic formatting.

For ``rcpp``, compilation happens inside the harness on first run; budget
the extra ~5–20 s in each case's ``maxtime`` (see docs/languages.md).
"""

from __future__ import annotations

import os

from autogradescoper.langs.base import LanguageBackend

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def _parse_arg_lines(args_path: str):
    with open(args_path) as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            typ, _, value = line.partition(":")
            yield typ.strip(), value.strip()


def _r_literal(typ: str, value: str, argname: str) -> str:
    if typ in ("numeric", "int"):
        vals = value.replace(",", " ").split()
        return f"{argname} <- c(" + ",".join(vals) + ")"
    if typ == "str":
        vals = value.split()
        return f"{argname} <- c(" + ",".join(f"'{v}'" for v in vals) + ")"
    if typ == "df":
        return f"{argname} <- read.table('{value}', header=TRUE)"
    if typ == "rds":
        return f"{argname} <- readRDS('{value}')"
    if typ == "json":
        return f"{argname} <- read_json_file('{value}')"
    if typ == "eval":
        return f"{argname} <- (function() {{ {value} }})()"
    if typ == "asis":
        return f"{argname} <- ( {value} )"
    raise ValueError(f"Unknown argument type '{typ}' in {argname}")


class RBackend(LanguageBackend):
    extension = "R"
    load_template = "source('{path}')"

    def write_harness(self, func, out_prefix, source_path, args_path,
                      digits, out_format, preload_paths):
        harness_path = f"{out_prefix}.harness.R"
        lines = [f"source('{os.path.join(_ASSETS, 'autogradescoper_utils.R')}')"]
        for p in preload_paths:
            if p:
                lines.append(f"source('{p}')")
        lines.append(self.load_template.format(path=os.path.abspath(source_path)))

        argnames = []
        for i, (typ, value) in enumerate(_parse_arg_lines(args_path), 1):
            argnames.append(f"arg{i}")
            lines.append(_r_literal(typ, value, f"arg{i}"))
        if not argnames:
            raise ValueError(f"No arguments found in {args_path}")

        lines.append(f"rst <- {func}(" + ", ".join(argnames) + ")")
        lines.append(
            f"write_result(rst, file='{out_prefix}.out', "
            f"digits={digits}, format='{out_format}')"
        )
        with open(harness_path, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        return harness_path

    def command(self, harness_path):
        return ["Rscript", "--vanilla", harness_path]

    def describe_args(self, args_path):
        descs = []
        for i, (typ, value) in enumerate(_parse_arg_lines(args_path), 1):
            descs.append(f"arg{i} ({typ}) = {value}")
        return f"{len(descs)} argument(s):\n" + "\n".join(descs)


class RcppBackend(RBackend):
    """C++ via Rcpp: submissions are .cpp files with // [[Rcpp::export]]."""

    extension = "cpp"
    load_template = "suppressMessages(Rcpp::sourceCpp('{path}'))"
