from django.shortcuts import render
from rest_framework.views import exception_handler

from foodgram.settings import DEBUG


def page_not_found(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data['status_code'] = response.status_code
    if not DEBUG:
        if response.data['status_code'] == 404:
            return render(context.get("request"), 'pages/404.html', status=404)
    return response
