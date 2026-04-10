from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        try:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/dashboard/')
            else:
                messages.error(request, 'Неверные учетные данные')
        except Exception as e:
            messages.error(request, f'Ошибка при входе: {str(e)}')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/')

def no_access(request):
    return render(request, 'no_access.html')