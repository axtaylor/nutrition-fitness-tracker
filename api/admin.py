from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from . import models

# Register your models here.
admin.site.register(models.WeightLog)
admin.site.register(models.NutritionLog)
admin.site.register(models.CompositionLog)
admin.site.register(models.TrainingLog)
admin.site.register(models.UserInformation)
admin.site.register(models.AIOverviewCache)

'''
DB link UserInfo and User
'''

class AccountInLine(admin.StackedInline):
    model = models.UserInformation 
    can_delete = False
    verbose_name_plural = 'Information'

class CustomizedUserAdmin(UserAdmin):
    inlines = (AccountInLine, )

admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)
