from ..models import WeightLog, NutritionLog, CompositionLog, TrainingLog, UserInformation
from ..forms import WeightLogForm, NutritionLogForm, CompositionLogForm, TrainingLogForm, UserInformationForm
from .. import services
from ..user_validator import profile_exists, is_guest

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError

'''
Logbooks

TODO: Training log not yet implemented
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


'''
The composition log calculates LBM, FM, and BF% based on the units entered on the log
When a post request is sent, the information is computed here, then the information is saved to the DB

'''
def _complete_composition_log(request, composition_log):

    try:
        gender = (
            UserInformation.objects.filter(user=request.user).first().gender
        )
        units = (
            UserInformation.objects.filter(user=request.user).first().units
        )
        composition_log.height = (
            UserInformation.objects.get(user=request.user).height
        )
        composition_log.bodyfat = (
            services.body_composition(gender, composition_log, units)['body_fat']
        )
        composition_log.lean_mass = (
            services.body_composition(gender, composition_log, units)['lean_mass']
        )
        composition_log.fat_mass = (
            services.body_composition(gender, composition_log, units)['fat_mass']
        )

    except UserInformation.DoesNotExist:
        messages.error(request, "Check Profile Configuration")
        raise



def generic_log_view(request, log_type):

    if not profile_exists(request):
        return (
            redirect('home')
        )
    
    config = LOG_CONFIGS[log_type]

    # All logs for the log_type specified
    queryset = (
        config['model'].objects.filter(user=request.user)
    )
    
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


def generic_add_log(request, log_type):

    if not profile_exists(request):
        return (
            redirect('home')
        )
    
    config = LOG_CONFIGS[log_type]

    # Send appropriate form for log type
    form_class = config['form']
    
    if request.method == 'POST':

        # POST completed by guest get sent to main log page
        if is_guest(request):
            return (
                redirect(config['redirect_name'])
            )

        form = form_class(request.POST)

        if form.is_valid():
            log_obj = form.save(commit=False) # Do not immediately commit to DB
            log_obj.user = request.user

            # Only composition log - need to convert entered information into BF, LBM, FM
            if config['pre_save']:

                try:
                    config['pre_save'](request, log_obj) # call complete lambda

                except Exception: # Should never be reached
                    context = {"add_form": form_class(), "type": "add"}
                    return (
                        render(request, 'api/add_edit.html', context)
                    )
            
            try:
                log_obj.save() # Commit to DB with completed info from lambda call
            except IntegrityError:
                messages.error(request, 'A log entry for this date already exists.')
                return (
                    redirect(f"{config['redirect_name']}")
                )

            return redirect(config['redirect_name'])
    

    context = {
        "add_form": form_class(),
        "type": "add",
        'log_info': config['redirect_name'],
    }

    return (
        render(request, 'api/add_edit.html', context)
    )


def generic_edit_log(request, log_type, uuid_key):

    config = LOG_CONFIGS[log_type]

    # Grab specific log based on UUID
    obj = (
        get_object_or_404(config['model'], id=uuid_key, user=request.user)
    )
    
    if obj.user != request.user:
        return redirect(config['redirect_name'])
    

    if request.method == "POST":

        if is_guest(request):
            return (
                redirect(config['redirect_name'])
            )

        form = (
            config['form'](request.POST, instance=obj)
        )

        if form.is_valid():

            log_obj = form.save(commit=False)
            log_obj.user = request.user
            
            if config['pre_save']:

                try:
                    config['pre_save'](request, log_obj)

                except Exception:
                    context = {'edit_form': config['form'](instance=obj)}
                    return render(request, 'api/add_edit.html', context)
            
            try:
                log_obj.save() 
            except IntegrityError:
                messages.error(request, 'A log entry for this date already exists.')
                return (
                    redirect(f"edit{config['redirect_name']}")
                )
            
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



def generic_delete_log(request, log_type, uuid_key):

    config = LOG_CONFIGS[log_type]

    obj = (
        get_object_or_404(config['model'], id=uuid_key, user=request.user)
    )
    
    if obj.user != request.user:
        return (
            redirect(config['redirect_name'])
        )
    
    if request.method == "POST":

        if is_guest(request):
            return redirect(config['redirect_name']) 
        
        obj.delete()
        return redirect(config['redirect_name'])
    
    context = {'deleting_object': obj}

    return render(
        request,
        'api/delete.html',
        context
    )

