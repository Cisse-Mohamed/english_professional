from django.urls import path
from . import views

app_name = 'peer_review'

urlpatterns = [
    path('assignment/<int:pk>/', views.PeerReviewAssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignment/<int:assignment_pk>/submit/', views.PeerReviewSubmissionCreateView.as_view(), name='submission_create'),
    path('submission/<int:submission_pk>/review/', views.PeerReviewReviewCreateView.as_view(), name='review_create'),
    path('lesson/<int:lesson_pk>/assignment/create/', views.PeerReviewAssignmentCreateView.as_view(), name='assignment_create'),
]
