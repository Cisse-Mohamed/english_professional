from django import forms
from .models import DiscussionThread, DiscussionPost


class DiscussionThreadForm(forms.ModelForm):
    """Form for creating and editing discussion threads."""
    
    class Meta:
        model = DiscussionThread
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter thread title',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your question or discussion topic',
                'rows': 6,
                'required': True
            }),
        }
        labels = {
            'title': 'Thread Title',
            'content': 'Description',
        }


class DiscussionPostForm(forms.ModelForm):
    """Form for creating and editing posts (replies to threads)."""
    
    class Meta:
        model = DiscussionPost
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your reply...',
                'rows': 4,
                'required': True
            }),
        }
        labels = {
            'content': 'Your Reply',
        }
