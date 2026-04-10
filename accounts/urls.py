from django.urls import path
from .views import login_view, logout_view, no_access

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', logout_view),
    path('no-access/', no_access, name='no_access'),
]
