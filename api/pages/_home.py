from django.shortcuts import redirect, render
from .home import home_context_builder

def home(request):

    # Fetch information from services for the specified user
    context = (
        home_context_builder.build_home_context(request)
    )

    # If profile information does not exist (edge case)
    if context is None:
        return (
            redirect('addprofile')
        )
    
    return render(
        request,
        'api/home.html',
        context,
    )
