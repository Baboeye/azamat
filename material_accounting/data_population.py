# data_population.py
import os
import sys
import django
from datetime import datetime, date

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'material_accounting.settings')
sys.path.insert(0, 'C:/Users/azama/Desktop/material_accounting/material_accounting')
django.setup()

from django.contrib.auth.models import User
from warehouse.models import Section, Contractor, Material, Receipt, Issue, Scrap, AuditLog
from production.models import ProductCategory, ProductTemplate, ProductMaterialRequirement, Product, MaterialConsumption, ProductShipment


def create_superuser():
    """Создание суперпользователя"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("✅ Создан суперпользователь: admin / admin")
    else:
        print("ℹ️ Суперпользователь уже существует")


def create_sections():
    """Создание секций склада"""
    sections_data = [
        {'name': 'Основной зал', 'description': 'Основное хранилище тканей и материалов'},
        {'name': 'Холодный склад', 'description': 'Хранение утеплителей и спецматериалов'},
        {'name': 'Мелкая фурнитура', 'description': 'Пуговицы, молнии, нитки, кнопки'},
        {'name': 'Готовая продукция', 'description': 'Склад готовой спецодежды'},
        {'name': 'Брак и отходы', 'description': 'Зона временного хранения брака'},
    ]
    
    for data in sections_data:
        Section.objects.get_or_create(name=data['name'], defaults=data)
    print(f"✅ Создано {len(sections_data)} секций склада")


def create_contractors():
    """Создание контрагентов (поставщиков и заказчиков)"""
    contractors_data = [
        # Поставщики
        {'name': 'ООО "ТекстильПром"', 'contractor_type': 'supplier', 
         'address': 'г. Москва, ул. Текстильщиков, 15', 
         'contact_info': '+7 (495) 123-45-67, info@textileprom.ru'},
        {'name': 'ЗАО "ТканиСнаб"', 'contractor_type': 'supplier',
         'address': 'г. Иваново, пр-т Ленина, 89',
         'contact_info': '+7 (4932) 12-34-56, sales@tkani-snab.ru'},
        {'name': 'ИП Петров С.А.', 'contractor_type': 'supplier',
         'address': 'г. Санкт-Петербург, наб. Фонтанки, 45',
         'contact_info': '+7 (812) 987-65-43, petrov.sa@mail.ru'},
        {'name': 'ООО "ФурнитураОпт"', 'contractor_type': 'supplier',
         'address': 'г. Новосибирск, ул. Кирова, 112',
         'contact_info': '+7 (383) 333-44-55, opt@furnitura.ru'},
        
        # Заказчики
        {'name': 'ПАО "НефтьГаз"', 'contractor_type': 'customer',
         'address': 'г. Уфа, ул. Промышленная, 25',
         'contact_info': '+7 (347) 222-33-44, zakupki@neftgaz.ru'},
        {'name': 'ООО "Северная нефть"', 'contractor_type': 'customer',
         'address': 'г. Ноябрьск, ул. Заводская, 8',
         'contact_info': '+7 (3496) 44-55-66, sn@severnaya.ru'},
        {'name': 'АО "Татнефть"', 'contractor_type': 'customer',
         'address': 'Респ. Татарстан, г. Альметьевск, ул. Нефтяников, 1',
         'contact_info': '+7 (8553) 77-88-99, tender@tatneft.ru'},
        {'name': 'ООО "УралЭнерго"', 'contractor_type': 'customer',
         'address': 'г. Екатеринбург, ул. Машиностроителей, 33',
         'contact_info': '+7 (343) 555-66-77, supply@uralenergo.ru'},
    ]
    
    for data in contractors_data:
        Contractor.objects.get_or_create(name=data['name'], defaults=data)
    print(f"✅ Создано {len(contractors_data)} контрагентов")


def create_materials():
    """Создание материалов на складе"""
    materials_data = [
        # Ткани основные
        {'name': 'Грета огнеупорная', 'article': 'TKN-001-GR', 'unit': 'м', 
         'quantity': 1250.5, 'min_stock': 200, 'section_name': 'Основной зал',
         'contractor_name': 'ООО "ТекстильПром"', 'color': 'Темно-синий',
         'width': 150, 'density': 280, 'composition': '100% хлопок, огнезащитная пропитка',
         'description': 'Основная ткань для летней спецодежды нефтяников'},
        
        {'name': 'Диагональ плотная', 'article': 'TKN-002-DG', 'unit': 'м',
         'quantity': 890.3, 'min_stock': 150, 'section_name': 'Основной зал',
         'contractor_name': 'ООО "ТекстильПром"', 'color': 'Васильковый',
         'width': 140, 'density': 320, 'composition': '80% хлопок, 20% полиэстер',
         'description': 'Ткань для костюмов повседневного ношения'},
        
        {'name': 'Саржа утепленная', 'article': 'TKN-003-SR', 'unit': 'м',
         'quantity': 45.8, 'min_stock': 100, 'section_name': 'Холодный склад',
         'contractor_name': 'ЗАО "ТканиСнаб"', 'color': 'Оранжевый',
         'width': 155, 'density': 450, 'composition': '65% полиэстер, 35% хлопок',
         'description': 'Зимняя ткань с водоотталкивающей пропиткой'},
        
        {'name': 'Оксфорд 600D', 'article': 'TKN-004-OX', 'unit': 'м',
         'quantity': 320.0, 'min_stock': 80, 'section_name': 'Основной зал',
         'contractor_name': 'ИП Петров С.А.', 'color': 'Хаки',
         'width': 160, 'density': 220, 'composition': '100% полиэстер',
         'description': 'Прочная ткань для брюк и накладок'},
        
        {'name': 'Флис плотный', 'article': 'TKN-005-FL', 'unit': 'м',
         'quantity': 12.5, 'min_stock': 50, 'section_name': 'Холодный склад',
         'contractor_name': 'ЗАО "ТканиСнаб"', 'color': 'Серый меланж',
         'width': 170, 'density': 380, 'composition': '100% полиэстер',
         'description': 'Подкладочный флис для зимней одежды'},
        
        # Утеплители
        {'name': 'Синтепон 300г/м2', 'article': 'UTP-001-SN', 'unit': 'м',
         'quantity': 180.0, 'min_stock': 40, 'section_name': 'Холодный склад',
         'contractor_name': 'ООО "ТекстильПром"', 'color': 'Белый',
         'width': 150, 'density': 300, 'composition': '100% полиэстер',
         'description': 'Утеплитель для зимних курток и комбинезонов'},
        
        {'name': 'Тинсулейт 150г', 'article': 'UTP-002-TN', 'unit': 'м',
         'quantity': 8.2, 'min_stock': 20, 'section_name': 'Холодный склад',
         'contractor_name': 'ИП Петров С.А.', 'color': 'Белый',
         'width': 160, 'density': 150, 'composition': 'Синтетическое микроволокно',
         'description': 'Высокотехнологичный утеплитель, замена пуху'},
        
        # Фурнитура
        {'name': 'Молния металл №5', 'article': 'FRN-001-ML', 'unit': 'шт',
         'quantity': 450, 'min_stock': 100, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Никель',
         'description': 'Металлическая молния для брюк и курток, 18 см'},
        
        {'name': 'Молния пластик №8', 'article': 'FRN-002-PL', 'unit': 'шт',
         'quantity': 280, 'min_stock': 80, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Черный',
         'description': 'Пластиковая молния для зимней одежды, 70 см'},
        
        {'name': 'Пуговица 20мм металл', 'article': 'FRN-003-PG', 'unit': 'шт',
         'quantity': 1500, 'min_stock': 300, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Темно-синий',
         'description': 'Металлические пуговицы с логотипом для костюмов'},
        
        {'name': 'Пуговица 15мм пластик', 'article': 'FRN-004-PP', 'unit': 'шт',
         'quantity': 2300, 'min_stock': 500, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Черный',
         'description': 'Пластиковые пуговицы для рубашек и брюк'},
        
        {'name': 'Кнопка Альфа 17мм', 'article': 'FRN-005-KN', 'unit': 'шт',
         'quantity': 890, 'min_stock': 200, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ИП Петров С.А.', 'color': 'Латунь',
         'description': 'Кнопки для утепленной одежды'},
        
        {'name': 'Пряжка ременная 40мм', 'article': 'FRN-006-PR', 'unit': 'шт',
         'quantity': 120, 'min_stock': 50, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Черный',
         'description': 'Пряжки для ремней и подтяжек'},
        
        # Нитки и расходники
        {'name': 'Нитки армированные 40/2', 'article': 'NTK-001-AR', 'unit': 'шт',
         'quantity': 85, 'min_stock': 20, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Ассорти',
         'description': 'Армированные нитки для шитья спецодежды, 5000м'},
        
        {'name': 'Нитки полиэстер 20/2', 'article': 'NTK-002-PL', 'unit': 'шт',
         'quantity': 120, 'min_stock': 30, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Черный',
         'description': 'Прочные нитки для отделочных швов'},
        
        {'name': 'Лента светоотражающая 25мм', 'article': 'LSR-001-SO', 'unit': 'м',
         'quantity': 340, 'min_stock': 100, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ИП Петров С.А.', 'color': 'Серебристый',
         'description': 'Светоотражающая лента для повышенной видимости'},
        
        {'name': 'Липучка 20мм', 'article': 'LPK-001-LP', 'unit': 'м',
         'quantity': 95, 'min_stock': 50, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Черный',
         'description': 'Лента-липучка для манжет и карманов'},
        
        {'name': 'Резинка брючная 3см', 'article': 'RSK-001-BR', 'unit': 'м',
         'quantity': 180, 'min_stock': 60, 'section_name': 'Мелкая фурнитура',
         'contractor_name': 'ООО "ФурнитураОпт"', 'color': 'Черный',
         'description': 'Эластичная резинка для поясов брюк'},
    ]
    
    admin_user = User.objects.get(username='admin')
    
    for data in materials_data:
        section_name = data.pop('section_name')
        contractor_name = data.pop('contractor_name', None)
        
        section = Section.objects.get(name=section_name)
        contractor = Contractor.objects.filter(name=contractor_name).first() if contractor_name else None
        
        material, created = Material.objects.get_or_create(
            article=data['article'],
            defaults={
                **data,
                'section': section,
                'contractor': contractor
            }
        )
        
        if created:
            # Создаем запись о приходе для истории
            Receipt.objects.create(
                material=material,
                quantity=data['quantity'],
                price=round(data['quantity'] * (100 + hash(data['article']) % 200), 2),
                contractor=contractor,
                document_number=f"Накладная №{hash(data['article']) % 10000}",
                created_by=admin_user,
                notes='Начальный остаток при создании системы'
            )
    
    print(f"✅ Создано {len(materials_data)} материалов")


def create_product_categories():
    """Создание категорий продукции"""
    categories_data = [
        {
            'name': 'Костюм рабочий утепленный',
            'climate_type': 'cold',
            'description': 'Зимняя спецодежда для работы в условиях крайнего севера',
            'temperature_range': 'от -40°C до -20°C'
        },
        {
            'name': 'Куртка демисезонная',
            'climate_type': 'moderate',
            'description': 'Переходная спецодежда для весны и осени',
            'temperature_range': 'от -5°C до +15°C'
        },
        {
            'name': 'Костюм летний',
            'climate_type': 'hot',
            'description': 'Легкая спецодежда для жаркого климата',
            'temperature_range': 'от +20°C до +45°C'
        },
        {
            'name': 'Костюм антистатический',
            'climate_type': 'extreme',
            'description': 'Защитная одежда для работы с ЛВЖ и ГВЖ',
            'temperature_range': 'от -20°C до +40°C'
        },
    ]
    
    for data in categories_data:
        ProductCategory.objects.get_or_create(name=data['name'], defaults=data)
    print(f"✅ Создано {len(categories_data)} категорий продукции")


def create_product_templates():
    """Создание шаблонов продукции"""
    templates_data = [
        {
            'name': 'Костюм "Север-1" для нефтяников',
            'article': 'SN-KS-001-W',
            'category_name': 'Костюм рабочий утепленный',
            'protection_level': 'high',
            'description': 'Зимний костюм для работы на нефтяных вышках. Влагостойкий, ветрозащитный, утепленный синтепоном.',
            'weight_kg': 2.8,
            'sizes_available': '44-46, 48-50, 52-54, 56-58, 60-62',
            'colors_available': 'Темно-синий, Оранжевый',
            'requirements': [
                {'article': 'TKN-003-SR', 'quantity': 3.2, 'waste': 12, 'notes': 'Основная ткань, учитывать направление ворса'},
                {'article': 'UTP-001-SN', 'quantity': 2.1, 'waste': 15, 'notes': 'Утеплитель для куртки и брюк'},
                {'article': 'FRN-002-PL', 'quantity': 2, 'waste': 0, 'notes': 'Молнии для куртки'},
                {'article': 'FRN-003-PG', 'quantity': 8, 'waste': 5, 'notes': 'Пуговицы на куртку и брюки'},
                {'article': 'NTK-001-AR', 'quantity': 1, 'waste': 10, 'notes': 'Нитки для шитья'},
                {'article': 'LSR-001-SO', 'quantity': 1.5, 'waste': 5, 'notes': 'Светоотражающие вставки'},
            ]
        },
        {
            'name': 'Куртка "Весна" нефтяника',
            'article': 'SN-KD-002-M',
            'category_name': 'Куртка демисезонная',
            'protection_level': 'standard',
            'description': 'Демисезонная куртка с водоотталкивающей пропиткой. Легкая и дышащая.',
            'weight_kg': 1.4,
            'sizes_available': '44-46, 48-50, 52-54, 56-58',
            'colors_available': 'Синий, Хаки',
            'requirements': [
                {'article': 'TKN-001-GR', 'quantity': 2.8, 'waste': 10, 'notes': 'Основная ткань'},
                {'article': 'FRN-001-ML', 'quantity': 1, 'waste': 0, 'notes': 'Молния для брюк'},
                {'article': 'FRN-003-PG', 'quantity': 6, 'waste': 5, 'notes': 'Пуговицы'},
                {'article': 'NTK-002-PL', 'quantity': 0.5, 'waste': 10, 'notes': 'Отделочные нитки'},
            ]
        },
        {
            'name': 'Костюм "Пустыня" летний',
            'article': 'SN-LS-003-H',
            'category_name': 'Костюм летний',
            'protection_level': 'standard',
            'description': 'Легкий дышащий костюм для работы в жарких условиях. Защита от солнца.',
            'weight_kg': 0.9,
            'sizes_available': '44-46, 48-50, 52-54, 56-58, 60-62, 64-66',
            'colors_available': 'Бежевый, Светло-серый',
            'requirements': [
                {'article': 'TKN-001-GR', 'quantity': 2.5, 'waste': 8, 'notes': 'Легкая ткань'},
                {'article': 'FRN-004-PP', 'quantity': 6, 'waste': 5, 'notes': 'Пластиковые пуговицы'},
                {'article': 'NTK-001-AR', 'quantity': 0.4, 'waste': 10, 'notes': 'Нитки'},
                {'article': 'RSK-001-BR', 'quantity': 0.8, 'waste': 5, 'notes': 'Резинка для пояса'},
            ]
        },
        {
            'name': 'Костюм взрывозащитный "Нефть-Газ"',
            'article': 'SN-VZ-004-E',
            'category_name': 'Костюм антистатический',
            'protection_level': 'max',
            'description': 'Специальная защитная одежда для работы с горючими веществами. Антистатическая.',
            'weight_kg': 2.2,
            'sizes_available': '44-46, 48-50, 52-54, 56-58',
            'colors_available': 'Оранжевый с синими вставками',
            'requirements': [
                {'article': 'TKN-002-DG', 'quantity': 3.0, 'waste': 10, 'notes': 'Плотная диагональ'},
                {'article': 'UTP-002-TN', 'quantity': 1.8, 'waste': 12, 'notes': 'Тонкий утеплитель'},
                {'article': 'FRN-005-KN', 'quantity': 4, 'waste': 0, 'notes': 'Кнопки вместо пуговиц'},
                {'article': 'FRN-006-PR', 'quantity': 2, 'waste': 0, 'notes': 'Пряжки'},
                {'article': 'LSR-001-SO', 'quantity': 2.0, 'waste': 5, 'notes': 'Широкие светоотражающие полосы'},
                {'article': 'LPK-001-LP', 'quantity': 0.5, 'waste': 5, 'notes': 'Липучка для манжет'},
            ]
        },
    ]
    
    for data in templates_data:
        category = ProductCategory.objects.get(name=data.pop('category_name'))
        requirements = data.pop('requirements')
        
        template, created = ProductTemplate.objects.get_or_create(
            article=data['article'],
            defaults={
                **data,
                'category': category,
                'is_active': True
            }
        )
        
        if created:
            # Создаем нормы расхода
            for req_data in requirements:
                material = Material.objects.get(article=req_data['article'])
                ProductMaterialRequirement.objects.create(
                    product_template=template,
                    material=material,
                    quantity_per_unit=req_data['quantity'],
                    waste_percent=req_data['waste'],
                    notes=req_data['notes']
                )
    
    print(f"✅ Создано {len(templates_data)} шаблонов продукции")


def create_production_orders():
    """Создание производственных заказов"""
    admin_user = User.objects.get(username='admin')
    
    orders_data = [
        {
            'template_article': 'SN-KS-001-W',
            'batch': 'Партия-2024-001',
            'size': '48-50',
            'color': 'Темно-синий',
            'quantity': 25,
            'date': date(2024, 1, 15),
            'location': 'ГП-Секция А',
            'status': 'ready'
        },
        {
            'template_article': 'SN-KS-001-W',
            'batch': 'Партия-2024-002',
            'size': '52-54',
            'color': 'Оранжевый',
            'quantity': 15,
            'date': date(2024, 2, 3),
            'location': 'ГП-Секция А',
            'status': 'ready'
        },
        {
            'template_article': 'SN-KD-002-M',
            'batch': 'Партия-2024-003',
            'size': '48-50',
            'color': 'Синий',
            'quantity': 30,
            'date': date(2024, 2, 20),
            'location': 'ГП-Секция Б',
            'status': 'ready'
        },
        {
            'template_article': 'SN-LS-003-H',
            'batch': 'Партия-2024-004',
            'size': '56-58',
            'color': 'Бежевый',
            'quantity': 20,
            'date': date(2024, 3, 5),
            'location': 'ГП-Секция Б',
            'status': 'in_production'
        },
        {
            'template_article': 'SN-VZ-004-E',
            'batch': 'Партия-2024-005',
            'size': '48-50',
            'color': 'Оранжевый с синими вставками',
            'quantity': 10,
            'date': date(2024, 3, 12),
            'location': 'ГП-Секция В',
            'status': 'quality_check'
        },
    ]
    
    for order_data in orders_data:
        template = ProductTemplate.objects.get(article=order_data.pop('template_article'))
        status = order_data.pop('status')
        
        product = Product.objects.create(
            template=template,
            batch_number=order_data['batch'],
            size=order_data['size'],
            color=order_data['color'],
            quantity_produced=order_data['quantity'],
            production_date=order_data['date'],
            produced_by=admin_user,
            warehouse_location=order_data['location'],
            status=status,
            labor_cost=order_data['quantity'] * 850.00  # 850 руб. работа на изделие
        )
        
        # Создаем расход материалов
        for req in template.material_requirements.all():
            total_used = req.total_required_per_unit * order_data['quantity']
            
            MaterialConsumption.objects.create(
                product=product,
                material=req.material,
                quantity_required=req.quantity_per_unit * order_data['quantity'],
                quantity_used=total_used,
                quantity_waste=total_used - (req.quantity_per_unit * order_data['quantity'])
            )
            
            # Списываем со склада
            req.material.quantity -= total_used
            req.material.save()
            
            # Лог в аудит
            AuditLog.objects.create(
                action='issue',
                material=req.material,
                quantity=-total_used,
                user=admin_user,
                details=f'Производство {order_data["batch"]}: {template.name}'
            )
        
        product.calculate_cost()
    
    print(f"✅ Создано {len(orders_data)} производственных заказов")


def create_shipments():
    """Создание отгрузок готовой продукции"""
    admin_user = User.objects.get(username='admin')
    
    shipments_data = [
        {
            'batch': 'Партия-2024-001',
            'quantity': 20,
            'customer': 'ПАО "НефтьГаз"',
            'date': date(2024, 1, 25),
            'document': 'Накладная №152 от 25.01.2024'
        },
        {
            'batch': 'Партия-2024-001',
            'quantity': 5,
            'customer': 'ООО "Северная нефть"',
            'date': date(2024, 1, 30),
            'document': 'Накладная №167 от 30.01.2024'
        },
        {
            'batch': 'Партия-2024-002',
            'quantity': 15,
            'customer': 'АО "Татнефть"',
            'date': date(2024, 2, 15),
            'document': 'Накладная №203 от 15.02.2024'
        },
        {
            'batch': 'Партия-2024-003',
            'quantity': 25,
            'customer': 'ООО "УралЭнерго"',
            'date': date(2024, 3, 1),
            'document': 'Накладная №245 от 01.03.2024'
        },
    ]
    
    for ship_data in shipments_data:
        product = Product.objects.get(batch_number=ship_data['batch'])
        customer = Contractor.objects.get(name=ship_data['customer'])
        
        ProductShipment.objects.create(
            product=product,
            quantity=ship_data['quantity'],
            shipped_to=customer,
            shipment_date=ship_data['date'],
            document_number=ship_data['document'],
            shipped_by=admin_user,
            notes='Отгрузка по договору поставки'
        )
    
    print(f"✅ Создано {len(shipments_data)} отгрузок")


def create_audit_logs():
    """Создание дополнительных записей аудита"""
    admin_user = User.objects.get(username='admin')
    
    # Дополнительные операции для истории
    materials = Material.objects.all()[:5]
    
    for i, material in enumerate(materials):
        AuditLog.objects.create(
            action='receipt',
            material=material,
            quantity=100 + i * 50,
            user=admin_user,
            details=f'Плановое пополнение склада'
        )
    
    print(f"✅ Созданы дополнительные записи аудита")


def main():
    """Основная функция заполнения данных"""
    print("=" * 60)
    print("🚀 НАЧАЛО ЗАПОЛНЕНИЯ ТЕСТОВЫМИ ДАННЫМИ")
    print("=" * 60)
    
    create_superuser()
    create_sections()
    create_contractors()
    create_materials()
    create_product_categories()
    create_product_templates()
    create_production_orders()
    create_shipments()
    create_audit_logs()
    
    print("=" * 60)
    print("✅ ВСЕ ДАННЫЕ УСПЕШНО СОЗДАНЫ!")
    print("=" * 60)
    print("\n📊 ИТОГО:")
    print(f"   • Пользователей: {User.objects.count()}")
    print(f"   • Секций склада: {Section.objects.count()}")
    print(f"   • Контрагентов: {Contractor.objects.count()}")
    print(f"   • Материалов: {Material.objects.count()}")
    print(f"   • Категорий продукции: {ProductCategory.objects.count()}")
    print(f"   • Шаблонов изделий: {ProductTemplate.objects.count()}")
    print(f"   • Производственных заказов: {Product.objects.count()}")
    print(f"   • Отгрузок: {ProductShipment.objects.count()}")
    print(f"   • Записей аудита: {AuditLog.objects.count()}")
    print("\n🔑 Доступ в систему:")
    print("   Логин: admin")
    print("   Пароль: admin")


if __name__ == '__main__':
    main()