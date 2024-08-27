# Проект "Gazprom"

Проект представляет собой MVP web-приложение для структурирования организации по проектам и командам. Для удобного
поиска участников, их статистических данных. Редактирование команд в виде дерева.

[![Code check](https://github.com/hackathon-Gazprom/Backend/actions/workflows/code_check.yml/badge.svg?branch=dev)](https://github.com/hackathon-Gazprom/Backend/actions/workflows/code_check.yml)

## Стек технологий

<p>
    <a href="https://www.djangoproject.com/">
        <img alt="Django" src="https://img.shields.io/badge/django-%23092E20.svg?&style=for-the-badge&logo=django&logoColor=white">
    </a>
    <a href="https://www.django-rest-framework.org/">
        <img alt="Django-REST-Framework" src="https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray">
    </a>
    <a href="https://www.postgresql.org/">
        <img alt="PostgreSQL" src="https://img.shields.io/badge/postgresql-%23336791.svg?&style=for-the-badge&logo=postgresql&logoColor=white">
    </a>
    <a href="https://redis.io">
        <img alt="PostgreSQL" src="https://img.shields.io/badge/redis-%23DC382D.svg?&style=for-the-badge&logo=redis&logoColor=white">
    </a>
    <a href="https://nginx.org/ru/">
        <img alt="Nginx" src="https://img.shields.io/badge/nginx-%23269539.svg?&style=for-the-badge&logo=nginx&logoColor=white">
    </a>
    <a href="https://gunicorn.org/">
        <img alt="gunicorn" src="https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white">
    </a>
    <a href="https://www.docker.com/">
        <img alt="docker" src="https://img.shields.io/badge/docker-%232496ED.svg?&style=for-the-badge&logo=docker&logoColor=white">
    </a>
</p>

### Ссылка на [Сайт](https://gazprom.hopto.org/)


```json
// админские данные
{
  "email": "admin@admin.com",
  "password": "admin"
}
// тестовые данные
{
  "email": "test@fake.com",
  "password": "test"
}
```

### Ссылка на [Swagger](https://gazprom.hopto.org/api/swagger/)


## Запуск

```shell
# Склонировать репозиторий
git clone git@github.com:hackathon-Gazprom/Backend.git
```

```shell
# установить и активировать виртуальное окружение
python -m venv venv
source .\venv\Scripts\activate

# установить зависимости
pip install -r requirements.txt

# перейти в папку с приложением
cd .\src\backend\

# сделать миграции
python manage.py migrate

# заполнить базу данных моковскими данными
python manage.py add_fake_data

# запустить сервер
python manage.py runserver
```

## Запуск через Docker

> [!IMPORTANT]
> Необходимо создать файл `.env` с переменными окружения в папке `infra`.</br>
> Пример файла [.env.example](infra/.env.example)

```shell
# перейти в папку с докером
cd .\infra\

# запустить докер
docker compose up --build -d

# заполнить базу данных моковскими данными
docker compose exec backend python manage.py add_fake_data
```

## Автор:

[<span><img src="https://cdn-icons-png.flaticon.com/128/906/906377.png" height="25" align="center" alt="Telegram" title="Telegram" style="right" /></span>](https://t.me/mxnoob) [Воробьев Кирилл](https://www.github.com/mxnoob) 
