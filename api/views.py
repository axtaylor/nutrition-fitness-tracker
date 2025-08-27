from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import WeightLog, NutritionLog, CompositionLog, TrainingLog, UserInformation
from .forms import WeightLogForm, NutritionLogForm, CompositionLogForm, TrainingLogForm, UserInformationForm
from . import services
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

    return render(request,
                   'api/login_register.html',
                   {'submit_type': 'login',
                    'hide_sidebar': False,
                    'form': form},
    )

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

    return render(request,
                "api/login_register.html",
                {
                    'reg_form': form,
                   'hide_sidebar': False,
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
    return render(request,
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

    total_cals = NutritionLog.objects.filter(user=request.user).order_by('-date').aggregate(Sum('calories'))

    context = {'update_form': form,
               'userprofile': UserInformation.objects.filter(user=request.user).first(),
               'height': services.units(UserInformation.objects.filter(user=request.user).first().units)['height'],
               'total_cals': total_cals['calories__sum'],
               'guest': is_guest(request)
    }
    
    return render(request,
                  'api/profile.html',
                  context,
    )
'''
Home Page
'''
#@allow_guest_user
@login_required(login_url="login")
def home(request):
    if profile_exists(request):

        data_sources, periods = {
            'weight': (WeightLog, 'weight'),
            'bodyfat': (CompositionLog, 'bodyfat'),
            'lean_mass': (CompositionLog, 'lean_mass'),
            'fat_mass': (CompositionLog, 'fat_mass'),
            'calories': (NutritionLog, 'calories'),
            'protein': (NutritionLog, 'protein'),
            'carbs': (NutritionLog, 'carbs'),
            'fat': (NutritionLog, 'fat'),
        }, [1, 7, 28, 365, 100000]

        data = {}
        for metric, (model, field) in data_sources.items():
            log = model.objects.filter(user=request.user).order_by('-date')
            df = services.as_dataframe(log, field)
            labels = df.get('date', [])
            values = df.get('result', [])
            imputed_values = df.get('filled_result', [])
            data[metric] = {}
            for period in periods:
                data[metric][f'labels_{period}'] = labels[-period:] if labels else []
                data[metric][f'data_{period}'] = values[-period:] if values else []   
                data[metric][f'imputed_data_{period}'] = imputed_values[-period:] if imputed_values else [] 
    
        user_information = UserInformation.objects.filter(user=request.user).first()
        composition_log = CompositionLog.objects.filter(user=request.user).order_by('-date').first()
        nutrition_logs = NutritionLog.objects.filter(user=request.user).order_by('-date')
        weight_logs = WeightLog.objects.filter(user=request.user).order_by('-date')
        weight_units = services.units(user_information.units)['weight']
        days = services.days_logged(weight_logs)

        recent_weight = weight_logs.first() if days > 0 else 0
        bmi = services.bmi(recent_weight, user_information)
        bmr = services.bmr(recent_weight, user_information)
        ffmi = services.ffmi(composition_log, user_information)

        def get_nutrition_value(nutrition_data, key):
            return nutrition_data[key] if nutrition_data is not None else 0
        
        total_nutrition, weekly_nutrition, monthly_nutrition = (services.nutrition_info(i, (weight_logs if days > 0 else 0), nutrition_logs) for i in [0, 7, 28])
        nutrition_keys = ['avg_cals', 'avg_protein', 'avg_fat', 'avg_carbs']

        total_cals, total_protein, total_fat, total_carbs = [get_nutrition_value(total_nutrition, key) for key in nutrition_keys]
        weekly_cals, weekly_protein, weekly_fat, weekly_carbs = [get_nutrition_value(weekly_nutrition, key) for key in nutrition_keys]
        monthly_cals, monthly_protein, monthly_fat, monthly_carbs = [get_nutrition_value(monthly_nutrition, key) for key in nutrition_keys]

        weight_change_total = data["weight"]['imputed_data_100000'][-1] - data["weight"]['imputed_data_100000'][0] if days > 0 else 0
        weight_change_week =  data["weight"]['imputed_data_7'][-1] - data["weight"]['imputed_data_7'][0] if days > 0 else 0
        weight_change_month =  data["weight"]['imputed_data_28'][-1] - data["weight"]['imputed_data_28'][0] if days > 0 else 0

        energy_expenditure_week, energy_expenditure_month, energy_expenditure_total = [services.daily_energy_expenditure(i, days, j) for i, j in zip(['week', 'month', 'total'], [weight_change_week, weight_change_month, weight_change_total])]

        maintenance_cals, bulk_cals, cut_cals, cut1_cals, cut2_cals, bulk1_cals, bulk2_cals = [services.energy_targets(energy_expenditure_month, monthly_cals, i) for i in [0, 500, -500, -250, -1000, 250, 1000]]

        activity_cals, activity_multiplier, activity_level = [services.activity_data(maintenance_cals, bmr)[i] for i in ["activity_cals", "activity_multiplier", "activity_level"]]

        bodyfats, tag = [5, 10, 15, 17.5, 20, 25, 30] if user_information.gender == "Male" else [10, 15, 20, 25, 30, 35, 40], ['Stage', 'Lean', 'Athletic', 'Average', 'Acceptable', 'Overweight', 'Obese']
        projections_list = [services.body_fat_projections(composition_log, i) for i in bodyfats]

        context = {
            'weight_units': weight_units,
            'start_weight': WeightLog.objects.filter(user=request.user).order_by('date').first(),
            'last_weight_log': recent_weight,
            'composition_logs': composition_log,
            'ffmi': round(ffmi,2),
            'bmi': round(bmi,2),
            'bmr': round(bmr,2),
            'total_cals': f"{total_cals:.0f}",
            'weekly_cals': f"{weekly_cals:.0f}",
            'monthly_cals': f"{monthly_cals:.0f}",
            'total_protein': f"{total_protein:.0f}",
            'weekly_protein': f"{weekly_protein:.0f}",
            'monthly_protein': f"{monthly_protein:.0f}",
            'total_fat': f"{total_fat:.0f}",
            'weekly_fat': f"{weekly_fat:.0f}",
            'monthly_fat': f"{monthly_fat:.0f}",
            'total_carbs': f"{total_carbs:.0f}",
            'weekly_carbs': f"{weekly_carbs:.0f}",
            'monthly_carbs': f"{monthly_carbs:.0f}",
            'weight_change_total': f"{weight_change_total:+.2f}",
            'weight_change_week': f"{weight_change_week:+.2f}",
            'weight_change_month': f"{weight_change_month:+.2f}",
            'energy_expenditure_total': f"{energy_expenditure_total:+.0f}",
            'energy_expenditure_week': f"{energy_expenditure_week:+.0f}",
            'energy_expenditure_month': f"{energy_expenditure_month:+.0f}",
            'maintenance_cals': f"{maintenance_cals:.0f}",
            'bulk_cals': f"{bulk_cals:.0f}",
            'cut_cals': f"{cut_cals:.0f}",
            'cut1_cals': f"{cut1_cals:.0f}",
            'cut2_cals': f"{cut2_cals:.0f}",
            'bulk1_cals': f"{bulk1_cals:.0f}",
            'bulk2_cals': f"{bulk2_cals:.0f}",
            'activity_calories': f"{activity_cals:.0f}",
            'activity_multiplier': f"{activity_multiplier:.2f}",
            'projections': zip(projections_list, bodyfats, tag),
            'activity_level': activity_level,
            'user': "guest" if is_guest(request) else None,
            'data': data,
    }
    else:
        context = {}
    return render(request,
                  'api/home.html',
                  context,
    )

def about(request):
    return render(request,
                  'api/about.html')

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

    #print(data['weight']['labels_28'])
    context = {
        'data': data
    }
    return render(request,
                  'api/graph.html',
                  context
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
    
    return render(request,
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
    
    return render(request,
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
    
    return render(request,
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
    return render(request,
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
