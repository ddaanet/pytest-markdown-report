# Skill: plan:design

Design phase planning for TDD implementation.

## Target Model
Opus (high-judgment tasks)

## Inputs Required
- Feature requirements or user request
- Relevant existing code/architecture (read AGENTS.md, relevant source files)

## Process

1. **Gather Context**
   - Read AGENTS.md for project conventions
   - Read relevant source files to understand current architecture
   - Identify affected components

2. **Spike Test (if applicable)**
   - Write throwaway test to verify current behavior
   - Document framework defaults that affect design
   - Identify what might "already work"

3. **Design Document Output**
   Write to `plans/{feature-name}-design.md`:
   - Goal statement (1-2 sentences)
   - Design decisions with options and rationale
   - Mark decisions requiring confirmation: `(REQUIRES CONFIRMATION)`
   - High-level implementation phases
   - Flag reference table (if adding CLI options)

4. **Handoff**
   - Document ready for plan:tdd phase
   - List any open questions for user

## Output Format
Terse design document. No implementation details - those come in plan:tdd phase.
