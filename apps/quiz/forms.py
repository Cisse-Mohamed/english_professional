from django import forms
from django.utils import timezone
from .models import Question, Choice, QuizQuestionAttempt

class QuizTakeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question_attempts = kwargs.pop('question_attempts')
        super().__init__(*args, **kwargs)

        # Dynamically create fields for each question
        for attempt in self.question_attempts:
            question = attempt.question
            field_name = f'question_{question.id}'
            
            if question.question_type == 'multiple_choice':
                self.fields[field_name] = forms.ModelChoiceField(
                    queryset=question.choices.all(),
                    widget=forms.RadioSelect,
                    label=question.text,
                    required=True,
                    empty_label=None,
                )
            elif question.question_type == 'essay':
                self.fields[field_name] = forms.CharField(
                    widget=forms.Textarea(attrs={'rows': 4}),
                    label=question.text,
                    required=False,
                )

    def save(self, submission, question_attempts):
        """
        Process the form data, save attempts, and calculate the score for MCQs.
        Returns the score.
        """
        score = 0
        cleaned_data = self.cleaned_data

        for attempt in question_attempts:
            question = attempt.question
            field_name = f'question_{question.id}'
            answer = cleaned_data.get(field_name)

            if not answer:
                continue

            if question.question_type == 'multiple_choice':
                attempt.selected_choice = answer
                if answer.is_correct:
                    score += 1
                    attempt.is_correct = True
                else:
                    attempt.is_correct = False
            elif question.question_type == 'essay':
                attempt.essay_answer = answer
            
            attempt.save()

        # Update submission score and end time
        submission.mcq_score = score
        submission.end_time = timezone.now()
        submission.save()
        return score

class EssayGradeForm(forms.ModelForm):
    class Meta:
        model = QuizQuestionAttempt
        fields = ['points_earned']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['points_earned'].label = "Points"
        self.fields['points_earned'].widget = forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 100px;'})
