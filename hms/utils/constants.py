"""
System-wide constants for Student Welfare Management System (SWMS)
Centralizes magic numbers and repeated strings for better maintainability
"""

# System Information
SYSTEM_NAME = "Student Welfare Management System"
SYSTEM_SHORT_NAME = "CampusCare"
SYSTEM_VERSION = "2.0"

# Pagination
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100

# File Upload Limits (in MB)
MAX_PROFILE_IMAGE_SIZE = 5
MAX_TIMETABLE_SIZE = 10
MAX_DOCUMENT_SIZE = 20
MAX_MAINTENANCE_PHOTO_SIZE = 5

# Date Formats
DISPLAY_DATE_FORMAT = '%B %d, %Y'
DISPLAY_TIME_FORMAT = '%I:%M %p'
DISPLAY_DATETIME_FORMAT = '%B %d, %Y at %I:%M %p'

# Meal Submission Time Limits
MEAL_BOOKING_CUTOFF_HOUR = 20  # 8 PM
EARLY_BREAKFAST_CUTOFF_HOUR = 18  # 6 PM

# Notification Types
NOTIFICATION_TYPE_INFO = 'info'
NOTIFICATION_TYPE_SUCCESS = 'success'
NOTIFICATION_TYPE_WARNING = 'warning'
NOTIFICATION_TYPE_ERROR = 'error'

# Request Status
STATUS_PENDING = 'pending'
STATUS_APPROVED = 'approved'
STATUS_REJECTED = 'rejected'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_RESOLVED = 'resolved'

# Priority Levels
PRIORITY_LOW = 'low'
PRIORITY_MEDIUM = 'medium'
PRIORITY_HIGH = 'high'
PRIORITY_CRITICAL = 'critical'
PRIORITY_URGENT = 'urgent'

# User Roles
ROLE_STUDENT = 'student'
ROLE_ADMIN = 'admin'
ROLE_WARDEN = 'warden'
ROLE_KITCHEN_STAFF = 'kitchen'

# Days of Week (for activities)
DAYS_OF_WEEK = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

# Room Types
ROOM_TYPE_SINGLE = 'single'
ROOM_TYPE_DOUBLE = 'double'
ROOM_TYPE_TRIPLE = 'triple'
ROOM_TYPE_QUAD = 'quad'

# Event Categories
EVENT_SOCIAL = 'social'
EVENT_EDUCATIONAL = 'educational'
EVENT_SPORTS = 'sports'
EVENT_CULTURAL = 'cultural'
EVENT_MEETING = 'meeting'

# Default Messages
MSG_LOGIN_REQUIRED = "You must be logged in to access this page."
MSG_UNAUTHORIZED = "You don't have permission to access this resource."
MSG_SUCCESS_CREATED = "{} created successfully!"
MSG_SUCCESS_UPDATED = "{} updated successfully!"
MSG_SUCCESS_DELETED = "{} deleted successfully!"
MSG_ERROR_GENERIC = "An error occurred. Please try again."
MSG_ERROR_NOT_FOUND = "{} not found."
