from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from warehouse.models import (
    Section, Contractor, Material, Receipt, Issue, Scrap, AuditLog
)
from production.models import (
    ProductCategory, ProductTemplate, ProductMaterialRequirement, 
    Product, MaterialConsumption, ProductShipment
)
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Инициализирует базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Начинаю инициализацию данных...\n')
        
        # Создание тестового аккаунта
        self.create_test_user()
        
        # Создание секций
        self.create_sections()
        
        # Создание контрагентов
        self.create_contractors()
        
        # Создание материалов
        self.create_materials()
        
        # Создание категорий продуктов
        self.create_product_categories()
        
        # Создание шаблонов продуктов
        self.create_product_templates()
        
        # Создание приемок и отпусков
        self.create_receipts_and_issues()
        
        # Создание продуктов
        self.create_products()
        
        # Создание отправок готовой продукции
        self.create_shipments()
        
        self.stdout.write(self.style.SUCCESS('✅ Инициализация завершена!'))
        self.stdout.write(f'\n📋 Тестовый аккаунт: azama / azamat\n')

    def create_test_user(self):
        """Создание тестового аккаунта"""
        if User.objects.filter(username='azama').exists():
            self.stdout.write('ℹ️  Пользователь azama уже существует')
            return
        
        user = User.objects.create_superuser(
            username='azama',
            email='azama@test.local',
            password='azamat'
        )
        
        # Создание профиля с правами
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = 'admin'
        profile.save()
        
        self.stdout.write(self.style.SUCCESS('✅ Создан тестовый аккаунт: azama/azamat'))

    def create_sections(self):
        """Создание секций склада"""
        sections = [
            {'name': 'Основной зал', 'description': 'Основное хранилище тканей и материалов'},
            {'name': 'Холодный склад', 'description': 'Хранение утеплителей и спецматериалов'},
            {'name': 'Мелкая фурнитура', 'description': 'Пуговицы, молнии, нитки, кнопки'},
            {'name': 'Готовая продукция', 'description': 'Склад готовой спецодежды'},
            {'name': 'Брак и отходы', 'description': 'Зона временного хранения брака'},
        ]
        
        created_count = 0
        for section_data in sections:
            _, created = Section.objects.get_or_create(
                name=section_data['name'],
                defaults=section_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ Секции: создано {created_count}, всего {Section.objects.count()}')

    def create_contractors(self):
        """Создание контрагентов"""
        contractors = [
            {
                'name': 'ООО "ТекстильПром"', 'contractor_type': 'supplier',
                'address': 'г. Москва, ул. Текстильщиков, 15',
                'contact_info': '+7 (495) 123-45-67'
            },
            {
                'name': 'ЗАО "ТканиСнаб"', 'contractor_type': 'supplier',
                'address': 'г. Иваново, пр-т Ленина, 89',
                'contact_info': '+7 (4932) 12-34-56'
            },
            {
                'name': 'ООО "ФурнитураОпт"', 'contractor_type': 'supplier',
                'address': 'г. Новосибирск, ул. Кирова, 112',
                'contact_info': '+7 (383) 333-44-55'
            },
            {
                'name': 'ПАО "НефтьГаз"', 'contractor_type': 'customer',
                'address': 'г. Уфа, ул. Промышленная, 25',
                'contact_info': '+7 (347) 222-33-44'
            },
            {
                'name': 'ООО "Северная нефть"', 'contractor_type': 'customer',
                'address': 'г. Ноябрьск, ул. Заводская, 8',
                'contact_info': '+7 (3496) 44-55-66'
            },
        ]
        
        created_count = 0
        for contractor_data in contractors:
            _, created = Contractor.objects.get_or_create(
                name=contractor_data['name'],
                defaults=contractor_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ Контрагенты: создано {created_count}, всего {Contractor.objects.count()}')

    def create_materials(self):
        """Создание материалов"""
        section_main = Section.objects.filter(name='Основной зал').first()
        section_cold = Section.objects.filter(name='Холодный склад').first()
        contractor_prom = Contractor.objects.filter(name='ООО "ТекстильПром"').first()
        contractor_tkan = Contractor.objects.filter(name='ЗАО "ТканиСнаб"').first()
        
        materials = [
            {
                'name': 'Грета огнеупорная', 'article': 'TKN-001-GR', 'unit': 'м',
                'quantity': 1250.5, 'min_stock': 200, 'section': section_main,
                'contractor': contractor_prom, 'color': 'Темно-синий',
                'width': 150, 'density': 280, 'price_per_unit': 450.00,
                'composition': '100% хлопок, огнезащитная пропитка',
                'description': 'Основная ткань для летней спецодежды'
            },
            {
                'name': 'Диагональ плотная', 'article': 'TKN-002-DG', 'unit': 'м',
                'quantity': 890.3, 'min_stock': 150, 'section': section_main,
                'contractor': contractor_prom, 'color': 'Васильковый',
                'width': 140, 'density': 320, 'price_per_unit': 380.00,
                'composition': '80% хлопок, 20% полиэстер',
                'description': 'Ткань для костюмов повседневного ношения'
            },
            {
                'name': 'Саржа утепленная', 'article': 'TKN-003-SR', 'unit': 'м',
                'quantity': 450.8, 'min_stock': 100, 'section': section_cold,
                'contractor': contractor_tkan, 'color': 'Оранжевый',
                'width': 155, 'density': 450, 'price_per_unit': 620.00,
                'composition': '65% полиэстер, 35% хлопок',
                'description': 'Зимняя ткань с водоотталкивающей пропиткой'
            },
            {
                'name': 'Нитки полиэстер', 'article': 'FUR-001-NIT', 'unit': 'шпуля',
                'quantity': 500, 'min_stock': 50, 'section': section_main,
                'contractor': contractor_prom, 'color': 'Темно-синий',
                'price_per_unit': 85.00,
                'description': 'Высокопрочные нитки для пошива'
            },
            {
                'name': 'Молния металл М4', 'article': 'FUR-002-MZN', 'unit': 'шт',
                'quantity': 350, 'min_stock': 50, 'section': section_main,
                'contractor': contractor_prom, 'color': 'Серебро',
                'price_per_unit': 125.00,
                'description': 'Металлические молнии РиР'
            },
        ]
        
        created_count = 0
        for mat_data in materials:
            _, created = Material.objects.get_or_create(
                article=mat_data['article'],
                defaults=mat_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ Материалы: создано {created_count}, всего {Material.objects.count()}')

    def create_product_categories(self):
        """Создание категорий продуктов"""
        categories = [
            {
                'name': 'Летний костюм', 'climate_type': 'hot',
                'description': 'Спецодежда для жаркого климата',
                'temperature_range': '+15°C до +40°C'
            },
            {
                'name': 'Демисезонный костюм', 'climate_type': 'moderate',
                'description': 'Спецодежда для умеренного климата',
                'temperature_range': '-5°C до +20°C'
            },
            {
                'name': 'Зимний комплект', 'climate_type': 'cold',
                'description': 'Спецодежда для холодного климата',
                'temperature_range': '-40°C до -5°C'
            },
            {
                'name': 'Защита от масла', 'climate_type': 'extreme',
                'description': 'Специальная защита от нефти и газа',
                'temperature_range': '-30°C до +50°C'
            },
        ]
        
        created_count = 0
        for cat_data in categories:
            _, created = ProductCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ Категории: создано {created_count}, всего {ProductCategory.objects.count()}')

    def create_product_templates(self):
        """Создание шаблонов продуктов"""
        cat_hot = ProductCategory.objects.filter(climate_type='hot').first()
        cat_cold = ProductCategory.objects.filter(climate_type='cold').first()
        
        templates = [
            {
                'name': 'Костюм нефтяника летний', 'article': 'PROD-001-LSN',
                'category': cat_hot, 'protection_level': 'high',
                'weight_kg': 0.8, 'description': 'Комплект для жарких условий',
                'colors_available': 'Темно-синий, Оранжевый, Красный'
            },
            {
                'name': 'Комплект зимний утепленный', 'article': 'PROD-002-ZUT',
                'category': cat_cold, 'protection_level': 'max',
                'weight_kg': 2.5, 'description': 'Полный комплект на морозы',
                'colors_available': 'Оранжевый, Красный'
            },
        ]
        
        created_count = 0
        for tmpl_data in templates:
            _, created = ProductTemplate.objects.get_or_create(
                article=tmpl_data['article'],
                defaults=tmpl_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ Шаблоны: создано {created_count}, всего {ProductTemplate.objects.count()}')

    def create_receipts_and_issues(self):
        """Создание приемок и отпусков материалов"""
        admin_user = User.objects.filter(username='azama').first()
        contractor = Contractor.objects.filter(contractor_type='supplier').first()
        materials = list(Material.objects.all()[:3])
        
        if not admin_user or not contractor or not materials:
            return
        
        created_receipts = 0
        created_issues = 0

        for index, material in enumerate(materials, start=1):
            receipt, created = Receipt.objects.get_or_create(
                material=material,
                document_number=f'RCPT-{index:04d}',
                defaults={
                    'quantity': 100 + index * 25,
                    'price': material.price_per_unit or 0,
                    'contractor': contractor,
                    'created_by': admin_user,
                    'notes': f'Тестовая приемка материала {material.name}',
                }
            )
            if created:
                created_receipts += 1

            issue, created = Issue.objects.get_or_create(
                material=material,
                issued_to='Производственный цех',
                purpose=f'Плановый расход материала {material.name}',
                defaults={
                    'quantity': 10 + index * 3,
                    'destination': 'Швейный участок',
                    'created_by': admin_user,
                }
            )
            if created:
                created_issues += 1
        
        self.stdout.write(f'✅ Приемки: создано {created_receipts}, всего {Receipt.objects.count()}')
        self.stdout.write(f'✅ Расходы: создано {created_issues}, всего {Issue.objects.count()}')

    def create_products(self):
        """Создание готовых продуктов"""
        template = ProductTemplate.objects.first()
        admin_user = User.objects.filter(username='azama').first()
        if not template or not admin_user:
            return
        
        created_count = 0
        for i in range(5):
            product, created = Product.objects.get_or_create(
                batch_number=f'BATCH-001-{i+1:03d}',
                defaults={
                    'template': template,
                    'size': '50-52',
                    'color': 'Темно-синий',
                    'status': 'ready',
                    'selling_price': 5500.00,
                    'markup_percent': 15.0,
                    'production_date': timezone.now().date(),
                    'produced_by': admin_user,
                    'quantity_produced': 10
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ Продукты: создано {created_count}, всего {Product.objects.count()}')

    def create_shipments(self):
        """Создание отправок продукции"""
        admin_user = User.objects.filter(username='azama').first()
        customer = Contractor.objects.filter(contractor_type='customer').first()
        product = Product.objects.first()
        
        if not admin_user or not customer or not product:
            return
        
        created_count = 0
        for i in range(2):
            shipment, created = ProductShipment.objects.get_or_create(
                product=product,
                shipped_to=customer,
                shipment_date=timezone.now().date() - timedelta(days=i*10),
                document_number=f'DOC-{i+1:04d}',
                defaults={
                    'shipped_by': admin_user,
                    'quantity': 10 + i*5,
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ Отправки: создано {created_count}, всего {ProductShipment.objects.count()}')
