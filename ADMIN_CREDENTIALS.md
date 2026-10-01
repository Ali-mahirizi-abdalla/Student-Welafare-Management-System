# Campus Care — Super Admin Credentials

### Login Information

| Role | Username | Password | Email |
|---|---|---|---|
| **Super Admin (Primary)** | `Ali-Mahrez` | `A8486aom` | `alimahrez744@gmail.com` |
| **Super Admin (Backup)** | `adminadmin` | `A8486aom` | `admin@example.com` |

---

### Access Portals

- **Staff / Super Admin Dashboard**: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/) (Redirects to `/manage/super-admin/`)
- **Django Administration**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

### Management Command (Automated Setup)

To automatically provision or reset super admin credentials on any local or remote server:

```bash
python manage.py create_superadmin
```
