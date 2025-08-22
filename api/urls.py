from django.urls import path
from . import views

urlpatterns = [

    path('', views.login_page, name="login"),
    path('logout/', views.logout_page, name="logout"),
    path('register/', views.register_user, name="register"),
    path("guest_login/", views.guest_login, name="guest_login"),

    path('about/', views.about, name="about"),
    path('home/', views.home, name="home"),
    path('graph/', views.graph, name="graph"),
    path('profile/', views.user_profile, name="profile"),
    path('addprofile', views.register_profile, name="addprofile"),

    path('weightlog/', views.weight_log, name="weightlog"),
    path('addweightlog/', views.add_log, name="addweightlog"),
    path('editweightlog/<uuid:uuid_key>/', views.edit_log, name="editweightlog"),
    path('deleteweightlog/<uuid:uuid_key>/', views.delete_log, name="deleteweightlog"),

    path('nutritionlog/', views.nutrition_log, name="nutritionlog"),
    path('addnutritionlog/', views.add_nutrition_log, name="addnutritionlog"),
    path('editnutritionlog/<uuid:uuid_key>/', views.edit_nutrition_log, name="editnutritionlog"),
    path('deletenutritionlog/<uuid:uuid_key>/', views.delete_nutrition_log, name="deletenutritionlog"),

    path('compositionlog/', views.composition_log, name="compositionlog"),
    path('addcompositionlog/', views.add_composition_log, name="addcompositionlog"),
    path('editcompositionlog/<uuid:uuid_key>/', views.edit_composition_log, name="editcompositionlog"),
    path('deletecompositionlog/<uuid:uuid_key>/', views.delete_composition_log, name="deletecompositionlog"),

    path('traininglog/', views.training_log, name="traininglog"),
    path('addtraininglog/', views.add_training_log, name="addtraininglog"),
    path('edittraininglog/<uuid:uuid_key>/', views.edit_training_log, name="edittraininglog"),
    path('deletetraininglog/<uuid:uuid_key>/', views.delete_training_log, name="deletetraininglog"),

]