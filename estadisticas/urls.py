from django.urls import path
from .views import *

urlpatterns = [
    path('devolverTopEvaluadores/', devolverTopEvaluadores, name="devolverTopEvaluadores"),
]
