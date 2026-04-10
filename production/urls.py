# production/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Дашборд
    path('', views.product_dashboard, name='production_dashboard'),
    
    # Готовая продукция
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/create/', views.production_order_create, name='production_order_create'),
    
    # Шаблоны/Модели
    path('templates/', views.template_list, name='template_list'),
    path('templates/<int:pk>/', views.template_detail, name='template_detail'),
    path('templates/create/', views.template_create, name='template_create'),
    path('templates/<int:template_pk>/requirements/add/', views.requirement_add, name='requirement_add'),
    
    # API
    path('api/check-materials/', views.api_check_materials, name='api_check_materials'),
    
    # Отчеты
    path('reports/', views.reports_production, name='production_reports'),
    path('products/<int:product_pk>/ship/', views.product_shipment_create, name='product_shipment_create'),
    path('categories/create/', views.category_create, name='category_create'),
     path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('products/<int:pk>/set-ready/', views.product_set_ready, name='product_set_ready'),
    path('reports/revenue/', views.monthly_revenue_report, name='monthly_revenue'),
]