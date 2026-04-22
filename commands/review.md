# *review

Process provisional MemPalace items — promote confirmed insights, deprecate stale ones.

## Behavior

1. Surface all `status: provisional` items (run `fmp list` filtered by status, or `fmp search "status:provisional"`).

2. If none: report "No provisional items. MemPalace is clean." Done.

3. For each provisional item, present:

```
[ID] — [category]
Claim: [the fact or insight]
Written: [date] | Source: [agent_derived / user_asserted]
Confidence: [inferred / observed]
Provenance: [what it was derived from, if any]

Options:
  PROMOTE — user confirms this is correct → confidence: user_confirmed, status: active
  DEPRECATE — no longer relevant → status: deprecated
  KEEP — leave as provisional for now
```

4. Process the decision:
   - **PROMOTE** → update item: `confidence: user_confirmed`, `status: active`, append to `confidence_history`
   - **DEPRECATE** → update item: `status: deprecated`, log reason
   - **KEEP** → no change

5. Report summary: "Reviewed [N] provisional items. [N] promoted, [N] deprecated, [N] kept."

## Note

Superseded items are not shown here — they're already filtered from retrieval. This command is only for active provisional items awaiting verification.
