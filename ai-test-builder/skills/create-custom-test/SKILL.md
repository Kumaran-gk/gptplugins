---
name: create-custom-test
description: Create new practice questions from a user's subject, topic, grade, difficulty, question types, and other preferences, even when no source paper or blueprint is supplied.
---

# Create custom test

Use this skill when someone asks for questions or a practice test based on their
preferences. Do not require a source paper, blueprint, API key, or a fixed subject.

1. Read the supplied preferences: subject, topic or unit, level, question count,
   question types, difficulty, marks, answer style, and requested format. Ask only
   for details that are essential to make a meaningful test. Choose sensible
   defaults for omitted preferences and state them briefly.
2. Draft original, subject-accurate questions. Match the requested scope and
   difficulty. Check that the count, marks, question types, and topics match.
3. If an answer key is requested or useful, solve every question independently.
   Keep solutions and marking guidance in a separate teacher version. Check
   calculations, units, formulas, and multiple-choice distractors.
4. Return the questions in the conversation. When the user wants files, call the
   `ai_test_builder.save_custom_test` MCP tool with complete student markdown and
   optional teacher markdown. It saves markdown and can export DOCX or PDF.
5. Give the user the created file paths. Never claim an export succeeded unless
   the tool returns its path.

If the user supplies old tests and wants their structure preserved, use
`build-test-pack` or `analyze-test` instead. If a valid blueprint is supplied,
use `generate-test`.
