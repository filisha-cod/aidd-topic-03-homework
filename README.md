# Investing Demo — Agent B

Вторая независимая ветка домашнего задания (другой AI Coding Agent).

## Новая функциональность

**Виртуальный инвестиционный портфель**
- создание персональных портфелей
- покупка / продажа акций (моделирование)
- средняя цена позиции, текущая стоимость, P&L
- журнал операций

## Запуск без токена

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

1. Зарегистрируйтесь / войдите  
2. Откройте **Портфели** → создайте портфель  
3. Совершите покупку/продажу по демо-акциям  

## SDK (опционально)

```powershell
pip install t-tech-investments --index-url https://opensource.tbank.ru/api/v4/projects/238/packages/pypi/simple
```
