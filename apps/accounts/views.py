from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import UpdateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import User
from django.db.models import Q

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'accounts/profile_edit.html'
    fields = ['first_name', 'last_name', 'profile_picture', 'background_picture', 'bio']
    success_url = reverse_lazy('dashboard:dashboard')

    def get_object(self):
        return self.request.user

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = User.objects.filter(is_active=True).exclude(pk=self.request.user.pk)
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | 
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query)
            )
        return queryset.order_by('username')

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If instructor, maybe show enrolled courses? For now basic info.
        return context
