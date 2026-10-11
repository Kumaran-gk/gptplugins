from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def pretty_dump_json(data: Any, *, sort_keys: bool = False) -> str:
    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
        sort_keys=sort_keys,
    )


def load_json_text(text: str) -> Any:
    return json.loads(text)


def load_json_file(file_path: str | Path) -> Any:
    path = Path(file_path)
    return load_json_text(path.read_text(encoding="utf-8"))


def write_json_file(
    file_path: str | Path,
    data: Any,
    *,
    sort_keys: bool = False,
) -> Path:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_dump_json(data, sort_keys=sort_keys), encoding="utf-8")
    return path
