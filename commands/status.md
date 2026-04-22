# *status

Report harness health.

## Behavior

Read the harness config and memory state, then report:

```
Harness Status — [agent name]
Last checked: [date]

MemPalace
  Total items: [N]
  Active: [N] | Provisional: [N] | Deprecated: [N] | Superseded: [N]
  By category: [category: N, category: N, ...]
  Supersession rate: [N]% (high = taxonomy churning)
  Provisional unpromoted > 30 days: [N] → run *reflect

LightRAG Corpus
  Sources: [N]
  Last ingested: [date or "unknown"]
  Server: [reachable / unreachable]

Gate Health
  [If logs/gates.log exists:]
    Turns logged: [N] (last 7 days)
    Groundedness: [N]% passed
    Retrieval empty after retries: [N]%
    Persist failures: [N]
  [If no logs:]
    No gate log found — confirm gates.py or gate instructions are active

Flags
  [Any provisionals > 30 days unpromoted]
  [Any persist failures]
  [LightRAG unreachable]
  [Corpus sources older than 90 days]
```

## If Not Onboarded

If `RUNTIME.md` does not exist:

```
Harness not installed. Run *onboard to build one.
```
