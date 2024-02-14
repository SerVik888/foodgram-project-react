# Проект Foodgram
![event parameter](https://github.com/SerVik888/foodgram-project-react/actions/workflows/main.yml/badge.svg?event=push)\
*Адрес сайта - https://safonov-sergey.ru*
*Документация - https://safonov-sergey.ru/api/docs/*

### Описание проекта:
Foodgram - Это сеть, где люди могут размещать рецепты. Здесь можно добавить, изменить или удалить рецепты, но для этого нужно зарегистрироваться иначе данные доступны только для просмотра. Изменять данные чужих рецептов нельзя, они доступны только для просмотра. Так же вы можете добавлять любые рецепты в избранное и список покупок потом список покупок можно скачать файлом.

### Как запустить проект:
`git clone git@github.com:SerVik888/foodgram-project-react.git` -> клонировать репозиторий

**При помощи docker**\
    Перед началом нужно установить и запустить Docker.\
    Из корня проекта выполнить команды\
    `docker-compose up` -> запустить Docker Compose\
    `docker compose exec backend python manage.py migrate` -> выполнить миграции\
    `docker compose exec backend python manage.py createsuperuser` -> создать суперпользователя\
    `docker-compose stop` -> остановить Docker Compose

*После запуска контейнеров будет доступна документация по адресу http://localhost/api/docs/.*

**Без docker**

Запуск backend

`cd backend` -> перейти в папку

* Если у вас Linux/macOS\
    `python3 -m venv env` -> создать виртуальное окружение\
    `source env/bin/activate` -> активировать виртуальное окружение\
    `python3 -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    `python3 manage.py migrate` -> выполнить миграции\
    `python3 manage.py createsuperuser` -> создать суперпользователя\
    `python3 manage.py runserver` -> запустить проект\
    `python3 manage.py import_csv` -> загрузка данных из файлов csv

* Если у вас windows\
    `python -m venv venv` -> создать виртуальное окружение\
    `source venv/Scripts/activate` -> активировать виртуальное окружение\
    `python -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    `python manage.py migrate` -> выполнить миграции\
    `python manage.py createsuperuser` -> создать суперпользователя\
    `python manage.py runserver` -> запустить проект\
    `python manage.py import_csv` -> загрузка данных из файлов csv

Запуск frontend нужно выполнять в другом терминале

`cd frontend` -> перейти в папку\
`npm i` -> установить зависимости\
`npm run start` -> запуск приложения

### Как тестировать проект:
Коллекция запросов для Postman Для тестирования и отладки работы текущей версии API для проекта Foodgram, мы предоставляем коллекцию запросов для Postman. Вы можете импортировать эту коллекцию в Postman и выполнять запросы для проверки функциональности API.

Подробная инструкция по работе с коллекцией находится в файле /postman_collection/README.md.

### Cписок используемых технологий:

- Django
- React
- djangorestframework
- Docker

### Как заполнить файл .env:
В проекте есть файл .env.example заполните свой по аналогии.

`POSTGRES_DB` - название базы\
`POSTGRES_USER` - пользователь базы\
`POSTGRES_PASSWORD` - пароль к базе\
`DB_NAME` - имя базы\
`DB_HOST` - имя контейнера, где запущен сервер БД\
`DB_PORT` - порт, по которому Django будет обращаться к базе данных\
`DB_SQLIGTH` - если эта переменная есть используется база sqlite если нет то postgres\
`SECRET_KEY` - ключ проекта\
`DEBUG` - режим дебаггинга\
`ALLOWED_HOSTS` - разрешённые хосты\

Автор: Сафонов Сергей\
Почта: [sergey_safonov86@inbox.ru](mailto:sergey_safonov86@inbox.ru)