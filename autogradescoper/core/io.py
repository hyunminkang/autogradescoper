"""Small shared I/O helpers (JSON/YAML round-trip, logging, diffs)."""

from __future__ import annotations

import difflib
import json
import logging
import os

import yaml


def create_custom_logger(name: str, logfile: str | None = None,
                         level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear()

    fmt = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    if logfile is not None:
        outdir = os.path.dirname(logfile)
        if outdir and not os.path.exists(outdir):
            os.makedirs(outdir)
        fh = logging.FileHandler(logfile)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


def load_file_to_dict(file_path: str, file_type: str | None = None):
    """Load a JSON or YAML file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    if file_type is None:
        file_type = os.path.splitext(file_path)[1].lower()[1:]
    with open(file_path) as fh:
        if file_type == "json":
            return json.load(fh)
        if file_type in ("yaml", "yml"):
            return yaml.safe_load(fh)
    raise ValueError("Unsupported file type: use .json, .yaml, or .yml")


def write_dict_to_file(data, file_path: str, file_type: str | None = None) -> None:
    """Write a dictionary to a JSON or YAML file."""
    if file_type is None:
        file_type = os.path.splitext(file_path)[1].lower()[1:]
    with open(file_path, "w") as fh:
        if file_type == "json":
            json.dump(data, fh, indent=2)
        elif file_type in ("yaml", "yml"):
            yaml.safe_dump(data, fh, default_flow_style=False)
        else:
            raise ValueError("Unsupported file type: use .json, .yaml, or .yml")


def diff_texts(expected: str, observed: str, max_chars: int = 500) -> str:
    """Unified diff between expected and observed output."""
    diff = "\n".join(difflib.unified_diff(
        expected.splitlines(), observed.splitlines(),
        fromfile="expected", tofile="observed", lineterm=""))
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n... (truncated)"
    return diff


def truncate(text: str, max_chars: int) -> str:
    if len(text) > max_chars:
        return text[:max_chars] + "\n... (truncated)"
    return text
