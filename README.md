# praktikum_new_diplom
<!-- TODO Нужно переписать папку в которую нужно перейти перед тем как запускать сборку -->
<!-- TODO Переписать описание проекта -->
<!-- TODO Переписать event parameter -->

![branch parameter](https://github.com/SerVik888/kittygram_final/actions/workflows/main.yml/badge.svg?branch=main)

![event parameter](https://github.com/SerVik888/kittygram_final/actions/workflows/main.yml/badge.svg?event=push)

### Описание проекта kittygram_final
Kittygram - Это сеть, где люди могут размещать фотографии и некоторые данные о своих питомцах. Здесь можно добавить, изменить или удалить данные о своих питомцах, но для этого нужно зарегистрироваться иначе данные доступны только для просмотра. Изменять данные чужих питомцев тоже нельзя, они доступны только для просмотра.

### Cписок используемых технологий

- Django
- React
- pytest
- djangorestframework
- Docker

### Как запустить проект:
`git clone git@github.com:SerVik888/foodgram-project-react.git` -> клонировать репозиторий

**При помощи docker**\
    Перед началом нужно установить и запустить Docker.

    `cd nginx` -> перейти в папку
    `docker-compose up` -> запустить Docker Compose
    `docker-compose stop` -> остановить Docker Compose

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
    `python3 manage.py runserver` -> запустить проект

* Если у вас windows\
    `python -m venv venv` -> создать виртуальное окружение\
    `source venv/Scripts/activate` -> активировать виртуальное окружение\
    `python -m pip install --upgrade pip` -> обновить установщик\
    `pip install -r requirements.txt` -> установить зависимости из файла requirements.txt\
    `python manage.py migrate` -> выполнить миграции\
    `python manage.py createsuperuser` -> создать суперпользователя\
    `python manage.py runserver` -> запустить проект

Запуск frontend нужно выполнять в другом терминале

`cd frontend` -> перейти в папку\
`npm i` -> установить зависимости\
`npm run start` -> запуск приложения

### Загрузка данных из файлов csv
    `python manage.py import_csv`

*Подробное описание доступных эндпоинтов проекта будет доступно в документации по адресу http://localhost/api/docs/redoc.html после запуска проекта.*

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

Автор:
Сафонов Сергей https://github.com/SerVik888 [sergey_safonov86@inbox.ru](mailto:sergey_safonov86@inbox.ru)