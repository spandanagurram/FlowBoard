# FlowBoard Glossary

This glossary captures the core terms used in the current implementation.

## Workspace
A workspace is the top-level collaboration container for projects, tasks, members, invitations, and activities.

## Workspace role
A workspace role is the canonical authorization concept in FlowBoard. The current roles are Owner, Admin, Member, and Viewer.

## Workspace member
A workspace member is a user with an active membership in a workspace. Membership records carry the user, workspace, role, invitation source, join time, and active state.

## Workspace invitation
A workspace invitation is a time-limited offer to join a workspace with a specified role. Invitations can be pending, accepted, rejected, revoked, or expired.

## Project
A project is a container within a workspace for tasks. Projects have a name, a short key, and optional description.

## Task
A task is a work item owned by a project. Tasks support assignment, priority, due dates, status, and optional subtasks.

## Subtask
A subtask is a task whose parent_task points to another task within the same project.

## Comment
A comment is a task-level discussion entry created by a workspace member.

## Activity log
An activity log is an immutable record of workspace events such as creation, updates, invitations, role changes, and deletions.

## Soft delete
Soft delete is the repository pattern used for workspaces, projects, tasks, and comments. Deleted records remain in storage but are excluded from normal reads through the is_deleted flag.

## Task number
A task number is a project-scoped identifier generated from the project key and an incrementing sequence.

## Project key
A project key is a short uppercase identifier used in task numbering and project identification.

## TODO
- TODO: Expand this glossary as additional domain terms are introduced in the codebase.
