# FlowBoard Deployment Guide

This guide describes the current production deployment approach for FlowBoard based on the repository implementation and the existing CI/CD workflow.

## Overview

FlowBoard uses a split deployment model. The React frontend is served separately from the Django API, while the backend runs as a containerized service on Google Cloud Run. PostgreSQL is hosted on Neon, Redis is provided by Upstash, and transactional invitation emails are sent through Gmail SMTP. The current deployment workflow builds the backend Docker image from the repository, pushes it to Google Artifact Registry, and deploys it to Cloud Run through GitHub Actions.

## Deployment Architecture

The production architecture is organized as follows:

- The frontend is a Vite + React application and is deployed separately on Vercel.
- The backend is a Django + Django REST Framework application packaged as a Docker image and deployed to Google Cloud Run.
- Neon hosts the production PostgreSQL database for Django models and application data.
- Upstash provides Redis for cache and Celery broker support.
- Cloud Run communicates with Neon and Upstash over the network connections configured through environment variables.
- GitHub pushes to the main branch trigger the backend deployment workflow, which builds and publishes a new container image and deploys the updated service to Cloud Run.

## Prerequisites

Before deploying or updating FlowBoard, the following services and access points should be in place:

- A Google Cloud project with billing enabled.
- A Google Artifact Registry repository for container images.
- A Cloud Run service for the backend application.
- Cloud Build or the current GitHub Actions-based deployment path enabled for the target project.
- Docker installed locally for building and testing images.
- A Vercel account and a connected GitHub repository for the frontend deployment.
- A Neon PostgreSQL database instance and connection details.
- An Upstash Redis instance and connection details.
- A Gmail account with an App Password configured for SMTP delivery.
- The required Google Cloud APIs enabled for Artifact Registry, Cloud Run, and Cloud Build-related deployment operations.

## Backend Deployment

The backend deployment path is defined in the repository workflow at [.github/workflows/backend-deploy.yml](../.github/workflows/backend-deploy.yml). The workflow performs the following steps:

1. Checks out the repository.
2. Authenticates to Google Cloud using a service account JSON credential.
3. Configures Docker for the target Artifact Registry region.
4. Builds the Docker image from [backend/Dockerfile](../backend/Dockerfile) using the backend source tree.
5. Pushes the image to Artifact Registry.
6. Deploys the image to the Cloud Run service named `flowboard-backend` in the configured region.

The container entry point starts Gunicorn with the Django WSGI application and binds to the Cloud Run-provided `PORT` environment variable. Environment variables for the service must be set explicitly in Cloud Run so the application can connect to PostgreSQL, Redis, SMTP, and the frontend URL.

## Database Deployment

FlowBoard uses Neon PostgreSQL as the production database. The backend configures the database through the Django settings using the environment variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.

The connection string is not assembled by a separate database URL helper in the current codebase; Django uses the individual settings values directly. In production, the database host should be configured with SSL enabled as required by Neon, and the application should be restarted after deployment so that the new environment values take effect.

After a deployment that changes models or schema, run Django migrations before validating the application. The expected operational step is:

- `python manage.py migrate`

## Redis Deployment

Redis is used for both caching and background-task messaging. The backend configuration reads the Redis connection from `REDIS_URL` and uses it for Django cache and Celery broker/result backend settings.

The current production approach does not run a dedicated Celery worker. Instead, the application uses the `USE_CELERY` setting to switch invitation email delivery between asynchronous Celery execution and synchronous execution. In production, `USE_CELERY` is set to `False`, so background tasks are executed inline rather than through a separate worker process.

## Environment Variables

The backend reads its runtime configuration from environment variables through `decouple`. The following variables are currently used by the application and should be configured for production.

### Django

- `SECRET_KEY`: Django secret key for signing and session security.
- `DEBUG`: Enables Django debug mode; this should remain `False` in production.
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames for the backend.
- `USE_CELERY`: Controls whether invitation emails run through Celery. Set to `True` locally and `False` in production Cloud Run. If a dedicated worker is deployed later, this should be set to `True` again.

### Database

- `DB_NAME`: PostgreSQL database name.
- `DB_USER`: PostgreSQL user name.
- `DB_PASSWORD`: PostgreSQL password.
- `DB_HOST`: Neon host address.
- `DB_PORT`: PostgreSQL port; typically `5432`.

### JWT

No additional JWT-specific environment variables are currently defined in the backend settings. The project uses Django REST Framework Simple JWT with the default token lifetimes configured in the code.

### Email

- `EMAIL_BACKEND`: SMTP backend class for Django email delivery.
- `EMAIL_HOST`: SMTP host, currently configured for Gmail.
- `EMAIL_PORT`: SMTP port, typically `587`.
- `EMAIL_USE_TLS`: Enables TLS for SMTP communication.
- `EMAIL_HOST_USER`: SMTP username.
- `EMAIL_HOST_PASSWORD`: SMTP password or app password.
- `DEFAULT_FROM_EMAIL`: Sender address used for outgoing mail.
- `FRONTEND_URL`: Frontend base URL used in invitation links.
- `BACKEND_URL`: Backend base URL used by the application.
- `GOOGLE_OAUTH_CLIENT_ID`: Google OAuth client identifier used by the login flow.

### Redis

- `REDIS_URL`: Primary Redis connection string used by Django cache and Celery configuration.
- `REDIS_HOST`: Redis host value used by the local environment example.
- `REDIS_PORT`: Redis port value used by the local environment example.
- `REDIS_DB`: Redis database number used by the local environment example.

### Celery

No separate Celery environment variables are required in the current implementation. The application derives both the broker and result backend from `REDIS_URL` in the Django settings.

## Frontend Deployment

The frontend is built with Vite and deployed to Vercel. The React application expects the backend API base URL through the `VITE_API_BASE_URL` environment variable, which is read by the HTTP client in [frontend/src/api/axios.js](../frontend/src/api/axios.js). The frontend also uses `VITE_GOOGLE_CLIENT_ID` for the Google authentication integration.

The production build command is:

- `npm run build`

The resulting static assets are then served by Vercel. The production environment variables for the frontend should match the deployed backend URL and Google OAuth configuration.

## Post-Deployment Verification

After deployment, verify the following:

- The backend responds successfully on the Cloud Run URL.
- Authentication endpoints work for login and registration.
- A new workspace can be created successfully.
- Invitation creation completes and the invitation email is sent.
- The frontend loads correctly and can reach the backend API.
- PostgreSQL connectivity is working and Django can read and write data.

## Monitoring & Logs

Operational visibility should be gathered from the following sources:

- Cloud Run logs for backend request failures, startup issues, and runtime exceptions.
- Cloud Build or GitHub Actions logs for failed image builds and deployment steps.
- Django application logs for authentication, permission, and database errors.
- SMTP delivery failures should be investigated immediately when invitation emails stop arriving.
- Redis connection failures should be checked when background task execution or cache access fails.

## Rollback Strategy

If a deployment introduces issues, roll back in the following order:

1. Revert the Cloud Run service to a previous successful revision in the Google Cloud console or with the Google Cloud CLI.
2. Restore the previous frontend deployment in Vercel if the frontend release introduced regressions.
3. Review any database migrations that were introduced in the failing deployment and confirm whether they need to be reversed or handled carefully before re-running the service.

## Troubleshooting

Common issues observed during this project include:

- Cloud Run deployment failures caused by missing image build or push steps.
- Missing or incorrect environment variables in Cloud Run.
- Redis SSL configuration issues when using Upstash connections.
- Celery worker not running when asynchronous execution is expected.
- SMTP authentication failures caused by incorrect Gmail app passwords or credentials.
- Neon connection errors caused by invalid host, port, or database credentials.
- Docker build failures caused by dependency or image issues.
- CORS issues when the frontend URL does not match the backend’s trusted origins.

## References

For broader context, refer to the related project documents:

- [docs/ARCHITECTURE.md](ARCHITECTURE.md) for the implementation architecture and component boundaries.
- [docs/API_REFERENCE.md](API_REFERENCE.md) for the backend API surface and endpoint conventions.
- [docs/authorization.md](authorization.md) for the current workspace-role authorization model.
- [docs/domains.md](domains.md) for domain boundaries and current workflow constraints.
- [docs/setup.md](setup.md) for local development and environment preparation guidance.
