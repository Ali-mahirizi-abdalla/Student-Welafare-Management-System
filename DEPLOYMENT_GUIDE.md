# PythonAnywhere Deployment Guide - CampusCare (SWMS)

This guide will walk you through deploying your Student Welfare Management System to PythonAnywhere.

## Prerequisites

- A PythonAnywhere account (free or paid)
- Your GitHub repository: https://github.com/Ali-mahirizi-abdalla/Student-Welafare-Management-System.git
- Database credentials from PythonAnywhere

---

## Step 1: Create PythonAnywhere Account

1. Go to [PythonAnywhere](https://www.pythonanywhere.com/)
2. Sign up for a free account (or upgrade for custom domains)
3. Note your username (e.g., `yourusername`)

---

## Step 2: Database Setup

> **⚠️ IMPORTANT:**
> - **Free Accounts**: PythonAnywhere Free Tier **does not support MySQL**. You MUST use SQLite. **Skip to Step 3**.
> - **Paid Accounts**: You can use MySQL. Follow the steps below.

### 2.1 Create Database (Paid Accounts Only)
1. Go to **Databases** tab in PythonAnywhere dashboard
2. Set a MySQL password (save this securely!)
3. Create a new database named: `yourusername$swms_db`
4. Note your database hostname: `yourusername.mysql.pythonanywhere-services.com`

### 2.2 Initialize Database Schema (Paid Accounts Only)
1. Open a **Bash console** from the Consoles tab
2. Connect to MySQL:
   ```bash
   mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p
   ```
3. Enter your MySQL password
4. Select your database:
   ```sql
   USE yourusername$swms_db;
   ```
5. You can exit MySQL for now:
   ```sql
   EXIT;
   ```

---

## Step 3: Clone Your Repository

In the Bash console:

```bash
cd ~
git clone https://github.com/Ali-mahirizi-abdalla/Student-Welafare-Management-System.git
cd Student-Welafare-Management-System/Student-Welfare-Management-System
```

---

## Step 4: Create Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.10 swms-env
```

Activate it (if not already activated):
```bash
workon swms-env
```

---

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: If you are on a Free Tier and `mysqlclient` fails to install, you can ignore it as you will be using SQLite.

---

## Step 6: Configure Environment Variables

### 6.1 Create .env File
```bash
cp .env.example .env
nano .env
```

### 6.2 Update .env with Your Values
Replace the placeholders with your actual values.

#### Option A: Free Tier (SQLite)
```env
USE_SQLITE=True
SECRET_KEY=your-django-secret-key-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
# Database details below will be ignored
```

#### Option B: Paid Tier (MySQL)
```env
USE_SQLITE=False
SECRET_KEY=your-django-secret-key-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com

DB_NAME=yourusername$swms_db
DB_USER=yourusername
DB_PASSWORD=your-mysql-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_PORT=3306
```

**To generate a new SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## Step 7: Update Django Settings

### 7.1 Check settings.py
Make sure your `settings.py` has:

```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'hms/static')]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Step 8: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 9: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

---

## Step 10: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## Step 11: Configure Web App

### 11.1 Create Web App
1. Go to **Web** tab in PythonAnywhere dashboard
2. Click **Add a new web app**
3. Choose **Manual configuration** (not Django wizard)
4. Select **Python 3.10**

### 11.2 Configure WSGI File
1. In the Web tab, find the **Code** section
2. Click on the WSGI configuration file link
3. **Delete all the existing content**
4. Copy the content from `pythonanywhere_wsgi.py` in your project
5. **Update the path** to match your username:
   ```python
   project_home = '/home/yourusername/Student-Welafare-Management-System/Student-Welfare-Management-System'
   ```
6. Save the file (Ctrl+S or click Save)

### 11.3 Set Virtual Environment
1. In the Web tab, find the **Virtualenv** section
2. Enter the path to your virtual environment:
   ```
   /home/yourusername/.virtualenvs/swms-env
   ```

### 11.4 Configure Static Files
In the **Static files** section, add two mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/Student-Welafare-Management-System/Student-Welfare-Management-System/staticfiles` |
| `/media/` | `/home/yourusername/Student-Welafare-Management-System/Student-Welfare-Management-System/media` |

---

## Step 12: Reload Web App

1. Scroll to the top of the Web tab
2. Click the green **Reload** button
3. Wait for the reload to complete

---

## Step 13: Test Your Application

1. Visit: `https://yourusername.pythonanywhere.com`
2. You should see your CampusCare login page!
3. Test login with the superuser account you created
4. Check that static files (CSS/images) are loading correctly

---

## Troubleshooting

### Error Logs
- Check error logs in the Web tab under **Log files**
- Look at both **Error log** and **Server log**

### Common Issues

#### 1. **500 Internal Server Error**
- Check error logs
- Verify `.env` file exists and has correct values
- Ensure `DEBUG=False` in production
- Check WSGI file path is correct

#### 2. **Static Files Not Loading**
- Run `python manage.py collectstatic` again
- Verify static file mappings in Web tab
- Check `STATIC_ROOT` in settings.py

#### 3. **Database Connection Error**
- Verify database credentials in `.env`
- Check database hostname format: `yourusername.mysql.pythonanywhere-services.com`
- Ensure database name includes username prefix: `yourusername$swms_db`

#### 4. **Import Errors**
- Activate virtual environment: `workon swms-env`
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version matches (3.10)

#### 5. **ALLOWED_HOSTS Error**
- Update `.env` with: `ALLOWED_HOSTS=yourusername.pythonanywhere.com`
- Reload web app

---

## Updating Your Application

When you make changes to your code:

```bash
# In Bash console
cd ~/Student-Welafare-Management-System/Student-Welfare-Management-System
workon swms-env

# Pull latest changes
git pull origin main

# Install any new dependencies
pip install -r requirements.txt

# Run migrations if models changed
python manage.py migrate

# Collect static files if CSS/JS changed
python manage.py collectstatic --noinput

# Reload web app (or use Web tab Reload button)
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

---

## Security Checklist

- ✅ `DEBUG=False` in production
- ✅ Strong `SECRET_KEY` (never commit to Git)
- ✅ Database password is secure
- ✅ `.env` file is in `.gitignore`
- ✅ `ALLOWED_HOSTS` is properly configured
- ✅ HTTPS is enabled (automatic on PythonAnywhere)

---

## Next Steps

1. **Set up email**: Configure SMTP settings for password reset emails
2. **Configure M-Pesa**: Add M-Pesa credentials if using payment features
3. **Custom domain**: Upgrade PythonAnywhere account to use your own domain
4. **Backups**: Set up regular database backups
5. **Monitoring**: Monitor error logs regularly

---

## Support

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Django Documentation: https://docs.djangoproject.com/
- Project Repository: https://github.com/Ali-mahirizi-abdalla/Student-Welafare-Management-System

---

**Deployment Date**: {{ date }}  
**Django Version**: 5.2.8  
**Python Version**: 3.10
