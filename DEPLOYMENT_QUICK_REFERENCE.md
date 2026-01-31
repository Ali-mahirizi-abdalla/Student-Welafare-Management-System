# PythonAnywhere Deployment - Quick Reference

## 📋 Files Created

1. **requirements.txt** - Python dependencies
2. **.env.example** - Environment variables template
3. **pythonanywhere_wsgi.py** - WSGI configuration for PythonAnywhere

## 🚀 Quick Start Commands

### On PythonAnywhere Bash Console:

```bash
# Clone repository
cd ~
git clone https://github.com/Ali-mahirizi-abdalla/Student-Welafare-Management-System.git
cd Student-Welafare-Management-System/Student-Welfare-Management-System

# Create virtual environment
mkvirtualenv --python=/usr/bin/python3.10 swms-env

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Edit with your values

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## 🔧 Web App Configuration

### WSGI File Path:
Copy content from `pythonanywhere_wsgi.py` and update:
```python
project_home = '/home/YOURUSERNAME/Student-Welafare-Management-System/Student-Welfare-Management-System'
```

### Virtual Environment:
```
/home/YOURUSERNAME/.virtualenvs/swms-env
```

### Static Files Mapping:
| URL | Directory |
|-----|-----------|
| `/static/` | `/home/YOURUSERNAME/Student-Welafare-Management-System/Student-Welfare-Management-System/staticfiles` |
| `/media/` | `/home/YOURUSERNAME/Student-Welafare-Management-System/Student-Welfare-Management-System/media` |

## 🔑 Required Environment Variables

### Option A: Free Tier (SQLite)
*(Use this if you have a free PythonAnywhere account)*
```env
USE_SQLITE=True
SECRET_KEY=generate-new-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
```

### Option B: Paid Tier (MySQL)
*(Use this if you upgraded your account)*
```env
USE_SQLITE=False
SECRET_KEY=generate-new-secret-key
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com

DB_NAME=yourusername$swms_db
DB_USER=yourusername
DB_PASSWORD=your-mysql-password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_PORT=3306
```

## 📚 Full Documentation

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete step-by-step instructions.

## ⚡ Update Commands

```bash
cd ~/Student-Welafare-Management-System/Student-Welfare-Management-System
workon swms-env
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```
