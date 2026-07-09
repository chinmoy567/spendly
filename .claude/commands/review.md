---
description: Review the current changes with the security-reviewer and code-reviewer sub-agents.
argument-hint: "(optional) file paths to review — defaults to the working diff"
allowed-tools: Read, Grep, Glob, Bash(git:*), Agent
---

You are coordinating a pre-commit review of the Spendly codebase.
Always follow the rules in CLAUDE.md.

User input: $ARGUMENTS

## Step 1 — Establish scope
- If `$ARGUMENTS` names specific files, that is the review scope.
- Otherwise, run `git diff` and `git diff --staged` to find the
  uncommitted changes. That working diff is the review scope.
- If there are no changes and no files were named, stop and tell
  the user there is nothing to review.

## Step 2 — Run both reviewers in parallel
Delegate to BOTH sub-agents in the same turn so they run concurrently:

1. **security-reviewer** — review the scope for exploitable
   security vulnerabilities (SQL injection, IDOR, XSS, auth/session
   flaws, CSRF, data exposure).

2. **code-reviewer** — review the scope for correctness bugs and
   Spendly convention violations.

Pass each sub-agent the exact scope from Step 1 (the named files, or
the working diff) so they review the same code.

## Step 3 — Consolidate the findings
Merge both reports into a single summary, de-duplicating any issue
both agents raised. Present findings in two sections:

### Security
Findings from security-reviewer, ranked by severity.

### Code quality & conventions
Findings from code-reviewer, ranked by severity.

For each finding keep: severity, `file_path:line_number`, the issue,
and the suggested fix.

## Step 4 — Final verdict
End with a single combined verdict:
- **Ready to commit** — no blocking issues from either reviewer.
- **Fix before commit** — list the blocking (critical/high) items.

Do not modify any code — this command is review-only. Let the user
decide which fixes to apply.
