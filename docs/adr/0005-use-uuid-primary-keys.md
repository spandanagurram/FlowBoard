# ADR 0005: Use UUID primary keys for domain entities

- Status: Accepted
- Date: 2026-07-23

## Context

The repository’s base model defines UUID primary keys for all domain entities via a shared abstract model. This pattern is inherited by accounts, workspaces, projects, tasks, comments, and activities.

## Decision

FlowBoard uses UUIDs as the primary key type for domain entities.

## Consequences

- Entity identifiers are globally unique and do not depend on database sequence state.
- APIs and persistence logic use UUID-based references for entity relationships.
- The shared base model provides a consistent identifier strategy across modules.
