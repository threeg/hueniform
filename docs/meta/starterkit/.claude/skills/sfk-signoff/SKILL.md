---
name: sfk-signoff
description: Sign off the current in-progress milestone — the human gate. Marks it Complete, moves the Current position to the next milestone, and commits that status change. Only run when the user explicitly approves the milestone's deliverable. Trigger on "sign off", "sign off the milestone", "approve this milestone", "mark it complete", or "this milestone is done".
---

# sfk-signoff — complete a milestone (the human gate)

Run this **only when the user explicitly approves** the current milestone's deliverable. It is the one
place a milestone becomes `Complete`. `sfk-next-milestone` produced and committed the draft; this skill
records the user's sign-off and advances the project.

## Procedure

1. **Confirm approval.** Verify the user is signing off the milestone that is currently `In progress`
   (🔶) in `process/milestone-plan.md`. If they have outstanding feedback, do **not** sign off — hand
   back to `sfk-next-milestone` to revise first.

2. **Check the deliverable is committed.** The milestone's draft and any revisions should already be
   committed (by `sfk-next-milestone`). If there are uncommitted changes, commit them first.

3. **Mark it `Complete` (✅)** in `process/milestone-plan.md` and **move the *Current position*** line
   to the next milestone (or, if this was the version's last milestone, note the version is ready to
   ship/tag and that `sfk-version` starts the next one).

4. **Commit the status change**, e.g. `process: <milestone> — signed off (complete)`. This commit
   carries the status flip and the *Current position* move; the deliverable itself was already
   committed.

5. **For the implementation milestone**, sign-off means the version's tickets are all `done` and the
   gates pass; on sign-off, note that the version can be tagged (e.g. `v0.1.0`) per
   `process/README.md`.

6. **Hand off.** Tell the user what is next: `sfk-next-milestone` for the following milestone, or
   `sfk-version` if the version is complete.

## Rules

- Run only on explicit user approval. The agent never self-signs-off a milestone.
- Sign-off is a status event: it flips the milestone and moves the *Current position*, nothing else.
- If the milestone isn't actually done (open feedback, failing gates), refuse and return to
  `sfk-next-milestone` or `sfk-next-ticket`.
