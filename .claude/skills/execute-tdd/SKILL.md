---
name: execute-tdd
description: Execute TDD cycles from plan, handling RED/GREEN/REFACTOR phases with structured logging.
---

# Skill: execute:tdd

Execute TDD cycles from plan.

## Target Model
Haiku (execution)

## Inputs Required
- TDD plan from plan:tdd phase
- Current test count baseline

## Protocol

For each cycle:

### 1. RED Phase
- Write test exactly as specified in plan
- Run test: `just test` or specified command
- **VERIFY test fails** with expected message
- If test passes unexpectedly → STOP (see stop conditions)

### 2. GREEN Phase
- Write minimal code to pass test
- Run test again
- **VERIFY test passes**
- Run full suite: `just test`
- If other tests fail → handle individually (never batch)

### Exploration Limit

During GREEN phase, if implementation is not straightforward:

**Allowed (1-2 attempts):**
- Fix syntax errors, typos
- Adjust minor details from plan

**STOP and document if:**
- Requires reading external documentation
- Requires > 2 implementation attempts
- Error is different from plan specification
- Requires researching pytest/framework internals

When stopping:
1. Document what was tried
2. Document what error occurred
3. Document what information is needed
4. Mark cycle as BLOCKED
5. Await guidance from orchestrator

Do NOT continue exploring. Extended exploration violates minimal GREEN principle.

### 3. REFACTOR Phase (optional)
- Only if code is unclear
- Run tests after any change

### 4. Structured Log Entry
After each cycle, append to `plans/session-log-{date}.md`:

```markdown
### Cycle X.Y: [name] [timestamp]
- Status: RED_VERIFIED | GREEN_VERIFIED | STOP_CONDITION | REGRESSION
- Test command: `[exact command run]`
- RED result: [FAIL as expected | PASS unexpected | N/A for regression]
- GREEN result: [PASS | FAIL - reason]
- Regression check: [N/N passed | N failures - list]
- Files modified: [list with line ranges]
- Stop condition: [none | description]
- Decision made: [none | description with rationale]
```

This structured format enables automated extraction by `claudeutils session-log`.

## Stop Conditions

**Test passes when should fail:**
- Check if cycle is marked `[REGRESSION]` → expected, proceed
- Otherwise: investigate, document finding
- If feature works via valid mechanism → mark complete, proceed
- If test is wrong → fix test, verify RED

**Existing tests fail:**
- Do NOT batch-update
- For each failure, choose one:
  - Test was wrong → update, document why
  - Implementation wrong → fix code
  - Intentional change → update as part of cycle

## Output
After all cycles, write raw session log to `plans/session-{date}-{feature}.md`:
- What happened (factual, no analysis)
- Test counts before/after
- Files modified
- Any stop conditions encountered
