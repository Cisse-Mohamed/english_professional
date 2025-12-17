# Advanced Features Implementation Guide

This document describes the implementation of advanced analytics and enhanced communication features for the Django learning platform.

## 🎯 Features Implemented

### 1. Advanced Analytics & Reporting

#### Student Performance Dashboard
- **Location**: `/analytics/student/<course_id>/`
- **Features**:
  - Quiz score averages with trends over time
  - Assignment grade tracking
  - Lesson completion rates
  - Engagement score (composite metric)
  - Performance trends visualization (Chart.js)
  - Recent quiz submissions history

#### Instructor Analytics Dashboard
- **Location**: `/analytics/instructor/<course_id>/`
- **Features**:
  - Course engagement metrics (total/active students, completion rates)
  - Student progress heatmap showing lesson completion and quiz scores
  - Dropout prediction (students at risk)
  - Activity timeline (last 30 days)
  - Forum activity tracking
  - Export capabilities (CSV)

#### Export Reports
- **Student Performance CSV**: `/analytics/export/students/<course_id>/csv/`
  - Student name, username, email
  - Quiz averages, assignment averages
  - Completion rates, engagement scores
  - Forum activity, last activity timestamp

- **Engagement Report CSV**: `/analytics/export/engagement/<course_id>/csv/`
  - Historical engagement metrics
  - Trends over time
  - At-risk student counts

#### Analytics Models
- `StudentPerformanceSnapshot`: Periodic snapshots for trend analysis
- `CourseEngagementMetrics`: Aggregated course-level metrics
- `StudentActivityLog`: Detailed activity tracking

### 2. Enhanced Communication

#### Announcement System
- **Location**: `/announcements/`
- **Features**:
  - Platform-wide or course-specific announcements
  - Priority levels (Low, Medium, High, Urgent)
  - Email notifications to recipients
  - Pin important announcements
  - Read/unread tracking
  - Automatic email sending via Django signals

#### Chat Enhancements
- **Video Message Support**: Added `video_file` field to Message model
- **Message Types**: Text, Audio, Video
- **Translation Support**:
  - `original_language` field
  - `translated_content` JSON field for storing translations
  - Integration with `deep-translator` library
- **@Mentions**: ManyToMany field for tagging users
- **Reactions**: `MessageReaction` model for emoji reactions

#### Forum Enhancements
- **@Mentions**: Tag users in threads and posts
- **Reactions**: `ForumReaction` model for emoji reactions on threads/posts
- **Thread Features**:
  - Pin threads
  - Lock threads
  - View count tracking
  - Mark posts as solutions

## 📦 Installation & Setup

### 1. Run Migrations

```bash
python manage.py makemigrations analytics announcements chat forum
python manage.py migrate
```

### 2. Generate Initial Analytics Data

```bash
# Generate performance snapshots for all courses
python manage.py generate_performance_snapshots

# Or for a specific course
python manage.py generate_performance_snapshots --course-id 1
```

### 3. Set Up Periodic Tasks (Optional)

For automatic daily analytics generation, set up a cron job or use Django-celery-beat:

```bash
# Daily at 2 AM
0 2 * * * cd /path/to/project && python manage.py generate_performance_snapshots
```

## 🔧 Configuration

### Email Settings (for Announcements)

Add to `settings.py`:

```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@yourplatform.com'
SITE_URL = 'https://yourplatform.com'  # For email links
```

For development, use console backend:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## 📊 Usage Examples

### Analytics

#### Track Student Activity

```python
from apps.analytics.utils import log_student_activity

# Log when a student completes a lesson
log_student_activity(
    student=request.user,
    activity_type='lesson_complete',
    course=course,
    lesson_id=lesson.id
)
```

#### Calculate Performance

```python
from apps.analytics.utils import calculate_student_performance

metrics = calculate_student_performance(student, course)
# Returns: {
#     'quiz_average': 85.5,
#     'assignment_average': 90.0,
#     'completion_rate': 75.0,
#     'engagement_score': 82.5
# }
```

### Chat Translation

```python
from apps.chat.utils import translate_message

# Translate a message
translated = translate_message(
    text="Hello, how are you?",
    target_language='es',  # Spanish
    source_language='en'   # English
)
```

### Mentions

```python
from apps.chat.utils import extract_mentions

# Extract mentioned users from text
text = "Hey @john and @jane, check this out!"
mentioned_users = extract_mentions(text)
# Returns: [<User: john>, <User: jane>]
```

### Announcements

```python
from apps.announcements.models import Announcement

# Create a course announcement
announcement = Announcement.objects.create(
    title="Important: Quiz Tomorrow",
    content="Don't forget about the quiz scheduled for tomorrow at 10 AM.",
    author=instructor,
    scope='course',
    course=course,
    priority='high',
    send_email=True,
    is_pinned=True
)
# Email notifications sent automatically via signal
```

## 🎨 Frontend Integration

### Analytics Charts

The analytics dashboards use Chart.js for visualizations. Make sure to include:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### AJAX for Real-time Updates

```javascript
// Get unread announcement count
fetch('/announcements/api/unread-count/')
    .then(response => response.json())
    .then(data => {
        console.log('Unread announcements:', data.unread_count);
    });

// Mark announcement as read
fetch('/announcements/123/mark-read/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCookie('csrftoken')
    }
});
```

## 🔐 Permissions

### Analytics
- Students: Can view their own performance dashboard
- Instructors: Can view analytics for courses they teach
- Instructors: Can export reports for their courses

### Announcements
- Students: Can view announcements
- Instructors: Can create course-specific announcements
- Staff: Can create platform-wide announcements

## 📝 Database Schema

### New Tables
- `analytics_studentperformancesnapshot`
- `analytics_courseengagementmetrics`
- `analytics_studentactivitylog`
- `announcements_announcement`
- `announcements_announcementread`
- `chat_messagereaction`
- `forum_forumreaction`

### Modified Tables
- `chat_message`: Added video_file, message_type, translations, mentions
- `forum_discussionthread`: Added mentions, pinned, locked, view_count
- `forum_discussionpost`: Added mentions, is_solution

## 🚀 API Endpoints

### Analytics API
- `GET /analytics/api/trends/<course_id>/` - Performance trends
- `GET /analytics/api/engagement/<course_id>/` - Engagement metrics

### Announcements API
- `GET /announcements/api/unread-count/` - Unread count
- `POST /announcements/<id>/mark-read/` - Mark as read

## 🧪 Testing

```python
# Test analytics calculation
from apps.analytics.utils import calculate_student_performance
from apps.courses.models import Course
from apps.accounts.models import User

student = User.objects.get(username='student1')
course = Course.objects.get(id=1)
metrics = calculate_student_performance(student, course)
print(metrics)

# Test announcement creation
from apps.announcements.models import Announcement

announcement = Announcement.objects.create(
    title="Test Announcement",
    content="This is a test",
    author=User.objects.get(username='instructor1'),
    scope='platform',
    priority='medium',
    send_email=False
)
```

## 📚 Additional Resources

- Chart.js Documentation: https://www.chartjs.org/docs/
- Deep Translator: https://deep-translator.readthedocs.io/
- Django Signals: https://docs.djangoproject.com/en/stable/topics/signals/

## 🐛 Troubleshooting

### Migrations Issues
```bash
python manage.py makemigrations --empty analytics
python manage.py makemigrations --empty announcements
```

### Email Not Sending
- Check EMAIL_BACKEND setting
- Verify SMTP credentials
- Check firewall/port settings
- Use console backend for testing

### Chart Not Rendering
- Verify Chart.js CDN is loaded
- Check browser console for errors
- Ensure JSON data is properly formatted

## 🔄 Future Enhancements

- PDF export for reports (using ReportLab or WeasyPrint)
- Real-time notifications using WebSockets
- Advanced filtering and search in analytics
- Predictive analytics using ML models
- Integration with external analytics tools (Google Analytics, Mixpanel)
- Mobile app support for announcements
- Rich text editor for announcements (CKEditor, TinyMCE)
- Announcement scheduling
- A/B testing for course content