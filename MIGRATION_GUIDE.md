# Student Welfare Management System (SWMS) - Migration Guide

## Overview

This guide explains how to migrate from the old Student Welfare Management System (SWMS) to the new Student Welfare Management System (SWMS), or how to set up SWMS from scratch with MySQL.

## What Changed?

### 1. **Project Name**
- **Old:** Student Welfare Management System (SWMS)
- **New:** Student Welfare Management System (SWMS)

### 2. **Database**
- **Old:** SQLite (development) / PostgreSQL (production)
- **New:** MySQL 8.0+

### 3. **Project Structure**
- **Old:** `Student_Welfare_System/` directory
- **New:** `Student_Welfare_System/` directory

### 4. **Code Organization**
- Added utility modules in `Student_Welfare_System/utils/`:
  - `constants.py` - System-wide constants
  - `helpers.py` - Reusable helper functions
  - `validators.py` - Custom validation functions
  - `decorators.py` - Access control decorators

## Migration Steps

### Option A: Fresh Installation (Recommended)

If you want a clean start:

1. Follow the [INSTALLATION.md](INSTALLATION.md) guide
2. Set up MySQL database
3. Run migrations
4. Create new superuser
5. Register students and set up system

### Option B: Migrate Existing Data

If you have existing data in SQLite that you want to preserve:

#### Step 1: Backup Current Database

```bash
# Copy your current database
copy db.sqlite3 db.sqlite3.backup

# Or for Linux/Mac
cp db.sqlite3 db.sqlite3.backup
```

#### Step 2: Export Existing Data

```bash
# Export all data to JSON fixture
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > data_backup.json
```

#### Step 3: Install MySQL and Create Database

Follow the MySQL Setup section in [INSTALLATION.md](INSTALLATION.md)

#### Step 4: Update settings

The settings have already been updated to use MySQL. Configure your `.env` file:

```env
DB_NAME=swms_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

#### Step 5: Run New Migrations

```bash
# Create fresh migrations for MySQL
python manage.py migrate
```

#### Step 6: Load Backed Up Data

```bash
# Load the data you exported earlier
python manage.py loaddata data_backup.json
```

**Note:** If you encounter errors during data loading:
- Some data might need manual adjustment
- User passwords will be preserved
- Check for MySQL-specific data type issues

#### Step 7: Verify Data

```bash
# Check that all data loaded correctly
python manage.py shell
```

```python
from django.contrib.auth.models import User
from Student_Welfare_System.models import Student, Room, Meal, Payment

print(f"Users: {User.objects.count()}")
print(f"Students: {Student.objects.count()}")
print(f"Rooms: {Room.objects.count()}")
print(f"Meals: {Meal.objects.count()}")
print(f"Payments: {Payment.objects.count()}")
```

## Post-Migration Tasks

### 1. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 2. Test the Application

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ and test:
- Login functionality
- Student dashboard
- Meal booking
- Room selection
- Admin panel

### 3. Update Environment Variables

Make sure all environment variables are properly set in your `.env` file:

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL Database
DB_NAME=swms_db
DB_USER=swms_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Email (optional for testing)
ADMIN_EMAIL=admin@swms.edu
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# M-Pesa (use sandbox for testing)
MPESA_CONSUMER_KEY=your-key
MPESA_CONSUMER_SECRET=your-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
```

## Troubleshooting Migration Issues

### Issue: MySQL Connection Refused

**Solution:**
```bash
# Check if MySQL is running
# Windows
net start MySQL80

# Linux
sudo systemctl start mysql

# macOS
brew services start mysql
```

### Issue: Data Import Fails

**Solution:**
1. Check that migrations ran successfully
2. Try importing in smaller chunks:
   ```bash
   # Export and import by app
   python manage.py dumpdata auth.user --indent 2 > users.json
   python manage.py dumpdata Student_Welfare_System --indent 2 > Student_Welfare_System_data.json
   
   # Then import separately
   python manage.py loaddata users.json
   python manage.py loaddata Student_Welfare_System_data.json
   ```

### Issue: Character Encoding Problems

**Solution:**
Ensure MySQL database uses utf8mb4:

```sql
ALTER DATABASE swms_db CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
```

### Issue: Foreign Key Constraints

**Solution:**
If you get foreign key errors during import:

```sql
-- Temporarily disable foreign key checks
SET FOREIGN_KEY_CHECKS=0;

-- Re-enable after import
SET FOREIGN_KEY_CHECKS=1;
```

## Code Changes Summary

### Updated Files

1. **Project Configuration**
   - `swms/settings.py` - MySQL database configuration
   - `swms/wsgi.py` - Updated module references
   - `swms/asgi.py` - Updated module references
   - `manage.py` - Updated settings module reference

2. **Documentation**
   - `README.md` - Updated with SWMS branding
   - `INSTALLATION.md` - New comprehensive guide
   - `MIGRATION_GUIDE.md` - This file

3. **Templates**
   - `base.html` - Updated branding
   - `login.html` - Updated branding
   - Other templates - Automated branding updates

4. **New Utility Modules**
   - `Student_Welfare_System/utils/constants.py`
   - `Student_Welfare_System/utils/helpers.py`
   - `Student_Welfare_System/utils/validators.py`
   - `Student_Welfare_System/utils/decorators.py`

### Removed Files

Unnecessary debug and fix scripts were removed:
- `fix_*.py` (9 files)
- `debug_*.py` (2 files)
- `check_*.txt` (2 files)
- Other temporary files

## Testing Checklist

After migration, verify the following features:

- [ ] User authentication (login/logout/register)
- [ ] Student dashboard loads
- [ ] Meal booking works
- [ ] Room selection and assignment
- [ ] Maintenance request submission
- [ ] Leave request submission
- [ ] Admin dashboard accessible
- [ ] Student management (admin)
- [ ] Announcements display
- [ ] Events and RSVP
- [ ] M-Pesa payment integration
- [ ] Profile updates
- [ ] File uploads (images, documents)

## For Developers

### Using New Utility Modules

```python
# Import constants
from hms.utils.constants import SYSTEM_NAME, PRIORITY_HIGH

# Import helpers
from hms.utils.helpers import get_user_role, format_phone_number, is_user_admin

# Import validators
from hms.utils.validators import validate_phone_number, validate_file_size

# Import decorators
from hms.utils.decorators import student_required, admin_required

# Example usage in views
@student_required
def my_student_view(request):
    role = get_user_role(request.user)
    return render(request, 'template.html', {'role': role})
```

### Database Optimization

The new MySQL setup includes:
- utf8mb4 character set for full Unicode support
- Indexed fields for faster queries
- Proper foreign key relationships
- Connection pooling ready

## Rollback Plan

If you need to rollback to the old system:

1. **Stop the server**
2. **Restore backup:**
   ```bash
   copy db.sqlite3.backup db.sqlite3
   ```
3. **Revert Git changes** (if using version control)
4. **Restart server**

## Getting Help

If you encounter issues during migration:
1. Check this guide thoroughly
2. Review error messages in console
3. Check MySQL error logs
4. Verify all environment variables are set
5. Ensure MySQL service is running

## Next Steps After Migration

1. **Configure System Settings**
   - Set up rooms and capacities
   - Create weekly activities
   - Add announcements

2. **User Management**
   - Create additional admin users if needed
   - Set up warden accounts
   - Register student accounts

3. **Test All Features**
   - Go through each section of the system
   - Test as both student and admin
   - Verify email notifications

4. **Production Deployment** (if applicable)
   - Set `DEBUG=False`
   - Configure proper database credentials
   - Set up SSL certificates
   - Use production-grade web server

---

**Migration completed!** Your system is now running as the Student Welfare Management System (SWMS) with MySQL.
