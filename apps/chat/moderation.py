import re

BANNED_KEYWORDS = [
    'spam',
    'inappropriate',
    'abuse',
    'badword',
    # Add more keywords as needed
]

def contains_inappropriate_content(text):
    if not text:
        return False
    # Create a regex pattern to match whole words, case-insensitive
    pattern = re.compile(r'\b(' + '|'.join(map(re.escape, BANNED_KEYWORDS)) + r')\b', re.IGNORECASE)
    return bool(pattern.search(text))