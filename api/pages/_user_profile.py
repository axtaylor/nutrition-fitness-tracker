from ..user_validator import profile_exists, is_guest
from ..forms import UserInformationForm
from ..models import NutritionLog, UserInformation
from .. import services

from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Sum

'''
View and Edit Profile Page

REDIRECT TO HOME: User does not own profile,
                  Profile does not yet exist
                  Guest user submit POST request

'''

def user_profile(request):

    if not profile_exists(request):
        return (
            redirect("home")
        )

    obj = UserInformation.objects.get(user=request.user)
    
    if obj.user != request.user:
        return (
            redirect('home')
        )

    form = UserInformationForm(instance=obj)

    if request.method == "POST":

        if is_guest(request):
            return (
                redirect('profile')
            )
        
        form = UserInformationForm(request.POST, instance=obj)

        if form.is_valid():
            info_form = form.save(commit=False)
            info_form.user = request.user
            info_form.save()
            messages.info(request, "Information Saved")

    context = {
        'update_form': form,
        'userprofile': UserInformation.objects.filter(user=request.user).first(),
        'height': services.units(UserInformation.objects.filter(user=request.user).first().units)['height'],
        'total_cals': NutritionLog.objects.filter(user=request.user).order_by('-date').aggregate(Sum('calories'))['calories__sum'],
        'guest': is_guest(request)
    }
    
    return render(
        request,
        'api/profile.html',
        context,
    )