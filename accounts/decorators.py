from django.shortcuts import redirect

def role_required(roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):

            # 🔥 SUPERUSER — ВСЕГДА ДОПУСК
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # ❗ если нет профиля — нет доступа
            if not hasattr(request.user, 'profile'):
                return redirect('/no-access/')

            # ❗ проверка роли
            if request.user.profile.role not in roles:
                return redirect('/no-access/')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
