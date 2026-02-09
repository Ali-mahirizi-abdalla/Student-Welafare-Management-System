# Render Deployment Guide

This guide details how to deploy your Student Welfare Management System (SWMS) to [Render](https://render.com/).

## Prerequisites

1.  GitHub Repository with your project code.
2.  Render Account (Login via GitHub recommended).

## Automatic Deployment Steps

1.  **Login to Render**: Go to [dashboard.render.com](https://dashboard.render.com/).
2.  **New Web Service**: Click **New +** > **Web Service**.
3.  **Connect GitHub**: Select **Build and deploy from a Git repository** and connect your `Student-Welafare-Management-System` repo.
4.  **Configure Service**:
    *   **Name**: `swms-app` (or similar)
    *   **Region**: Frankfurt (or closest to you)
    *   **Branch**: `main`
    *   **Runtime**: `Python 3`
    *   **Build Command**: `./build.sh`
    *   **Start Command**: `gunicorn swms.wsgi:application`
    *   **Instance Type**: `Free`
5.  **Environment Variables**:
    *   Scroll down to **Environment Variables** and add:
        *   `PYTHON_VERSION`: `3.11.0` (or your local version)
        *   `SECRET_KEY`: (Generate a secure random string)
        *   `DEBUG`: `False`
        *   `DATABASE_URL`: (See Database Section below)
        *   `RENDER_EXTERNAL_HOSTNAME`: (Render creates this automatically, but good to know)
        *   `DISABLE_COLLECTSTATIC`: `0`

## Database Setup (Free PostgreSQL on Neon or Render)

### Option A: Render PostgreSQL (Free Trial / Paid)
1.  Click **New +** > **PostgreSQL**.
2.  Name it `swms-db`.
3.  Copy the **Internal Database URL** once created.
4.  Go back to your Web Service > **Environment Variables**.
5.  Add `DATABASE_URL` and paste the value.

### Option B: Neon (Recommended for Free Tier)
1.  Go to [neon.tech](https://neon.tech) and sign up.
2.  Create a project.
3.  Copy the **Connection String** (Postgres URL).
4.  In Render Web Service > **Environment Variables**, add `DATABASE_URL` with this value.

## Post-Deployment

1.  **Create Superuser**:
    *   Render > Dashboard > Shell.
    *   Run: `python manage.py createsuperuser`

## Troubleshooting

-   **Build Failed**: Ensure `build.sh` has `+x` permission (I have handled this in git).
-   **Database Error**: Check `DATABASE_URL` variable.
