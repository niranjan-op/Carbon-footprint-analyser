from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            messages.success(request, f"Welcome, {username}! You are now logged in.")
            return redirect(next_url)
        else:
            error_message = 'Invalid Username or Password'
            return render(request, 'login/login.html', {'error': error_message})
    return render(request, "login/login.html")

@login_required
def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('home')
    return render(request, 'logout/logout.html')