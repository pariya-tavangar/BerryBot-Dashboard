# ADR-002: Bound dashboard queries without caching counts

## Status

Accepted

## Context

The shared page context loaded every bot and separately counted bots, even on
the dashboard that displays only four bot rows. Pages that need the full bot
list also issued a count query for rows already loaded. Caching counts would
introduce invalidation and stale-statistics behavior.

## Decision

- The dashboard loads only its four displayed bots and gets total/active counts
  from one database aggregate.
- Pages that already load the full bot list derive total and active counts
  from those in-memory rows.
- Counts are not cached.

## Alternatives considered

- Keep the shared eager queryset and count query on every page.
- Cache counts and invalidate them on each bot change.
- Add pagination and searchable selectors immediately.

## Consequences

### Advantages

- Dashboard bot-row retrieval is bounded independently of total bot count.
- Pages with a full bot list avoid another database query.
- Counts remain current without cache invalidation logic.

### Trade-offs

- Pages that need all bot records still materialize the full list.
- The dashboard performs an aggregate for counts in addition to fetching its
  four displayed rows.
- Pagination remains future work if real usage outgrows the current local
  dashboard.

## Verification

Query-count regression tests and the synthetic-data measurements are recorded
in [BOTTLENECK_ANALYSIS.md](../BOTTLENECK_ANALYSIS.md) and
[PERFORMANCE_REPORT.md](../PERFORMANCE_REPORT.md).
