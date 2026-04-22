# *reflect

Review MemPalace health and surface items needing attention.

## Behavior

1. **Surface provisional items** — run `fmp list` or `fmp search` filtered to `status: provisional`. For each item: show the claim, category, when it was written, and what evidence level it has.

2. **Check stale derivations** — for provisional items with provenance, check if the MemPalace items or LightRAG chunks they depend on have since been superseded or removed. Flag any that have lost their ground truth.

3. **Check corpus freshness** — review `memory/LIGHTRAG.md` source list. Flag any sources that look out of date or mention documents that may have been updated.

4. **Report:**

```
MemPalace Reflection — [agent name]

Provisional items: [N]
  [N] recent (< 7 days) — likely still active
  [N] aging (7–30 days) — worth reviewing
  [N] stale (> 30 days) — consider promoting or deprecating

Stale derivations: [N] (sources superseded or missing)
Corpus gaps flagged: [N]

Run *review to process provisional items.
```

If nothing needs attention:

```
MemPalace is healthy. [N] active items, [N] provisional (all recent). Corpus sources current.
```
