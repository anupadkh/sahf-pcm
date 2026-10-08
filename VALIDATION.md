# Validation

Validated on 30 September 2026 on Windows with Node 26.5.0 and Python 3.11.

- Angular production build passed (approximately 333 kB initial JavaScript/CSS; approximately 85 kB estimated transfer).
- Backend workflow suite: four tests passed. Covered draft/review/return/publication, published visibility, contributor edit locks, reviewer authorization, organization isolation, country restrictions, logout revocation, negative amounts, invalid date ranges, pillar policy, audit access, atomic spreadsheet imports, monetary-unit conversion and duplicate imports.
- Browser smoke checks: public Angular page renders; selecting Completed updates project count, investment, country count, pillar/hazard counts, map and treemap to zero for the illustrative portfolio. Contributor routing and sign-in load the organization’s three records.
- Mobile-sized browser preview inspected visually.
- Dependency install reported zero npm audit vulnerabilities.

Starlette emitted a non-failing warning that its HTTPX TestClient transport is deprecated. This does not affect the passing workflow tests.

See REPORT_MAPPING.md for Power BI parity limitations. Embedded PBIX data was not extracted or reconciled. Preview records are illustrative. Legacy workbook migration and external deployment were not validated.
