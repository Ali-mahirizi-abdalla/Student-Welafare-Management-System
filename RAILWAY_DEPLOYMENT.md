# Railway Deployment Guide

This guide details how to deploy your Student Welfare Management System (SWMS) to [Railway](https://railway.app/).

## Prerequisites

1.  GitHub Repository with your project code.
2.  Railway Account (Login via GitHub recommended).

## Automatic Deployment Steps

1.  **Login to Railway**: Go to [railway.app](https://railway.app/) and log in.
2.  **New Project**: Click **+ New Project** > **Deploy from GitHub repo**.
3.  **Select Repository**: Choose `Student-Welafare-Management-System`.
4.  **Add Database**:
    *   Right-click on the project canvas (or click **+ New**).
    *   Select **Database** > **PostgreSQL**.
    *   This will automatically create a `DATABASE_URL` environment variable that your app will use.
5.  **Configure Environment Variables**:
    *   Click on your Django application service card.
    *   Go to the **Variables** tab.
    *   Add the following variables:
        *   `SECRET_KEY`: (Generate a secure random string)
        *   `DEBUG`: `False`
        *   `ALLOWED_HOSTS`: `*` (or your specific railway domain)
        *   `CSRF_TRUSTED_ORIGINS`: `https://your-project-url.railway.app`
        *   `DISABLE_COLLECTSTATIC`: `0` (Railway runs collectstatic automatically if detected, but ensuring it runs is good)
        *   *Optional (if using AWS/Cloudinary)*: Add your `AWS_...` or `CLOUDINARY_...` keys.
6.  **Build & Deploy**:
    *   Railway usually detects the `Procfile` and builds using the Python buildpack.
    *   Watch the **Deployments** logs for progress.

## Post-Deployment

1.  **Create Superuser**:
    *   Go to your service in Railway.
    *   Click **Shell** (or predefined command in settings).
    *   Run: `python manage.py createsuperuser`
2.  **Run Migrations**:
    *   Railway usually runs the build command. If migrations didn't run, execute: `python manage.py migrate` in the Shell.

## Troubleshooting

-   **Build Failed**: Check the build logs. Ensure `requirements.txt` is in the root.
-   **Application Error**: Check the Deploy logs.
    -   *Database errors*: Ensure the PostgreSQL service is attached to your Django service (Variables should show `DATABASE_URL`).
    -   *Static files*: Ensure `whitenoise` is configured (it is).
