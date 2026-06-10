from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect, render

'''
Register Account Page

REDIRECT TO HOME: User is registered in the DB.

Successful POST: User is directed to add profile URL to submit more information

'''

def register_user(request):

    form = UserCreationForm()

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'Your account creation was successful.')

            return (
                redirect('addprofile')
            )
        
        else:
            messages.error(request, 'Error: Registration Issue')

    return render(
        request,
        "api/login_register.html",
        {
            'reg_form': form,
            'data': True, # Hide navbar boolean
        },
    )