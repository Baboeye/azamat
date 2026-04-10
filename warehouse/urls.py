from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Материалы
    path('materials/', views.materials, name='materials'),
    path('materials/add/', views.material_add, name='material_add'),
    path('materials/<int:pk>/', views.material_detail, name='material_detail'),
    path('materials/<int:pk>/edit/', views.material_edit, name='material_edit'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    
    # Операции (ИСПРАВЛЕНО: нет дубликатов!)
    path('materials/<int:pk>/receipt/', views.material_receipt, name='material_receipt'),
    path('materials/<int:pk>/issue/', views.material_issue, name='material_issue'),
    path('materials/<int:pk>/scrap/', views.material_scrap, name='material_scrap'),
    
    # Контрагенты
    path('contractors/', views.contractors, name='contractors'),
    path('contractors/add/', views.add_contractor, name='add_contractor'),
    path('contractors/<int:pk>/edit/', views.edit_contractor, name='edit_contractor'),
    path('contractors/<int:pk>/delete/', views.delete_contractor, name='delete_contractor'),
    
    # Склад/Секции
    path('warehouse/', views.warehouse, name='warehouse'),
    path('warehouse/add/', views.add_section, name='add_section'),
    path('warehouse/<int:pk>/delete/', views.delete_section, name='delete_section'),
    
    # Отчеты
    path('reports/', views.reports, name='reports'),
    path('reports/stock/', views.stock_report, name='stock_report'),
    
    # Аудит
    path('audit/', views.audit_log, name='audit_log'),
    
    # API
    path('api/materials/', views.api_materials, name='api_materials'),
    
    # Экспорт
    path('export/materials/excel/', views.export_materials_excel, name='export_materials_excel'),
        path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]