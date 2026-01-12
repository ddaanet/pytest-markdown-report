---
name: plan-tdd
description: Create detailed TDD cycle plans from design documents with exact test specifications and stop conditions.
---

# Skill: plan:tdd

Create detailed TDD cycle plan from design document.

## Target Model
Sonnet (detailed planning)

## Inputs Required
- Design document from plan:design phase
- AGENTS.md for project conventions

## Process

1. **Read Design Document**
   - Understand goals and design decisions
   - Note any `(REQUIRES CONFIRMATION)` items - ask user if unresolved

2. **Define TDD Cycles**
   For each cycle specify:
   - Cycle ID (e.g., 1.1, 1.2)
   - Dependencies: `[DEPENDS: x.y]` or `[REGRESSION]` for verification tests
   - RED: Exact test to write (function name, assertions)
   - Expected failure message
   - GREEN: Minimal implementation description
   - Files affected

3. **Stop Conditions**
   Include standard stop conditions:
   ```
   STOP if test passes when should be RED:
   - If feature already works: convert to [REGRESSION], mark complete, proceed
   - If test is wrong: fix test, verify RED, continue

   STOP if existing tests break:
   - Evaluate each failure individually (never batch-update)
   - Document rationale for each test change
   ```

4. **Output**
   Write to `plans/{feature-name}-tdd.md`:
   - Link to design document
   - Cycle-by-cycle plan with exact test code
   - Stop conditions
   - Expected test count progression

## Extraction Compatibility

Structure cycles to support automated extraction:
- Use consistent cycle IDs (X.Y format)
- Include expected failure messages (enables RED verification check)
- Mark `[REGRESSION]` cycles explicitly
- Specify exact test commands

## Constraints
- Each cycle must be independently verifiable
- Cycles should be small (1-3 assertions per test)
- Mark cycles that verify existing behavior as `[REGRESSION]`
