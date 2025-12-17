import re
from django.contrib.auth import get_user_model

User = get_user_model()


def extract_mentions(text):
    """Extract @mentions from text and return list of User objects"""
    # Pattern to match @username
    mention_pattern = r'@(\w+)'
    usernames = re.findall(mention_pattern, text)
    
    # Get unique usernames
    usernames = list(set(usernames))
    
    # Find users
    mentioned_users = User.objects.filter(username__in=usernames)
    
    return list(mentioned_users)


def format_text_with_mentions(text, mentioned_users):
    """Format text with clickable mention links"""
    for user in mentioned_users:
        pattern = f'@{user.username}'
        replacement = f'<a href="/accounts/profile/{user.id}/" class="mention">@{user.username}</a>'
        text = text.replace(pattern, replacement)
    
    return text