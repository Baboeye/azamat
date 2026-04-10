from django.contrib import admin
from .models import Material, Contractor, Section, Receipt, Issue, Scrap, AuditLog


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'unit', 'quantity', 'min_stock', 'section', 'is_low_stock')
    list_filter = ('section', 'contractor', 'created_at')
    search_fields = ('name', 'article', 'description')


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('material', 'quantity', 'contractor', 'created_at', 'created_by')
    list_filter = ('created_at', 'material')
    date_hierarchy = 'created_at'


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('material', 'quantity', 'issued_to', 'destination', 'created_at')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(Scrap)
class ScrapAdmin(admin.ModelAdmin):
    list_display = ('material', 'quantity', 'reason', 'created_at')
    list_filter = ('created_at',)


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contractor_type', 'contact_info')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'material', 'quantity', 'user', 'created_at')
    list_filter = ('action', 'created_at')
    readonly_fields = ('created_at',)