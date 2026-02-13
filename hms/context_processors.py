from .models import Message

def unread_messages(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_messages': count}
    return {'unread_messages': 0}

def staff_role_info(request):
    if request.user.is_authenticated:
        staff_profile = getattr(request.user, 'staff_profile', None)
        if staff_profile:
            category = staff_profile.get_category()
            return {
                'staff_category': category.replace('_', ' ').title() if category else "Staff",
                'staff_category_raw': category,
                'staff_role': staff_profile.get_role_display()
            }
    return {'staff_category': None, 'staff_category_raw': None, 'staff_role': None}
