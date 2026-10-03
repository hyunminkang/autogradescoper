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
bool       scalar or comma/space-separated logical vector
           (TRUE/FALSE, T/F, 1/0, case-insensitive)
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

#: max characters of a single argument value shown in student-visible output
ARG_DISPLAY_MAX = 120


def format_arg_value(typ: str, value: str, max_chars: int = ARG_DISPLAY_MAX) -> str:
    """Render one argument value for student-visible display.

    Long values (e.g. a 1,000-element vector) are truncated to
    ``max_chars`` characters at a token boundary, with a note giving the
    total number of values so students still know the full input size.
    """
    value = value.strip()
    if len(value) <= max_chars:
        return value
    n_values = len(value.replace(",", " ").split())
    cut = value[:max_chars]
    # do not cut in the middle of a token
    for sep in (",", " "):
        pos = cut.rfind(sep)
        if pos > 0:
            cut = cut[:pos]
            break
    return f"{cut}, ... [truncated; {n_values} values in total]"


def parse_bool_token(v: str) -> bool:
    """Parse one bool-type token (TRUE/FALSE, T/F, 1/0; case-insensitive)."""
    u = v.strip().upper()
    if u in ("TRUE", "T", "1"):
        return True
    if u in ("FALSE", "F", "0"):
        return False
    raise ValueError(f"Invalid bool token: {v!r}")


class LanguageBackend(ABC):
    """One per language; stateless."""

    #: submission file extension, e.g. "R", "py", "cpp"
    extension: str = ""

    @abstractmethod
    def write_harness(self, func: str, out_prefix: str, source_path: str,
                      args_path: str, digits: int, out_format: str,
                      preload_paths: list[str | None],
                      entry_path: str | None = None) -> str:
        """Write the driver script; return its path.

        `entry_path`, when given, is a file of given code loaded after the
        submission; `func` is looked up there instead of in the submission.
        """

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
