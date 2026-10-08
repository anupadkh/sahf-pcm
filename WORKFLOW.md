# Project ownership and approval workflow

## Contributor

Contributors can upload a worksheet or create records for any supported country. Every new record stores the authenticated creator's email and creation time. A contributor's private list includes only their own records; sharing an organization does not grant access to another contributor's work.

Imports create drafts. After import, filters are cleared and the Pending / drafts tab opens so the imported records are visible. Contributors may edit drafts, submitted records, returned records and published records. Editing an unpublished submitted record withdraws it to draft for resubmission. Saving an edit to a record with an approved public version automatically requests review while leaving the approved version intact. Reviewer comments remain visible in the record and its comment history.

## Reviewer and administrator

Both roles see all records and creator information. Tabs show All records, Pending / drafts, Published, Sent for review, Returned for correction, and Consolidated. The Published tab includes records with approved snapshots even when a new revision is awaiting review.

Reviewers and administrators can review, correct, return and approve submissions. The record editor compares a proposed revision against its approved public version. Approval copies the working data into the approved snapshot. Return-for-correction requires a comment. An approval based on an outdated open record is rejected so newer contributor changes cannot be approved without inspection.

## Conflicts

Potential duplicate imports are retained as drafts with warnings. Conflicting lender/project IDs, or matching title/country where an external ID is unavailable, block ordinary publication. Distinct external IDs can legitimately share a project title.

Moderators see existing and incoming values side by side. They can replace the existing record with the submitted data, or edit selected fields of the existing record and approve those corrections. The canonical existing ID and creator are retained; the incoming record is marked Consolidated and linked to that canonical record. Both prior versions and moderation comments are retained in history. Another unresolved approved conflict or an existing record with its own unresolved revision must be handled before consolidation.

## Public

Public queries read only approved snapshots. Drafts, submissions and unapproved edits are never substituted for public data. The previous approved version remains visible during edits, technical review and correction. Consolidated source records do not create a second public entry.

## Existing data migration

Startup adds creator fields, approved snapshots, history and comment tables without removing project data. Existing published records become approved snapshots. Creator identity is recovered from exact creation audit entries, or an unambiguous import audit event near the original insertion timestamp and organization. Where the old database has insufficient evidence, the creator remains unknown; those records remain visible to reviewers/admins instead of being attributed to a contributor without evidence. New uploads record exact per-project creation audit entries.

## Deletion and admin list approvals

Contributors can delete their own unpublished records; reviewers and admins can delete unpublished records across the workspace. Deletion requires a reason and retains the record and audit history internally.

Any record with an approved public version requires a deletion request, including records with unapproved edits. Its public version remains visible until an reviewer or administrator approves removal. Reviewers and admins can approve or reject deletion requests. Pending deletion records cannot be edited or consolidated. Rejection restores the previous workflow status.

Reviewers and admins can approve individual publications or deletion requests directly in the list, or select multiple eligible records in the current filtered list. Bulk actions process each record independently and reports failures without undoing successful approvals. Conflicting publications require individual moderation; outdated selections are rejected.


## Direct moderator actions and ownership filters

Technical reviewers and admins can create records and directly approve drafts, returned records or published revisions without contributor submission. The original creator email remains unchanged when a moderator edits, publishes, rejects or deletes another person's record. Contributor access is scoped to that email, including contributors in the same organization.

Every private record has a selection checkbox. Selection is available to contributors and moderators, including conflicts and consolidated records. Selecting a record does not bypass conflict moderation or archived-record protection: unsupported actions report a per-record error. Bulk Approve, Reject and Delete act on selected records in the current filtered list with one common message, required for rejection and deletion. Reject returns a record for correction or rejects a pending deletion; approved public snapshots remain unchanged. Delete initiates deletion requests for records with a public snapshot; those requests are approved using Approve. Each action retains audit/history and checks for stale changes.

Admin and technical views can filter by creator name with email shown to distinguish namesakes. Moderator-created records are included in the same filter.


## Excel field validation issues

Invalid workbook cells are retained in a separate description field labelled "Issues while importing from excel", with one `Field label: original Excel cell value` entry per problematic field. The importer creates editable drafts with safe temporary values for invalid fields instead of rejecting the entire workbook. Existing descriptions and notes remain separate. Correct the affected fields and clear the issue description before publishing or approving moderated corrections. Blank template rows are skipped.


## Admin pages and user management

Administration uses separate guarded pages: `/administrator` for policies, `/administrator/records` for Manage Records, `/administrator/users` for Users, and `/administrator/audit` for System Audit Log. Each table appears on its own page. Deep links and refreshes are supported by FastAPI.

Users can be created, modified and deleted from the Users page. Profile fields, role, organization, country and an optional password can be changed; email remains immutable to preserve ownership. Deleting a user disables access and revokes sessions while retaining the identity for project ownership and audit history. Accounts can be restored using Modify and Active account. Role changes and password resets revoke existing sessions. Administrators cannot delete, deactivate or demote their own account. Audit events record user administration changes without passwords.


## Public overview and Screen Options

The public overview and project details show business fields only. Workflow/review status, ownership, organization metadata, reviewer comments, data confidence, timestamps and Excel import issues are excluded from public API responses and cannot be exposed using column settings.

Admins can configure Screen Options exclusively on the Screen Options page at `/administrator/screen-options`. Hidden from public removes a business field from public API data, tables, project details, filters, charts and CSV exports. Show in table controls that field's table column across workspaces; a public field not shown in the table still appears in project details. The two options are independent. Public CSV uses the visible table columns only. Private records preserve full data and ownership. Changes are saved in SQLite, audited and applied when a page reloads or is revisited.


## Selection and action update

Contributor selection is enabled, with Select all, Submit selected for review and Delete selected. Ownership remains enforced by the backend. Only drafts/returned records can be submitted; published records use deletion requests. Admin/technical bulk actions use an in-app confirmation dialog, with a shared message and per-record results. Rejection/deletion require a message at confirmation, rather than disabling the initial action button. Screen Options is available only at `/administrator/screen-options`, via the Screen Options navigation tab.

