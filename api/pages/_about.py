from django.shortcuts import redirect, render

def about(request):
    return render(
        request,
        'api/about.html'
    )