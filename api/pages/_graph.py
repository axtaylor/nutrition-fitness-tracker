from ..models import WeightLog, NutritionLog, CompositionLog
from .. import services
from django.shortcuts import render

'''
Graph page for displaying all collected user info

TODO: Fix the graph JS and reopen this URL
'''

def graph(request):

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