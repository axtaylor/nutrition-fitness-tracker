from django.shortcuts import render

def ai_analysis(request):
        
    return render(
        request,
        'api/ai-analysis.html',
    )