from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib import messages

'''
Login Page for Registered Users

'''
def login_page(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":

        # Mutable copy of post to lower the entered username
        post_data = request.POST.copy()
        if 'username' in post_data:
            post_data['username'] = post_data['username'].lower()

        form = AuthenticationForm(request, data=post_data)

        if form.is_valid():
            login(request, form.get_user())
            return redirect('addprofile')
        
        else:
            messages.error(request, 'Invalid Credentials')

    else:
        form = AuthenticationForm()

    return render(
        request,
        'api/login_register.html',
        {
            'submit_type': 'login',
            'data': True,
            'form': form
        },
    )