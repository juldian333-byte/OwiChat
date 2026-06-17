from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import UserProfile
from chat.models import Conversation

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return render(request, 'users/register.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        
        login(request, user)
        return redirect('chat:chat_list')

    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat:chat_list')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})

    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required(login_url='users:login')
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user=user)
    
    is_friend = False
    if request.user.is_authenticated:
        conversation = Conversation.objects.filter(
            conversation_type='private',
            participants=request.user
        ).filter(participants=user)
        is_friend = conversation.exists()
    
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'profile': profile,
        'is_friend': is_friend
    })

@login_required(login_url='users:login')
def edit_profile(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        profile.phone = request.POST.get('phone', '')
        profile.bio = request.POST.get('bio', '')
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        return redirect('users:user_profile', username=request.user.username)
    
    return render(request, 'users/edit_profile.html', {'profile': profile})

@login_required(login_url='users:login')
def search_users(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = User.objects.filter(username__icontains=query).exclude(id=request.user.id)[:10]
    
    return render(request, 'users/search.html', {'results': results, 'query': query})
