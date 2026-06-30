---
name: sfk-next-ticket
description: Implement the next ready ticket in the queue, one ticket per commit, during the implementation milestone. Picks the lowest-numbered todo ticket whose dependencies are all done, implements it test-first where applicable, and keeps the ticket, board, and tests honest in the same commit. Trigger on "next ticket", "work the next ticket", "implement the next ticket", or "keep building".
---

# sfk-next-ticket — implement one ticket

Use during the implementation milestone. One invocation does exactly one ticket and produces one
commit. Follow the ticket-workflow rules in `process/tickets/CLAUDE.md` and the definition of done in
the root `CLAUDE.md`.

## Procedure

1. **Pick the ticket.** From `process/tickets/BOARD.md`, take the lowest-numbered `todo` ticket whose
   every `depends_on` id is `done`. Never start a ticket whose dependencies are not done. If none are
   ready, say so and stop.

2. **Load context.** Read the ticket file, the `## Notes` of its `depends_on` tickets, and the spec
   sections it references (`process/requirements/requirements.md` for its `implements` ids,
   `process/architecture/architecture.md`, `process/architecture/api-contract.md`, the relevant
   wireframe). The ticket plus that spec should be enough — no conversational context required.

3. **Set `in-progress`** in the ticket and its `BOARD.md` row.

4. **Implement.** Honour the architecture dependency rule. Use test-first (red–green) for deterministic
   and contract-pinned work (write the failing test from the requirement/contract, confirm it fails for
   the right reason, then implement); characterisation tests for probabilistic/external layers. New or
   changed numbered-requirement behaviour ships with its tests **in the same commit**.

5. **Run the gates.** The default gate must pass with zero warnings; run the heavier gate the ticket
   names (model / perf / e2e) where it applies; hold the core coverage gate for core-touching work.

6. **Close honestly, in one commit.** Set the ticket `done`, append a dated `## Notes` line with the
   **completion report** (plain-language summary + one-line sanity test; for UI tickets, fill
   `## QA steps`), and update the `BOARD.md` row — all in the same commit as the code and tests. Commit
   message: `<PRJ>-NNN: <short imperative>`. Close the parent epic if this was its last child.

7. **At batch boundaries, run `sfk-verify`.** After a batch of related tickets, invoke `sfk-verify` to
   review for reuse/quality/efficiency and propose cleanup tickets; promote any critical finding before
   the gate it would affect.

When the version's tickets are all `done` and the gates pass, the implementation milestone is ready for
the user to sign off with `sfk-signoff`.

## Rules

- One ticket, one commit. Never combine unrelated changes.
- A ticket is not `done` until committed; "done on my machine" is `in-review`.
- If implementing reveals the spec is wrong, change the relevant `process/` file first and reference it
  — do not silently reinterpret a settled decision.


## Thread name

Run this in its own thread. Cowork auto-titles a thread and **cannot rename it programmatically** —
only the user can. As your **first action**, suggest the name below and ask the user to rename this
thread to it. `PROJCODE` is the project code (the ticket prefix) recorded as `project_code` in
`process/.sfk/manifest.md`, set when the project was created with `sfk-init` (e.g. `/sfk-init HUE`).

**Suggested name:** `PROJCODE Implementation`  (e.g. `HUE Implementation`)
