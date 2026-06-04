from django.core.cache import cache

EXISTING_FEATURES = [
    { "name": "student_registration", "label": "Student Registration", "icon": "fa-user-graduate", "description": "Student account creation and enrollment" },
    { "name": "deferment_management", "label": "Deferment Management", "icon": "fa-calendar-times", "description": "Student deferment requests and approvals" },
    { "name": "payment_processing", "label": "Payment Processing", "icon": "fa-money-bill-wave", "description": "M-Pesa payments and receipts" },
    { "name": "health_appointments", "label": "Health Appointments", "icon": "fa-heartbeat", "description": "Clinic appointments and medical records" },
    { "name": "maintenance_requests", "label": "Maintenance Requests", "icon": "fa-tools", "description": "Facility maintenance tickets" },
    { "name": "accommodation", "label": "Accommodation", "icon": "fa-bed", "description": "Room allocation and check-in/out" },
    { "name": "visitor_logs", "label": "Visitor Logs", "icon": "fa-user-friends", "description": "Security visitor tracking" },
    { "name": "news_alerts", "label": "News & Alerts", "icon": "fa-newspaper", "description": "Announcements and emergency alerts" }
]

NEW_FEATURES = [
    { "name": "whatsapp_notifications", "label": "WhatsApp Notifications", "icon": "fa-whatsapp", "description": "Send notifications via WhatsApp", "default": False },
    { "name": "ai_chat_assistant", "label": "AI Chat Assistant", "icon": "fa-robot", "description": "AI-powered student support chatbot", "default": False },
    { "name": "mobile_app_api", "label": "Mobile App API", "icon": "fa-mobile-alt", "description": "REST API for mobile application", "default": False },
    { "name": "advanced_reports", "label": "Advanced Reports", "icon": "fa-chart-line", "description": "Detailed analytics and reporting", "default": False },
    { "name": "parent_portal", "label": "Parent Portal", "icon": "fa-users", "description": "Parent access to student progress", "default": False },
    { "name": "e_learning", "label": "E-Learning Integration", "icon": "fa-laptop-code", "description": "Online course management", "default": False },
    { "name": "library_management", "label": "Library Management", "icon": "fa-book", "description": "Digital library and book tracking", "default": True },
    { "name": "alumni_portal", "label": "Alumni Portal", "icon": "fa-graduation-cap", "description": "Graduate alumni network", "default": False }
]

class FeatureLookup:
    def __init__(self, checker_func):
        self._checker_func = checker_func

    def __getattr__(self, name):
        return self._checker_func(name)

    def __getitem__(self, name):
        return self._checker_func(name)

    def __call__(self, name):
        return self._checker_func(name)

class FeatureFlags:
    def __init__(self):
        self.is_enabled = FeatureLookup(self._is_enabled_internal)

    def _is_enabled_internal(self, name):
        # 1. Existing features are locked to ON
        existing_names = [f["name"] for f in EXISTING_FEATURES]
        if name in existing_names:
            return True
            
        # 2. Check if name is in new features
        new_feature_defaults = {f["name"]: f["default"] for f in NEW_FEATURES}
        if name not in new_feature_defaults:
            return False
            
        # 3. Check database (with caching)
        cache_key = f"feature_flag_{name}"
        state = cache.get(cache_key)
        if state is not None:
            return state
            
        try:
            from hms.models import FeatureFlag
            flag = FeatureFlag.objects.get(name=name)
            state = flag.is_enabled
        except FeatureFlag.DoesNotExist:
            state = new_feature_defaults[name]
            
        cache.set(cache_key, state, 300)
        return state

    def set_enabled(self, name, enabled):
        existing_names = [f["name"] for f in EXISTING_FEATURES]
        if name in existing_names:
            return
            
        new_feature_defaults = {f["name"]: f["default"] for f in NEW_FEATURES}
        if name not in new_feature_defaults:
            return
            
        from hms.models import FeatureFlag
        flag, created = FeatureFlag.objects.get_or_create(
            name=name,
            defaults={'is_enabled': enabled}
        )
        if not created:
            flag.is_enabled = enabled
            flag.save()
            
        cache_key = f"feature_flag_{name}"
        cache.set(cache_key, enabled, 300)

    def __getattr__(self, name):
        # Allow feature_flags.whatsapp_notifications
        if name == 'is_enabled':
            return self.is_enabled
        return self._is_enabled_internal(name)

    def __getitem__(self, name):
        # Allow feature_flags['whatsapp_notifications']
        return self._is_enabled_internal(name)

feature_flags = FeatureFlags()
