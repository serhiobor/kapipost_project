from typing import Any, Dict
from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    '''About author.'''
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context['title'] = 'About author'
        return context


class AboutTechView(TemplateView):
    '''Abouth the technologies used.'''
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Technologies used'
        return context
