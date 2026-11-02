# Bottleneck Analysis

## Fixed findings

| Priority | Finding and evidence | Root cause | Fix |
|---|---|---|---|
| Medium | Dashboard loaded every bot while displaying at most four. With 1,000 synthetic bots, it previously materialized all 1,000 rows. | The shared context eagerly loaded the bot queryset for every page. | Dashboard now fetches only four rows and uses a conditional aggregate for counts. |
| Medium | Bot management, messages, and reactions loaded bot rows and then issued a separate total count. Baseline query counts: 3, 4, and 3. | Counts were repeated even when the complete bot list was already needed. | Those pages derive total and active counts from the already-loaded list. Final query counts: 2, 3, and 2. |
| Low | Bot-management Active statistic always equaled the total. | Template rendered `bot_count` twice. | The active count is now computed and rendered separately. |
| Medium | Shared and reaction JavaScript used malformed static paths; reactions also lacked the `static` tag library. | Invalid template tag spacing and missing template-library load. | Fixed static tags and added route/script rendering tests. |
| Medium | Long saved templates were truncated when copied to the composer. | JavaScript read the truncated preview paragraph. | The button carries the complete escaped template body in a data attribute. |
| Low | The selected default reaction and submitted hidden value disagreed. | The first displayed emoji differed from the hard-coded form value. | Both now default to the same emoji. |
| Medium | Malformed Telegram JSON could raise an attribute/key error; a nonnumeric posted bot ID could raise a server error. | Response shape and identifier were assumed valid. | Validate response dictionaries and return 404 for invalid bot IDs. Profile-image parsing also validates response shapes. |
| Low | Settings and customization GET requests read the singleton preference twice. | Each view fetched it before calling the shared context builder. | The redundant GET read was removed. |
| Low | The shared dashboard icon was 1,123,856 bytes at 1254x1254 pixels. | The original PNG was not optimized. | Lossless PNG optimization reduced it to 791,348 bytes with pixel equality verified. |

## Remaining bottlenecks and reliability risks

1. **Synchronous external requests (Medium).** Telegram validation and profile
   photo retrieval occur in the request thread. The code uses sequential
   timeouts (12 seconds for bot validation; 15/15/15/30 seconds for the
   profile-image API/download requests). These are per-request timeouts, not a
   guaranteed total request deadline. A background task/worker would require
   deployment infrastructure and is not introduced here.
2. **Unpaginated lists (Medium at larger scale).** The bot-management page and
   bot selectors require full bot lists. The dashboard is bounded, but
   messages/templates and management views are not paginated.
3. **Public dashboard and plaintext credentials (High if network-exposed).**
   No login/ownership checks protect dashboard actions, and Telegram tokens
   are stored in plaintext. The app is currently documented as local-use.

## Query-count measurements

An isolated SQLite test database was seeded with 1,000 bots, 500 templates,
2,000 activity rows, and one preference row. Counts are per rendered request.

| Route | Before | After |
|---|---:|---:|
| Dashboard | 7 | 6 |
| Bots | 3 | 2 |
| Messages | 4 | 3 |
| Reactions | 3 | 2 |
| Customization | 3 | 2 |
| Settings | 3 | 2 |

The dashboard still needs a bot count and active-bot count, so it retains a
single aggregate query. The full list pages do not issue a separate count
query after loading their rows.

See [PERFORMANCE_REPORT.md](./PERFORMANCE_REPORT.md) for render-time and asset
measurements, including their limitations.
