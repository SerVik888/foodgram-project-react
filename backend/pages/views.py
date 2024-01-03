from django.shortcuts import render


def page_not_found(request, exception):
    """Функция для обработки ошибок"""
    return render(request, 'pages/404.html', status=404)
