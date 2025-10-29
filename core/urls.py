from django.contrib import admin
from django.urls import path 
from .views import database_view, login_view, logout_view , chatbot_view , chatbot_api

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('database/', database_view, name='database'),
    path('chatbot/', chatbot_view, name='chatbot'),
    path('api/chatbot/', chatbot_api, name='chatbot_api'),
]