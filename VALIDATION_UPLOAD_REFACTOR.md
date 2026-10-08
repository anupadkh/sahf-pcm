# Upload and refactor validation

Validated on 30 September 2026.

- Seven backend tests passed, including the supplied workbook itself: worksheet discovery selects the revised portfolio instead of the empty PCM Template, all 24 revised records import as drafts, monetary annotations and undisclosed amounts are handled, narrative sector cells are retained for review, and distinct project IDs sharing titles are accepted.
- Contributor parsing of the supplied revised sheet yields two Nepal records and explicitly excludes 22 other-country rows.
- Empty worksheets produce a 422 error rather than a misleading zero-row success.
- Whitespace/case normalization of Yes/No and IBF flags is covered.
- Existing workflow, organization permissions, revoked sessions, validation policies, duplicate rejection and atomic error handling tests continue to pass.
- Angular production build checked after separating application bootstrap, shell, models, services, guards, login, upload, editor and utilities.
- Browser end-to-end test imported the two Nepal records from the actual uploaded reference workbook and displayed the 22 excluded-country rows plus review warnings. Tested against a separate preview database; the project's existing database was not modified.
- Browser role checks confirmed logged-out contributor URLs redirect to sign-in, only Contributor navigation appears after contributor login, and administrator URLs redirect the contributor to their own workspace.
- Fixed zoneless Angular rendering after asynchronous worksheet discovery so the worksheet dropdown appears and processing state clears.

The source workbook contains genuine data quality issues; import warnings are intentionally retained for technical review. Undisclosed funding is not converted to zero.
