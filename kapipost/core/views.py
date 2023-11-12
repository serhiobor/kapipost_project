from django.http import HttpResponse
from django.shortcuts import render


def page_not_found(request, exception) -> HttpResponse:
    '''404-view'''
    return render(
        request=request,
        template_name='core/404.html',
        context={
            'path': request.path,
            'title': 'Ooops, something went wrong...'},
        status=404
    )


def csrf_failure(request, reason='') -> HttpResponse:
    return render(request=request, template_name='core/403csrf.html')
