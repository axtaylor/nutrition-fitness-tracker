import math
import datetime
from django.db.models import Avg
from decimal import Decimal

'''
UNITS

Return the weight and height units as a string to be displayed on the page
'''
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
    
'''
BODY COMPOSITION

Used to complete the composition log after the user enters measurements

unit-agnostic metric/imperial

'''
def body_composition(gender_input, composition_data, units) -> dict[float, float, float]:
    try:
        print(units)
        if units == "Metric":
            multiplier = 0.393701
        else:
            multiplier = 1

        # Male body fat percentage
        if gender_input == "Male":
            bf = (
                86.010*math.log10(
                (float(composition_data.waist)*multiplier)-(float(composition_data.neck)*multiplier)
                )
                -70.041*math.log10(
                float(composition_data.height)*multiplier
                )
                +36.76
            )
        else: # Female body fat percentage
            bf = (
                163.205*math.log10(
                (float(composition_data.waist)*multiplier)+(float(composition_data.hips)*multiplier)-(float(composition_data.neck)*multiplier)
                )
                -97.684*math.log10(
                (float(composition_data.height)*multiplier)
                )
                -78.387
            )
        lean_mass, fat_mass = (
            float(composition_data.weight)-(float(composition_data.weight)*((bf/100))),
            float(composition_data.weight)*(bf/100)
        )
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
    
'''
BODY FAT PROJECTIONS

Used in home context builder

Given the user's lean mass and a target %, bf, the total weight 
at the target body fat % will be calculated.

'''
def body_fat_projections(last_composition_log, target_bf) -> float:
    try:
        return round(float(last_composition_log.lean_mass)/(1-(target_bf/100)), 2)
    except Exception:
        return 0
    
'''
FFMI

Not unit agnostic

Collects lean mass, height, and user units from the given db entry
converts all to metric
computes ffmi and normalizes it

'''
def ffmi(last_composition_log, user_information_log) -> float:
    try:
        lean_mass, height, units = (
            float(last_composition_log.weight-(last_composition_log.weight*((last_composition_log.bodyfat/100)))),
            float(last_composition_log.height),
            str(user_information_log.units)
        )

        weight_multiplier, height_multiplier = (
            0.453592 if units == "Imperial" else 1,
            0.0254 if units == "Imperial" else 1
        )

        ffmi = (
            (lean_mass*weight_multiplier)/(((height*height_multiplier))**2)
        )

        ffmi_normalized = (
            ffmi+(6.3*(1.8-(height*height_multiplier)))
        )

        return ffmi_normalized
    
    except (Exception, ZeroDivisionError):  
        return 0

'''
Total amount of days logged including gaps.

+ 1 since the first day is counted as day 1.

'''
def days_logged(weight_logs) -> int:
    try:
        log = list(weight_logs)
        days = ((log[0].date - log[-1].date).days)+1
        return days
    
    except Exception:  
        return 0

'''
Non unit-agnostic BMI calculation
'''
def bmi(last_weight_log, user_info) -> float:
    try:
        weight, height, units = (
            float(last_weight_log.weight),
            float(user_info.height),
            str(user_info.units)
        )
        return (
            ((weight/(height**2))*703)
            if units == "Imperial" else
            (weight/(height**2))*10000
        )
    
    except (Exception):
        return 0

'''
Non unit agnostic BMR calculation
'''
def bmr(last_weight_log, queryset_info) -> float:
    try:
        weight, height, age, gender, units = (
            float(last_weight_log.weight),
            float(queryset_info.height),
            float(queryset_info.age),
            str(queryset_info.gender),
            str(queryset_info.units)
        )

        weight_multiplier, height_multiplier = (
            0.453592 if units == "Imperial" else 1,
            2.54 if units == "Imperial" else 1
        )

        if gender == "Male":
            return (
                (5 + (10*(weight*weight_multiplier))+(6.25*(height*height_multiplier))-(5*age))
            )
        else:
            return (
                (-161 + (10*(weight*weight_multiplier))+(6.25*(height*height_multiplier))-(5*age))
            )
        
    except (Exception):
        return 0

'''
NUTRITION INFO

Return DAILY Calorie/Carb/Fat/Protein averages for a given time frame

DAILY averages from one MONTH are used to compute caloric predictions,
as such there is a relation check for the dates in the users weight logs.

'''
def nutrition_info(timeframe_to_return: int, weight_logs, nutrition_logs) -> dict[float, float, float, float]:
    try:
        
        
        #TIMEFRAME = 0 -> Return the overall averages for all of the nutrition information
      
        if timeframe_to_return == 0:
            return {
            'avg_cals': nutrition_logs.aggregate(avg_calories=Avg('calories'))['avg_calories'] if nutrition_logs.exists() else 0,
            'avg_protein': nutrition_logs.aggregate(avg_protein=Avg('protein'))['avg_protein'] if nutrition_logs.exists() else 0,
            'avg_fat': nutrition_logs.aggregate(avg_fat=Avg('fat'))['avg_fat'] if nutrition_logs.exists() else 0,
            'avg_carbs': nutrition_logs.aggregate(avg_carbs=Avg('carbs'))['avg_carbs'] if nutrition_logs.exists() else 0,
        }

        # MOVING AVERAGES -> Last 7 or last 28 days
        elif timeframe_to_return == 7 or timeframe_to_return == 28:
            
            # SPECIAL CASE (28)
            # The 28 day moving average for nutrition consumption information is
            # used to return the dynamic caloric predictions based on the 
            # users most recent weight logs. 
            # As such, the data needs to be in sync
            # CONDITION: If the most recent weight log date is >28 days 
            # from the most recent nutrition log, the results will be
            # UNRELIABLE, so the system will return 0 and not generate
            # inaccurate predictions.
            if timeframe_to_return == 28: 

                if abs(((list(weight_logs)[0].date) - (list(nutrition_logs)[0].date)).days) > timeframe_to_return:
                    return {
                        'avg_cals': 0.0,
                        'avg_protein': 0.0,
                        'avg_fat': 0.0,
                        'avg_carbs': 0.0,
                    }
            
            
            # Here, either the 28 day weight and nutrition logs are in sync,
            # Or the 7 day nutrition logs exist
            # It does not matter if the 7 day logs are in sync with 
            # weight, because they are too volatile to use to predict
            # recommended caloric intakes.

            # Given all of the logs, filter the most recent 7/28 objects
            # Sorted [most recent, -> oldest]
            log = list(nutrition_logs)[:timeframe_to_return]

            # 7/28 logs are filtered. But the date gaps may be >7/28        
            valid_dates, start_sequence = (
                [log[0].date],
                log[0].date
            )

            for entry in log[1:]:

                # Check if the date of the most recent entry
                # is less than 7/28 days from each other entry
                # collected in "log"
                difference = (start_sequence - entry.date).days

                # If it is less than 7/28, add to valid dates list
                if difference < timeframe_to_return:
                    valid_dates.append(entry.date)

                # Stop when the log is out of bounds
                elif difference >= timeframe_to_return:
                    break # Break is safe because the DB is sorted by date.


            # {'calories' : nutrition_log_item.calories (Only if this item.date in valid dates)}
            nutrition_data = {
                field: [
                    getattr(entry, field)
                    for entry in log
                    if entry.date in valid_dates
                ]
                for field in ['calories', 'protein', 'fat', 'carbs']
            }

            valid_cals, valid_protein, valid_fat, valid_carbs = nutrition_data.values()

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

'''
PRECURSOR FOR CALORIC PREDICTIONS

This function will determine how many calories the user is 
expending or holding, given their weight change,
over three different time frames.

'''
def daily_energy_expenditure(type: str, days: int, weight_change: float, units: str) -> float:

    # Conversion hardcodes 500calories weekly deficit to 1lb weight loss
    if units == "kg":
        weight_change = float(weight_change) * 2.20462

    try:
        # Receives weight changes list len(7) -> already in weekly
        if type == 'week':
            weight = float(weight_change) 

        # Receives weight changes list len(28) -> must divide by 4 to return weekly
        elif type == 'month': 
            weight = (float(weight_change)/4) 
        
        # Receives weight changes list len(MAX), must divide by total days/7 to return weekly
        elif type == 'total':
            weight = (float(weight_change)/(days/7)) if (days > 0) else 0

        # Weight will be average weekly weight change
        # Weekly weight needed for caloric conversion constant 500.
        return (
            weight*500
            if abs(weight*500) > 0
            else 0
        )
    
    except Exception:  
        return 0

'''
CALORIC PREDICTIONS

Uses monthly moving averages

'''
def energy_targets(daily_energy_expenditure_month: float, daily_consumed_calories_month: float, target_expenditure=0):
    try:

        # Maintenance = daily calories - daily expenditure
        # Gain weight = maintain + GAIN CONSTANT
        #... 
        target = (
            round(float(daily_consumed_calories_month)-float(daily_energy_expenditure_month)+target_expenditure,2)
            if float(daily_consumed_calories_month) > 0 and float(daily_energy_expenditure_month)
            else 0
        )

        # Prevent Exploding predictions
        return (
            0 if target < 500 or target > 6000
            else target
        )
    
    except Exception:  
        return 0
    
'''
ACTIVITY MULTIPLIER

BMR - calories needed to stay alive,, bodily function,, etc

MAINTENANCE - Calories needed to maintain weight given BMR + activity level

'''
def activity_data(maintenance: float, bmr: float) -> dict[float, float, str]:
    try:

        # Excess calories burned by activity
        activity_cals = (
            maintenance-bmr
            if maintenance > 0
            else 0
        )

        # Multiplier 
        activity_multiplier = (
            maintenance/bmr
            if bmr > 0
            else 0
        )

        # Calories, multiplier, semantic level.
        return {
            "activity_cals": activity_cals,
            "activity_multiplier": activity_multiplier,
            "activity_level":  "" if activity_multiplier == 0
                               else "Sedentary" if activity_multiplier < 1.2875
                               else "Lightly Active" if activity_multiplier < 1.4625
                               else "Moderately Active" if activity_multiplier < 1.6375
                               else "Active" if activity_multiplier < 1.8125
                               else "Very Active"
        }
    
    except (Exception): 
        return {
            "activity_cals": 0.0,
            "activity_multiplier": 0.0,
            "activity_level": "",
        }

'''
Create a hashmap dataframe given a log

'''
def as_dataframe(selected_log, type: str) -> dict[datetime.datetime, Decimal, Decimal]:
    try:
        
        # List of log objects sorted by date [recent, ..., oldest]
        log = list(selected_log)

        formatted_dates, previous_date = (
            [log[0].date], log[0].date
        )

        # The dates may have gaps. They need to be filled 
        # With a valid date and an empty value
        for entry in log[1:]:

            # Get the date difference for each entry in the log
            current_date = entry.date
            difference = (previous_date - current_date).days

            # Fill in the gap with none values * days missing
            if difference > 1:
                formatted_dates.extend([None] * (difference-1))

            # Then add the date in its correct place
            formatted_dates.append(current_date)

            # Update previous date marker
            previous_date = current_date


        if type in {
            "weight",
            "bodyfat",
            "lean_mass",
            "fat_mass",
            "calories",
            "protein",
            "carbs",
            "fat"
        }:
            
            # Attribute
            attr = type

            # Log date: log object
            log_date = {j.date: j for j in log}

            # Format the values of the log the same way as formatted dates
            # ex. formatted dates = [04, 03, None, 01]
            # then formatted result = [150, 151, None, 154]
            formatted_result = [
                getattr(log_date.get(date), attr, None) if log_date.get(date) else None
                for date in formatted_dates
            ]


        # Fill in the None dates
        filled_dates = []

        for i in formatted_dates:

            # Add already collected days
            if i is not None:
                filled_dates.append(i)
            
            # If there is None, fill it with the previous day
            # ex. [05, 04, None] -> [05, 04, 03]
            else:

                last = (
                    filled_dates[-1]
                    if filled_dates != []
                    else None
                )

                filled_dates.append(last-datetime.timedelta(days=1))

        # Reverse the list
        # Was counting [recent, ..., oldest] -> [oldest, ..., recent]
        formatted_result = formatted_result[::-1]

        # With weight data, interpolation is safe.
        # This is used to return weight statistics
        # when the user skips some days.
        filled_result = (
            interpolate(formatted_result)
            if type == "weight"
            else []
        )

        return {
            #'unfilled_date': formatted_dates[::-1],
            'date': filled_dates[::-1],  # [oldest, ... recent]
            'result': formatted_result,  # [oldest, ... recent]
            'filled_result': filled_result # [oldest, ... recent]
        }
    
    except Exception:
        return {
            #'unfilled_date': 0,
            'date': [],
            'result': [],
            'filled_result': [],
        }
    

'''
Interpolation for weight (linear)

'''
def interpolate(formatted_result: list) -> list[Decimal]:

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