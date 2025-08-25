import math
import datetime
from django.db.models import Avg
from decimal import Decimal

def units(user_units) -> dict[str, str]:
    try:
        return {"height": " Inches", "weight": " Lbs"} if user_units == "Imperial" else {"height": "cm", "weight": "kg"}
    except (Exception, AttributeError): 
        return {"height": "", "weight": ""}

def body_composition(gender_input, composition_data) -> dict[float, float, float]:
    try:
        if gender_input == "Male":
            bf = 86.010*math.log10(composition_data.waist-composition_data.neck)-70.041*math.log10(composition_data.height)+36.76
        else:
            bf = 163.205*math.log10(composition_data.waist+composition_data.hips-composition_data.neck)-97.684*math.log10(composition_data.height)-78.387
        lean_mass, fat_mass = float(composition_data.weight)-(float(composition_data.weight)*((bf/100))), float(composition_data.weight)*(bf/100)
        return {'body_fat': bf, 'lean_mass': lean_mass, 'fat_mass': fat_mass}
    except (Exception, ValueError):
        return {'body_fat': 0, 'lean_mass': 0, 'fat_mass': 0}

def body_fat_projections(composition_log, bf) -> float:
    try:
        return round(float(composition_log.lean_mass)/(1-(bf/100)),2)
    except Exception:
        return 0

def ffmi(composition_log, queryset_info) -> float:
    try:
        lean_mass, height, units = float(composition_log.weight-(composition_log.weight*((composition_log.bodyfat/100)))), float(composition_log.height), str(queryset_info.units)
        weight_multiplier = 0.453592 if units == "Imperial" else 1
        height_multiplier =0.0254 if units == "Imperial" else 1
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
        weight_multiplier = 0.453592 if units == "Imperial" else 1
        height_multiplier = 2.54 if units == "Imperial" else 1
        if gender == "Male":
            return ( 5 + (10*(weight*weight_multiplier))+(6.25*(height*height_multiplier))-(5*age))
        else:
             return ( -161 + (10*(weight*weight_multiplier))+(6.25*(height*height_multiplier))-(5*age))
    except (Exception):
        return 0

# Dynamic calories average function that handles time gaps
def average_calories(relative_days, days: int, nutrition_logs) -> float:
    try:
        if days == 0:
            avg = nutrition_logs.aggregate(avg_calories=Avg('calories'))['avg_calories']
            return avg if avg else 0
        elif days == 6 or days == 27:
            if abs(((list(relative_days)[0].date) - (list(nutrition_logs)[0].date)).days) > days:
                return 0 # Weight log out of sync - means calorie information is dated.
            log = list(nutrition_logs)
            valid_dates, start_sequence = [log[0].date], log[0].date
            for entry in log[1:]:
                difference = (start_sequence - entry.date).days
                if difference <= days:
                    valid_dates.append(entry.date) # Only take logged dates within given time range
                elif difference > days:
                    break
            valid_cals = [i.calories for i in log if i.date in valid_dates] 
            return sum(valid_cals)/len(valid_cals)
        else:
            return 0
    except (TypeError):
        return 0

# Dynamic weight change function that handles time gaps
''' Depreciated, replaced with interpolation on a dataframe for better accuracy
def weight_change(days: int, weight_logs) -> float:
    try:
        log = list(weight_logs)
        recent_weight = log[0].weight
        if days == 0: 
            return recent_weight-log[-1].weight
        elif days == 6 or days == 27:
            valid_dates, start_sequence = [log[0].date], log[0].date
            for entry in log[1:]:
                difference = (start_sequence - entry.date).days
                if difference <= days:
                    valid_dates.append(entry.date) # Only take logged dates within given time range
                elif difference > days:
                    break
            return recent_weight - [i.weight for i in log if i.date == valid_dates[-1]][0]
        else:
            return 0
    except Exception:  
        return 0
'''

# Weekly caloric expenditure over three time intervals
def daily_energy_expenditure(type: str, days: int, weight_change: float) -> float:
    try:
        if type == 'week':
            weight = float(weight_change)
        elif type == 'month': 
            weight = (float(weight_change)/4) # ''' (float(weight_change)/(days/7)) if days < 28 and days > 0 else''' 
        elif type == 'total':
            weight = (float(weight_change)/(days/7)) if (days > 0) else 0
        return weight*500 if abs(weight*500) > 0 else 0
    except Exception:  
        return 0

def energy_targets(energy_expenditure: float, consumed_calories: float, target_expenditure=0):
    try:
        target = round(float(consumed_calories)-float(energy_expenditure)+target_expenditure,2) if float(consumed_calories) > 0 and float(energy_expenditure) else 0
        # The initial predictions are volatile, this will restrict the user until they have stabilized.
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

        filled_result = linear_interpolation_algo(formatted_result)

        print(formatted_result if type == "weight" else "")
        print(filled_result if type == "weight" else "")
        
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
    
# In the case of weight tracking, this is going to be more accurate than employing ML
# This could potentially be more accurate than daily tracking for energy targets, since white noise is eliminated.
# Lots of comments to understand this data structure
def linear_interpolation_algo(formatted_result: list) -> list[Decimal]:
    if not formatted_result:
        return []
    filled_result = formatted_result.copy()
    n = len(filled_result)

    i = 0
    while i < n:
        if filled_result[i] is not None:
            j = i+1 # Stop at first, add J as second sequence

            while j < n and filled_result[j] is None:
                j+=1 # Increment J until list over or J is not None
                
            if j < n: # If the loop broke, and Not end of list
                start = filled_result[i] # First non-none
                end = filled_result[j] # Last non none
                gap = j - i # days between

                for k in range(i+1,j): # Iterate all Nones between i+1 and j
                    progress = Decimal(k-i) / Decimal(gap) # Spaces from start/ length of nones
                    interpolation = start + (progress * (end-start)) # 200LBS + 50% * (100-200) = 150 (Interpolation val for midpoint val between 100 and 200)
                    filled_result[k] = interpolation # Fill in the none @ k with the interpolated value
                
                i = j # Set I to the next segment 
            else:
                break # Break if list is over (no interpolation needed)
        else:
            i += 1 #Incase None is the first (should not be reached)

    return filled_result