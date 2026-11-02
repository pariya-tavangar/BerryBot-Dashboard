# Test Report

**Run date:** 2026-11-02

## Results

| Check | Result |
|---|---|
| Baseline Django tests | 3 passed |
| Final Django tests | 17 passed |
| `python manage.py check` | Passed; no issues |
| `python manage.py makemigrations --check --dry-run` | Passed; no changes detected |
| `python manage.py check --deploy` | Three warnings: HSTS, SSL redirect, and weak default `SECRET_KEY` |
| Frontend JavaScript syntax check | Not run; Node.js is unavailable |

The test suite uses Django's isolated test database. It does not modify the
development database.

## Coverage added

- Successful rendering for dashboard, bot management, messages, reactions,
  customization, and settings.
- Static script URLs on shared and reaction pages.
- Dashboard row limit and SQL query budget.
- Bot-list, message, and reaction query budgets.
- Correct active-bot count.
- Saving and rejecting empty message templates; retaining the full body of
  long templates for the composer.
- Bot creation after mocked Telegram validation.
- Successful mocked message sending, saved-chat persistence, and activity log.
- Malformed Telegram JSON and invalid bot IDs.
- Invalid reaction IDs and successful mocked reactions.
- Profile-image handling for malformed Telegram JSON.
- Settings preference persistence.

## Gaps and limits

- Telegram API calls are mocked; no credentials or live external calls are
  used in tests.
- No browser/JavaScript runtime was available, so interaction tests validate
  rendered data and script references but do not execute the scripts.
- Authentication is not implemented. The current anonymous page-render tests
  reflect the app's local-use behavior; they do not establish safe access
  control for a network deployment.
- Concurrency, multi-worker behavior, production database engines, static-file
  serving, and sustained load are not tested.
- No lint or type-check command is configured in the project.

## Unresolved critical checks before public deployment

Design and implement authentication and authorization boundaries, protect
plaintext bot tokens, and validate HTTPS/cookie behavior with the deployment
topology before exposing the app to untrusted users.
