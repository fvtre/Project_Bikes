from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url='/login/',  # Redirige al login si no es administrador
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def staff_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/login/',  # Redirige al login si no es staff
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def customer_required(function=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_active and not u.is_staff,
        login_url='/login/',  # Redirige al login si no es cliente
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator