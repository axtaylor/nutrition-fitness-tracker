from django.forms import ModelForm
from django import forms
from . import models

class WeightLogForm(ModelForm):
    class Meta:
        model = models.WeightLog
        fields = ['date', 'weight']
        widgets = {
                'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }

class NutritionLogForm(ModelForm):
    class Meta:
        model = models.NutritionLog
        fields = ['date', 'calories', 'protein', 'fat', 'carbs', 'response_html']
        widgets = {
        'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    })
}

class CompositionLogForm(ModelForm):
    class Meta:
        model = models.CompositionLog
        fields = ['date', 'weight', 'calves', 'quads', 'waist', 'bicep', 'hips', 'neck']
        widgets = {
        'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    })
}
        
class TrainingLogForm(ModelForm):
    class Meta:
        model = models.TrainingLog
        fields = ['date']
        widgets = {
        'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    })
}
        
class UserInformationForm(ModelForm):
    class Meta:
        model = models.UserInformation
        fields = ['units', 'height', 'age', 'gender']

