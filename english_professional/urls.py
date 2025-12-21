from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('', include('apps.core.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('courses/', include('apps.courses.urls')),
    path('chat/', include('apps.chat.urls')),
    path('quiz/', include('apps.quiz.urls')),
    path('gamification/', include('apps.gamification.urls')),
    path('forum/', include('apps.forum.urls')),
    path('analytics/', include('apps.analytics.urls')),
    path('announcements/', include('apps.announcements.urls')),
    path('peer-review/', include('apps.peer_review.urls', namespace='peer_review')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
