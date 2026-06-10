import markdown
import json
import hashlib
import os
from dotenv import load_dotenv
from openai import OpenAI
from django.http import HttpResponse
from django.shortcuts import redirect, render
from ..models import UserInformation, AIOverviewCache
from .. import services
from .home import home_context_builder

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_KEY:
    raise ValueError("API_KEY not found. Please check your .env file.")

def ai_analysis(request):    
    return render(
        request,
        'api/ai-analysis.html',
    )

def ai_analysis_overview(request):

    generate = True

    context = (
        home_context_builder.build_home_context(request)
    )

    if context is None:
        return redirect('addprofile')

    user_information = (
        UserInformation.objects.filter(user=request.user).first()
    )

    try:
        gender = user_information.gender
        height = user_information.height
        units_weight = services.units(user_information.units)['weight']
        units_height = services.units(user_information.units)['height']
    except:
        gender = None
        height = None
        units_weight, units_height = None, None
        generate = False

    if not context["last_weight_log"]:
        weight = None
        bmi = None
        bmr = None
        generate = False
    else:
        weight = context["last_weight_log"].weight
        bmi = context["bmi"]
        bmr = context["bmr"]

    if not context["composition_logs"]:
        body_fat = None
        lbm = None
        fat_mass = None
        ffmi = None
    else:
        body_fat = context["composition_logs"].bodyfat
        lbm = context["composition_logs"].lean_mass
        fat_mass = context["composition_logs"].fat_mass
        ffmi = context["ffmi"]


    weight_month_log = [
    {"date": str(date), "weight_lbs": float(round(weight, 2))}
        for date, weight in zip(
            context["data"]['weight']['labels_28'],
            context["data"]['weight']['imputed_data_28']
        )
    ]
    calories_month_log = [
        {"date": str(date), "calories": cals}
        for date, cals in zip(
            context["data"]['calories']['labels_28'],
            context["data"]['calories']['data_28']
        )
    ]

    projection_vars = {}
    for entry, level, tag in context["projections"]:
        projection_vars[f"{level}%_weight"] = entry

    hash_input = json.dumps({
        "weight": str(weight),
        "bmi": str(bmi),
        "bmr": str(bmr),
        "weight_change_total": context["weight_change_total"],
        "weight_change_week": context["weight_change_week"],
        "weight_change_month": context["weight_change_month"],
        "energy_expenditure_total": context['energy_expenditure_total'],
        "energy_expenditure_week": context['energy_expenditure_week'],
        "energy_expenditure_month": context['energy_expenditure_month'],
        "monthly_cals": context["monthly_cals"],
        "monthly_protein": context["monthly_protein"],
        "monthly_fat": context["monthly_fat"],
        "monthly_carbs": context["monthly_carbs"],
        "body_fat": str(body_fat),
        "ffmi": str(ffmi),
    }, sort_keys=True)

    current_hash = hashlib.sha256(hash_input.encode()).hexdigest()

    cache = AIOverviewCache.objects.filter(user=request.user).first()
    if cache and cache.data_hash == current_hash:
        return HttpResponse(cache.response_html)

    if generate:

        system_prompt = """
        You are an AI nutritionist and fitness coach inside "Nutrition Fitness Tracker". You are not a medical professional.
        Omitted fields (None, 0, "", or empty) mean the user has not tracked that category — skip them silently.
        The only data reported by the user is daily weight logs, daily calorie and nutrient logs, and body measurement logs.
        All metrics are calculated using these values for accuracy. Body composition is calculated using US Navy Body Fat measurements.
        Analyze the user's data and provide a comprehensive response containing:
        <h3><strong>Overall Snapshot</strong></h3>
        <p></p>
        <h3><strong>Weight &amp; Calorie Trend Analysis</strong></h3>
        <p></p>
        <h3><strong>Body Composition Summary</strong></h3>
        <p></p>
        <h3><strong>Activity Summary</strong></h3>
        <p></p>
        <h3><strong>Disclaimer</strong></h3>
        <p></p>
        Wrap all text in a <p></p> element.
        Ensure to mention:
        Protein relative to bodyweight (g/lb or g/kg)
        """

        user_data = f"""
        User profile and units: {gender}, {height}{units_height}, {weight}{units_weight}
        BMI: {bmi}
        BMR: {bmr} kcal
        Activity: {context["activity_level"]}, {context["activity_multiplier"]}, {context["activity_calories"]} kcal over BMR)
        Maintenance: {context["maintenance_cals"]} kcal
        Weight change - all-time: {context["weight_change_total"]}{units_weight} | 7d: {context["weight_change_week"]}{units_weight} | 28d: {context["weight_change_month"]}{units_weight}
        Daily cal deficit/surplus - all-time: {context['energy_expenditure_total']} | 7d: {context['energy_expenditure_week']} | 28d: {context['energy_expenditure_month']}
        28-day averages: {context["monthly_cals"]} kcal | {context["monthly_protein"]}g protein | {context["monthly_fat"]}g fat | {context["monthly_carbs"]}g carbs
        Body composition: {body_fat}% BF | LBM: {lbm}{units_weight} | Fat mass: {fat_mass}{units_weight} | FFMI: {ffmi}
        Body Fat percentage projections: {projection_vars}
        JSON Weight Month Log: {weight_month_log}
        JSON Calories Month Log: {calories_month_log} (Monitor for old data)
        """

        print(system_prompt+user_data)
        try:
            client = OpenAI(
              base_url="https://openrouter.ai/api/v1",
              api_key=OPENAI_KEY,
            )

            response = client.chat.completions.create(
            model="google/gemma-4-31b-it:free",
            messages=[
                {
                    "role": "system",      
                    "content": system_prompt
                },
                {
                    "role": "user",         
                    "content": user_data
                }
            ],
            extra_body={"reasoning": {"enabled": True}}
            )

            html_response = markdown.markdown(response.choices[0].message.content)

            AIOverviewCache.objects.update_or_create(
                user=request.user,
                defaults={
                    "response_html": html_response,
                    "data_hash": current_hash,
                }
            )

            return HttpResponse(html_response)
        
        except Exception as e:

            print(f"AI Overview error: {e}")

            if cache:
                return HttpResponse(cache.response_html)
            
            return HttpResponse("<span>AI Overview is currently unavailable. Please try again momentarily.</span>")

    else:
        error_message = "<span>Begin tracking to use AI overview features!</span>"
        return HttpResponse(error_message)
