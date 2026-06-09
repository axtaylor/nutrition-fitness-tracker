from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from .pages import (
    _guest_login, _login_page, _logout_page, _register_user, _register_profile,
    _user_profile, _home, _graph, _ai_analysis, _logbooks, _about)

@csrf_protect
def guest_login(request):
    return _guest_login.guest_login(request)

@csrf_protect
def login_page(request):
    return _login_page.login_page(request)

@login_required(login_url="login")
def logout_page(request):
    return _logout_page.logout_page(request)

@csrf_protect
def register_user(request):
    return _register_user.register_user(request)

@csrf_protect
@login_required(login_url="login")
def register_profile(request):
    return _register_profile.register_profile(request)

@csrf_protect
@login_required(login_url="login")
def user_profile(request):
    return _user_profile.user_profile(request)

@login_required(login_url="login")
def home(request):
    return _home.home(request)

@login_required
def graph(request):
    return _graph.graph(request)

@login_required(login_url="login")
def ai_analysis(request):
    return _ai_analysis.ai_analysis(request)

@login_required(login_url="login")
def about(request):
    return _about.about(request)

@login_required(login_url="login")
def weight_log(request):
    return _logbooks.generic_log_view(request, 'weight')

@csrf_protect
@login_required(login_url="login")
def add_log(request):
    return _logbooks.generic_add_log(request, 'weight')

@csrf_protect
@login_required(login_url="login")
def edit_log(request, uuid_key):
    return _logbooks.generic_edit_log(request, 'weight', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_log(request, uuid_key):
    return _logbooks.generic_delete_log(request, 'weight', uuid_key)

@login_required(login_url="login")
def nutrition_log(request):
    return _logbooks.generic_log_view(request, 'nutrition')

@csrf_protect
@login_required(login_url="login")
def add_nutrition_log(request):
    return _logbooks.generic_add_log(request, 'nutrition')

@csrf_protect
@login_required(login_url="login")
def edit_nutrition_log(request, uuid_key):
    return _logbooks.generic_edit_log(request, 'nutrition', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_nutrition_log(request, uuid_key):
    return _logbooks.generic_delete_log(request, 'nutrition', uuid_key)

@login_required(login_url="login")
def composition_log(request):
    return _logbooks.generic_log_view(request, 'composition')

@csrf_protect
@login_required(login_url="login")
def add_composition_log(request):
    return _logbooks.generic_add_log(request, 'composition')

@csrf_protect
@login_required(login_url="login")
def edit_composition_log(request, uuid_key):
    return _logbooks.generic_edit_log(request, 'composition', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_composition_log(request, uuid_key):
    return _logbooks.generic_delete_log(request, 'composition', uuid_key)

@login_required(login_url="login")
def training_log(request):
    return _logbooks.generic_log_view(request, 'training')

@csrf_protect
@login_required(login_url="login")
def add_training_log(request):
    return _logbooks.generic_add_log(request, 'training')

@csrf_protect
@login_required(login_url="login")
def edit_training_log(request, uuid_key):
    return _logbooks.generic_edit_log(request, 'training', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_training_log(request, uuid_key):
    return _logbooks.generic_delete_log(request, 'training', uuid_key)
