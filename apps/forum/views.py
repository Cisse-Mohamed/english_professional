from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Max
from django.http import HttpResponseForbidden, JsonResponse
from apps.courses.models import Course
from .models import DiscussionThread, DiscussionPost
from .forms import DiscussionThreadForm, DiscussionPostForm
import os # For accessing environment variables
import json # Potentially for handling structured data

# Placeholder for AI model integration
# In a real application, you would initialize your AI model here,
# e.g., using Google Gemini client library or a direct API call.
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
# if GEMINI_API_KEY:
#     import google.generativeai as genai
#     genai.configure(api_key=GEMINI_API_KEY)
#     model = genai.GenerativeModel('gemini-pro')
# else:
#     print("GEMINI_API_KEY not found. Chatbot will use simulated responses.")


@login_required
def chatbot_query(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        thread_title = request.POST.get('thread_title', 'No Title')
        thread_content = request.POST.get('thread_content', 'No Content')
        posts_content = request.POST.get('posts_content', '') # This will be a single string of all posts

        # Construct a comprehensive prompt for the AI model
        prompt_text = f"""
        You are a helpful assistant for a forum discussion. Your goal is to answer questions based on the provided context of the forum thread.

        Forum Thread Title: {thread_title}

        Forum Thread Content:
        {thread_content}

        Discussion Posts:
        {posts_content}

        User's Question: {user_message}

        Based on the above information, please provide a concise and helpful answer.
        """

        # --- AI Model Integration Placeholder ---
        # In a real scenario, you would make an API call to your AI model here.
        # For example, using Google Gemini:
        # try:
        #     if GEMINI_API_KEY:
        #         response = model.generate_content(prompt_text)
        #         ai_response = response.text
        #     else:
        #         ai_response = f"AI Simulation: I would analyze your question about '{user_message}' within the context of '{thread_title}' and the discussion. For example, if you asked about a specific term, I'd search the thread content and posts for explanations. (API Key Missing)"
        # except Exception as e:
        #     print(f"Error calling AI model: {e}")
        #     ai_response = "I apologize, but I'm having trouble connecting to the AI at the moment."
        
        # Simulated AI response for demonstration
        # This part will be replaced by actual AI model invocation
        if "hello" in user_message.lower() or "hi" in user_message.lower():
            ai_response = "Hello there! How can I assist you with this thread?"
        elif "summary" in user_message.lower() or "summarize" in user_message.lower():
            ai_response = f"This thread, titled '{thread_title}', discusses: {thread_content[:100]}... and has {len(posts_content.split('---POST_SEPARATOR---'))} replies. (This is a simulated summary based on available context.)"
        elif "posts" in user_message.lower():
            ai_response = f"There are several posts in this discussion. The posts cover various aspects related to the main topic. (This is a simulated response.)"
        else:
            ai_response = f"AI Simulation: I've received your question: '{user_message}'. I would typically process this using an AI model by considering the thread title '{thread_title}', the main content, and all replies to provide a relevant answer. Currently, I'm giving a generic response. Please integrate an actual AI model for better results!"

        return JsonResponse({'response': ai_response})
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def forum_list(request, course_id):
    """Display all discussion threads for a course."""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is enrolled in the course or is the instructor
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_instructor = request.user in course.instructors.all()
    
    if not (is_enrolled or is_instructor):
        messages.error(request, "You must be enrolled in this course to view the forum.")
        return redirect('courses:course_detail', pk=course_id)
    
    # Get all threads for this course with post count and last activity
    threads = DiscussionThread.objects.filter(course=course).annotate(
        post_count=Count('posts'),
        last_activity=Max('posts__created_at')
    ).select_related('author').order_by('-updated_at')
    
    # Pagination
    paginator = Paginator(threads, 15)  # 15 threads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'course': course,
        'threads': page_obj,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
    }
    return render(request, 'forum/forum_list.html', context)


@login_required
def thread_detail(request, thread_id):
    """Display a thread and all its posts."""
    thread = get_object_or_404(DiscussionThread.objects.select_related('author', 'course'), id=thread_id)
    course = thread.course
    
    # Check if user is enrolled in the course or is the instructor
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_instructor = request.user in course.instructors.all()
    
    if not (is_enrolled or is_instructor):
        messages.error(request, "You must be enrolled in this course to view this thread.")
        return redirect('courses:course_detail', pk=course.id)
    
    # Get all posts for this thread
    posts = thread.posts.select_related('author').all()
    
    # Pagination for posts
    paginator = Paginator(posts, 20)  # 20 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'thread': thread,
        'posts': page_obj,
        'course': course,
        'is_enrolled': is_enrolled,
        'is_instructor': is_instructor,
    }
    return render(request, 'forum/thread_detail.html', context)


@login_required
def thread_create(request, course_id):
    """Create a new discussion thread."""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is enrolled in the course or is the instructor
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_instructor = request.user in course.instructors.all()
    
    if not (is_enrolled or is_instructor):
        messages.error(request, "You must be enrolled in this course to create threads.")
        return redirect('courses:course_detail', pk=course_id)
    
    if request.method == 'POST':
        form = DiscussionThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.course = course
            thread.author = request.user
            thread.save()
            messages.success(request, "Thread created successfully!")
            return redirect('forum:thread_detail', thread_id=thread.id)
    else:
        form = DiscussionThreadForm()
    
    context = {
        'form': form,
        'course': course,
        'action': 'Create',
    }
    return render(request, 'forum/thread_form.html', context)


@login_required
def thread_edit(request, thread_id):
    """Edit an existing thread."""
    thread = get_object_or_404(DiscussionThread, id=thread_id)
    
    # Only the author or instructor can edit
    if request.user != thread.author and request.user not in thread.course.instructors.all():
        return HttpResponseForbidden("You don't have permission to edit this thread.")
    
    if request.method == 'POST':
        form = DiscussionThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            messages.success(request, "Thread updated successfully!")
            return redirect('forum:thread_detail', thread_id=thread.id)
    else:
        form = DiscussionThreadForm(instance=thread)
    
    context = {
        'form': form,
        'course': thread.course,
        'thread': thread,
        'action': 'Edit',
    }
    return render(request, 'forum/thread_form.html', context)


@login_required
def thread_delete(request, thread_id):
    """Delete a thread."""
    thread = get_object_or_404(DiscussionThread, id=thread_id)
    course_id = thread.course.id
    
    # Only the author or instructor can delete
    if request.user != thread.author and request.user not in thread.course.instructors.all():
        return HttpResponseForbidden("You don't have permission to delete this thread.")
    
    if request.method == 'POST':
        thread.delete()
        messages.success(request, "Thread deleted successfully!")
        return redirect('forum:forum_list', course_id=course_id)
    
    context = {
        'thread': thread,
        'course': thread.course,
    }
    return render(request, 'forum/thread_confirm_delete.html', context)


@login_required
def post_create(request, thread_id):
    """Create a new post (reply to a thread)."""
    thread = get_object_or_404(DiscussionThread, id=thread_id)
    course = thread.course
    
    # Check if user is enrolled in the course or is the instructor
    is_enrolled = course.students.filter(id=request.user.id).exists()
    is_instructor = request.user in course.instructors.all()
    
    if not (is_enrolled or is_instructor):
        messages.error(request, "You must be enrolled in this course to reply.")
        return redirect('courses:course_detail', pk=course.id)
    
    if request.method == 'POST':
        form = DiscussionPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.thread = thread
            post.author = request.user
            post.save()
            
            # Update thread's updated_at timestamp
            thread.save()
            
            messages.success(request, "Reply posted successfully!")
            return redirect('forum:thread_detail', thread_id=thread.id)
    else:
        form = DiscussionPostForm()
    
    context = {
        'form': form,
        'thread': thread,
        'course': course,
    }
    return render(request, 'forum/post_form.html', context)


@login_required
def post_edit(request, post_id):
    """Edit an existing post."""
    post = get_object_or_404(DiscussionPost, id=post_id)
    
    # Only the author can edit their post
    if request.user != post.author:
        return HttpResponseForbidden("You don't have permission to edit this post.")
    
    if request.method == 'POST':
        form = DiscussionPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Reply updated successfully!")
            return redirect('forum:thread_detail', thread_id=post.thread.id)
    else:
        form = DiscussionPostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
        'thread': post.thread,
        'course': post.thread.course,
    }
    return render(request, 'forum/post_form.html', context)


@login_required
def post_delete(request, post_id):
    """Delete a post."""
    post = get_object_or_404(DiscussionPost, id=post_id)
    thread_id = post.thread.id
    
    # Only the author or instructor can delete
    if request.user != post.author and request.user not in post.thread.course.instructors.all():
        return HttpResponseForbidden("You don't have permission to delete this post.")
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Reply deleted successfully!")
        return redirect('forum:thread_detail', thread_id=thread_id)
    
    context = {
        'post': post,
        'thread': post.thread,
        'course': post.thread.course,
    }
    return render(request, 'forum/post_confirm_delete.html', context)
