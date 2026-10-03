# Preload for python problems: restrict imports to the standard library.
# The python analogue of preload_baseonly.R. Reference it from a problem:
#
#   problems:
#     - name: myFunc
#       lang: python
#       preload: preload_stdlib_only.py   # copy this file into your assignment
#
# It installs an import hook BEFORE the submission module is imported, so any
# `import numpy` inside the submission raises ImportError. This is a fairness
# mechanism (level playing field), not a security sandbox -- Gradescope's
# container is the security boundary.

import sys

_BLOCKED = {
    "numpy", "scipy", "pandas", "sklearn", "statsmodels", "sympy",
    "numba", "cython", "torch", "tensorflow", "jax", "polars", "pyarrow",
}

_real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) \
    else __builtins__.__import__


def _guarded_import(name, *args, **kwargs):
    root = name.split(".")[0]
    if root in _BLOCKED:
        raise ImportError(
            f"Importing '{root}' is not allowed in this assignment "
            f"(standard library only).")
    return _real_import(name, *args, **kwargs)


if isinstance(__builtins__, dict):
    __builtins__["__import__"] = _guarded_import
else:
    __builtins__.__import__ = _guarded_import

# also block anything already imported by the harness from being abused
for _mod in list(_BLOCKED):
    sys.modules.pop(_mod, None)
