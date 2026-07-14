## Current task

Recover `scripts/benchmark.py` output — `main()` counts tokens correctly (edify integration works) but prints nothing because the result-table `print()` calls were stripped, leaving dead f-strings and `if: pass / else: pass` around lines 104–131.

## Open decisions

- What the benchmark results table should look like: it has per-format `tokens` and `lines`, plus percentage deltas vs the default-pytest baseline and vs the tuned-pytest baseline, and a markdown-vs-pytest-default comparison — decide the columns/layout to print (the stripped code computed the two `+X%` deltas, so at minimum name / tokens / lines / %-vs-baseline / %-vs-tuned).
