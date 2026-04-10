# production/forms.py
from django import forms
from .models import (
    ProductTemplate, Product, ProductMaterialRequirement, 
    ProductCategory, ProductShipment
)
from warehouse.models import Material


class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name', 'climate_type', 'description', 'temperature_range']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Костюм рабочий утепленный'}),
            'climate_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'temperature_range': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'от -40°C до -20°C'}),
        }


class ProductTemplateForm(forms.ModelForm):
    class Meta:
        model = ProductTemplate
        fields = [
            'name', 'article', 'category', 'protection_level', 'description',
            'weight_kg', 'sizes_available', 'colors_available', 'image', 'technical_drawing', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'article': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SN-2024-Z-001'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'protection_level': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sizes_available': forms.TextInput(attrs={'class': 'form-control'}),
            'colors_available': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductMaterialRequirementForm(forms.ModelForm):
    class Meta:
        model = ProductMaterialRequirement
        fields = ['material', 'quantity_per_unit', 'waste_percent', 'notes']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantity_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'waste_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ProductionOrderForm(forms.Form):
    """Форма создания заказа на производство"""
    template = forms.ModelChoiceField(
        queryset=ProductTemplate.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Модель спецодежды"
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        label="Количество"
    )
    size = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '48-50'}),
        label="Размер"
    )
    color = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Темно-синий'}),
        label="Цвет"
    )
    production_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Дата производства"
    )
    batch_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Партия №2024-001'}),
        label="Номер партии"
    )
    warehouse_location = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Секция ГП-1'}),
        label="Место хранения"
    )
    markup_percent = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        initial=20.00,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '20.00'
        }),
        label="Наценка %",
        help_text="Процент наценки на готовую продукцию (например: 20 для 20%)"
    )
    labor_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        }),
        label="Стоимость работы",
        help_text="Затраты на работу за всю партию (необязательно)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        template = cleaned_data.get('template')
        quantity = cleaned_data.get('quantity')
        
        if template and quantity:
            errors = []
            warnings = []
            
            for req in template.material_requirements.select_related('material').all():
                total_needed = req.total_required_per_unit * quantity
                available = req.material.quantity
                
                if available < total_needed:
                    errors.append(
                        f"Недостаточно материала '{req.material.name}' (арт. {req.material.article}). "
                        f"Требуется: {total_needed:.2f} {req.material.unit}, "
                        f"Доступно: {available:.2f} {req.material.unit}"
                    )
                elif available < total_needed * 1.2:  # Менее 20% запаса
                    warnings.append(
                        f"Внимание: остаток материала '{req.material.name}' критически низкий после производства"
                    )
            
            if errors:
                raise forms.ValidationError(errors)
            
            # Сохраняем предупреждения для использования в view
            self.warnings = warnings
        
        return cleaned_data
    
    def calculate_estimated_cost(self):
        """Предварительный расчет себестоимости и цены продажи"""
        cleaned_data = self.cleaned_data
        template = cleaned_data.get('template')
        quantity = cleaned_data.get('quantity', 0)
        markup = cleaned_data.get('markup_percent', 20)
        labor = cleaned_data.get('labor_cost', 0)
        
        if not template or not quantity:
            return None
        
        material_cost = 0
        material_details = []
        
        for req in template.material_requirements.select_related('material').all():
            needed = req.total_required_per_unit * quantity
            price = float(req.material.price_per_unit) if req.material.price_per_unit else 0
            cost = price * needed
            
            material_details.append({
                'name': req.material.name,
                'quantity': needed,
                'unit': req.material.unit,
                'price': price,
                'cost': cost
            })
            material_cost += cost
        
        total_cost = material_cost + float(labor)
        selling_price = total_cost * (1 + float(markup) / 100)
        
        return {
            'material_cost': material_cost,
            'labor_cost': float(labor),
            'total_cost': total_cost,
            'markup_percent': float(markup),
            'selling_price': selling_price,
            'profit': selling_price - total_cost,
            'materials': material_details
        }


class ProductFilterForm(forms.Form):
    """Форма фильтрации готовой продукции"""
    category = forms.ModelChoiceField(
        queryset=ProductCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Категория"
    )
    climate = forms.ChoiceField(
        choices=[('', 'Все')] + ProductCategory.CLIMATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Климат"
    )
    status = forms.ChoiceField(
        choices=[('', 'Все')] + Product.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Статус"
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по артикулу или названию...'}),
        label="Поиск"
    )


class ProductShipmentForm(forms.ModelForm):
    """Форма отгрузки готовой продукции"""
    class Meta:
        model = ProductShipment
        fields = ['quantity', 'shipped_to', 'shipment_date', 'document_number', 'notes']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Количество штук'
            }),
            'shipped_to': forms.Select(attrs={'class': 'form-control'}),
            'shipment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Накладная №123 от 01.01.2024'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Дополнительная информация об отгрузке'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем контрагентов только типа "customer" (Заказчик)
        from warehouse.models import Contractor
        self.fields['shipped_to'].queryset = Contractor.objects.filter(contractor_type='customer')
        self.fields['shipped_to'].label = "Заказчик"
        self.fields['shipped_to'].empty_label = "Выберите заказчика"