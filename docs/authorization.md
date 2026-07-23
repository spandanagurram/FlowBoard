# FlowBoard Authorization Model

This document defines the canonical authorization model for FlowBoard.

## Canonical rule

Workspace membership roles are the single source of authorization throughout FlowBoard.

Every resource-specific permission policy is expressed in terms of the requester’s Workspace role:

- Owner
- Admin
- Member
- Viewer

A user must also be an active member of the target Workspace before they can perform workspace-scoped actions. Roles do not create separate resource-specific permission systems.

## Role definitions

- Owner: full control over the Workspace and its child resources, subject to the resource-specific rules below.
- Admin: high-control access for day-to-day management, but not full ownership.
- Member: standard collaborator access with limited editing rights.
- Viewer: read-only access to workspace content.

## Common access rules

These rules apply across the product unless a specific resource section states otherwise:

- Any active Workspace member can read Workspace, Project, Task, Comment, and Activity content for that Workspace.
- Only Owners and Admins may create or manage Projects.
- Only Owners and Admins may create tasks.
- Viewers cannot create or edit content.
- Members may only perform a narrow set of task updates.

## Workspace and membership permissions

| Action | Owner | Admin | Member | Viewer |
| --- | --- | --- | --- | --- |
| View Workspace details and members | Yes | Yes | Yes | Yes |
| Update Workspace name/description | Yes | No | No | No |
| Delete Workspace | Yes | No | No | No |
| Transfer Workspace ownership | Yes | No | No | No |
| Change member roles | Yes | Limited | No | No |
| Remove members | Yes | Limited | No | No |
| Invite users to the Workspace | Yes | Yes | No | No |
| View pending invitations | Yes | Yes | No | No |
| Revoke invitations | Yes | Limited | No | No |

### Notes on membership management

- Owners can manage all non-owner members.
- Admins can change Member and Viewer roles, but cannot assign the Admin role or modify other Admins.
- Admins can remove Members and Viewers, but cannot remove Owners.
- Owners can revoke any pending invitation. Admins can revoke only invitations they sent.

## Project permissions

| Action | Owner | Admin | Member | Viewer |
| --- | --- | --- | --- | --- |
| View Projects | Yes | Yes | Yes | Yes |
| Create Project | Yes | Yes | No | No |
| Update Project | Yes | Yes | No | No |
| Delete Project | Yes | No | No | No |

## Task permissions

| Action | Owner | Admin | Member | Viewer |
| --- | --- | --- | --- | --- |
| View Tasks | Yes | Yes | Yes | Yes |
| Create Task | Yes | Yes | No | No |
| Update task metadata and assignment | Yes | Yes | No | No |
| Update task status | Yes | Yes | Yes, if assigned to the task and only through the allowed transition path | No |
| Delete Task | Yes | No | No | No |

### Task update policy

Members are intentionally restricted to status changes only. They cannot rename tasks, reassign tasks, change priority, or edit due dates.

## Comment permissions

| Action | Owner | Admin | Member | Viewer |
| --- | --- | --- | --- | --- |
| View Comments | Yes | Yes | Yes | Yes |
| Create Comment | Yes | Yes | Yes | No |
| Edit own Comment | Yes | Yes | Yes | No |
| Delete own Comment | Yes | Yes | Yes | No |
| Delete another user’s Comment | Yes | Yes | No | No |

## Invitation permissions

| Action | Owner | Admin | Member | Viewer |
| --- | --- | --- | --- | --- |
| View pending invitations | Yes | Yes | No | No |
| Create invitation | Yes | Yes | No | No |
| Revoke invitation | Yes | Limited | No | No |
| Accept invitation | Yes, for the invited recipient | Yes, for the invited recipient | Yes, for the invited recipient | Yes, for the invited recipient |
| Reject invitation | Yes, for the invited recipient | Yes, for the invited recipient | Yes, for the invited recipient | Yes, for the invited recipient |

### Invitation workflow note

Invitation acceptance and rejection are tied to the invited email identity rather than to a Workspace role. This is a workflow exception, not a second authorization system.

## Activity permissions

| Action | Owner | Admin | Member | Viewer |
| --- | --- | --- | --- | --- |
| View Activity log | Yes | Yes | Yes | Yes |
| Create Activity log | System-generated only | System-generated only | System-generated only | System-generated only |

## Implementation guidance

When adding new capabilities, the rule of thumb should be:

1. Determine whether the requester is an active member of the Workspace.
2. Resolve the requester’s Workspace role.
3. Apply the resource-specific policy using that role.

No action should introduce a separate permission layer that is not reducible to Workspace role plus active membership.
