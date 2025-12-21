from django.urls import path, re_path
from . import views

app_name = 'videoconference'

urlpatterns = [
    path('', views.index, name='video_index'),
    # Main video session room
    path('<str:session_slug>/', views.room, name='room'),
    # Breakout room within a video session
    path('<str:session_slug>/breakout/<str:breakout_slug>/', views.room, name='breakout_room'),

    # Instant Session URLs
    path('instant/create/', views.create_instant_session, name='create_instant_session'),
    path('instant/<slug:slug>/', views.join_instant_session, name='join_instant_session'),

    # API endpoints for Breakout Room management
    path('api/breakout-rooms/create/', views.create_breakout_room, name='create_breakout_room'),
    path('api/breakout-rooms/list/', views.list_breakout_rooms, name='list_breakout_rooms'),
    path('api/breakout-rooms/assign/', views.assign_participant_to_breakout_room, name='assign_participant_to_breakout_room'),

    # API endpoints for Recording management
    path('api/recording/start/', views.start_recording, name='start_recording'),
    path('api/recording/stop/', views.stop_recording, name='stop_recording'),
    path('api/recordings/list/', views.list_recordings, name='list_recordings'),

    # API endpoints for Attendance management
    path('api/attendance/list/', views.list_attendance, name='list_attendance'),
]
