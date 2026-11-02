# Performance Report

**Run date:** 2026-11-02

## Method

Measurements used Django's test client against an isolated SQLite test
database, seeded with 1,000 bots, 500 message templates, 2,000 activity rows,
and one preference. No Telegram requests were made. Query counts were captured
with Django's `CaptureQueriesContext`; page render times use `perf_counter`.

The baseline used one warm-up request and 10 samples per page. The final run
used five warm-up requests and 30 samples per page. Because warm-up/sample
counts differ and host load varies, render times are indicative rather than a
controlled benchmark. Query counts and rendered-row limits are the more
reproducible measurements.

## Before and after

| Route | Baseline queries | Final queries | Baseline median | Final median |
|---|---:|---:|---:|---:|
| Dashboard | 7 | 6 | 13.59 ms | 3.74 ms |
| Bots | 3 | 2 | 86.26 ms | 94.66 ms |
| Messages | 4 | 3 | 25.85 ms | 29.22 ms |
| Reactions | 3 | 2 | 15.74 ms | 17.47 ms |
| Customization | 3 | 2 | 1.16 ms | 1.34 ms |
| Settings | 3 | 2 | 1.22 ms | 1.40 ms |

Each final route returned HTTP 200. The dashboard median was 72.5% lower in
this sample, and its bot rows materialized fell from 1,000 to 4. However,
medians on several other routes varied in both directions despite lower query
counts. These short local runs do not establish general response-time
improvements; no latency claim is made for those routes.

## Static asset

| Asset | Before | After | Change |
|---|---:|---:|---:|
| `static/images/berrybot.png` | 1,123,856 bytes | 791,348 bytes | 332,508 bytes saved (29.6%) |

The PNG was re-encoded losslessly; decoded pixels were compared before writing
the optimized image and were identical. The banner is referenced by the
README, not loaded by dashboard pages, and was not changed.

## Interpretation and limits

- Fewer SQL round trips are verified by query capture and regression
  assertions.
- The home page no longer loads off-screen bot records.
- Time measurements are from local SQLite and synthetic data; they exclude
  production network, database, and browser behavior.
- Telegram request latency was not benchmarked. The synchronous network path
  remains a reliability and tail-latency risk.
- No before/after browser paint, memory, or JavaScript execution metrics are
  available in this environment.
