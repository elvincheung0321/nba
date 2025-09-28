from django.urls import path
from hub import views

urlpatterns = [
    path('', views.landing, name='landing'),
]
