# Project Audit

## Summary

The project is a small Django dashboard for managing Telegram bots, messages,
and reactions. The codebase passes Django's system checks and migration drift
check. The current regression suite contains 17 tests; it exercises rendered
pages and important local workflows but does not contact Telegram.

The review found 10 actionable application defects or performance issues. All
10 were fixed in this pass. Authentication and plaintext token storage remain
application-level blockers for untrusted network exposure. Django's
deployment check also reports three configuration warnings.

## Findings

### Fixed

1. **Medium — Dashboard loaded every bot while showing only four.** The home
   page now fetches only its four displayed bot rows. Conditional aggregates
   provide the dashboard totals in one query.
2. **Medium — Bot-list pages queried counts after loading the same rows.**
   Bot management, messaging, and reactions now derive counts from the bot
   list they already need.
3. **Low — The bot-management Active metric displayed the total bot count.**
   It now displays the actual active count.
4. **Medium — Shared and reaction JavaScript URLs were malformed.** Fixed
   their static tags and loaded Django's static template tags on the reactions
   page.
5. **Medium — Selecting a long message template copied its truncated preview.**
   The full escaped body is now provided to the composer.
6. **Low — The selected default reaction differed from the submitted value.**
   The initial hidden value now matches the selected emoji.
7. **Medium — Unexpected Telegram JSON shapes and nonnumeric bot IDs could
   produce server errors.** Responses are shape-checked and invalid bot IDs
   return 404 responses.
8. **Low — Profile-image responses with malformed JSON could fail after bot
   creation.** The optional image fetch now rejects malformed response shapes.
9. **Low — Customization and settings GETs read preferences twice.** The
   redundant reads were removed.
10. **Low — The dashboard icon was oversized for its use.** Its PNG was
    losslessly optimized from 1,123,856 to 791,348 bytes.

The two query optimizations are considered one dashboard/list-query finding;
the profile image and preference read improvements are supporting fixes.

## Remaining high-impact risks

- **High, conditional on network exposure — No authentication or per-user
  authorization protects bot management, message sending, reactions, or
  settings.** The UI itself documents that this version is intended for local
  use. Do not expose it to untrusted users without an access-control design.
- **High — Telegram bot tokens are stored in plaintext in the SQLite database.**
  Restrict database access and use a deliberate secret-storage strategy before
  production deployment.
- **High — The current default `SECRET_KEY` is weak and predictable.** Supply
  a unique, long random key through the deployment environment.
- **Deployment configuration — HTTPS redirect and HSTS are not configured in
  Django.** Configure them in Django or at the trusted reverse proxy; enable
  HSTS only after HTTPS is fully established.
- **Medium — Telegram calls run synchronously in web requests.** Bot
  validation and profile-image retrieval can hold a request open across several
  sequential network calls.
- **Medium at larger scale — Bot and message-template lists are unpaginated.**
  Some pages need the full bot list for their selectors; pagination or a
  searchable selector should be considered as real usage grows.

## Verification

- `python manage.py test`: 17 tests passed.
- `python manage.py check`: no issues.
- `python manage.py makemigrations --check --dry-run`: no changes detected.
- `python manage.py check --deploy`: three warnings: `security.W004` (HSTS),
  `security.W008` (SSL redirect), and `security.W009` (weak default secret).
- Detailed test and benchmark conditions are in
  [TEST_REPORT.md](./TEST_REPORT.md) and
  [PERFORMANCE_REPORT.md](./PERFORMANCE_REPORT.md).

## Audit limits

External Telegram behavior was mocked, not exercised against live credentials.
No browser automation or JavaScript runtime was available in the environment.
The benchmark uses a local isolated SQLite test database and synthetic data;
it is not a production-load forecast.
