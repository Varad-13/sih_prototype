from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('schedule/', schedule, name='schedule'),
    path('add_user/', user_creation, name="onboarding")
]