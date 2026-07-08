---
description: Generate implementation planning document from a specification
argument-hint: "Specification name without .md (e.g., 02_registration)"
allowed-tools: Read, Write, Glob, Bash(git:*), Grep
---

# Implement Command — Plan Generator

Generate an implementation plan from any specification file.

## Step 1: Validate input

If $ARGUMENTS is empty, ask user for spec name and stop.

## Step 2: Locate spec file

Search for `.claude/specs/<spec-name>.md`:
```bash
find ".claude/specs" -name "*${SPEC_NAME}*" -type f
```

If not found or multiple matches, ask user to disambiguate.

## Step 3: Analyze codebase

Read and understand:
- `.claude/CLAUDE.md` — architecture, constraints, schema, routes
- `app.py` — existing routes and patterns
- `database/db.py` — database schema and helper functions
- `templates/base.html` — template patterns
- `requirements.txt` — available packages

## Step 4: Generate implementation plan

Create `.claude/plans/<spec-name>-plan.md` with these sections:

### 1. Feature Overview
- What will be built and why
- Connection to project roadmap

### 2. Current Architecture Analysis
- Relevant existing routes, database tables, templates
- Existing patterns to follow (validation, error handling, styling)

### 3. Dependencies
- What previous features must be complete
- What database changes are needed first
- What helper functions are required

### 4. Files to Modify
For each file:
- **Purpose:** Why it changes
- **Key changes:** Specific additions/modifications
- **Existing patterns:** Conventions to follow

### 5. Files to Create
For each new file:
- **Purpose:** What it does
- **Integration:** How it fits into the system

### 6. Implementation Phases

Break into concrete, testable phases:

#### Phase 1: [Name]
**Files:** [Which files]  
**Steps:**
1. Specific task
2. Specific task
3. Specific task

**Validation:**
- [ ] Testable check 1
- [ ] Testable check 2

#### Phase 2: [Name]
[Same format]

[Continue for each phase]

### 7. Validation Checklist
- [ ] Manual test case 1 (specific, runnable)
- [ ] Manual test case 2 (specific, runnable)
- [ ] Manual test case 3 (specific, runnable)
- [ ] Database state verified
- [ ] No errors in dev server
- [ ] Existing features still work

### 8. Risks & Edge Cases
- Specific risks to watch for
- Edge cases to handle (empty input, duplicates, constraints, etc.)
- How to handle each

### 9. Error Handling Strategy
- Where validation happens (client, server, database)
- How errors are displayed
- Form data preservation on error
- User-friendly error messages

### 10. Acceptance Criteria
Extract from spec's "Definition of done":
- [ ] Specific criterion 1
- [ ] Specific criterion 2
- [ ] Specific criterion 3
- [ ] All existing features work (no regressions)
- [ ] Code follows CLAUDE.md conventions
- [ ] All validation and error handling implemented

---

## Step 5: Save and report

Save to: `.claude/plans/<spec-name>-plan.md`

Print to user:
```
✓ Implementation plan generated
Spec:  .claude/specs/<spec-name>.md
Plan:  .claude/plans/<spec-name>-plan.md
```

Tell user: "Review the plan at `.claude/plans/<spec-name>-plan.md`. When ready, enter Plan Mode to begin."

Do not print the full plan unless asked.
