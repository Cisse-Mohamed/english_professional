from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    path('', views.announcement_list, name='list'),
    path('<int:announcement_id>/', views.announcement_detail, name='detail'),
    path('create/', views.announcement_create, name='create'),
    path('<int:announcement_id>/mark-read/', views.mark_announcement_read, name='mark_read'),
    path('api/unread-count/', views.unread_announcements_count, name='unread_count'),
]