from ..user_validator import profile_exists, is_guest
from django.shortcuts import redirect, render
from ..forms import UserInformationForm

'''
Create Profile Information

REDIRECT TO HOME: Profile already exits,
                  User Registers Profile Info
                  User is Guest

'''

def register_profile(request):

    if profile_exists(request):
        return (
            redirect("home")
        )
    
    if is_guest(request):
        return (
            redirect('home')
        )

    if request.method == "POST":

        form = UserInformationForm(request.POST)

        if form.is_valid():
            info_form = form.save(commit=False)
            info_form.user = request.user
            info_form.save()

            return (
                redirect('home')
            )
        
    form = UserInformationForm()

    return render(
        request,
        'api/add_profile.html',
        {'info_form': form},
    )