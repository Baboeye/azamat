from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from warehouse import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 auth
    path('', include('accounts.urls')),   # ТОЛЬКО login / logout

    # 📊 dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # 📦 warehouse — С ПРЕФИКСОМ
    path('', include('warehouse.urls')),
    path('production/', include('production.urls')),
]

# Serve media files in both DEBUG and PRODUCTION
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# IMPORTANT: WhiteNoise handles static files in production
# In development, Django serves them via DEBUG=True
