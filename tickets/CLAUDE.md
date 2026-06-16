# Ticket workflow

The build runs ticket by ticket. The system is defined in `tickets/CONVENTIONS.md`; the per-ticket
format in `tickets/TICKET-TEMPLATE.md`; the execution order in `tickets/BOARD.md`.

- **Work tickets, not epics.** Epics (`HUE-E0n`) are a capability view only — no code ships against
  them; they close when their children are `done`. The unit of work is the leaf ticket (`HUE-NNN`).
- **Go in order.** Pick the lowest-numbered `todo` ticket whose every `depends_on` id is `done`.
  `BOARD.md` top-to-bottom is a legal sequence. **Never start a ticket whose dependencies aren't done.**
- **One ticket per commit.** A commit moves exactly one ticket: its code, its tests, its
  `status`/`## Notes`, and its `BOARD.md` row — together. This is the §12.3.7 rule and what keeps the
  history honest and reviewable.
- **Status lifecycle:** `todo → in-progress → in-review → done` (`blocked` when stuck). Set
  `in-progress` when you start; `done` only when the ticket's Definition of done holds in full.
- **Commit message:** `HUE-NNN: <short imperative>` (e.g. `HUE-007: matcher.constants`).
- **Close epics when their last child closes.** Check the epic's children list in its ticket file
  (`HUE-E0n`); if every child is `done`, mark the epic `done` in both its ticket file and the
  BOARD.md epic table in that same commit.
- **Run `/verify` after each batch.** This reviews the batch for reuse, quality and efficiency
  issues and proposes cleanup tickets. Accepted tickets go to the cleanup backlog in `BOARD.md`
  (CONVENTIONS.md §6); critical ones are promoted into the main sequence before the gate they affect.
