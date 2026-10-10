from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def role_required(role):
    """
    Usage:
        @role_required('farmer')
        def add_crop(request): ...

        @role_required('retailer')
        def checkout(request): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, "profile"):
                messages.error(request, "Profile missing. Contact support.")
                return redirect("home")
            if request.user.profile.role != role:
                messages.error(request, "You are not authorized to view that page.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
