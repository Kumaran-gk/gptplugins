from __future__ import annotations


VALID_SKILLS = {
    "analyze-test": "analyze_test",
    "generate-test": "generate_test",
    "build-cumulative-test": "build_cumulative_test",
    "build-test-pack": "build_test_pack",
}


def resolve_skill(skill_name: str) -> str:
    """Map CLI skill names to workflow method names."""
    if skill_name not in VALID_SKILLS:
        valid = ", ".join(VALID_SKILLS.keys())
        raise ValueError(f"Unknown skill '{skill_name}'. Valid skills: {valid}")
    return VALID_SKILLS[skill_name]
