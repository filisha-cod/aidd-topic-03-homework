# Investing Demo (modernized)

## Быстрый запуск БЕЗ токена Tinkoff

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Открой http://127.0.0.1:8000/ — увидишь 5 демо-акций с историей цен и графиками.

## С T-Invest API (опционально)

```powershell
pip install t-tech-investments --index-url https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple
```

В `.env` укажи `TINKOFF_TOKEN=...`, затем:

```powershell
python manage.py add_shares
```

Импорт в коде: `from t_tech.invest import Client`  
(старый `from tinkoff.invest import ...` тоже поддерживается через совместимый слой).

## Команды

| Команда | Описание |
|---------|----------|
| `python manage.py seed_demo` | Демо-акции + история цен (без API) |
| `python manage.py seed_demo --days 60 --clear` | Пересоздать демо за 60 дней |
| `python manage.py add_shares` | Загрузить акции из T-Invest API |

## Что сделано

- Django 4.2+, Bootstrap 5, SQLite
- Исправлены баги (detetime, None-сравнение, точность цены)
- История цен + страница `/<id>/history/`
- Работа без TOKEN на демо-данных
- Совместимость с `t_tech.invest` и старым `tinkoff.invest`
