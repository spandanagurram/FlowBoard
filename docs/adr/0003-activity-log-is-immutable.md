# ADR 0003: Treat activity logs as immutable append-only records

- Status: Accepted
- Date: 2026-07-23

## Context

The activity log model is designed as an append-only audit trail. The implementation deliberately prevents update and delete operations on ActivityLog records after creation.

## Decision

FlowBoard stores workspace activity as immutable audit records. Activity logs are created by the application and are not intended to be modified or removed.

## Consequences

- Activity logs provide a stable audit trail for workspace actions.
- The application must treat activity history as read-only data.
- This supports traceability for actions such as workspace changes, invitations, project and task lifecycle events, and comments.
