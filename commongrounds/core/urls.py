from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('schedule/', schedule, name='schedule'),
]