# ADR 0001: Use Workspace membership roles as the canonical authorization model

- Status: Accepted
- Date: 2026-07-23

## Context

The repository implements authorization checks in service-layer methods by resolving the requester’s active membership in a Workspace and then applying role-based rules. The same role model is used across workspaces, projects, tasks, comments, invitations, and activity visibility.

## Decision

FlowBoard uses Workspace membership roles as the canonical authorization model. Resource-specific policies are expressed in terms of the user’s Workspace role rather than introducing resource-specific roles or separate permission systems.

## Consequences

- Authorization logic is centralized around Workspace membership and role.
- Resource-specific behavior remains explicit in each service module, but it is always interpreted through the Workspace role model.
- New features should follow the same pattern: resolve active membership, resolve role, and then apply the resource-specific policy.
