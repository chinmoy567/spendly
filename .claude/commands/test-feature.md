---
description: Generate pytest test cases for a feature using the test-generator sub-agent.
argument-hint: <feature-name>
---

# Generate Tests

Generate comprehensive pytest test cases for the requested feature.

## Instructions

1. Identify the requested feature.

2. Locate its specification under:

- `.claude/specs/`
- `docs/`
- `IMPLEMENTATION_PLAN.md`
- `README.md`

3. Delegate the work to the **test-generator** sub-agent.

The sub-agent must:

- Read the specification.
- Extract all acceptance criteria.
- Generate pytest test cases.
- Save them inside the appropriate `tests/` directory.
- Run the generated tests.
- Fix only test-related issues.
- Report coverage and any implementation mismatches.

After the sub-agent finishes, summarize:

- Specification used
- Test file created
- Number of tests
- Coverage
- Remaining issues