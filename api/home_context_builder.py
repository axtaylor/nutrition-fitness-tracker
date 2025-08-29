from .models import WeightLog, CompositionLog, NutritionLog, UserInformation
from . import views
from . import services

def build_home_context(request):
    if not views.profile_exists(request):
        return None
    
    composition_logs = CompositionLog.objects.filter(user=request.user).order_by('-date')
    nutrition_logs = NutritionLog.objects.filter(user=request.user).order_by('-date')
    weight_logs = WeightLog.objects.filter(user=request.user).order_by('-date')
    composition_log = composition_logs.first()
    user_information = UserInformation.objects.filter(user=request.user).first()

    data_sources, periods = {
        'weight': (weight_logs, 'weight'),
        'bodyfat': (composition_logs, 'bodyfat'),
        'lean_mass': (composition_logs, 'lean_mass'),
        'fat_mass': (composition_logs, 'fat_mass'),
        'calories': (nutrition_logs, 'calories'),
        'protein': (nutrition_logs, 'protein'),
        'carbs': (nutrition_logs, 'carbs'),
        'fat': (nutrition_logs, 'fat'),
    }, [1, 7, 28, 365, 100000]

    data = {}
    for metric, (model, field) in data_sources.items():
        df = services.as_dataframe(model, field)
        labels = df.get('date', [])
        values = df.get('result', [])
        imputed_values = df.get('filled_result', [])
        data[metric] = {}
        for period in periods:
            data[metric][f'labels_{period}'] = labels[-period:] if labels else []
            data[metric][f'data_{period}'] = values[-period:] if values else []   
            data[metric][f'imputed_data_{period}'] = imputed_values[-period:] if imputed_values else [] 

    weight_units = services.units(user_information.units)['weight']
    days = services.days_logged(weight_logs)
    recent_weight = weight_logs.first() if days > 0 else 0
    bmi = services.bmi(recent_weight, user_information)
    bmr = services.bmr(recent_weight, user_information)
    ffmi = services.ffmi(composition_log, user_information)

    nutrition_info = {
        timeframe: services.nutrition_info(timeframe, (weight_logs if days > 0 else 0), nutrition_logs)
        for timeframe in [0, 7, 28]
    }
    
    (total_cals, total_protein, total_fat, total_carbs,
     weekly_cals, weekly_protein, weekly_fat, weekly_carbs,
     monthly_cals, monthly_protein, monthly_fat, monthly_carbs) = [
        nutrition[key] 
        for nutrition in nutrition_info.values() 
        for key in ['avg_cals', 'avg_protein', 'avg_fat', 'avg_carbs']
    ]

    weight_changes = {
        period: data["weight"][period][-1] - data["weight"][period][0] if days > 0 else 0
        for period in ['imputed_data_100000', 'imputed_data_7', 'imputed_data_28']
    }
    weight_change_total, weight_change_week, weight_change_month = weight_changes.values()

    energy_expenditures = {
        period: services.daily_energy_expenditure(period, days, change)
        for period, change in zip(['week', 'month', 'total'], [weight_change_week, weight_change_month, weight_change_total])
    }
    energy_expenditure_week, energy_expenditure_month, energy_expenditure_total = energy_expenditures.values()

    caloric_predictions = {
        target: services.energy_targets(energy_expenditure_month, monthly_cals, target)
        for target in [0, 500, -500, -250, -1000, 250, 1000]
    }
    maintenance_cals, bulk_cals, cut_cals, cut1_cals, cut2_cals, bulk1_cals, bulk2_cals = caloric_predictions.values()

    activity_data = {
        activity_type: services.activity_data(maintenance_cals, bmr)[activity_type]
        for activity_type in ["activity_cals", "activity_multiplier", "activity_level"]
    }
    activity_cals, activity_multiplier, activity_level = activity_data.values()

    intervals = [5, 10, 15, 17.5, 20, 25, 30] if user_information.gender == "Male" else [10, 15, 20, 25, 30, 35, 40]
    projections_list = [
        services.body_fat_projections(composition_log, i)
        for i in intervals
    ]
    projections = zip(projections_list, intervals, ['Stage', 'Lean', 'Athletic', 'Average', 'Acceptable', 'Overweight', 'Obese'])

    return {
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
        'projections': projections,
        'activity_level': activity_level,
        'user': views.is_guest(request),
        'data': data,
    }