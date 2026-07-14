## Current task

No work in progress — the dev→main reconciliation, agent-core backout, and CLAUDE.md refresh are all finished; main now stands as a clean non-agent-core project.

## Open decisions

- Whether to re-adopt agent-core later in a controlled way (restore the submodule from the external repo + wire hooks into `settings.json`) or keep main hook-free. The backout removed all local skills/hooks/fragments; their content survives only in the external agent-core repo.
