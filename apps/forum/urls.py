from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Forum list for a course
    path('course/<int:course_id>/', views.forum_list, name='forum_list'),
    
    # Thread operations
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('course/<int:course_id>/new/', views.thread_create, name='thread_create'),
    path('thread/<int:thread_id>/edit/', views.thread_edit, name='thread_edit'),
    path('thread/<int:thread_id>/delete/', views.thread_delete, name='thread_delete'),
    
    # Post operations
    path('thread/<int:thread_id>/reply/', views.post_create, name='post_create'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
]
