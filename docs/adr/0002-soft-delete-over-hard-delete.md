# ADR 0002: Use soft delete for core domain entities

- Status: Accepted
- Date: 2026-07-23

## Context

The repository implements soft-delete fields for workspaces, projects, tasks, and comments. These entities include is_deleted, deleted_at, and deleted_by fields and are filtered out from normal reads when deleted.

## Decision

FlowBoard uses soft delete for core domain entities so that historical references and activity trails remain intact even after an entity is removed from normal usage.

## Consequences

- Deleted entities remain present in storage and can be inspected or referenced safely.
- Normal reads and business logic must explicitly filter out soft-deleted rows.
- The data model supports historical continuity for tasks, projects, comments, and workspaces.
