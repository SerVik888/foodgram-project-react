from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render
from rest_framework.views import exception_handler


def page_not_found(exc, context):
    """Для обработки кастомной страниы с ошибкой 404."""
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    if not settings.DEBUG:
        if response.data['status_code'] == 404:
            return render(context.get("request"), 'pages/404.html', status=404)
    return response


def download_file(data, name):
    """Метод для скачивания файла."""
    with open(f'{name}.txt', '+w', encoding='utf-8') as file:
        file.write(data)
        file.close()
    return FileResponse(open(f'{name}.txt', 'rb'))
