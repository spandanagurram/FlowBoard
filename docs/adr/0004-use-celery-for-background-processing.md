# ADR 0004: Use Celery for background processing

- Status: Accepted
- Date: 2026-07-23

## Context

The repository includes asynchronous task execution for non-blocking workflows such as password reset email delivery and workspace invitation email delivery. These tasks are implemented through Celery shared tasks and are wired to Redis-backed broker and result backend configuration.

## Decision

FlowBoard uses Celery for background processing of asynchronous work that should not block the main request path.

## Consequences

- The application can offload time-consuming or side-effecting work from request handling.
- Background jobs depend on a Celery worker and Redis-backed broker configuration.
- Email delivery and other asynchronous operations are implemented as shared tasks rather than inline request processing.
