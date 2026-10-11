from __future__ import annotations

from src.blueprint.validator import validate_blueprint


def test_valid_blueprint_passes(valid_blueprint, repo_schema_path):
    result = validate_blueprint(valid_blueprint, repo_schema_path)
    assert result["is_valid"] is True
    assert result["error_count"] == 0


def test_invalid_blueprint_fails(valid_blueprint, repo_schema_path):
    invalid = dict(valid_blueprint)
    invalid.pop("topic_distribution", None)

    result = validate_blueprint(invalid, repo_schema_path)
    assert result["is_valid"] is False
    assert result["error_count"] >= 1