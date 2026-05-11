from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/chat/',     views.chat_api,         name='chat'),
    path('api/feedback/', views.feedback_api,      name='feedback'),
    path('api/history/',  views.chat_history_api,  name='history'),
    path('api/clear/',    views.clear_chat_api,    name='clear'),
]
