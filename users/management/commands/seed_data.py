from django.core.management.base import BaseCommand

from projects.models import Project
from users.models import User


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей и проекты"

    def handle(self, *args, **options):
        users_data = [
            {"email": "alice@example.com", "name": "Alice", "surname": "Smith", "password": "pass1234", "phone": "+79161234567"},
            {"email": "bob@example.com",   "name": "Bob",   "surname": "Jones", "password": "pass1234", "phone": "+79261234567"},
            {"email": "carol@example.com", "name": "Carol", "surname": "White", "password": "pass1234", "phone": "+79361234567"},
            {"email": "linus@example.com", "name": "Linus", "surname": "Torvalds", "password": "pass1234", "phone": "+79121234451", "about": "ищи в гугле самая лучшая ОС там будет LINUX"},
            {"email": "dave@example.com",  "name": "Dave",  "surname": "Brown", "password": "pass1234", "phone": "+79461234567"},
            {"email": "eve@example.com",   "name": "Eve",   "surname": "Davis", "password": "pass1234", "phone": "+79561234567"},
            {"email": "frank@example.com", "name": "Frank", "surname": "Miller", "password": "pass1234", "phone": "+79661234567"},
            {"email": "grace@example.com", "name": "Grace", "surname": "Wilson", "password": "pass1234", "phone": "+79761234567"},
            {"email": "henry@example.com", "name": "Henry", "surname": "Moore", "password": "pass1234", "phone": "+79861234567"},
            {"email": "iris@example.com",  "name": "Iris",  "surname": "Taylor", "password": "pass1234", "phone": "+79961234567"},
            {"email": "jack@example.com",  "name": "Jack",  "surname": "Anderson", "password": "pass1234", "phone": "+79071234567"},
            {"email": "kate@example.com",  "name": "Kate",  "surname": "Thomas", "password": "pass1234", "phone": "+79081234567"},
            {"email": "leo@example.com",   "name": "Leo",   "surname": "Jackson", "password": "pass1234", "phone": "+79091234567"},
            {"email": "mia@example.com",   "name": "Mia",   "surname": "White", "password": "pass1234", "phone": "+79101234567"},
            {"email": "noah@example.com",  "name": "Noah",  "surname": "Harris", "password": "pass1234", "phone": "+79111234567"},
            {"email": "olivia@example.com","name": "Olivia","surname": "Martin", "password": "pass1234", "phone": "+79121234567"},
        ]

        created_users = []
        for data in users_data:
            email = data["email"]
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                self.stdout.write(f"Пользователь {email} уже существует")
            else:
                user = User.objects.create_user(
                    email=email,
                    name=data["name"],
                    surname=data["surname"],
                    password=data["password"],
                    phone=data["phone"],
                )
                if "about" in data:
                    user.about = data["about"]
                    user.save(update_fields=["about"])
                self.stdout.write(self.style.SUCCESS(f"Создан пользователь {email}"))
            created_users.append(user)

        alice, bob, carol, linus = created_users[:4]
        extra_users = created_users[4:]

        projects_data = [
            {
                "name": "Open Source Todo App",
                "description": "Простое приложение для управления задачами на Django и React.",
                "owner": alice,
                "github_url": "https://github.com/alice/todo-app",
                "status": Project.STATUS_OPEN,
            },
            {
                "name": "ML Image Classifier",
                "description": "Классификатор изображений на PyTorch с REST API.",
                "owner": bob,
                "github_url": "https://github.com/bob/image-clf",
                "status": Project.STATUS_OPEN,
            },
            {
                "name": "Portfolio Generator",
                "description": "Генератор портфолио из GitHub-репозиториев.",
                "owner": carol,
                "github_url": "https://github.com/carol/portfolio-gen",
                "status": Project.STATUS_CLOSED,
            },
            {"name": "Telegram Bot для новостей", "description": "Бот собирает новости из RSS и отправляет в Telegram.", "owner": extra_users[0], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "CRM для малого бизнеса", "description": "Управление клиентами и продажами.", "owner": extra_users[1], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "Сайт-визитка фотографа", "description": "Портфолио с галереей работ.", "owner": extra_users[2], "github_url": "https://github.com/frank", "status": Project.STATUS_OPEN},
            {"name": "Мобильное приложение для йоги", "description": "Трекер тренировок и медитаций.", "owner": extra_users[3], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "Парсер цен маркетплейсов", "description": "Мониторинг цен на Wildberries и Ozon.", "owner": extra_users[4], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "Онлайн-курс по Python", "description": "Платформа с видеоуроками и тестами.", "owner": extra_users[5], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "Чат-бот поддержки", "description": "Автоматические ответы на частые вопросы.", "owner": extra_users[6], "github_url": "https://github.com", "status": Project.STATUS_CLOSED},
            {"name": "Трекер привычек", "description": "Приложение для формирования полезных привычек.", "owner": extra_users[7], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "API для погодного виджета", "description": "REST API с кэшированием данных.", "owner": extra_users[8], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "Блог о путешествиях", "description": "Личный блог с фото и заметками.", "owner": extra_users[9], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "Сервис сокращения ссылок", "description": "Аналог bit.ly с аналитикой.", "owner": extra_users[10], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {"name": "Планировщик задач для команд", "description": "Kanban-доска для небольших команд.", "owner": extra_users[11], "github_url": "https://github.com", "status": Project.STATUS_OPEN},
            {
                "name": "Linux",
                "description": "Лучшая операционная система",
                "owner": linus,
                "github_url": "https://github.com/torvalds/linux",
                "status": Project.STATUS_OPEN,
            },
        ]

        for data in projects_data:
            if Project.objects.filter(name=data["name"]).exists():
                self.stdout.write(f"Проект '{data['name']}' уже существует")
                continue
            project = Project.objects.create(**data)
            project.participants.add(data["owner"])
            self.stdout.write(self.style.SUCCESS(f"Создан проект '{data['name']}'"))

        # добавляем несколько участников и избранных для демонстрации
        proj1 = Project.objects.filter(name="Open Source Todo App").first()
        proj2 = Project.objects.filter(name="ML Image Classifier").first()

        if proj1 and proj2:
            proj1.participants.add(bob)
            proj2.participants.add(alice)
            carol.favorites.add(proj1)
            alice.favorites.add(proj2)
            self.stdout.write(self.style.SUCCESS("Добавлены участники и избранные"))

        self.stdout.write(self.style.SUCCESS("Готово! Тестовые данные созданы."))
