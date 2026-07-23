# FlowBoard Architecture

This document describes the current implementation architecture of FlowBoard as reflected in the repository.

## Scope

FlowBoard is a Django-based backend application with a Vite-based frontend. The backend exposes a JSON API for workspace, project, task, comment, activity, authentication, and dashboard operations.

## High-level structure

- Backend: Django REST Framework application in [backend](../backend)
- Frontend: Vite + React application in [frontend](../frontend)
- Infrastructure: PostgreSQL and Redis via [docker-compose.yml](../docker-compose.yml)

## Backend architecture

### Application layout

The backend is organized as Django apps under [backend/apps](../backend/apps):

- accounts: authentication, registration, password reset, Google login, and profile access
- workspaces: workspace lifecycle, memberships, invitations, and invitation email delivery
- projects: project lifecycle and project-level access control
- tasks: task lifecycle, numbering, hierarchy, assignment, and status transitions
- comments: task comments with soft-delete semantics
- activities: immutable activity log entries for workspace events
- dashboard: aggregate summary counts for the signed-in user
- common: shared base models, cache helpers, and email helpers

### Request flow

1. A client sends an HTTP request to a Django URL route defined in the backend URL configuration.
2. The request is handled by a DRF GenericAPIView in the relevant app.
3. The view delegates business logic to a service class in that app.
4. The service performs repository access, validation, permission checks, and side effects.
5. The service may create immutable activity records and trigger background tasks.
6. The view serializes the result and returns a JSON response.

## Data model foundations

### Shared model conventions

All domain models inherit from [backend/apps/common/models.py](../backend/apps/common/models.py), which provides:

- UUID primary keys
- created_at timestamp
- updated_at timestamp

### Soft delete pattern

Several domain entities use a soft-delete pattern rather than hard deletion:

- Workspace
- Project
- Task
- Comment

These models carry fields such as is_deleted, deleted_at, and deleted_by. This allows historical references to remain intact while the entity is hidden from normal reads.

## Domain modules

### Accounts

The accounts module is responsible for authentication and user identity. It exposes endpoints for:

- registration
- login
- password reset
- Google-based login
- profile retrieval
- logout

The implementation uses Django’s custom user model and JWT authentication via REST framework simple JWT.

### Workspaces

The workspaces module owns workspace creation, updates, deletion, membership management, ownership transfer, and invitations.

Key implementation characteristics:

- Workspaces are scoped by an active membership model.
- Workspace ownership is represented by the owner foreign key on Workspace.
- Membership is a separate model, WorkspaceMember, with role-based state.
- Invitations are represented by WorkspaceInvitation and include expiry and status transitions.
- Invitation emails are sent asynchronously by Celery.

### Projects

Projects live within a Workspace and carry project-level constraints such as unique names and unique keys per Workspace.

Projects are created and managed by Owners and Admins, and are soft-deleted rather than permanently removed.

### Tasks

Tasks belong to a Project and support:

- hierarchical subtasks via parent_task
- unique task numbers per project
- assignment to workspace members
- priority and due-date information
- status transitions
- soft deletion

Task numbers are generated in a deterministic per-project pattern using the project key and an incrementing sequence.

### Comments

Comments belong to Tasks and are soft-deleted. They support creation, updating, and deletion by authorized workspace members.

### Activities

ActivityLog is an immutable append-only event store for workspace actions. The model prevents updates and deletes after creation.

### Dashboard

The dashboard summary endpoint aggregates counts of workspaces, projects, and tasks visible to the authenticated user.

## Authentication and authorization

The current authorization model is documented in [docs/authorization.md](authorization.md).

Implementation details:

- Authentication uses JWT via REST framework simple JWT.
- Authorization is evaluated in service layer methods using the requester’s active Workspace membership and role.
- The role model is Workspace-based, not resource-specific.

## Background processing

Background jobs are handled by Celery.

Current repository evidence shows:

- Celery app initialization in [backend/config/celery.py](../backend/config/celery.py)
- Redis-backed broker and result backend in [backend/config/settings.py](../backend/config/settings.py)
- Invitation email delivery task in [backend/apps/workspaces/tasks.py](../backend/apps/workspaces/tasks.py)

## Persistence and infrastructure

The repository uses PostgreSQL as the primary database and Redis as a cache and message broker dependency.

Current implementation evidence:

- PostgreSQL configuration in [backend/config/settings.py](../backend/config/settings.py)
- Redis configuration in [backend/config/settings.py](../backend/config/settings.py)
- Docker service definitions in [docker-compose.yml](../docker-compose.yml)

## Frontend integration

The frontend is a Vite React application that consumes the backend API over HTTP. The repository structure suggests a feature-oriented organization under [frontend/src](../frontend/src), but this document intentionally limits itself to the implementation that is directly evidenced in the backend and repository structure.

## TODOs

- TODO: Document the frontend route structure in more detail once the frontend implementation is fully mapped.
- TODO: Document any additional asynchronous workflows beyond invitation email delivery if they are added to the repository.
