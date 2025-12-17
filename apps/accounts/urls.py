from django.urls import path
from . import views

urlpatterns = [
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
