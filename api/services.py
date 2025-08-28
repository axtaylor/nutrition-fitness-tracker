import math
import datetime
from django.db.models import Avg
from decimal import Decimal

def units(user_units) -> dict[str, str]:
    try:
        return {
            "height": " Inches",
            "weight": " Lbs",
        } if user_units == "Imperial" else {
            "height": "cm",
            "weight": "kg"
        }
    except (Exception, AttributeError): 
        return {
            "height": "",
            "weight": ""
        }

def body_composition(gender_input, composition_data) -> dict[float, float, float]:
    try:
        if gender_input == "Male":
            bf = 86.010*math.log10(composition_data.waist-composition_data.neck)-70.041*math.log10(composition_data.height)+36.76
        else:
            bf = 163.205*math.log10(composition_data.waist+composition_data.hips-composition_data.neck)-97.684*math.log10(composition_data.height)-78.387

        lean_mass, fat_mass = float(composition_data.weight)-(float(composition_data.weight)*((bf/100))), float(composition_data.weight)*(bf/100)
        return {
            'body_fat': bf,
            'lean_mass': lean_mass,
            'fat_mass': fat_mass,
        }
    except (Exception, ValueError):
        return {
            'body_fat': 0,
            'lean_mass': 0,
            'fat_mass': 0,
        }

def body_fat_projections(composition_log, bf) -> float:
    try:
        return round(float(composition_log.lean_mass)/(1-(bf/100)), 2)
    
    except Exception:
        return 0

def ffmi(composition_log, queryset_info) -> float:
    try:
        lean_mass, height, units = float(composition_log.weight-(composition_log.weight*((composition_log.bodyfat/100)))), float(composition_log.height), str(queryset_info.units)
        weight_multiplier, height_multiplier = 0.453592 if units == "Imperial" else 1, 0.0254 if units == "Imperial" else 1
        ffmi = (lean_mass*weight_multiplier)/(((height*height_multiplier))**2)
        ffmi_normalized = ffmi+(6.3*(1.8-(height*height_multiplier)))
        return ffmi_normalized
    
    except (Exception, ZeroDivisionError):  
        return 0
    
def days_logged(weight_log) -> int:
    try:
        return ((list(weight_log)[0].date - list(weight_log)[-1].date).days)+1
    
    except Exception:  
        return 0
    
def bmi(last_weight_log, queryset_info) -> float:
    try:
        weight, height, units = float(last_weight_log.weight), float(queryset_info.height), str(queryset_info.units)
        return ((weight/(height**2))*703) if units == "Imperial" else (weight/(height**2))
    
    except (Exception):
        return 0

def bmr(last_weight_log, queryset_info) -> float:
    try:
        weight, height, age, gender, units = float(last_weight_log.weight), float(queryset_info.height), float(queryset_info.age), str(queryset_info.gender), str(queryset_info.units)
        weight_multiplier, height_multiplier = 0.453592 if units == "Imperial" else 1, 2.54 if units == "Imperial" else 1

        if gender == "Male":
            return (5 + (10*(weight*weight_multiplier))+(6.25*(height*height_multiplier))-(5*age))
        else:
             return (-161 + (10*(weight*weight_multiplier))+(6.25*(height*height_multiplier))-(5*age))
        
    except (Exception):
        return 0

def nutrition_info(days: int, relative_days, nutrition_logs) -> dict[float, float, float, float]:
    try:
        if days == 0:
            return {
            'avg_cals': nutrition_logs.aggregate(avg_calories=Avg('calories'))['avg_calories'] if nutrition_logs.exists() else 0,
            'avg_protein': nutrition_logs.aggregate(avg_protein=Avg('protein'))['avg_protein'] if nutrition_logs.exists() else 0,
            'avg_fat': nutrition_logs.aggregate(avg_fat=Avg('fat'))['avg_fat'] if nutrition_logs.exists() else 0,
            'avg_carbs': nutrition_logs.aggregate(avg_carbs=Avg('carbs'))['avg_carbs'] if nutrition_logs.exists() else 0,
        }
        elif days == 7 or days == 28:
            
            if days == 28: # Monthly data used to make predictions, so ensure not out of sync with weight
                if abs(((list(relative_days)[0].date) - (list(nutrition_logs)[0].date)).days) > days:
                    return {
                        'avg_cals': 0.0,
                        'avg_protein': 0.0,
                        'avg_fat': 0.0,
                        'avg_carbs': 0.0,
                    }
            
            log = list(nutrition_logs)[:days]
            valid_dates, start_sequence = [log[0].date], log[0].date

            for entry in log[1:]:
                difference = (start_sequence - entry.date).days
                if difference < days:
                    valid_dates.append(entry.date)
                elif difference >= days:
                    break

            valid_cals, valid_protein, valid_fat, valid_carbs = zip(
                *[(i.calories, i.protein, i.fat, i.carbs) for i in log if i.date in valid_dates]
            ) or ([], [], [], [])

            return {
                'avg_cals': sum(valid_cals)/len(valid_cals),
                'avg_protein': sum(valid_protein)/len(valid_protein),
                'avg_fat': sum(valid_fat)/len(valid_fat),
                'avg_carbs': sum(valid_carbs)/len(valid_carbs),
            }
    except (Exception):
        return {
            'avg_cals': 0.0,
            'avg_protein': 0.0,
            'avg_fat': 0.0,
            'avg_carbs': 0.0,
        }

def daily_energy_expenditure(type: str, days: int, weight_change: float) -> float:
    try:
        if type == 'week':
            weight = float(weight_change)
        elif type == 'month': 
            weight = (float(weight_change)/4) 
        elif type == 'total':
            weight = (float(weight_change)/(days/7)) if (days > 0) else 0
        return weight*500 if abs(weight*500) > 0 else 0
    except Exception:  
        return 0

def energy_targets(energy_expenditure: float, consumed_calories: float, target_expenditure=0):
    try:
        target = round(float(consumed_calories)-float(energy_expenditure)+target_expenditure,2) if float(consumed_calories) > 0 and float(energy_expenditure) else 0
        return 0 if target < 500 or target > 6000 else target
    except Exception:  
        return 0
    
def activity_data(maintenance: float, bmr: float) -> dict[float, float, str]:
    try:
        activity_cals = maintenance-bmr if maintenance>0 else 0
        activity_multiplier = maintenance/bmr if bmr > 0 else 0

        return {
            "activity_cals": activity_cals,
            "activity_multiplier": activity_multiplier,
            "activity_level": "" if activity_multiplier == 0 else "Sedentary" if activity_multiplier < 1.2875 else "Lightly Active" if activity_multiplier < 1.4625 else "Moderately Active" if activity_multiplier < 1.6375 else "Active" if activity_multiplier < 1.8125 else "Very Active",
        }
    except (Exception): 
        return {"activity_cals": 0.0, "activity_multiplier": 0.0, "activity_level": "",}

def as_dataframe(selected_log, type: str) -> dict[datetime.datetime, float]:
    try:
        log = list(selected_log)
        formatted_dates, previous_date = [log[0].date], log[0].date

        for entry in log[1:]:
            current_date = entry.date
            difference = (previous_date - current_date).days
            if difference == 1:
                formatted_dates.append(current_date)
            elif difference > 1:
                for _ in range(1,difference):
                    formatted_dates.append(None)
                formatted_dates.append(current_date)
            previous_date = current_date

        if type in {"weight", "bodyfat", "lean_mass", "fat_mass", "calories", "protein", "carbs", "fat"}:
            attr = type
            formatted_result = [
                next((getattr(j, attr) for j in log if j.date == date), None)
                for date in formatted_dates
            ]

        filled_dates = []
        for i in formatted_dates:
            if i is not None:
                filled_dates.append(i)
            else:
                last = filled_dates[-1] if filled_dates != [] else None
                filled_dates.append(last-datetime.timedelta(days=1))

        formatted_result = formatted_result[::-1]
        filled_result = linear_interpolation_algo(formatted_result) if type == "weight" else []

        return {
            #'unfilled_date': formatted_dates[::-1],
            'date': filled_dates[::-1],
            'result': formatted_result,
            'filled_result': filled_result
        }
    
    except Exception:
        return {
            #'unfilled_date': 0,
            'date': [],
            'result': [],
            'filled_result': [],
        }
    
def linear_interpolation_algo(formatted_result: list) -> list[Decimal]:

    if not formatted_result:
        return []
    
    filled_result = formatted_result.copy()
    n = len(filled_result)
    i = 0

    while i < n:
        if filled_result[i] is not None:
            j = i+1 
            while j < n and filled_result[j] is None:
                j+=1 
            if j < n: 
                start = filled_result[i] 
                end = filled_result[j] 
                gap = j - i 
                for k in range(i+1,j): 
                    progress = Decimal(k-i) / Decimal(gap)
                    interpolation = start + (progress * (end-start)) 
                    filled_result[k] = interpolation 
                i = j 
            else:
                break 
        else:
            i += 1

    return filled_result