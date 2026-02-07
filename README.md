# Student Welfare Management System (SWMS)

## Overview
The **Student Welfare Management System (SWMS)** is a comprehensive platform designed to manage student accommodation, meals, welfare, and activities. It streamlines administrative tasks for the warden/kitchen staff and provides students with an easy-to-use portal for their daily needs.

## Features

### For Students
- **Dashboard**: View daily meal status, announcements, and quick actions.
- **Meal Management**: Book/Confirm meals (Breakfast, Lunch, Supper).
- **Accommodation**: View room details and request room changes.
- **Welfare**: Submit maintenance requests and leave applications.
- **Activities**: View and RSVP for hostel events.
- **Notifications**: Real-time alerts for announcements and status updates.

### For Administrators
- **Student Management**: Register, view, and manage student profiles.
- **Meal Analytics**: Track daily meal consumption and trends.
- **Room Management**: Assign rooms and manage occupancy.
- **Communication**: Post announcements and message students.
- **Reports**: Export data and generate welfare reports.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Ali-mahirizi-abdalla/Student-Welafare-Management-System.git
    cd Student-Welfare-Management-System
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file based on `.env.example`.

5.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run Server:**
    ```bash
    python manage.py runserver
    ```

## Technology Stack
- **Backend**: Django (Python)
- **Database**: MySQL / SQLite (Dev)
- **Frontend**: HTML5, CSS3, JavaScript (Django Templates)
- **Styling**: Bootstrap / Custom CSS

## Contributing
Please see `CONTRIBUTING.md` for guidelines.

## License
MIT License