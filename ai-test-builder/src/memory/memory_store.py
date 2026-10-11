from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from src.utils.logging_utils import get_logger


LOGGER = get_logger("memory.store")


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _memory_file_name(subject_slug: str) -> str:
    return f"{subject_slug}_memory_index.jsonl"


def append_memory_record(
    *,
    memory_dir: str | Path,
    subject_slug: str,
    record: Dict[str, Any],
) -> Path:
    memory_dir_path = _ensure_dir(Path(memory_dir))
    file_path = memory_dir_path / _memory_file_name(subject_slug)

    with file_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    LOGGER.info(
        "Appended memory record type=%s subject=%s path=%s",
        record.get("record_type"),
        subject_slug,
        file_path,
    )
    return file_path


def load_memory_records(
    *,
    memory_dir: str | Path,
    subject_slug: str,
) -> List[Dict[str, Any]]:
    memory_dir_path = Path(memory_dir)
    file_path = memory_dir_path / _memory_file_name(subject_slug)

    if not file_path.exists():
        return []

    records: List[Dict[str, Any]] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))

    LOGGER.info(
        "Loaded memory records subject=%s count=%s path=%s",
        subject_slug,
        len(records),
        file_path,
    )
    return records
