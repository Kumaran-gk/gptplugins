ANALYZE_TEST_INTENT = """
Analyze one or more source tests and extract a reusable blueprint.
Focus on:
- structure
- topic distribution
- difficulty profile
- trap patterns
- generation rules
"""

GENERATE_TEST_INTENT = """
Generate a fresh test from an existing blueprint.
Preserve:
- structure
- topic weighting
- difficulty intent
- style constraints
Avoid copying source questions verbatim.
"""

BUILD_CUMULATIVE_TEST_INTENT = """
Build one coherent cumulative test from multiple blueprints.
Preserve:
- fair unit balance
- difficulty progression
- structure coherence
- overall assessment identity
"""