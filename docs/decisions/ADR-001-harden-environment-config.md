# ADR-001: Harden environment defaults and document local configuration

## Status
Accepted

## Context
The application stored project configuration directly in `settings.py` with permissive defaults and no sample environment file. This makes local setup harder to reason about and leaves non-debug deployments exposed to weak security defaults.

## Decision
We standardised the local configuration approach using `.env.example` and introduced safer Django defaults for non-debug environments, including explicit cookie and referrer policy settings.

## Alternatives Considered
- Leave the default insecure settings in place.
- Require a fully custom deployment config without providing a starter template.

## Consequences

### Advantages
- Easier onboarding for new developers.
- Clear separation between local and deployment settings.
- Improved protection for cookies and browser security behavior.

### Disadvantages
- The project still depends on a single local SQLite database and should eventually move to a stronger secret-management model.
- Additional environment variables must be explicitly configured before production use.

## Implementation
Affected files:

- `strawberry/settings.py`
- `.env.example`
- `README.md`
