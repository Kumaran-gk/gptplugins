from __future__ import annotations

from pathlib import Path
from typing import Any

from src.utils.json_utils import write_json_file


def ensure_parent_dir(file_path: str | Path) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_json(file_path: str | Path, data: Any) -> Path:
    path = ensure_parent_dir(file_path)
    return write_json_file(path, data)


def write_text(file_path: str | Path, text: str) -> Path:
    path = ensure_parent_dir(file_path)
    path.write_text(text, encoding="utf-8")
    return path
