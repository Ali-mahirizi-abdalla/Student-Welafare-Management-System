# Student Welfare Management System (SWMS) - Installation Guide

## Prerequisites

Before installing SWMS, ensure you have the following installed on your system:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **MySQL Server 8.0+** - [Download MySQL](https://dev.mysql.com/downloads/mysql/)
- **Git** - [Download Git](https://git-scm.com/downloads/)
- **pip** (Python package installer) - Usually comes with Python

## MySQL Setup

### Windows Installation

1. **Download MySQL Installer**
   - Visit [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
   - Download the MySQL Installer for Windows

2. **Install MySQL Server**
   - Run the installer
   - Choose "Custom" installation
   - Select "MySQL Server" and "MySQL Workbench"
   - Set a root password (remember this!)
   - Complete the installation

3. **Create Database for SWMS**
   ```sql
   -- Open MySQL Workbench or MySQL Command Line Client
   -- Login with root user
   
   CREATE DATABASE swms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   -- Optional: Create a dedicated user for SWMS
   CREATE USER 'swms_user'@'localhost' IDENTIFIED BY 'your_password_here';
   GRANT ALL PRIVILEGES ON swms_db.* TO 'swms_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Linux Installation (Ubuntu/Debian)

```bash
# Update package index
sudo apt update

# Install MySQL Server
sudo apt install mysql-server

# Secure MySQL installation
sudo mysql_secure_installation

# Login to MySQL
sudo mysql

# Create database and user
CREATE DATABASE swms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'swms_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON swms_db.* TO 'swms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### macOS Installation

```bash
# Install MySQL using Homebrew
brew install mysql

# Start MySQL service
brew services start mysql

# Secure MySQL installation
mysql_secure_installation

# Login and create database
mysql -u root -p

CREATE DATABASE swms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'swms_user'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON swms_db.* TO 'swms_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## SWMS Installation

### Step 1: Clone the Repository

```bash
cd /path/to/your/projects
git clone <repository-url> swms
cd swms
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you encounter issues installing `mysqlclient` on Windows:
1. Download the appropriate wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient)
2. Install it: `pip install mysqlclient-<version>.whl`

### Step 4: Configure Environment Variables

1. **Copy the example environment file:**
   ```bash
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/macOS
   ```

2. **Edit `.env` file with your settings:**
   ```env
   # Django Settings
   SECRET_KEY=your-very-secret-key-here-change-this
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # MySQL Database
   DB_NAME=swms_db
   DB_USER=swms_user          # or root
   DB_PASSWORD=your_password  # your MySQL password
   DB_HOST=localhost
   DB_PORT=3306

   # Email Configuration (for development, use console backend)
   ADMIN_EMAIL=admin@swms.edu
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password

   # M-Pesa Configuration (use sandbox credentials for testing)
   MPESA_CONSUMER_KEY=your-key
   MPESA_CONSUMER_SECRET=your-secret
   MPESA_SHORTCODE=174379
   MPESA_PASSKEY=your-passkey
   MPESA_CALLBACK_URL=http://localhost:8000/payment/callback/
   ```

3. **Generate a secure SECRET_KEY:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Step 5: Apply Database Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to create database tables
python manage.py migrate

# Verify database connection
python manage.py check --database default
```

### Step 6: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email address
- Password

### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 8: Run Development Server

```bash
python manage.py runserver
```

The application should now be running at: **http://127.0.0.1:8000/**

## Initial Setup

### Access the Application

1. **Student Portal:** http://127.0.0.1:8000/
2. **Admin Panel:** http://127.0.0.1:8000/admin/

### Create Sample Data (Optional)

You can create sample data through the admin panel:

1. Log in to the admin panel
2. Create:
   - **Rooms** (Admin > Rooms)
   - **Activities** (Admin > Activities)
   - **Announcements** (Admin > Announcements)
3. Register student accounts through the main site

## Troubleshooting

### MySQL Connection Errors

**Error: `Can't connect to MySQL server`**
- Ensure MySQL service is running
- Check DB_HOST, DB_PORT in .env file
- Verify MySQL credentials

**Error: `Access denied for user`**
- Check DB_USER and DB_PASSWORD in .env
- Verify user has permissions: `GRANT ALL PRIVILEGES ON swms_db.* TO 'swms_user'@'localhost';`

**Error: `Unknown database 'swms_db'`**
- Create the database: `CREATE DATABASE swms_db;`

### Python Package Errors

**Error: `mysqlclient installation failed`**

**Windows:**
1. Install Visual C++ Build Tools from Microsoft
2. Or download pre-built wheel from [pythoninternals](https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient)

**Linux:**
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

**macOS:**
```bash
brew install mysql-client
export PATH="/usr/local/opt/mysql-client/bin:$PATH"
pip install mysqlclient
```

### Django Errors

**Error: `No module named 'swms'`**
- Ensure you're in the correct directory
- Activate your virtual environment
- Check manage.py has correct DJANGO_SETTINGS_MODULE

**Error: `SECRET_KEY not set`**
- Create .env file from .env.example
- Set SECRET_KEY in .env file

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in .env
2. Set proper `ALLOWED_HOSTS`
3. Use a strong `SECRET_KEY`
4. Configure proper email backend (SMTP)
5. Set up SSL certificates
6. Use a production-grade web server (Gunicorn + Nginx)

See DEPLOYMENT.md for detailed production setup instructions.

## Getting Help

If you encounter issues:

1. Check this documentation
2. Review error messages carefully
3. Check Django and MySQL logs
4. Ensure all environment variables are set correctly

## Next Steps

Once installation is complete:

1. Log in as admin
2. Configure system settings
3. Create rooms and assign capacities
4. Add weekly activities
5. Create announcements
6. Register student accounts

Enjoy using the Student Welfare Management System (SWMS)!
