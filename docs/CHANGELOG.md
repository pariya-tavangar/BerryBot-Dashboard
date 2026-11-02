# Changelog

## Unreleased

### Fixed

- Limited dashboard bot retrieval to the four rows displayed and removed
  duplicate bot-count queries on pages that already load the bot list.
- Corrected the active-bot statistic on the bot-management page.
- Fixed static JavaScript references and enabled the reactions page's static
  template tag.
- Preserved full message-template bodies when copying them into the composer.
- Matched the selected reaction emoji to the form's initial submitted value.
- Returned controlled errors for malformed Telegram response JSON and
  nonnumeric bot IDs.
- Removed duplicate preference reads on settings and customization pages.

### Added

- Added regression tests for page rendering, query budgets, Telegram workflows,
  malformed responses, and template/reaction behavior.
- Added test, bottleneck, optimization, and performance reports in `docs/`.

### Improved

- Losslessly optimized the dashboard icon from 1,123,856 to 791,348 bytes.

### Notes

- Environment hardening and the local environment template were already
  present in the working tree before this audit; see ADR-001.
- Authentication, per-user authorization, and token encryption remain
  unresolved deployment risks.
- `python manage.py check --deploy` reports missing HSTS/SSL redirect settings
  and a weak fallback secret; configure these for the actual HTTPS deployment.
- See [PERFORMANCE_REPORT.md](./PERFORMANCE_REPORT.md) for measurement
  conditions and limitations.
