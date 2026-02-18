# 💰 Subscription System Guide

A complete subscription management system has been added to Campus Care.

## 📅 Key Dates
- **Grace Period Ends:** March 1, 2026
- **System Locks:** March 1, 2026 (if no payment)
- **Subscription Cost:** KES 3,000 / month

---

## 🛠️ How It Works

### 1. Verification Logic
- **Before March 1, 2026:**
  - The system checks the date.
  - Since it is before the deadline, **ALL pages are accessible**.
  - No payment is required.

- **On/After March 1, 2026:**
  - The system checks for an **Active Subscription**.
  - If found: Access is granted.
  - If NOT found: All pages redirect to `/subscription/`.
  - Logins and Admin panels are protected but accessible to allow management.

### 2. Testing The Lock (Before March 1)
To verify the locking mechanism *before* March 1, you can:
1. Open `subscription/middleware.py`.
2. Change line 19: `cutoff_date = datetime.date(2026, 3, 1)` to a past date (e.g., `2025, 1, 1`).
3. Refresh any page. You should be redirected to the subscription page.

### 3. Simulating Payment
- Visit `/subscription/` (or wait until you are redirected).
- Click "Pay Now via MPESA".
- This will create a 30-day active subscription.

### 4. Automatic Expiration
- A management command has been created to expire subscriptions.
- Run manually: `python manage.py check_subscriptions`
- Set up as a daily cron job in production.

---

## 📂 Implementation Details

### New App: `subscription`
- **Models:** `Subscription` (tracks dates, status, payment)
- **Views:** Index, Payment, Status, Expired
- **Middleware:** `SubscriptionMiddleware` (handles the locking logic)

### Changes to Core
- **Settings:** Added `subscription` app and middleware.
- **URLs:** Included `subscription/` routes.
- **Commands:** Added `check_subscriptions`.

---

## ✅ Verification Steps

1. **Verify Setup:**
   Run `python manage.py check` to ensure no errors.
   
2. **Check Subscription Status:**
   Visit `/subscription/status/` to see current status.

3. **Management:**
   Admins can view/edit subscriptions in the Django Admin panel (requires registering the model in `admin.py`).

---
**Created by Antigravity**
