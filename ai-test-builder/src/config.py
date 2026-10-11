from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


def slugify(value: str) -> str:
    """Convert a runtime subject like 'Grade 11 Physics' into a safe folder slug."""
    return (
        value.strip()
        .lower()
        .replace("&", "and")
        .replace("/", "-")
        .replace("\\", "-")
        .replace(" ", "-")
    )


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    schemas_dir: Path
    data_dir: Path
    input_dir: Path
    blueprints_dir: Path
    generated_tests_dir: Path
    memory_dir: Path
    blueprint_schema_path: Path

    @classmethod
    def load(cls) -> "Settings":
        root = Path(__file__).resolve().parent.parent
        data_dir = root / "data"
        schemas_dir = root / "schemas"
        return cls(
            root_dir=root,
            schemas_dir=schemas_dir,
            data_dir=data_dir,
            input_dir=data_dir / "input",
            blueprints_dir=data_dir / "blueprints",
            generated_tests_dir=data_dir / "generated_tests",
            memory_dir=data_dir / "memory",
            blueprint_schema_path=schemas_dir / "blueprint_schema.json",
        )

    def ensure_subject_dirs(self, subject: str) -> Dict[str, Path]:
        subject_slug = slugify(subject)

        input_path = self.input_dir / subject_slug
        blueprint_path = self.blueprints_dir / subject_slug
        generated_path = self.generated_tests_dir / subject_slug

        input_path.mkdir(parents=True, exist_ok=True)
        blueprint_path.mkdir(parents=True, exist_ok=True)
        generated_path.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        return {
            "subject_slug": Path(subject_slug),
            "input_path": input_path,
            "blueprint_path": blueprint_path,
            "generated_path": generated_path,
            "memory_path": self.memory_dir,
        }