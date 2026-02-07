
# ==================== Audit Logs ====================

@login_required
@role_required(['Admin', 'Finance'])
def audit_log_list(request):
    """
    Admin/Finance view for Audit Logs.
    Includes filtering, search, and pagination.
    """
    logs = AuditLog.objects.all().select_related('user')
    
    # Search
    query = request.GET.get('q', '').strip()
    if query:
        logs = logs.filter(
            models.Q(user__username__icontains=query) |
            models.Q(object_repr__icontains=query) |
            models.Q(details__icontains=query) |
            models.Q(ip_address__icontains=query)
        )
        
    # Filter by Action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
        
    # Filter by Model
    model = request.GET.get('model')
    if model:
        logs = logs.filter(model_name=model)
        
    # Pagination
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Unique values for filters
    unique_actions = AuditLog.objects.exclude(action__exact='').values_list('action', flat=True).distinct().order_by('action')
    unique_models = AuditLog.objects.exclude(model_name__isnull=True).values_list('model_name', flat=True).distinct().order_by('model_name')
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'current_action': action,
        'current_model': model,
        'unique_actions': unique_actions,
        'unique_models': unique_models,
    }
    return render(request, 'hms/admin/audit_logs.html', context)
