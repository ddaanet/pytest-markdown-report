# Skill: review:analysis

Analyze TDD session data and produce recommendations.

## Target Model
Sonnet (detailed analysis)

## Inputs Required
- Extracted session log from `claudeutils session-log`
- Original TDD plan document
- Git diff of changes

## Process

1. **Compare Plan vs Execution**
   - Cycles planned vs completed
   - Order followed vs deviations
   - Stop conditions and how handled

2. **Assess TDD Compliance**
   For each cycle:
   - Was RED verified before GREEN?
   - Was GREEN minimal?
   - Were regressions handled individually?

3. **Identify Issues**
   - Planning gaps (cycles that were already done)
   - Execution issues (batch updates, skipped verification)
   - Design decisions made without approval

4. **Code Quality Check**
   - Review diffs for obvious issues
   - Check test quality (clear assertions, good names)
   - Note any code smells

5. **Output**
   Write to `plans/review-analysis-{date}.md`:
   - Summary (3-4 sentences)
   - TDD compliance table (cycle | RED | GREEN | issues)
   - Planning issues (bullet list)
   - Execution issues (bullet list)
   - Code quality notes
   - Recommendations (actionable, specific)

## Constraints
- Analysis only - do not modify any files
- Be specific: cite cycle numbers, line numbers, exact deviations
- Recommendations must name what file/section to change
