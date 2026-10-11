from __future__ import annotations

import pytest

from src.generation.custom_test_writer import save_custom_test


def test_save_custom_test_writes_separate_versions_without_overwriting(temp_settings):
    kwargs = {
        "settings": temp_settings,
        "subject": "Biology",
        "title": "Cell Division Review",
        "student_markdown": "# Questions\n\n1. Explain mitosis.",
        "teacher_markdown": "# Answers\n\n1. Mitosis produces two daughter cells.",
    }
    first = save_custom_test(**kwargs)
    second = save_custom_test(**kwargs)

    first_student = first["outputs"]["student_md"]
    second_student = second["outputs"]["student_md"]
    assert first_student != second_student
    assert "1. Explain mitosis." in open(first_student, encoding="utf-8").read()
    assert "Mitosis produces" in open(first["outputs"]["teacher_md"], encoding="utf-8").read()


def test_save_custom_test_rejects_invalid_formats(temp_settings):
    with pytest.raises(ValueError, match="export_formats"):
        save_custom_test(
            settings=temp_settings,
            subject="Math",
            title="Algebra",
            student_markdown="# Questions",
            export_formats=["html"],
        )
