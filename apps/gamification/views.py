from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserPoints

class LeaderboardView(LoginRequiredMixin, ListView):
    model = UserPoints
    template_name = 'gamification/leaderboard.html'
    context_object_name = 'rankings'

    def get_queryset(self):
        return UserPoints.objects.select_related('user').order_by('-total_points')[:20]
