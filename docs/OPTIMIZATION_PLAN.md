# Optimization Plan

## Completed

| Priority | Work | Status |
|---|---|---|
| Medium | Bound dashboard bot retrieval to the four displayed rows and consolidate dashboard counts. | Done |
| Medium | Derive bot-list counts from rows already loaded for management and selectors. | Done |
| Medium | Fix broken JavaScript static references and template-selection truncation. | Done |
| Medium | Guard malformed Telegram response shapes and invalid posted bot identifiers. | Done |
| Low | Correct the active-bot metric and default reaction value. | Done |
| Low | Remove duplicate preference reads and optimize the shared icon losslessly. | Done |
| Low | Add regression tests and query-count budgets for the affected routes. | Done |

## Prioritized remaining work

| Priority | Work | Status / reason |
|---|---|---|
| Critical before public exposure | Add authentication and authorization for every dashboard action, with account ownership rules. | Pending product/deployment decision; current app is explicitly local-use and has a single global preference record. |
| High before production | Protect bot tokens at rest and restrict access to the database and backups. | Pending secret-storage and key-management design. |
| High before production | Replace the predictable fallback `SECRET_KEY` and configure HTTPS redirect/HSTS in Django or the trusted reverse proxy. | `check --deploy` reports W004, W008, and W009; HSTS depends on confirmed HTTPS deployment. |
| Medium | Move Telegram validation/profile retrieval and other slow external actions out of request workers. | Pending task-queue/worker infrastructure decision. |
| Medium when data grows | Paginate bot/template/activity lists or provide searchable bot selectors. | Not justified by current small local-use footprint. |
| Low | Add browser-based interaction, accessibility, and responsive-layout tests. | No browser automation or JavaScript runtime was available for this audit. |
| Low | Add production-database and concurrency coverage. | Current project is SQLite-based and has no configured CI/test matrix. |

Do not treat the synthetic local SQLite timings as a capacity forecast. Re-run
with representative data and deployment infrastructure before making scaling
decisions.
