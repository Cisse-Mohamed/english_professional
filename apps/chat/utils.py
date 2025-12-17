from deep_translator import GoogleTranslator
import re
from django.contrib.auth import get_user_model

User = get_user_model()


def translate_message(text, target_language='en', source_language='auto'):
    """Translate message text to target language"""
    try:
        translator = GoogleTranslator(source=source_language, target=target_language)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return text


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


def format_message_with_mentions(text, mentioned_users):
    """Format message text with clickable mention links"""
    for user in mentioned_users:
        pattern = f'@{user.username}'
        replacement = f'<a href="/accounts/profile/{user.id}/" class="mention">@{user.username}</a>'
        text = text.replace(pattern, replacement)
    
    return text