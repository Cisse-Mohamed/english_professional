from django import forms
from .models import Submission, Course, Lesson, Assignment

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['file']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'image', 'students']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_file', 'pdf_file', 'order']

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'file']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local'})
