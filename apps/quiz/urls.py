from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:pk>/take/', views.QuizTakeView.as_view(), name='quiz_take'),
    path('<int:pk>/start/', views.QuizStartView.as_view(), name='quiz_start'),
]
