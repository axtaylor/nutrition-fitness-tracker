from django.shortcuts import redirect
from django.contrib.auth import logout

'''
Log Out Functionality

Executes logout URL
'''

def logout_page(request):

    logout(request)
    return (
        redirect('login')
    )