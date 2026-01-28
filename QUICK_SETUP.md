# Quick Setup Guide for SWMS Database

## Step 1: Set Your MySQL Password

Open the `.env` file and add your MySQL root password:

```env
DB_PASSWORD=your_mysql_root_password
```

If your MySQL has no password, leave it empty:
```env
DB_PASSWORD=
```

## Step 2: Create the Database

**Option A: Using MySQL Workbench (Recommended)**
1. Open MySQL Workbench
2. Connect to your MySQL server (localhost)
3. Click on the SQL editor tab
4. Run this command:
   ```sql
   CREATE DATABASE IF NOT EXISTS swms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
5. Click the lightning bolt icon to execute

**Option B: Using MySQL Command Line**
1. Open Command Prompt
2. Navigate to MySQL bin directory:
   ```
   cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
   ```
3. Login to MySQL:
   ```
   mysql -u root -p
   ```
4. Enter your password when prompted
5. Create database:
   ```sql
   CREATE DATABASE swms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   exit;
   ```

## Step 3: Run Django Migrations

Once the database is created and `.env` is configured:

```bash
# Stop the current server (Ctrl+C)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Troubleshooting

**Error: "Access denied"**
- Check your MySQL password in `.env` file
- Ensure MySQL service is running

**Error: "Unknown database"**
- The database hasn't been created yet
- Follow Step 2 above

**Error: "Can't connect to MySQL server"**
- MySQL service isn't running
- Start it from Services (Windows) or run: `net start MySQL80`
