from .models import UserInformation
'''
Allows HTML to have variable 'has_user_profile" for frontend validation
The backend handles access permissions, but for the navbar it is required
to hide the non-permissible links.
'''
def user_profile_context(request):
    context = {}
    if request.user.is_authenticated:
        context['has_user_profile'] = UserInformation.objects.filter(user=request.user).exists()
    else:
        context['has_user_profile'] = False
    return context