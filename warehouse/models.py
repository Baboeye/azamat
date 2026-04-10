from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


# Определяем СНАЧАЛА Section, потом Material
class Section(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Contractor(models.Model):
    TYPE_CHOICES = [('supplier', 'Поставщик'), ('customer', 'Заказчик')]
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contractor_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contact_info = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=255)
    article = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=50, default='м')
    quantity = models.FloatField(default=0, validators=[MinValueValidator(0)])
    min_stock = models.FloatField(default=10)
    image = models.ImageField(upload_to='materials/', blank=True, null=True)
    
    # Цена за единицу измерения (метр, кг, штука и т.д.)
    price_per_unit = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Цена за единицу",
        help_text="Цена за метр, кг или штуку"
    )
    
    # Важно: используем строку 'Section' или убедимся что Section определен выше
    section = models.ForeignKey(
        'Section',  # Используем строку для ленивой загрузки
        on_delete=models.CASCADE, 
        related_name='materials',
        null=True,
        blank=True
    )
    
    contractor = models.ForeignKey(
        'Contractor',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=100, blank=True)
    width = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    composition = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.article})"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock
    
    @property
    def status_class(self):
        if self.quantity <= self.min_stock:
            return 'critical'
        elif self.quantity <= self.min_stock * 2:
            return 'warning'
        return 'good'
    
    @property
    def total_value(self):
        """Общая стоимость материала на складе"""
        return float(self.price_per_unit) * self.quantity
    
    contractor = models.ForeignKey(
        'Contractor',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    color = models.CharField(max_length=100, blank=True)
    width = models.FloatField(null=True, blank=True)
    density = models.FloatField(null=True, blank=True)
    composition = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.article})"
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock
    
    @property
    def status_class(self):
        if self.quantity <= self.min_stock:
            return 'critical'
        elif self.quantity <= self.min_stock * 2:
            return 'warning'
        return 'good'


class Receipt(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='receipts')
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    contractor = models.ForeignKey(Contractor, on_delete=models.SET_NULL, null=True, blank=True)
    document_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.material.quantity += self.quantity
            self.material.save()


class Issue(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='issues')
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    issued_to = models.CharField(max_length=255)
    destination = models.CharField(max_length=255, blank=True)
    purpose = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.material.quantity -= self.quantity
            self.material.save()


class Scrap(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='scraps')
    quantity = models.FloatField(validators=[MinValueValidator(0.01)])
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.material.quantity -= self.quantity
            self.material.save()


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('receipt', 'Приход'),
        ('issue', 'Расход'),
        ('scrap', 'Списание'),
        ('edit', 'Редактирование'),
        ('delete', 'Удаление'),
        ('create', 'Создание'),
    ]
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='audit_logs')
    quantity = models.FloatField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def action_icon(self):
        icons = {
            'receipt': '➕',
            'issue': '➖',
            'scrap': '🗑️',
            'edit': '✏️',
            'delete': '❌',
            'create': '✨'
        }
        return icons.get(self.action, '📝')