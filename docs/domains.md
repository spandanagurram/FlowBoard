# FlowBoard Domain Boundaries

This document maps the domain responsibilities currently implemented by FlowBoard. It is intentionally separate from the system architecture and glossary described in [CONTEXT-MAP.md](../CONTEXT-MAP.md).

## Workspace participation

The Workspaces module owns Workspace lifecycle, Membership, roles, ownership transfer, and Invitations. Other modules inherit Workspace authorization rather than defining their own participation model.

### Invitation lifecycle

An Invitation is a time-limited offer to join a Workspace with a role. Its states are Pending, Accepted, Rejected, Revoked, and Expired.

Expiration is currently a **lazy state transition**. The system marks a pending Invitation as expired when it is retrieved, accepted or rejected, included in an invitation listing, or superseded while creating another Invitation for the same Workspace and email address. Celery delivers invitation email but does not currently run a scheduled expiry job.

Time-based background expiry is a future enhancement, not part of the current architecture.
