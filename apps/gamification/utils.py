from .models import UserPoints, Badge, UserBadge

def check_badges(user):
    """
    Checks if the user qualifies for any badges based on their total points
    and awards them if they don't already have them.
    """
    user_points, _ = UserPoints.objects.get_or_create(user=user)
    
    # Check for point-based badges
    # We filter for badges the user qualifies for
    badges = Badge.objects.filter(points_required__lte=user_points.total_points)
    
    for badge in badges:
        # get_or_create ensures we don't award the same badge twice
        UserBadge.objects.get_or_create(user=user, badge=badge)
