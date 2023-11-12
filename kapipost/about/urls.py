from django.urls import path, URLPattern
from . import views

app_name = 'about'

urlpatterns: list[URLPattern] = [
    # about author page
    path(route='author/', view=views.AboutAuthorView.as_view(), name='author'),
    # about technologies page
    path(route='tech/', view=views.AboutTechView.as_view(), name='tech'),
]
