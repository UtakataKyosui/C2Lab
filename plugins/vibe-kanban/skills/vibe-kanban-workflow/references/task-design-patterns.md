# Task Design Patterns for vibe-kanban

## Issue Template

```markdown
## Context
[Current state of the code, what exists, what behavior is expected]

## Goal
[Specific, measurable outcome]

## Acceptance Criteria
- [ ] [Specific condition 1]
- [ ] [Specific condition 2]
- [ ] [Tests pass for new functionality]

## Files to Check
- `src/path/to/relevant/file.ts`
- `tests/unit/relevant-test.spec.ts`

## Out of Scope
- [Do NOT touch X]
- [Do NOT refactor Y while fixing this]
```

---

## Pattern 1: Bug Fix

**Good:**
```
Title: Fix null pointer crash in UserProfile when bio field is missing

Context: UserProfile component crashes with "Cannot read properties of null (reading 'length')"
when a user has no bio. Error occurs at UserProfile.tsx:47.

Goal: Render an empty string or placeholder when bio is null/undefined.

Acceptance Criteria:
- [ ] UserProfile renders without error when bio is null
- [ ] UserProfile renders without error when bio is undefined
- [ ] Existing tests pass
- [ ] Add test case for null bio

Files to Check:
- src/components/UserProfile.tsx (line 47)
- tests/unit/UserProfile.spec.ts
```

**Bad:**
```
Title: Fix the profile bug

[No description]
```

Why bad: Claude Code cannot locate the bug or understand the expected behavior.

---

## Pattern 2: New Feature (Bounded)

**Good:**
```
Title: Add CSV export button to the Reports page

Context: Reports page at /reports shows a table of monthly metrics.
The table component is DataTable in src/components/DataTable.tsx.

Goal: Add a "Export CSV" button above the table that downloads the current
table data as a CSV file with headers matching column names.

Acceptance Criteria:
- [ ] Button appears above the DataTable with label "Export CSV"
- [ ] Clicking exports a CSV file with correct headers
- [ ] CSV filename format: report_YYYY-MM-DD.csv
- [ ] Empty table exports header row only (no error)

Out of Scope:
- Do NOT add Excel/PDF export
- Do NOT change existing table component internals
```

**Bad:**
```
Title: Add data export functionality

[No description - Claude Code will invent scope]
```

---

## Pattern 3: Test Coverage

**Good:**
```
Title: Add unit tests for the calculateShipping() function

Context: calculateShipping() in src/utils/shipping.ts is currently untested.
Function signature: calculateShipping(weightKg: number, distanceKm: number, express: boolean): number

Goal: Write comprehensive unit tests covering all branches and edge cases.

Acceptance Criteria:
- [ ] Test normal case (weight > 0, distance > 0, express false)
- [ ] Test express shipping (express = true adds 20% surcharge)
- [ ] Test zero weight (should return base handling fee)
- [ ] Test negative weight (should throw RangeError)
- [ ] Test zero distance (should return minimum charge)
- [ ] All tests pass with `pnpm test`

Files to Check:
- src/utils/shipping.ts
- tests/unit/shipping.spec.ts (create if not exists)
```

---

## Pattern 4: Refactor (Bounded)

**Good:**
```
Title: Extract validation logic from UserForm into a standalone validateUser() function

Context: UserForm.tsx contains inline validation logic (lines 45-120) that is duplicated
in EditUserForm.tsx. Both use the same rules.

Goal: Extract shared validation into src/utils/validateUser.ts and import it in both forms.
Do not change validation rules or form behavior.

Acceptance Criteria:
- [ ] validateUser.ts created with extracted logic
- [ ] UserForm.tsx imports and uses validateUser()
- [ ] EditUserForm.tsx imports and uses validateUser()
- [ ] Existing form tests still pass
- [ ] Add tests for validateUser() directly

Out of Scope:
- Do NOT change validation rules
- Do NOT touch other forms
- Do NOT add new validation fields
```

---

## Antipatterns to Avoid

### Antipattern 1: Decision-Required Tasks

```
Title: Choose between REST and GraphQL for the new API

[Claude Code cannot make architectural decisions on behalf of the team]
```

**Fix**: Make the decision yourself, then create: "Implement GraphQL API for /users endpoint"

---

### Antipattern 2: Open-Ended Exploration

```
Title: Improve performance of the dashboard

[Without metrics or specific targets, Claude Code will make arbitrary changes]
```

**Fix**: Profile first, then: "Replace O(n²) sort in fetchUserStats() with O(n log n) sort (currently takes 800ms for 1000 users)"

---

### Antipattern 3: Cross-Cutting Concerns

```
Title: Add error handling to the entire application

[Too broad - Claude Code will attempt to touch every file]
```

**Fix**: Break into bounded tasks:
- "Add error boundary to DataTable component"
- "Add try-catch to all API calls in userService.ts"
- "Add 404 handler to Express router"

---

### Antipattern 4: Interactive Dependency

```
Title: Set up the database (ask me for credentials during setup)

[Claude Code cannot pause for human input mid-session]
```

**Fix**: Provide all information upfront or use environment variables:
"Set up PostgreSQL connection using DATABASE_URL from .env.example"

---

## Task Sizing Guidelines

| Size | Duration | Characteristics |
|------|----------|-----------------|
| **XS** | < 5 min | Single function change, obvious fix |
| **S** | 5-15 min | Single component, clear scope |
| **M** | 15-30 min | Multi-file feature, clear boundaries |
| **L** | 30-60 min | Multiple components, integration work |
| **XL** | > 60 min | Consider splitting into smaller tasks |

Prefer M and smaller for better results. XL tasks risk context overflow and wandering scope.
