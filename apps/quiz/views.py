from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.courses.models import Lesson
from .models import Quiz, QuizSubmission

class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quiz/quiz_detail.html'

    def get_queryset(self):
        # Ensure user can only view quizzies for courses they are enrolled in
        # Simpler check for now: allow if lesson is accessible
        return Quiz.objects.all() 
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if user has already submitted
        submission = QuizSubmission.objects.filter(
            student=self.request.user, 
            quiz=self.object
        ).first()
        context['submission'] = submission
        if submission:
            context['questions'] = submission.questions.all()
        return context

class QuizStartView(LoginRequiredMixin, View):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        
        # Check if user has already a submission
        submission, created = QuizSubmission.objects.get_or_create(
            student=request.user, 
            quiz=quiz,
        )

        if not created and submission.end_time:
            messages.info(request, "You have already completed this quiz.")
            return redirect('quiz_detail', pk=pk)

        if created:
            # Select random questions from the bank
            all_questions = list(quiz.question_bank.questions.all())
            import random
            random_questions = random.sample(all_questions, min(len(all_questions), quiz.number_of_questions))
            submission.questions.set(random_questions)
            submission.total_questions = len(random_questions)
            submission.save()

        return redirect('quiz_detail', pk=pk)

import os
import google.generativeai as genai

def get_ai_feedback(question_text, answer_text):
    """
    Gets AI feedback for an essay question.
    """
    try:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"Question: {question_text}\nAnswer: {answer_text}\n\n" \
                 f"Please provide a score from 0 to 100 and feedback for this answer."
        response = model.generate_content(prompt)
        
        # Very basic parsing of the response. 
        # A more robust solution would be to use a structured response from the model.
        parts = response.text.split("Score: ")
        if len(parts) > 1:
            score_part = parts[1].split("\n")[0]
            score = int(score_part)
            feedback = parts[1]
        else:
            score = 0
            feedback = response.text
            
        return feedback, score

    except Exception as e:
        return f"Error getting AI feedback: {e}", 0

class QuizTakeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        
        # Check for existing submission
        submission = QuizSubmission.objects.filter(student=request.user, quiz=quiz).first()
        if not submission or submission.end_time:
             messages.error(request, "You have not started this quiz or have already completed it.")
             return redirect('quiz_detail', pk=pk)

        # Calculate score for multiple choice questions
        score = 0
        
        for question in submission.questions.all():
            if question.question_type == 'multiple_choice':
                selected_choice_id = request.POST.get(f'question_{question.id}')
                if selected_choice_id:
                    try:
                        selected_choice = question.choices.get(pk=selected_choice_id)
                        if selected_choice.is_correct:
                            score += 1
                    except:
                        pass
            elif question.question_type == 'essay':
                answer_text = request.POST.get(f'question_{question.id}')
                if answer_text:
                    from .models import EssayQuestionSubmission
                    essay_submission = EssayQuestionSubmission.objects.create(
                        submission=submission,
                        question=question,
                        answer=answer_text
                    )
                    # Get AI feedback
                    feedback, ai_score = get_ai_feedback(question.text, answer_text)
                    essay_submission.ai_feedback = feedback
                    essay_submission.ai_score = ai_score
                    essay_submission.save()

        
        # Update submission
        submission.score = score
        from django.utils import timezone
        submission.end_time = timezone.now()
        submission.save()

        # Award Points (e.g. 10 points per correct answer)
        points_earned = score * 10
        if points_earned > 0:
            from apps.gamification.models import UserPoints
            from apps.gamification.utils import check_badges
            user_points, created = UserPoints.objects.get_or_create(user=request.user)
            user_points.total_points += points_earned
            user_points.save()
            check_badges(request.user)
        
        messages.success(request, f"Quiz submitted! You scored {score}/{submission.total_questions} on multiple choice questions. Essay questions will be graded separately.")
        return redirect('quiz_detail', pk=pk)

class QuizEssaySubmissionsView(LoginRequiredMixin, View):
    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        if not request.user.is_instructor:
            messages.error(request, "You are not authorized to view this page.")
            return redirect('quiz_detail', pk=pk)
            
        submissions = EssayQuestionSubmission.objects.filter(submission__quiz=quiz)
        context = {
            'quiz': quiz,
            'submissions': submissions
        }
        return render(request, 'quiz/essay_submissions.html', context)

    def post(self, request, pk):
        if not request.user.is_instructor:
            messages.error(request, "You are not authorized to perform this action.")
            return redirect('quiz_detail', pk=pk)

        submission_id = request.POST.get('submission_id')
        score = request.POST.get('score')

        submission = get_object_or_404(EssayQuestionSubmission, pk=submission_id)
        submission.instructor_score = score
        submission.save()
        
        messages.success(request, "Score updated successfully.")
        return redirect('quiz_essay_submissions', pk=pk)


