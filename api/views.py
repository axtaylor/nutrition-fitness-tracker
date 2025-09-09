from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import WeightLog, NutritionLog, CompositionLog, TrainingLog, UserInformation
from .forms import WeightLogForm, NutritionLogForm, CompositionLogForm, TrainingLogForm, UserInformationForm
from . import services, home_context_builder
from django.views.decorators.csrf import csrf_protect
from django.db.models import Sum

def profile_exists(request) -> bool:
    try:
        return True if UserInformation.objects.filter(user=request.user).exists() else False
    except (AttributeError):
        return False
    
def is_guest(request):
    try:
        return request.user == User.objects.get(username="temporary_user")
    except Exception:
        return False
#####################################################################################################
'''
Login Page

REDIRECT TO HOME: User is authenticated.
'''
@csrf_protect
def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
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

@csrf_protect
def guest_login(request):
    guest_user = User.objects.get(username="temporary_user")
    login(request, guest_user)
    return redirect("home")
'''
Log Out Functionality
'''
@login_required(login_url="login")
def logout_page(request):
    logout(request)
    return redirect('login')

'''
Register Account Page

REDIRECT TO HOME: User is registered in the DB.
'''
@csrf_protect
def register_user(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return redirect('addprofile')
        else:
            messages.error(request, 'Error: Registration Issue')

    return render(
        request,
        "api/login_register.html",
        {
            'reg_form': form,
            'data': True,
        },
    )

'''
Create Profile Information

REDIRECT TO HOME: Profile already exits,
                  User Registers Profile Info
                  User is Guest
'''
@csrf_protect
@login_required(login_url="login")
def register_profile(request):

    if profile_exists(request):
        return redirect("home")
    if is_guest(request):
        return redirect('home')

    if request.method == "POST":
        form = UserInformationForm(request.POST)
        if form.is_valid():
            info_form = form.save(commit=False)
            info_form.user = request.user
            info_form.save()
            return redirect('home')
        
    form = UserInformationForm()
    return render(
        request,
        'api/add_profile.html',
        {'info_form': form},
    )

'''
View and Edit Profile Page

REDIRECT TO HOME: User does not own profile,
                  Profile does not yet exist
                  Guest user submit POST request
'''
@csrf_protect
@login_required(login_url="login")
def user_profile(request):
    if not profile_exists(request):
        return redirect("home")

    obj = UserInformation.objects.get(user=request.user)
    
    if obj.user != request.user:
        return redirect('home')

    form = UserInformationForm(instance=obj)

    if request.method == "POST":
        if is_guest(request):
            return redirect('profile')
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
'''
Home Page
'''
#@allow_guest_user
@login_required(login_url="login")
def home(request):
    context = home_context_builder.build_home_context(request)

    if context is None:
        return redirect('addprofile')
    
    return render(
        request,
        'api/home.html',
        context,
    )

def about(request):
    return render(
        request,
        'api/about.html'
    )

@login_required
def graph(request, context={}):

    data_sources, periods = {
        'weight': (WeightLog, 'weight'),
        'bodyfat': (CompositionLog, 'bodyfat'),
        'lean_mass': (CompositionLog, 'lean_mass'),
        'fat_mass': (CompositionLog, 'fat_mass'),
        'calories': (NutritionLog, 'calories'),
        'protein': (NutritionLog, 'protein'),
        'carbs': (NutritionLog, 'carbs'),
        'fat': (NutritionLog, 'fat'),
    }, [7, 28, 365]

    data = {}
    for metric, (model, field) in data_sources.items():

        log = model.objects.filter(user=request.user).order_by('-date')
        df = services.as_dataframe(
            log, 
            field
        )
        labels = df.get('date', [])
        values = df.get('result', [])

        data[metric] = {}
        for period in periods:
            data[metric][f'labels_{period}'] = labels[-period:] if labels else []
            data[metric][f'data_{period}'] = values[-period:] if values else []

    context = {
        'data': data
    }
    return render(
        request,
        'api/graph.html',
        context,
    )
#####################################################################################################
'''
Logbook views
'''
LOG_CONFIGS = {
    'weight': {
        'model': WeightLog,
        'form': WeightLogForm,
        'redirect_name': 'weightlog',
        'template_context': lambda request: {
            'type': 'weight',
            'units': services.units(UserInformation.objects.filter(user=request.user).first().units)['weight']},
        'pre_save': None,
    },
    'nutrition': {
        'model': NutritionLog,
        'form': NutritionLogForm,
        'redirect_name': 'nutritionlog',
        'template_context': lambda request: {'type': 'nutrition'},
        'pre_save': None,
    },
    'composition': {
        'model': CompositionLog,
        'form': CompositionLogForm,
        'redirect_name': 'compositionlog',
        'template_context': lambda request: {
            'type': 'composition',
            'measurement': services.units(UserInformation.objects.filter(user=request.user).first().units)['height'],
            'weight': services.units(UserInformation.objects.filter(user=request.user).first().units)['weight'],
        },
        'pre_save': lambda request, obj: _complete_composition_log(request, obj),
    },
    'training': {
        'model': TrainingLog,
        'form': TrainingLogForm,
        'redirect_name': 'traininglog',
        'template_context': lambda request: {'type': 'training'},
        'pre_save': None,
    },
}

def _complete_composition_log(request, composition_log):
    try:
        gender = UserInformation.objects.filter(user=request.user).first().gender
        composition_log.height = UserInformation.objects.get(user=request.user).height
        composition_log.bodyfat = services.body_composition(gender, composition_log)['body_fat']
        composition_log.lean_mass = services.body_composition(gender, composition_log)['lean_mass']
        composition_log.fat_mass = services.body_composition(gender, composition_log)['fat_mass']
    except UserInformation.DoesNotExist:
        messages.error(request, "Check Profile Configuration")
        raise

@login_required(login_url="login")
def generic_log_view(request, log_type):

    if not profile_exists(request):
        return redirect('home')
    
    config = LOG_CONFIGS[log_type]
    queryset = config['model'].objects.filter(user=request.user)
    
    context = {
        'logbook': queryset,
        'guest': is_guest(request),
        **config['template_context'](request)
    }
    
    return render(
        request,
        'api/log.html',
        context,
    )

@csrf_protect
@login_required(login_url="login") # GUEST blocked from competing POST
def generic_add_log(request, log_type):

    if not profile_exists(request):
        return redirect('home')
    
    config = LOG_CONFIGS[log_type]
    form_class = config['form']
    
    if request.method == 'POST':

        if is_guest(request):
            return redirect(config['redirect_name'])

        form = form_class(request.POST)

        if form.is_valid():
            log_obj = form.save(commit=False)
            log_obj.user = request.user

            if config['pre_save']:
                try:
                    config['pre_save'](request, log_obj)
                except Exception:
                    context = {"add_form": form_class(), "type": "add"}
                    return render(request,
                                  'api/add_edit.html',
                                  context,
                                  )
            
            log_obj.save()
            return redirect(config['redirect_name'])
    
    context = {
        "add_form": form_class(),
        "type": "add",
        'log_info': config['redirect_name'],
    }
    
    return render(
        request,
        'api/add_edit.html',
        context,
                  
    )

@csrf_protect
@login_required(login_url="login") # GUEST blocked from competing POST
def generic_edit_log(request, log_type, uuid_key):

    config = LOG_CONFIGS[log_type]
    obj = get_object_or_404(config['model'], id=uuid_key)
    
    if obj.user != request.user:
        return redirect(config['redirect_name'])
    
    if request.method == "POST":

        if is_guest(request):
            return redirect(config['redirect_name'])

        form = config['form'](request.POST, instance=obj)

        if form.is_valid():
            log_obj = form.save(commit=False)
            log_obj.user = request.user
            
            if config['pre_save']:
                try:
                    config['pre_save'](request, log_obj)
                except Exception:
                    context = {'edit_form': config['form'](instance=obj)}
                    return render(request, 'api/add_edit.html', context)
            
            log_obj.save()
            return redirect(config['redirect_name'])
    
    form = config['form'](instance=obj)
    context = {
        'edit_form': form,
        'log_info': config['redirect_name'],
        }
    
    return render(
        request,
        'api/add_edit.html',
        context,
    )


@csrf_protect
@login_required(login_url="login")
def generic_delete_log(request, log_type, uuid_key):

    config = LOG_CONFIGS[log_type]
    obj = get_object_or_404(config['model'], id=uuid_key)
    
    if obj.user != request.user:
        return redirect(config['redirect_name'])
    
    if request.method == "POST":
        if is_guest(request):
            return redirect(config['redirect_name']) # no GUEST
        obj.delete()
        return redirect(config['redirect_name'])
    
    context = {'deleting_object': obj}
    return render(
        request,
        'api/delete.html',
        context
    )


@login_required(login_url="login")
def weight_log(request):
    return generic_log_view(request, 'weight')

@csrf_protect
@login_required(login_url="login")
def add_log(request):
    return generic_add_log(request, 'weight')

@csrf_protect
@login_required(login_url="login")
def edit_log(request, uuid_key):
    return generic_edit_log(request, 'weight', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_log(request, uuid_key):
    return generic_delete_log(request, 'weight', uuid_key)

@login_required(login_url="login")
def nutrition_log(request):
    return generic_log_view(request, 'nutrition')

@csrf_protect
@login_required(login_url="login")
def add_nutrition_log(request):
    return generic_add_log(request, 'nutrition')

@csrf_protect
@login_required(login_url="login")
def edit_nutrition_log(request, uuid_key):
    return generic_edit_log(request, 'nutrition', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_nutrition_log(request, uuid_key):
    return generic_delete_log(request, 'nutrition', uuid_key)

@login_required(login_url="login")
def composition_log(request):
    return generic_log_view(request, 'composition')

@csrf_protect
@login_required(login_url="login")
def add_composition_log(request):
    return generic_add_log(request, 'composition')

@csrf_protect
@login_required(login_url="login")
def edit_composition_log(request, uuid_key):
    return generic_edit_log(request, 'composition', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_composition_log(request, uuid_key):
    return generic_delete_log(request, 'composition', uuid_key)

@login_required(login_url="login")
def training_log(request):
    return generic_log_view(request, 'training')

@csrf_protect
@login_required(login_url="login")
def add_training_log(request):
    return generic_add_log(request, 'training')

@csrf_protect
@login_required(login_url="login")
def edit_training_log(request, uuid_key):
    return generic_edit_log(request, 'training', uuid_key)

@csrf_protect
@login_required(login_url="login")
def delete_training_log(request, uuid_key):
    return generic_delete_log(request, 'training', uuid_key)
