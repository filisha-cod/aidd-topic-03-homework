# ANALYSIS.md — Анализ приложения Investing Demo

## 1. Назначение приложения и технологический стек

**Назначение:**  
Веб-приложение «Investing Demo» — демонстрационный дашборд для просмотра и управления списком акций (shares). Пользователи могут просматривать список акций с текущими ценами, детальную информацию с графиком изменения цены за 180 дней, добавлять/редактировать/удалять акции (только авторизованные). Цены обновляются периодически через Celery-задачи с использованием Tinkoff Invest API. Предусмотрен REST API для CRUD-операций над акциями.

**Технологический стек (исходный):**
- **Backend:** Python, Django 4.1.7
- **API:** Django REST Framework 3.14.0 + django-filter
- **БД:** PostgreSQL (psycopg2-binary)
- **Асинхронные задачи:** Celery 5.2.7 + Redis (broker)
- **Рыночные данные:** tinkoff-investments (0.2.0b50) / tinkoff
- **Визуализация:** Plotly 5.13.1
- **UI:** Bootstrap 3/4 (через crispy-forms + bootstrap3), Font Awesome, jQuery
- **Аутентификация:** Django Auth (кастомные формы с email в качестве username)
- **Инфраструктура:** Docker Compose (PostgreSQL), management-команда `add_shares`
- **Тесты:** Django TestCase + APIClient

## 2. Структура проекта, основные компоненты и их назначение

```
investing/
├── config/                 # Настройки Django-проекта
│   ├── settings.py         # Основные настройки, Celery, TINKOFF_TOKEN, БД
│   ├── urls.py             # Корневые URL
│   ├── celery.py           # Конфигурация Celery
│   ├── asgi.py / wsgi.py
├── dashboard/              # Основное приложение (акции)
│   ├── models.py           # Модель Share
│   ├── views.py            # Class-based views (List, Detail, Create, Update, Delete)
│   ├── forms.py            # ShareModelForm
│   ├── urls.py
│   ├── admin.py
│   ├── tasks.py            # Celery-задача update_last_price
│   ├── services/
│   │   ├── market_data.py  # Получение последней цены через Tinkoff
│   │   └── graph.py        # Построение графика Plotly
│   ├── api/v1/             # REST API (ViewSet + Serializer)
│   ├── management/commands/add_shares.py  # Загрузка акций из API
│   ├── templates/dashboard/
│   ├── static/
│   └── tests.py
├── user/                   # Аутентификация и регистрация
│   ├── forms.py            # RegistrationForm, AuthForm
│   ├── views.py            # AuthView, RegistrationView, LogoutView
│   ├── urls.py
│   └── templates/user/
├── docker-compose.yml      # PostgreSQL
├── requirements.txt
├── manage.py
└── README.md
```

**Основные компоненты:**
- `Share` — центральная сущность.
- `ShareListView` / `ShareDetailView` — публичный просмотр.
- CRUD-views с `IsUserAuthenticatedMixin` (UserPassesTestMixin).
- Celery task `update_last_price` — периодическое обновление цен и флага тренда.
- REST API `/api/v1/shares/` — полный CRUD.
- Management command — первоначальное наполнение БД акциями из Tinkoff.

## 3. Архитектура приложения и взаимодействие компонентов

**Архитектура:** Классический монолит Django (MTV) + REST API + фоновые задачи.

```
[Browser] ←→ [Django Views / Templates] ←→ [Models / ORM] ←→ [PostgreSQL]
                 ↑                                    ↑
[DRF ViewSet] ←──┘                                    │
                                                      │
[Celery Worker] ←→ [Redis] ←→ [Beat] ──→ [tasks.update_last_price]
                 ↓
         [Tinkoff Invest gRPC API]
                 ↓
         [services.market_data / graph]
```

- Пользовательский интерфейс — server-rendered templates (Bootstrap).
- API — stateless REST.
- Обновление цен — асинхронно через Celery (не блокирует веб).
- Аутентификация — session-based (Django).
- График строится «на лету» при открытии детальной страницы (запрос к Tinkoff за 180 дней свечей).

## 4. Используемые библиотеки и внешние зависимости

См. `requirements.txt`. Ключевые:
- Django + DRF + django-filter + crispy-forms
- Celery + Redis + kombu + billiard
- tinkoff-investments (устаревший beta)
- plotly
- psycopg2-binary
- grpcio, protobuf (для Tinkoff)

Внешние сервисы:
- Tinkoff Invest API (требуется токен)
- PostgreSQL
- Redis

## 5. Модель данных: сущности, атрибуты и связи

**Единственная бизнес-сущность — Share:**

| Поле          | Тип              | Ограничения          | Описание                          |
|---------------|------------------|----------------------|-----------------------------------|
| id            | BigAutoField     | PK                   |                                   |
| figi          | CharField(255)   | unique               | FIGI инструмента Tinkoff          |
| isin          | CharField(255)   |                      | ISIN                              |
| name          | CharField(255)   |                      | Наименование компании             |
| ticker        | CharField(10)    | unique               | Тикер                             |
| currency      | CharField(20)    |                      | Валюта                            |
| uid           | CharField(255)   | unique               | UID Tinkoff                       |
| last_price    | FloatField       | null/blank           | Последняя известная цена          |
| is_trend_high | BooleanField     | null/blank           | True = цена выросла/не упала      |
| updated_at    | DateTimeField    | auto_now             | Время последнего обновления       |

Связей с другими моделями нет. Пользователи — стандартный Django User (username = email).

Миграции: 0001–0007 (поэтапное добавление полей).

## 6. Механизмы обработки пользовательских запросов и взаимодействия с БД

- **Список акций:** `ShareListView` → `Share.objects.all().order_by("name")` + pagination (100).
- **Детальная:** `Share.objects.get(id=pk)` + вызов `get_graph(share)` (внешний API).
- **CRUD:** стандартные CBV + `ShareModelForm` (fields="__all__").
- **Авторизация:** кастомные FormView-подобные views; `authenticate(username=email)`.
- **API:** ModelViewSet + ShareSerializer + фильтрация.
- **Обновление цен:** Celery task итерирует все Share, вызывает `get_last_data`, обновляет `last_price` и `is_trend_high` через `filter().update()`.
- **Загрузка акций:** management command использует Tinkoff Client для получения списка shares и bulk_create/update.

**Взаимодействие с БД:** только через Django ORM. Нет raw SQL.

---

## Восстановленные функциональные требования (Задание №2)

На основании анализа исходного кода восстановлены **фактически реализованные** требования:

1. **Система должна позволять любому пользователю просматривать список акций** с отображением тикера, названия, ISIN, текущей цены и цветовой индикации тренда (зелёный/красный). Подтверждение: `ShareListView`, шаблон `list.html`, поле `is_trend_high`.

2. **Система должна поддерживать пагинацию списка акций** (по 100 записей на страницу). Подтверждение: `paginate_by = 100` в `ShareListView`.

3. **Система должна позволять просматривать детальную страницу акции** с графиком изменения цены закрытия за последние 180 дней (дневные свечи). Подтверждение: `ShareDetailView` + `get_graph()` + Plotly Scatter.

4. **Только аутентифицированные пользователи могут создавать, редактировать и удалять акции.** Подтверждение: `IsUserAuthenticatedMixin` на Create/Update/Delete views; кнопки в шаблонах отображаются только при `user.is_authenticated`.

5. **Система должна предоставлять формы создания/редактирования акций** со всеми полями модели Share. Подтверждение: `ShareModelForm` (fields="__all__"), шаблон `create.html`.

6. **Система должна предоставлять подтверждение удаления акции.** Подтверждение: `ShareDeleteView` + шаблон `delete.html`.

7. **Система должна поддерживать регистрацию пользователей по email и паролю** с проверкой совпадения паролей и уникальности email. Подтверждение: `RegistrationForm.clean()` и `.save()`.

8. **Система должна поддерживать вход/выход пользователей** (email + пароль). Подтверждение: `AuthView`, `LogoutView`.

9. **Система должна периодически обновлять последнюю цену и направление тренда всех акций** через фоновую задачу. Подтверждение: `tasks.update_last_price` + `get_last_data`.

10. **Система должна предоставлять REST API** для полного CRUD операций над акциями с пагинацией и фильтрацией. Подтверждение: `ShareViewSet`, `ShareSerializer`, router, `tests.py`.

11. **Система должна позволять администратору управлять акциями** через Django Admin. Подтверждение: `ShareAdmin`.

12. **Система должна предоставлять management-команду для первоначальной загрузки списка акций** из Tinkoff Invest API. Подтверждение: `add_shares.py`.

### Выявленные неоднозначности, противоречия и дефекты реализации

- **Дефект:** В `tasks.py` переменная названа `detetime` (опечатка), значение времени не используется.
- **Дефект:** Сравнение `share.last_price > last_price` падает с TypeError при `last_price=None` (обрабатывается слишком широко try/except).
- **Дефект:** `get_last_data` и `get_graph` используют только `.units` цены, игнорируя `.nano` (потеря точности).
- **Дефект:** `SECRET_KEY = ""` и `TINKOFF_TOKEN = ""` — приложение не запускается «из коробки».
- **Дефект:** `IsUserAuthenticatedMixin.handle_no_permission` всегда редиректит на index, а не на login.
- **Неоднозначность:** Нет явной настройки расписания Celery Beat (в коде отсутствует `CELERY_BEAT_SCHEDULE`).
- **Дефект:** RegistrationForm создаёт пользователя с `User.objects.create_user(email, email, password)` — работает, но username=email.
- **Устаревшие зависимости:** Django 4.1, старый beta tinkoff-investments, Bootstrap 3/4 mix, старые версии Celery/Redis-клиентов.
- **Отсутствие:** Нет модели истории цен, нет персональных watchlist/портфелей (это и есть предмет Задания №4).

Эти дефекты **не** включены в список функциональных требований, т.к. описывают реализованное (пусть и с ошибками) поведение.
