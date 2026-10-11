from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from jsonschema import Draft202012Validator

from src.utils.json_utils import load_json_file
from src.utils.logging_utils import get_logger


LOGGER = get_logger("blueprint.validator")


def load_schema(schema_path: str | Path) -> Dict[str, Any]:
    path = Path(schema_path)

    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")

    return load_json_file(path)


def validate_blueprint(
    blueprint: Dict[str, Any],
    schema_path: str | Path,
) -> Dict[str, Any]:
    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema)

    errors: List[Dict[str, Any]] = []
    for error in sorted(validator.iter_errors(blueprint), key=lambda e: list(e.path)):
        errors.append(
            {
                "path": ".".join(str(part) for part in error.path) or "<root>",
                "message": error.message,
            }
        )

    result = {
        "is_valid": len(errors) == 0,
        "error_count": len(errors),
        "errors": errors,
    }
    LOGGER.info(
        "Validated blueprint id=%s valid=%s errors=%s",
        blueprint.get("blueprint_id"),
        result["is_valid"],
        result["error_count"],
    )
    return result
