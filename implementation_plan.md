# Implementation Plan: Role-Based Access Control (RBAC)

This plan outlines the steps to implement a professional RBAC system in the CampusCare SWMS, providing standardized roles, dedicated dashboards, and dynamic navigation.

## User Review Required

> [!IMPORTANT]
> - This plan will refactor the existing [dashboard_admin](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/views.py#592-785) into role-specific dashboards.
> - We will use Django Groups as the primary source of truth for permissions.
> - Access to existing generic admin URLs will be restricted based on specific roles.

## Proposed Changes

### Core Security & Models

#### [MODIFY] [models.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/models.py)
- Ensure [StaffProfile](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/models.py#191-325) role choice mappings align with the new standardized roles.
- Add helper methods to `User` or [StaffProfile](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/models.py#191-325) to check for specific roles easily.

#### [NEW] [rbac_setup.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/scripts/rbac_setup.py)
- A management script to create groups (Super Admin, Welfare Officer, etc.) and assign default permissions.

### Dashboards & Views

#### [MODIFY] [views.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/views.py)
- **Refactor [user_login](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/views.py#210-235)**: Redirect based on Group membership.
- **New Dashboard Views**:
  - `super_admin_dashboard`
  - `welfare_officer_dashboard`
  - `hostel_manager_dashboard`
  - `kitchen_manager_dashboard`
  - `security_dashboard`
- **Dashboard Templates**: Use fragments or specific files for each role's dashboard.

#### [MODIFY] [urls.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/urls.py)
- Add paths for each new dashboard.

### Template Logic

#### [MODIFY] [base.html](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/templates/hms/base.html)
- Implement dynamic sidebar logic using template tags or context processors to show links based on user group.

### Access Control

#### [MODIFY] [decorators.py](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/decorators.py)
- Simplify [role_required](file:///c:/Users/jamal/OneDrive/Desktop/Student-Welfare-Management-System/hms/decorators.py#5-49) to prioritize Group checks.
- Add specific role decorators (e.g., `@welfare_officer_required`).

## Verification Plan

### Automated Tests
- Script to verify that users in each group can only access their designated dashboards.
- Verify 403 response for unauthorized access attempt.

### Manual Verification
- Log in as each of the 6 roles and verify:
  - Correct dashboard redirection.
  - Sidebar shows ONLY the relevant links for that role.
  - Profile visibility is correct.
