from django.contrib.auth.models import User
from django.contrib.auth import login
from django.shortcuts import redirect

def guest_login(request):

    guest_user = (
        User.objects.get(username="temporary_user")
    )

    login(request, guest_user)

    return redirect("home")