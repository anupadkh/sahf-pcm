# Ownership and approval validation

- Backend tests cover supplied workbook parsing, creator ownership within the same organization, uploaded draft visibility, edit/return/resubmit workflows, immutable approved public snapshots, reviewer/admin conflict replacement and selective corrections, canonical record IDs, creator attribution, comment history, stale approval rejection, and idempotent migration of existing published data.
- Final result: 14 tests passed.
- Angular production build validates the project-list component, workflow tabs, creator columns, editable published records, approved-version comparisons, and moderation controls.
- Browser checks use an isolated preview database rather than the live project's data.
- Browser upload imported all 24 revised portfolio records and immediately selected Pending / drafts, showing those records and their uploader. Switching to Sent for review showed the submitted queue.

Conflicted imports are intentionally retained for moderation. Undisclosed amounts and narrative sector fields continue to carry review notes.

Deletion update verification: 17 backend tests pass, including published deletion approval permissions, rejection, draft deletion, ownership and stale-request checks. Angular production build passes.
