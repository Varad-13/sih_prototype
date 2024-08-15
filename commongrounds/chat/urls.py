# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<int:chat_id>/', views.chat_view, name='chat_view'),
    path('<int:chat_id>/send/', views.send_message, name='send_message'),
    path('<int:message>/response/', views.get_response, name='get_response')
]
