# FlowBoard API Reference

This document is a baseline implementation reference for the current backend API.

## Base URL

The backend routes are mounted under the following prefixes:

- /api/auth/
- /api/dashboard/
- /api/workspaces/
- /api/invitations/
- /api/projects/
- /api/tasks/
- /api/comments/

## Authentication

The API uses JWT-based authentication.

### Endpoints

#### POST /api/auth/register/

Creates a new user account.

Request body:

- username: string
- email: string
- password: string

Response:

- 201 Created
- Returns a serialized user object

#### POST /api/auth/login/

Authenticates a user and returns JWT tokens.

Request body:

- email: string
- password: string

Response:

- 200 OK
- Returns access, refresh, and user data

#### POST /api/auth/forgot-password/

Requests a password reset email.

Request body:

- email: string

Response:

- 200 OK
- Returns a generic message regardless of whether the account exists

#### POST /api/auth/reset-password/

Completes a password reset flow.

Request body:

- uid: string
- token: string
- password: string

Response:

- 200 OK

#### POST /api/auth/google/

Authenticates a user via Google ID token.

Request body:

- id_token: string

Response:

- 200 OK

#### GET /api/auth/profile/

Returns the current authenticated user profile.

Response:

- 200 OK
- Returns user fields: id, username, email

#### POST /api/auth/token/refresh/

Refreshes an access token using a refresh token.

This endpoint is provided by Django REST Framework Simple JWT.

#### POST /api/auth/logout/

Blacklists a refresh token.

Request body:

- refresh: string

Response:

- 200 OK

## Dashboard

#### GET /api/dashboard/summary/

Returns a summary of counts visible to the authenticated user.

Response body:

- workspace_count: integer
- project_count: integer
- task_count: integer

## Workspaces

#### GET /api/workspaces/

Lists workspaces visible to the authenticated user.

Query parameters:

- search: string
- ordering: string

Response:

- 200 OK
- Returns a paginated list when pagination is enabled

#### POST /api/workspaces/

Creates a new workspace.

Request body:

- name: string
- description: string
- logo: file (optional)

Response:

- 201 Created
- Returns workspace data

#### GET /api/workspaces/<workspace_id>/

Returns a single workspace.

#### PATCH /api/workspaces/<workspace_id>/

Updates workspace name or description.

Request body:

- name: string
- description: string

Response:

- 200 OK

#### DELETE /api/workspaces/<workspace_id>/

Soft-deletes a workspace.

Response:

- 204 No Content

#### PATCH /api/workspaces/<workspace_id>/transfer-ownership/

Transfers workspace ownership to another active workspace member.

Request body:

- user_id: string (UUID)

#### GET /api/workspaces/<workspace_id>/members/

Lists workspace members for a workspace.

Response body:

- current_user_role: string
- members: array

#### PATCH /api/workspaces/<workspace_id>/members/<user_id>/role/

Changes a member role.

Request body:

- role: one of ADMIN, MEMBER, VIEWER

#### DELETE /api/workspaces/<workspace_id>/members/<member_id>/

Removes a member from the workspace.

#### GET /api/workspaces/<workspace_id>/invitations/

Lists pending invitations for a workspace.

Query parameters:

- search: string

#### POST /api/workspaces/<workspace_id>/invitations/

Creates a workspace invitation.

Request body:

- email: string
- role: one of ADMIN, MEMBER, VIEWER

#### GET /api/invitations/<token>/

Returns invitation details for a token.

#### POST /api/invitations/<token>/accept/

Accepts an invitation for the authenticated user.

#### POST /api/invitations/<token>/reject/

Rejects an invitation for the authenticated user.

#### POST /api/invitations/<invitation_id>/revoke/

Revokes a pending invitation.

## Projects

#### GET /api/workspaces/<workspace_id>/projects/

Lists projects for a workspace.

Query parameters:

- search: string
- ordering: string

#### POST /api/workspaces/<workspace_id>/projects/

Creates a project in a workspace.

Request body:

- name: string
- key: string
- description: string

Response:

- 201 Created

#### GET /api/projects/<project_id>/

Returns a project.

#### PATCH /api/projects/<project_id>/

Updates a project.

Request body:

- name: string
- description: string

#### DELETE /api/projects/<project_id>/

Soft-deletes a project.

## Tasks

#### GET /api/projects/<project_id>/tasks/

Lists tasks for a project.

Query parameters:

- search: string
- ordering: string

#### POST /api/projects/<project_id>/tasks/

Creates a task in a project.

Request body:

- parent_task: UUID or null
- title: string
- description: string
- status: string (optional)
- priority: string (optional)
- assignee: UUID or null
- due_date: string (date) or null

#### GET /api/tasks/<task_id>/

Returns a task.

#### PATCH /api/tasks/<task_id>/

Updates a task.

Request body:

- title: string
- description: string
- priority: string
- assignee: UUID or null
- due_date: string (date) or null
- status: string

#### DELETE /api/tasks/<task_id>/

Soft-deletes a task.

## Comments

#### GET /api/tasks/<task_id>/comments/

Lists comments for a task.

Query parameters:

- search: string

#### POST /api/tasks/<task_id>/comments/

Creates a comment on a task.

Request body:

- content: string

#### PATCH /api/comments/<comment_id>/

Updates a comment.

Request body:

- content: string

#### DELETE /api/comments/<comment_id>/

Soft-deletes a comment.

## Activities

#### GET /api/workspaces/<workspace_id>/activities/

Lists activity log entries for a workspace.

Query parameters:

- search: string

## Data shapes

### Workspace

- id: string (UUID)
- name: string
- description: string
- logo: string or null
- owner: string (UUID)
- created_at: string (datetime)
- updated_at: string (datetime)

### Project

- id: string (UUID)
- workspace: string (UUID)
- name: string
- key: string
- description: string
- created_by: string (UUID)
- updated_by: string (UUID)
- created_at: string (datetime)
- updated_at: string (datetime)

### Task

- id: string (UUID)
- project: string (UUID)
- workspace: string (UUID)
- parent_task: string (UUID) or null
- task_number: string
- title: string
- description: string
- status: string
- priority: string
- assignee: string (UUID) or null
- assignee_name: string or null
- due_date: string (date) or null
- completed_at: string (datetime) or null
- created_by: string (UUID)
- updated_by: string (UUID)
- created_at: string (datetime)
- updated_at: string (datetime)

### Comment

- id: string (UUID)
- task: string (UUID)
- content: string
- created_by: string (UUID)
- created_by_name: string
- updated_by: string (UUID)
- edited_at: string (datetime) or null
- created_at: string (datetime)
- updated_at: string (datetime)

### ActivityLog

- id: string (UUID)
- workspace: string (UUID)
- actor: string (UUID) or null
- action: string
- description: string
- entity_type: string
- entity_id: string (UUID) or null
- metadata: object
- created_at: string (datetime)
- updated_at: string (datetime)

## TODOs

- TODO: Add endpoint-level examples once the frontend or API contract tests are expanded.
- TODO: Add response schema details for validation errors once the error format is standardized.
