from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_index, name='chat_index'),
    path('<int:thread_id>/', views.chat_thread, name='chat_thread'),
    path('<int:thread_id>/send/', views.send_message, name='send_message'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
]
