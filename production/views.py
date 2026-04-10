# production/views.py - проверьте импорты в начале файла
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime

from .models import (
    ProductCategory, ProductTemplate, ProductMaterialRequirement, 
    Product, MaterialConsumption, ProductShipment  # ProductShipment должен быть здесь
)
from .forms import (
    ProductCategoryForm, ProductTemplateForm, ProductMaterialRequirementForm,
    ProductionOrderForm, ProductFilterForm, ProductShipmentForm  # ProductShipmentForm должен быть здесь
)
from warehouse.models import Material, AuditLog, Contractor  # Contractor тоже нужен

from .models import (
    ProductCategory, ProductTemplate, ProductMaterialRequirement, 
    Product, MaterialConsumption
)
from .forms import (
    ProductCategoryForm, ProductTemplateForm, ProductMaterialRequirementForm,
    ProductionOrderForm, ProductFilterForm
)
from warehouse.models import Material, AuditLog


@login_required
def product_dashboard(request):
    """Дашборд производства"""
    total_products = Product.objects.count()
    products_ready = Product.objects.filter(status='ready').count()
    products_in_production = Product.objects.filter(status='in_production').count()
    
    categories_stats = ProductCategory.objects.annotate(
        products_count=Sum('templates__products__quantity_produced')
    )
    
    recent_products = Product.objects.select_related('template', 'template__category').order_by('-created_at')[:10]
    
    critical_materials = Material.objects.filter(
        used_in_products__isnull=False,
        quantity__lte=F('min_stock')
    ).distinct()[:5]
    
    return render(request, 'production/dashboard.html', {
        'total_products': total_products,
        'products_ready': products_ready,
        'products_in_production': products_in_production,
        'categories_stats': categories_stats,
        'recent_products': recent_products,
        'critical_materials': critical_materials,
    })


@login_required
def product_list(request):
    """Список готовой продукции с фильтрами"""
    queryset = Product.objects.select_related('template', 'template__category').all()
    
    form = ProductFilterForm(request.GET)
    
    if form.is_valid():
        if form.cleaned_data['category']:
            queryset = queryset.filter(template__category=form.cleaned_data['category'])
        if form.cleaned_data['climate']:
            queryset = queryset.filter(template__category__climate_type=form.cleaned_data['climate'])
        if form.cleaned_data['status']:
            queryset = queryset.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['search']:
            search = form.cleaned_data['search']
            queryset = queryset.filter(
                Q(template__name__icontains=search) | 
                Q(template__article__icontains=search) |
                Q(batch_number__icontains=search)
            )
    
    paginator = Paginator(queryset.order_by('-production_date'), 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    return render(request, 'production/product_list.html', {
        'products': products,
        'filter_form': form,
        'total_count': queryset.count(),
    })


@login_required
def product_detail(request, pk):
    """Детальная информация о продукте - ЕДИНСТВЕННАЯ ВЕРСИЯ"""
    product = get_object_or_404(
        Product.objects.select_related('template', 'template__category', 'produced_by'),
        pk=pk
    )
    
    # === ОБРАБОТКА ИЗМЕНЕНИЯ СТАТУСА ===
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'set_ready':
            if product.status in ['in_production', 'quality_check']:
                product.status = 'ready'
                product.save()
                messages.success(request, f'✅ Партия {product.batch_number} готова к отгрузке!')
                return redirect('product_detail', pk=pk)
            else:
                messages.warning(request, f'Нельзя перевести в готовность. Текущий статус: {product.get_status_display()}')
                
        elif action == 'set_quality_check':
            if product.status == 'in_production':
                product.status = 'quality_check'
                product.save()
                messages.success(request, f'🔍 Партия {product.batch_number} отправлена на проверку качества')
                return redirect('product_detail', pk=pk)
            else:
                messages.warning(request, f'Нельзя отправить на проверку. Текущий статус: {product.get_status_display()}')
                
        elif action == 'set_shipped':
            if product.status == 'ready':
                product.status = 'shipped'
                product.save()
                messages.success(request, f'🚚 Партия {product.batch_number} отгружена')
                return redirect('product_detail', pk=pk)
    
    # GET запрос - показываем детали
    consumptions = product.material_consumptions.select_related('material').all()
    shipments = product.shipments.select_related('shipped_to').all()
    
    return render(request, 'production/product_detail.html', {
        'product': product,
        'consumptions': consumptions,
        'shipments': shipments,
    })


@login_required
@transaction.atomic
def production_order_create(request):
    """Создание заказа на производство со списанием материалов"""
    if request.method == 'POST':
        form = ProductionOrderForm(request.POST)
        if form.is_valid():
            try:
                # Создаем продукт
                product = Product.objects.create(
                    template=form.cleaned_data['template'],
                    batch_number=form.cleaned_data['batch_number'],
                    size=form.cleaned_data['size'],
                    color=form.cleaned_data['color'],
                    quantity_produced=form.cleaned_data['quantity'],
                    production_date=form.cleaned_data['production_date'],
                    produced_by=request.user,
                    warehouse_location=form.cleaned_data.get('warehouse_location', ''),
                    status='in_production'
                )
                
                # Списываем материалы
                template = form.cleaned_data['template']
                quantity = form.cleaned_data['quantity']
                
                for req in template.material_requirements.select_related('material').all():
                    total_needed = req.total_required_per_unit * quantity
                    material = req.material
                    
                    # Проверка еще раз (на случай race condition)
                    if material.quantity < total_needed:
                        raise ValueError(f"Недостаточно материала {material.name}")
                    
                    # Списание со склада
                    old_quantity = material.quantity
                    material.quantity -= total_needed
                    material.save()
                    
                    # Запись о расходе
                    MaterialConsumption.objects.create(
                        product=product,
                        material=material,
                        quantity_required=req.quantity_per_unit * quantity,
                        quantity_used=total_needed,
                        quantity_waste=total_needed - (req.quantity_per_unit * quantity)
                    )
                    
                    # Аудит
                    AuditLog.objects.create(
                        action='issue',
                        material=material,
                        quantity=-total_needed,
                        user=request.user,
                        details=f'Производство {product.batch_number}: {template.name} (x{quantity})'
                    )
                
                # Расчет себестоимости
                product.calculate_cost()
                
                messages.success(
                    request, 
                    f'Производственный заказ {product.batch_number} создан. '
                    f'Списано материалов на сумму {product.material_cost} ₽'
                )
                
                # Предупреждения о критических остатках
                if hasattr(form, 'warnings') and form.warnings:
                    for warning in form.warnings:
                        messages.warning(request, warning)
                
                return redirect('product_detail', pk=product.pk)
                
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('production_order_create')
    else:
        form = ProductionOrderForm()
    
    return render(request, 'production/production_order_form.html', {
        'form': form,
        'title': 'Новый заказ на производство'
    })


@login_required
def template_list(request):
    """Список шаблонов/моделей спецодежды"""
    templates = ProductTemplate.objects.select_related('category').filter(is_active=True)
    
    # Группировка по климату
    categories = ProductCategory.objects.prefetch_related('templates').all()
    
    return render(request, 'production/template_list.html', {
        'categories': categories,
        'templates_count': templates.count(),
    })


@login_required
def template_detail(request, pk):
    """Детали шаблона с нормами расхода"""
    template = get_object_or_404(
        ProductTemplate.objects.select_related('category'),
        pk=pk
    )
    requirements = template.material_requirements.select_related('material').all()
    
    return render(request, 'production/template_detail.html', {
        'template': template,
        'requirements': requirements,
    })


@login_required
def template_create(request):
    """Создание нового шаблона"""
    if request.method == 'POST':
        form = ProductTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Шаблон {template.name} создан. Теперь добавьте нормы расхода материалов.')
            return redirect('template_detail', pk=template.pk)
    else:
        form = ProductTemplateForm()
    
    return render(request, 'production/template_form.html', {
        'form': form,
        'title': 'Новая модель спецодежды'
    })


@login_required
def requirement_add(request, template_pk):
    """Добавление нормы расхода материала"""
    template = get_object_or_404(ProductTemplate, pk=template_pk)
    
    if request.method == 'POST':
        form = ProductMaterialRequirementForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.product_template = template
            req.save()
            messages.success(request, f'Норма расхода для {req.material.name} добавлена')
            return redirect('template_detail', pk=template_pk)
    else:
        form = ProductMaterialRequirementForm()
    
    return render(request, 'production/requirement_form.html', {
        'form': form,
        'template': template,
        'title': f'Добавить материал для {template.name}'
    })


@login_required
def api_check_materials(request):
    """API для проверки достаточности материалов (AJAX)"""
    template_id = request.GET.get('template_id')
    quantity = request.GET.get('quantity', 1)
    
    print(f"DEBUG: template_id={template_id}, quantity={quantity}")  # Добавь для отладки
    
    if not template_id:
        return JsonResponse({'error': 'No template_id'}, status=400)
    
    try:
        quantity = int(quantity)
        template = ProductTemplate.objects.get(pk=template_id)
    except (ValueError, ProductTemplate.DoesNotExist):
        return JsonResponse({'error': 'Invalid template or quantity'}, status=404)
    
    materials_status = []
    can_produce = True
    
    # Проверяем, есть ли нормы расхода
    requirements = template.material_requirements.select_related('material').all()
    print(f"DEBUG: найдено {requirements.count()} норм расхода")  # Отладка
    
    if not requirements.exists():
        return JsonResponse({
            'can_produce': False,
            'error': 'У модели не заданы нормы расхода материалов',
            'materials': []
        })
    
    for req in requirements:
        total_needed = req.total_required_per_unit * quantity
        available = req.material.quantity
        price = float(req.material.price_per_unit) if req.material.price_per_unit else 0
        enough = available >= total_needed
        
        if not enough:
            can_produce = False
        
        materials_status.append({
            'material_name': req.material.name,
            'material_article': req.material.article,
            'required': round(total_needed, 2),
            'available': round(available, 2),
            'unit': req.material.unit,
            'enough': enough,
            'shortage': round(total_needed - available, 2) if not enough else 0,
            'price': price,  # Добавляем цену для отображения
            'cost': round(price * total_needed, 2)  # Стоимость материала
        })
    
    return JsonResponse({
        'can_produce': can_produce,
        'materials': materials_status,
        'total_materials': len(materials_status),
        'estimated_cost': sum(m['cost'] for m in materials_status)
    })


@login_required
def reports_production(request):
    """Отчеты по производству"""
    # Статистика за период
    from_date = request.GET.get('from_date', timezone.now().replace(day=1).date())
    to_date = request.GET.get('to_date', timezone.now().date())
    
    if isinstance(from_date, str):
        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
    if isinstance(to_date, str):
        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
    
    products = Product.objects.filter(
        production_date__gte=from_date,
        production_date__lte=to_date
    )
    
    stats = {
        'total_produced': products.aggregate(total=Sum('quantity_produced'))['total'] or 0,
        'total_cost': sum(p.total_cost for p in products),
        'by_category': {},
    }
    
    for product in products:
        cat_name = product.template.category.name
        if cat_name not in stats['by_category']:
            stats['by_category'][cat_name] = {'count': 0, 'cost': 0}
        stats['by_category'][cat_name]['count'] += product.quantity_produced
        stats['by_category'][cat_name]['cost'] += float(product.total_cost)
    
    return render(request, 'production/reports.html', {
        'stats': stats,
        'from_date': from_date,
        'to_date': to_date,
    })
    
@login_required
@transaction.atomic
def product_shipment_create(request, product_pk):
    """Создание отгрузки готовой продукции"""
    product = get_object_or_404(Product, pk=product_pk)
    
    # Проверяем, что продукт готов к отгрузке
    if product.status not in ['ready', 'quality_check']:
        messages.error(request, 'Этот продукт не готов к отгрузке')
        return redirect('product_detail', pk=product_pk)
    
    # Считаем уже отгруженное количество
    shipped_total = product.shipments.aggregate(total=Sum('quantity'))['total'] or 0
    available = product.quantity_produced - shipped_total
    
    if available <= 0:
        messages.error(request, 'Вся продукция уже отгружена')
        return redirect('product_detail', pk=product_pk)
    
    if request.method == 'POST':
        form = ProductShipmentForm(request.POST)
        if form.is_valid():
            shipment = form.save(commit=False)
            shipment.product = product
            shipment.shipped_by = request.user
            
            # Проверяем, не превышаем ли доступное количество
            if form.cleaned_data['quantity'] > available:
                messages.error(request, f'Нельзя отгрузить больше {available} единиц')
                return redirect('product_shipment_create', product_pk=product_pk)
            
            shipment.save()
            
            # Обновляем статус если все отгружено
            new_shipped_total = shipped_total + shipment.quantity
            if new_shipped_total >= product.quantity_produced:
                product.status = 'shipped'
                product.save()
                messages.success(request, f'Отгрузка оформлена. Вся партия {product.batch_number} отгружена.')
            else:
                messages.success(request, f'Отгрузка на {shipment.shipped_to.name} оформлена. Остаток: {product.quantity_produced - new_shipped_total} шт.')
            
            return redirect('product_detail', pk=product_pk)
    else:
        form = ProductShipmentForm()
        form.fields['shipment_date'].initial = timezone.now().date()
        # Ограничиваем максимальное количество
        form.fields['quantity'].widget.attrs['max'] = available
    
    return render(request, 'production/shipment_form.html', {
        'form': form,
        'product': product,
        'available': available,
        'shipped': shipped_total,
    })
    
@login_required
def category_create(request):
    """Создание новой категории спецодежды"""
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Категория успешно создана')
            return redirect('template_list')
    else:
        form = ProductCategoryForm()
    
    return render(request, 'production/category_form.html', {
        'form': form,
        'title': 'Новая категория'
    })
    
@login_required
def category_edit(request, pk):
    """Редактирование категории"""
    category = get_object_or_404(ProductCategory, pk=pk)
    
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Категория "{category.name}" обновлена')
            return redirect('template_list')
    else:
        form = ProductCategoryForm(instance=category)
    
    return render(request, 'production/category_form.html', {
        'form': form,
        'category': category,
        'title': f'Редактирование: {category.name}',
        'is_edit': True
    })


@login_required
def category_delete(request, pk):
    """Удаление категории"""
    category = get_object_or_404(ProductCategory, pk=pk)
    
    # Проверяем, есть ли связанные модели
    templates_count = category.templates.count()
    
    if request.method == 'POST':
        if templates_count > 0:
            messages.error(request, f'Нельзя удалить категорию с {templates_count} моделями. Сначала удалите или перенесите модели.')
            return redirect('template_list')
        
        category_name = category.name
        category.delete()
        messages.success(request, f'Категория "{category_name}" удалена')
        return redirect('template_list')
    
    return render(request, 'production/category_confirm_delete.html', {
        'category': category,
        'templates_count': templates_count,
    })
    
@login_required
def product_set_ready(request, pk):
    """Изменение статуса продукта на 'Готов к отгрузке'"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        if product.status == 'in_production':
            product.status = 'ready'
            product.save()
            messages.success(request, f'Партия {product.batch_number} переведена в статус "Готов к отгрузке"')
        else:
            messages.warning(request, f'Нельзя изменить статус. Текущий статус: {product.get_status_display()}')
    
    return redirect('product_detail', pk=pk)


@login_required
def monthly_revenue_report(request):
    """Отчет по выручке за месяц"""
    from datetime import datetime
    from django.db.models import Sum, F, ExpressionWrapper, DecimalField
    
    # Получаем месяц из параметра или текущий
    month_str = request.GET.get('month', timezone.now().strftime('%Y-%m'))
    try:
        year, month = map(int, month_str.split('-'))
    except (ValueError, AttributeError):
        # Если формат неверный, используем текущий месяц
        now = timezone.now()
        year, month = now.year, now.month
        month_str = f"{year}-{month:02d}"
    
    # Начало и конец месяца
    from_date = datetime(year, month, 1).date()
    if month == 12:
        to_date = datetime(year + 1, 1, 1).date()
    else:
        to_date = datetime(year, month + 1, 1).date()
    
    # Отгрузки за месяц с оптимизацией запросов
    shipments = ProductShipment.objects.filter(
        shipment_date__gte=from_date,
        shipment_date__lt=to_date
    ).select_related('product', 'product__template', 'shipped_to').order_by('-shipment_date')
    
    # Расчет выручки и прибыли
    total_revenue = 0
    total_cost = 0
    total_quantity = 0
    shipment_data = []
    
    for shipment in shipments:
        # Получаем цену продажи за единицу
        unit_price = float(shipment.product.selling_price) if shipment.product.selling_price else 0
        cost_price = float(shipment.product.total_cost) if shipment.product.total_cost else 0
        
        # Считаем суммы
        revenue = unit_price * shipment.quantity
        cost = cost_price * shipment.quantity
        profit = revenue - cost
        
        shipment_data.append({
            'date': shipment.shipment_date,
            'product': shipment.product.template.name,
            'article': shipment.product.template.article,
            'batch': shipment.product.batch_number,
            'customer': shipment.shipped_to.name if shipment.shipped_to else '—',
            'quantity': shipment.quantity,
            'unit_price': unit_price,
            'revenue': revenue,
            'cost': cost,
            'profit': profit,
            'margin_percent': (profit / revenue * 100) if revenue > 0 else 0
        })
        
        total_revenue += revenue
        total_cost += cost
        total_quantity += shipment.quantity
    
    # Итоговые расчеты
    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    avg_check = (total_revenue / len(shipment_data)) if shipment_data else 0
    
    # Статистика по категориям
    category_stats = {}
    for item in shipment_data:
        # Получаем категорию через шаблон продукта
        category_name = item.get('product_category', 'Без категории')
        if category_name not in category_stats:
            category_stats[category_name] = {
                'revenue': 0,
                'profit': 0,
                'quantity': 0,
                'count': 0
            }
        category_stats[category_name]['revenue'] += item['revenue']
        category_stats[category_name]['profit'] += item['profit']
        category_stats[category_name]['quantity'] += item['quantity']
        category_stats[category_name]['count'] += 1
    
    # Сортировка категорий по выручке
    category_stats = dict(sorted(
        category_stats.items(), 
        key=lambda x: x[1]['revenue'], 
        reverse=True
    ))
    
    # Данные для навигации по месяцам
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_month_str = f"{prev_year}-{prev_month:02d}"
    
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    next_month_str = f"{next_year}-{next_month:02d}"
    
    # Название месяца на русском
    month_names = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    current_month_name = f"{month_names[month]} {year}"
    
    context = {
        'month': month_str,
        'month_name': current_month_name,
        'prev_month': prev_month_str,
        'next_month': next_month_str,
        'shipments': shipment_data,
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'total_quantity': total_quantity,
        'total_shipments': len(shipment_data),
        'avg_check': avg_check,
        'category_stats': category_stats,
    }
    
    return render(request, 'production/monthly_revenue.html', context)