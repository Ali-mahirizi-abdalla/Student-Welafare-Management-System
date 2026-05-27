# Render Deployment Guide - Student Welfare Management System (SWMS)

This guide walks you through deploying your Django-based **Student Welfare Management System** (CampusCare) to **Render**.

Render is a modern cloud platform that is highly compatible with Django. Since your system is already configured with **Whitenoise** (for static files) and **dj-database-url** (for dynamic database configurations), it is extremely easy to host on Render.

---

## Deployment Options

You have two main paths to deploy your database on Render:

1. **Option A: PostgreSQL Managed Database (Highly Recommended)**
   * **Pros:** Secure, scalable, automated backups, no data loss.
   * **Cons:** Requires a database adapter package in `requirements.txt` (which we will add).
2. **Option B: SQLite with Render Persistent Disk (Free & Simple)**
   * **Pros:** Completely free, uses your existing SQLite database (`db.sqlite3`).
   * **Cons:** Requires attaching a persistent disk on Render so your database isn't deleted when the server restarts.

---

## Option A: PostgreSQL Setup (Highly Recommended)

### 1. Add PostgreSQL Adapter to `requirements.txt`
Django needs a library to communicate with PostgreSQL. Open your `requirements.txt` file and add:
```txt
psycopg2-binary==2.9.9
```
*(Or install `psycopg` if you prefer the modern v3 adapter).*

### 2. Create a PostgreSQL Database on Render
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** and select **PostgreSQL**.
3. Fill in the details:
   * **Name:** `swms-db`
   * **Database:** `swms_db`
   * **User:** `swms_user`
   * **Region:** Choose the region closest to your users.
4. Click **Create Database**.
5. Once active, copy the **Internal Database URL** (for Render services) or **External Database URL** (for local testing). It looks like this:
   `postgres://swms_user:password@host:port/swms_db`

---

## Option B: SQLite with Persistent Disk Setup

If you prefer to keep using SQLite without setting up PostgreSQL, you must use a **Persistent Disk** on Render because standard Render disks are ephemeral (rebooting the service wipes all local file changes).

### 1. Update `swms/settings.py` for Persistent Disk
To make sure your SQLite database points to the mounted persistent disk on Render, modify the SQLite settings block in `swms/settings.py` (around line 170):

```python
if os.getenv('USE_SQLITE', 'False') == 'True' and not os.getenv('DATABASE_URL'):
    # Check if we are on Render and have a persistent disk directory
    RENDER_DISK_DIR = os.getenv('RENDER_DISK_DIR', '')
    if RENDER_DISK_DIR:
        db_path = Path(RENDER_DISK_DIR) / 'db.sqlite3'
    else:
        db_path = BASE_DIR / 'db.sqlite3'
        
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path,
        }
    }
```

### 2. Attach a Persistent Disk in Render
When creating your Web Service (detailed below), you will need to add a Disk in the **Advanced** section:
* **Name:** `sqlite-db-disk`
* **Mount Path:** `/data`
* **Size:** `1 GB` (Plenty for SQLite)
* Set the environment variable `RENDER_DISK_DIR=/data` in your Web Service configuration.

---

## Deploying the Web Service on Render

### Step 1: Push your Code to GitHub
Ensure all your local changes (including `requirements.txt` updates) are pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure requirements and deployment settings for Render"
git push origin main
```

### Step 2: Create the Web Service on Render
1. Go to your Render Dashboard, click **New +**, and select **Web Service**.
2. Connect your GitHub account and select your repository: `Student-Welfare-Management-System`.
3. Configure the Web Service settings:
   * **Name:** `campus-care`
   * **Region:** Select the same region as your database.
   * **Branch:** `main` (or whichever branch you deploy from).
   * **Runtime:** `Python`
   * **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   * **Start Command:**
     ```bash
     gunicorn swms.wsgi
     ```

### Step 3: Add Environment Variables
Scroll down to the **Environment Variables** section and add the following keys:

| Key | Value | Notes |
|---|---|---|
| `PYTHON_VERSION` | `3.13.0` | Forces Render to use Python 3.13 |
| `SECRET_KEY` | *[Generate a strong secret key]* | E.g., generate one with `openssl rand -hex 32` |
| `DEBUG` | `False` | Turn off debug mode in production |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Replace with your actual Render URL |
| `DATABASE_URL` | *[Your PostgreSQL Database URL]* | **For Option A** (Render automatically configures this if you link them) |
| `USE_SQLITE` | `True` | **For Option B** (If using SQLite) |
| `RENDER_DISK_DIR` | `/data` | **For Option B** (If using SQLite persistent disk) |

*If you are using Cloudinary for media uploads (highly recommended as standard web services don't store uploaded student files permanently unless uploaded to Cloud), also add:*
* `USE_CLOUDINARY=True`
* `CLOUDINARY_CLOUD_NAME=...`
* `CLOUDINARY_API_KEY=...`
* `CLOUDINARY_API_SECRET=...`

### Step 4: Deploy!
Click **Create Web Service**. Render will now pull your repository, build the environment, run database migrations, collect all CSS/JS static assets using Whitenoise, and spin up your application using Gunicorn!

Once the build is complete, you will see a live URL (e.g., `https://campus-care.onrender.com`). Open it in your browser and you're good to go!

---

## (Optional) Celery Background Workers & Redis

Since your `Procfile` defines a Celery worker (`worker: celery -A swms worker --loglevel=info`) and a beat scheduler (`beat: celery -A swms beat --loglevel=info`), you can also run background tasks on Render:

1. **Redis Cache:** Click **New +** -> **Redis** on Render to spin up a managed Redis instance. Use the connection string as your `REDIS_URL` environment variable.
2. **Celery Worker:** Click **New +** -> **Background Worker**. Connect your repo and set the Start Command to:
   ```bash
   celery -A swms worker --loglevel=info
   ```
