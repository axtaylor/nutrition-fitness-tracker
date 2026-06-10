from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.contrib import messages
from axes.decorators import axes_dispatch
from axes.helpers import get_lockout_response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

'''
Login Page for Registered Users

'''

@axes_dispatch
@never_cache
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

def lockout_response(request, credentials, *args, **kwargs):
    form = AuthenticationForm()
    return render(
        request,
        'api/login_register.html',
        {
            'submit_type': 'login',
            'data': True,
            'form': form,
            'locked_out': True,
            'lockout_message': 'Too many failed attempts. Please try again in 3 minutes.',
        },
        status=200,
    )