#!/bin/bash
# DEPLOYMENT SCRIPT FOR CAMPUS CARE
# Run this script on your VPS (38.247.148.232)

APP_DIR="/var/www/campus-care/Student-Welafare-Management-System"
VENV_NAME="venv"

# Function to print step
print_step() {
    echo "=================================================="
    echo "$1"
    echo "=================================================="
}

print_step "🚀 Starting Deployment..."

# 1. Navigate to project directory
if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR"
    echo "📂 Changed directory to $APP_DIR"
else
    echo "❌ Directory not found: $APP_DIR"
    exit 1
fi

# 2. Pull latest changes
print_step "⬇️ Pulling latest changes..."
git pull origin main

# 3. Virtual Environment Setup
print_step "🐍 Setting up Virtual Environment..."

# Check if venv exists
if [ ! -d "$VENV_NAME" ]; then
    echo "⚠️ Virtual environment '$VENV_NAME' not found."
    echo "🔨 Creating virtual environment..."
    python3 -m venv "$VENV_NAME"
fi

# Activate venv
source "$VENV_NAME/bin/activate"

# Verify python path
PYTHON_BIN=$(which python)
echo "🔍 Using Python: $PYTHON_BIN"

# 4. Install dependencies
print_step "📦 Installing dependencies..."
pip install -r requirements.txt

# 5. Apply Migrations
print_step "🗄️ Applying migrations..."
python manage.py migrate

# 6. Collect Static
print_step "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# 7. Check Subscriptions
print_step "💳 Checking subscriptions..."
python manage.py check_subscriptions

# 8. Restart Services
print_step "🔄 Restarting services..."

# Try to find the service file
# Common names: gunicorn, campus-care, swms, django
POSSIBLE_SERVICES=("gunicorn" "campus-care" "swms" "django_app")
RESTARTED=false

for SERVICE in "${POSSIBLE_SERVICES[@]}"; do
    if systemctl is-active --quiet "$SERVICE"; then
        echo "✅ Found active service: $SERVICE"
        sudo systemctl restart "$SERVICE"
        echo "🔄 $SERVICE restarted."
        RESTARTED=true
        break
    fi
done

if [ "$RESTARTED" = false ]; then
    echo "❌ Could not auto-detect Gunicorn service name."
    echo "👉 Please run: sudo systemctl restart <your-service-name>"
    echo "👉 List available services: ls /etc/systemd/system/"
fi

# Reload Nginx
if systemctl is-active --quiet nginx; then
    sudo systemctl reload nginx
    echo "✅ Nginx reloaded."
else
    echo "⚠️ Nginx not found or not active."
fi

print_step "✅ Deployment Complete!"
