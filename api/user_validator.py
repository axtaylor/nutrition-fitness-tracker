from django.contrib.auth.models import User
from .models import UserInformation

def profile_exists(request) -> bool:
    try:
        return (
            True if UserInformation.objects.filter(user=request.user).exists()
            else False
        )
    except (AttributeError):
        return False

def is_guest(request):
    try:
        return (
            request.user == User.objects.get(username="temporary_user")
        )
    except Exception:
        return False