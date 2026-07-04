"""Language backend interface.

A backend does exactly two things:

1. ``write_harness(...)`` — generate a small driver script that loads a
   preload file (optional), loads the solution/submission source, parses the
   test-case ``.args`` file into native values, calls the target function,
   and writes the result to ``<out_prefix>.out`` in a deterministic text
   format.
2. ``command(...)`` — return the argv list that executes that harness.

Everything else (timeouts, comparison, scoring, reporting) is language-
agnostic and lives in :mod:`autogradescoper.core`.

Because a submission is always compared against a solution *in the same
language*, backends only need internally-consistent output formatting — no
cross-language equivalence is required.

The ``.args`` file format (one argument per line, ``type:value``):

=========  =====================================================
type       meaning
=========  =====================================================
numeric    scalar or comma/space-separated numeric vector
int        scalar or comma/space-separated integer vector
str        one or more whitespace-separated strings
df         path to a TSV/whitespace table with a header row
json       path to a JSON file
eval       language-native expression evaluated in the harness
asis       language-native literal inserted verbatim
rds        (R family only) path to an .rds file
=========  =====================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LanguageBackend(ABC):
    """One per language; stateless."""

    #: submission file extension, e.g. "R", "py", "cpp"
    extension: str = ""

    @abstractmethod
    def write_harness(self, func: str, out_prefix: str, source_path: str,
                      args_path: str, digits: int, out_format: str,
                      preload_paths: list[str | None]) -> str:
        """Write the driver script; return its path."""

    @abstractmethod
    def command(self, harness_path: str) -> list[str]:
        """Return the argv list that runs the harness."""

    @abstractmethod
    def describe_args(self, args_path: str) -> str:
        """Human-readable description of a test case's arguments."""


def get_backend(lang: str) -> LanguageBackend:
    from autogradescoper.langs.python_lang import PythonBackend
    from autogradescoper.langs.r import RBackend, RcppBackend

    backends = {"r": RBackend, "rcpp": RcppBackend, "python": PythonBackend}
    if lang not in backends:
        raise ValueError(f"Unsupported language: {lang}")
    return backends[lang]()
