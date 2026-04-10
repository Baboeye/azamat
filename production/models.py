# production/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from warehouse.models import Material  # Импорт существующей модели материалов


class ProductCategory(models.Model):
    """Категории спецодежды по климату/сезону"""
    CLIMATE_CHOICES = [
        ('cold', 'Холодный климат (зима)'),
        ('moderate', 'Умеренный климат (демисезон)'),
        ('hot', 'Жаркий климат (лето)'),
        ('extreme', 'Экстремальные условия'),
    ]
    
    name = models.CharField(max_length=100)
    climate_type = models.CharField(max_length=20, choices=CLIMATE_CHOICES)
    description = models.TextField(blank=True)
    temperature_range = models.CharField(max_length=50, help_text="Например: от -40°C до -20°C")
    
    class Meta:
        verbose_name = 'Категория спецодежды'
        verbose_name_plural = 'Категории спецодежды'
        ordering = ['climate_type', 'name']
    
    def __str__(self):
        return f"{self.get_climate_type_display()} — {self.name}"


class ProductTemplate(models.Model):
    """Шаблон/модель спецодежды (нефтяник)"""
    PROTECTION_LEVELS = [
        ('basic', 'Базовая защита'),
        ('standard', 'Стандартная защита'),
        ('high', 'Повышенная защита'),
        ('max', 'Максимальная защита'),
    ]
    
    name = models.CharField(max_length=255, help_text="Например: Костюм нефтяника зимний")
    article = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='templates')
    protection_level = models.CharField(max_length=20, choices=PROTECTION_LEVELS, default='standard')
    description = models.TextField(blank=True)
    
    # Характеристики
    weight_kg = models.FloatField(validators=[MinValueValidator(0)], help_text="Вес комплекта в кг")
    sizes_available = models.CharField(max_length=255, default="44-46, 48-50, 52-54, 56-58, 60-62")
    colors_available = models.CharField(max_length=255, default="Темно-синий, Оранжевый, Красный")
    
    # Изображения
    image = models.ImageField(upload_to='products/templates/', blank=True, null=True)
    technical_drawing = models.ImageField(upload_to='products/drawings/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = 'Шаблон изделия'
        verbose_name_plural = 'Шаблоны изделий'
    
    def __str__(self):
        return f"{self.article} — {self.name}"


class ProductMaterialRequirement(models.Model):
    """Нормы расхода материалов на единицу продукции"""
    product_template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name='material_requirements')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='used_in_products')
    quantity_per_unit = models.FloatField(
        validators=[MinValueValidator(0.01)],
        help_text="Количество материала на одно изделие"
    )
    waste_percent = models.FloatField(default=5, help_text="Норма отходов в %")
    notes = models.TextField(blank=True, help_text="Особенности раскроя, расположение деталей")
    
    class Meta:
        unique_together = ['product_template', 'material']
        verbose_name = 'Норма расхода материала'
        verbose_name_plural = 'Нормы расхода материалов'
    
    def __str__(self):
        return f"{self.product_template.name}: {self.material.name} — {self.quantity_per_unit}{self.material.unit}"
    
    @property
    def total_required_per_unit(self):
        """Общее количество с учетом отходов"""
        return self.quantity_per_unit * (1 + self.waste_percent / 100)


class Product(models.Model):
    """Готовая продукция на складе"""
    STATUS_CHOICES = [
        ('in_production', 'В производстве'),
        ('quality_check', 'Проверка качества'),
        ('ready', 'Готов к отгрузке'),
        ('shipped', 'Отгружен'),
    ]
    
    template = models.ForeignKey(ProductTemplate, on_delete=models.CASCADE, related_name='products')
    batch_number = models.CharField(max_length=50, unique=True, help_text="Номер партии производства")
    
    # Параметры конкретного изделия
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Производство
    quantity_produced = models.PositiveIntegerField(default=1)
    production_date = models.DateField()
    produced_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='produced_products')
    
    # Склад
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_production')
    warehouse_location = models.CharField(max_length=50, blank=True, help_text="Место хранения на складе готовой продукции")
    
    # Себестоимость (рассчитывается автоматически на основе цен материалов)
    material_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Наценка и цена продажи
    markup_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=20.00,
        verbose_name="Наценка %",
        help_text="Процент наценки на готовую продукцию"
    )
    selling_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Цена продажи за штуку",
        help_text="Цена с учетом наценки"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-production_date', 'batch_number']
        verbose_name = 'Готовая продукция'
        verbose_name_plural = 'Готовая продукция'
    
    def __str__(self):
        return f"{self.template.name} (р.{self.size}, {self.color}) — Партия {self.batch_number}"
    
    def calculate_cost(self):
        """Расчет себестоимости на основе использованных материалов с их ценами"""
        total_material_cost = 0
        
        # Считаем стоимость всех использованных материалов
        for consumption in self.material_consumptions.select_related('material').all():
            # Получаем цену материала за единицу
            material_price = float(consumption.material.price_per_unit) if consumption.material.price_per_unit else 0
            # Считаем стоимость использованного количества (с учетом отходов)
            material_cost = material_price * float(consumption.quantity_used)
            total_material_cost += material_cost
        
        self.material_cost = total_material_cost
        # Общая себестоимость = материалы + работа
        self.total_cost = total_material_cost + float(self.labor_cost)
        
        # Расчет цены продажи с наценкой
        markup_multiplier = 1 + (float(self.markup_percent) / 100)
        self.selling_price = float(self.total_cost) * markup_multiplier
        
        self.save(update_fields=['material_cost', 'total_cost', 'selling_price'])
        return self.total_cost
    
    @property
    def profit_per_unit(self):
        """Прибыль за единицу продукции"""
        return float(self.selling_price) - float(self.total_cost)
    
    @property
    def total_profit(self):
        """Общая прибыль за всю партию"""
        return self.profit_per_unit * self.quantity_produced
    
    @property
    def total_revenue_potential(self):
        """Потенциальная выручка за всю партию"""
        return float(self.selling_price) * self.quantity_produced
    
    def get_available_for_shipment(self):
        """Получить количество доступное для отгрузки"""
        from django.db.models import Sum
        shipped = self.shipments.aggregate(total=Sum('quantity'))['total'] or 0
        return self.quantity_produced - shipped


class MaterialConsumption(models.Model):
    """Фактический расход материалов при производстве"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='material_consumptions')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_required = models.FloatField(help_text="Требовалось по норме")
    quantity_used = models.FloatField(help_text="Фактически использовано")
    quantity_waste = models.FloatField(default=0, help_text="Отходы/брак")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Расход материала'
        verbose_name_plural = 'Расход материалов'


class ProductShipment(models.Model):
    """Отгрузка готовой продукции"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shipments')
    quantity = models.PositiveIntegerField()
    shipped_to = models.ForeignKey('warehouse.Contractor', on_delete=models.SET_NULL, null=True, limit_choices_to={'contractor_type': 'customer'})
    shipment_date = models.DateField()
    document_number = models.CharField(max_length=100, blank=True)
    shipped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-shipment_date']