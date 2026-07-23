# FlowBoard

FlowBoard is a collaboration platform where people organise work inside Workspaces. The backend and frontend share this single domain context.

## Work structure

**Workspace**:
The top-level collaboration space that owns its Projects, Memberships, Invitations, and Activity Logs.
_Avoid_: Team, organisation

**Project**:
A named collection of work inside one Workspace, identified within that Workspace by a project key.
_Avoid_: Board, workspace

**Task**:
A unit of work belonging to one Project. A Task can be assigned, prioritised, scheduled, and progressed through its status.
_Avoid_: Ticket, issue, card

**Subtask**:
A Task whose parent is another Task in the same Project. A Subtask cannot itself have Subtasks.
_Avoid_: Child task, nested task

## Participation

**User**:
A person with a FlowBoard account. A User participates in a Workspace only through a Membership.
_Avoid_: Account, workspace user

**Membership**:
An active or inactive association between one User and one Workspace, carrying that User's Workspace role.
_Avoid_: Member, workspace user

**Workspace role**:
The sole permission level held through a Membership: Owner, Admin, Member, or Viewer. Permissions are enforced at the Workspace level and inherited by its Projects and Tasks; there are no Project-level or Task-level overrides.
_Avoid_: Permission, access level

**Invitation**:
A time-limited offer for an email address to join a Workspace with a specified Workspace role. An Invitation may be pending, accepted, rejected, revoked, or expired.
_Avoid_: Invite, membership request

## Task management

**Assignee**:
The active, non-Viewer Workspace member responsible for a Task. A Task may have no Assignee.
_Avoid_: Owner, task owner

**Task status**:
The current work state of a Task: Todo, In Progress, Review, Done, or Reopened.
_Avoid_: Stage, state

**Priority**:
The relative urgency of a Task: Low, Medium, or High.
_Avoid_: Severity, importance

**Due date**:
The calendar date by which a Task is expected to be completed.
_Avoid_: Deadline

## Cross-cutting concerns

**Authentication**:
The process of establishing a User's identity before they access FlowBoard.
_Avoid_: Login, authorization

**Authorization**:
The enforcement of what a User may do through their Membership and Workspace role.
_Avoid_: Authentication, permissions

**Activity Log**:
The implemented Workspace-visible audit history: an ordered record of an event, including its actor, action, affected entity, description, and optional metadata.
_Avoid_: Audit log, history

**Dashboard**:
The user-level summary of accessible Workspaces, Projects, and Tasks.
_Avoid_: Home page, overview

**Comment**:
Text authored by a User on a Task, with edit and deletion history retained.
_Avoid_: Note, reply


