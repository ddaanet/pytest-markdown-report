# Skill: review:updates

Execute process improvements based on analysis.

## Target Model
Opus (high-judgment decisions)

## Inputs Required
- Analysis document from review:analysis
- AGENTS.md
- Relevant skill files

## Process

1. **Triage Recommendations**
   From analysis, categorize each recommendation:
   - ACCEPT: Clear improvement, low risk
   - REJECT: Not worth complexity, or disagree
   - MODIFY: Good idea, different implementation
   - DEFER: Needs more data or user input

2. **Execute Accepted Changes**
   For each ACCEPT/MODIFY:
   - Update target file (AGENTS.md, skills, plan templates)
   - Keep changes minimal and focused
   - Add brief comment explaining change origin

3. **Document Decisions**
   Append to `plans/review-updates-{date}.md`:
   - Each recommendation with disposition (ACCEPT/REJECT/MODIFY/DEFER)
   - Rationale for non-obvious decisions
   - Files modified

4. **User Questions**
   If any recommendations need user input:
   - List at end of output
   - Do not guess - ask

## Constraints
- Only modify persistent files (AGENTS.md, skills)
- Do not modify session-specific files (session.md, plans/*.md)
- Preserve existing content - add/refine, don't rewrite
