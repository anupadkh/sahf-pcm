# Current Power BI report → Angular dashboard

Source: `pcm (1).pbix`, Report/Layout, Page 1 (nine visual containers).

| Power BI visual | Angular equivalent |
| --- | --- |
| Country dropdown | Country filter |
| Project Status dropdown | Project status filter, distinct from review workflow |
| Implementing Partner dropdown | Implementing partner filter |
| Funding Partner dropdown | Funding partner filter |
| Sector dropdown | Sector filter |
| Count of Project ID card | Project record count |
| Count of Country card | Distinct country coverage |
| Country map, size by non-null Project ID count | Interactive bubbles positioned at country centres, sized by record count |
| Funding Partner treemap, value by non-null Project ID count | Interactive proportional-area partner tiles, sized by record count |

All five filters update cards, map bubbles, partner tiles, pillar matrix, hazard counts, and project table. Selecting a map bubble or partner tile applies the associated filter. The additional EW4All matrix and project table come from the supplied HTML prototypes.

The report layout was extracted directly from the PBIX archive. Its binary DataModel was not extracted; there is no verified data or total reconciliation with Power BI. The map is a geographic bubble plot without geographic boundaries or map tiles. Country coverage uses distinct countries, while the PBIX card is labelled Count of Country; exact measure parity requires the original model definition and data. Angular counts all project records, including records without an external project ID. The Power BI map and treemap use non-null Project ID counts. These choices avoid excluding legitimate records whose optional external ID is blank.

The shipped local database is seeded with three explicitly illustrative HTML prototype projects. Real workbook records enter the contributor/reviewer workflow as drafts and only reach the public report after review. No automatic publication of the workbook portfolio occurs.
