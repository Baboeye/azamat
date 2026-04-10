from django import forms
from django.core.validators import MinValueValidator
from .models import Material, Contractor, Section


class MaterialForm(forms.ModelForm):
    """Форма для материала с валидацией"""
    
    class Meta:
        model = Material
        fields = [
            'name', 'article', 'description', 'unit', 'quantity', 
            'min_stock', 'section', 'contractor', 'image',
            'color', 'width', 'density', 'composition', 'price_per_unit'  # Добавлено поле цены
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Хлопок стрейч'
            }),
            'article': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Артикул (уникальный)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание материала'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'м, кг, шт...'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'min_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'price_per_unit': forms.NumberInput(attrs={  # Добавлен виджет для цены
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'contractor': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Красный, синий...'
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'см'
            }),
            'density': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'placeholder': 'г/м²'
            }),
            'composition': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '95% хлопок, 5% эластан'
            }),
        }
    
    def clean_article(self):
        """Проверка уникальности артикула"""
        article = self.cleaned_data.get('article')
        if article:
            article = article.strip().upper()
            qs = Material.objects.filter(article=article)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Материал с таким артикулом уже существует')
        return article
    
    def clean_quantity(self):
        """Проверка количества"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError('Количество не может быть отрицательным')
        return quantity
    
    def clean_price_per_unit(self):
        """Проверка цены"""
        price = self.cleaned_data.get('price_per_unit')
        if price is not None and price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной')
        return price
    
    def clean_article(self):
        """Проверка уникальности артикула"""
        article = self.cleaned_data.get('article')
        if article:
            article = article.strip().upper()
            qs = Material.objects.filter(article=article)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Материал с таким артикулом уже существует')
        return article
    
    def clean_quantity(self):
        """Проверка количества"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise forms.ValidationError('Количество не может быть отрицательным')
        return quantity


class ContractorForm(forms.ModelForm):
    """Форма для контрагента"""
    
    class Meta:
        model = Contractor
        fields = ['name', 'contractor_type', 'address', 'contact_info']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название компании'
            }),
            'contractor_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Юридический адрес'
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефон, email...'
            }),
        }


class SectionForm(forms.ModelForm):
    """Форма для секции склада"""
    
    class Meta:
        model = Section
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Основной зал'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Описание секции'
            }),
        }