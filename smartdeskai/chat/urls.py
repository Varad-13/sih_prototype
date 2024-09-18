# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<int:chat_id>/', views.chat_view, name='chat'),
    path('<int:chat_id>/response/', views.get_response, name='get_response'),
    path('new/', views.create_chat, name='create_chat')
]
