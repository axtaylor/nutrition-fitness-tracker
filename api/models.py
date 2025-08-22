from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
 
class WeightLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date = models.DateField(null=False)

    weight = models.DecimalField(decimal_places=2, max_digits=12, null=False, default=0)

    class Meta():
        ordering = ["user", "-date"]

class NutritionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date = models.DateField(null=False)

    calories = models.IntegerField(null=False, default=0)
    protein = models.IntegerField(null=False, default=0)
    fat = models.IntegerField(null=False, default=0)
    carbs = models.IntegerField(null=False, default=0)

    class Meta():
        ordering = ["user", "-date"]


class CompositionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date = models.DateField(null=False)
    bodyfat = models.DecimalField(decimal_places=2, max_digits=6)
    lean_mass = models.DecimalField(decimal_places=2, max_digits=6,null=True)
    fat_mass = models.DecimalField(decimal_places=2, max_digits=6, null=True)

    weight = models.DecimalField(decimal_places=2, max_digits=6, null=False, default=0)
    height = models.DecimalField(decimal_places=2, max_digits=6, null=False, default=0)

    calves = models.DecimalField(decimal_places=2, max_digits=6, null=False,default=0)
    quads = models.DecimalField(decimal_places=2, max_digits=6, null=False, default=0)
    waist = models.DecimalField(decimal_places=2, max_digits=6, null=False, default=0)
    bicep = models.DecimalField(decimal_places=2, max_digits=6, null=False, default=0)
    hips = models.DecimalField(decimal_places=2, max_digits=6, null=False, default=0)
    neck = models.DecimalField(decimal_places=2, max_digits=6, null=False, default=0)

    class Meta():
        ordering = ["user", "-date"]

class TrainingLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    date = models.DateField(null=False)

    class Meta():
        ordering = ["user", "-date"]

class UserInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, primary_key=True)
    height = models.DecimalField(decimal_places=2, max_digits=12, null=False)
    age = models.IntegerField(null=False, default=0)
    gender = models.CharField(null=False,
                              max_length=12,
                              default="Male",
                              choices=[("Male", "Male"),
                                       ("Female", "Female"),
                                    ])
    units = models.CharField(null=False,
                             max_length=12,
                             default="Imperial",
                             choices=[
                                      ("Imperial", "Imperial"),
                                      ("Metric", "Metric"),
                                    ])



