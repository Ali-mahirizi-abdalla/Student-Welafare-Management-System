# Role-Based Access Control Implementation Plan

- [x] Backend Security Restrictions
  - [x] Implement `@category_required` decorator in [decorators.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/decorators.py) (Already supported via [role_required(allowed_categories=[...])](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/decorators.py#5-49))
  - [x] Apply `@category_required` to all specific views in [views.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/views.py) (Students, Deferments, Payments, etc.)
- [x] Sidebar Menu Restrictions
  - [x] Update [hms/templates/hms/includes/sidebar.html](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/templates/hms/includes/sidebar.html) using `staff_category_raw` conditions (Verified existing logic)
- [x] Dashboard Context Restrictions
  - [x] Update [dashboard_admin](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/views.py#589-782) in [views.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/views.py) to exclude querying irrelevant data for certain roles (optimization/security)
  - [x] Wrap stat cards and action buttons in [dashboard.html](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/templates/hms/admin/dashboard.html) with explicit group checks (Verified existing logic)
- [x] Verification
  - [x] Test access with a created user (non-Executive)
  - [x] Test access with Superuser
- [x] Fix Internal Server Error (Post-Deployment)
  - [x] Diagnose syntax error in views.py
  - [x] Remove accidental backslashes from decorators
  - [x] Push fix to GitHub

- [x] Make Dashboard Graphs Functional
  - [x] Implement rolling 7-day window for weekly analytics
  - [x] Support monthly rolling window
  - [x] Fix empty data scenarios
  - [x] Add more detailed analytics reports in [analytics_dashboard](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/views.py#2079-2267)
  - [x] Verify frontend visualization is accurate
