from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('/dashboard/')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/')

def no_access(request):
    return render(request, 'no_access.html')