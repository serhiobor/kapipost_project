from django.urls import reverse
from django.test import TestCase, Client
from ..forms import CreationForm


class UserViewTest(TestCase):
    '''Проверка view-функции signup'''
    def setUp(self) -> None:
        self.guest_client = Client()
        self.reverse_url = reverse('users:signup')
        self.template = 'users/signup.html'
        self.response = self.guest_client.get(self.reverse_url)

    def test_signup_page_returns_correct_template(self):
        '''Проверка на возврат signup корректного шаблон'''
        self.assertTemplateUsed(self.response, self.template)

    def test_login_return_form(self):
        '''Проверка, что signup возвращает форму регистрации'''
        self.assertIsInstance(self.response.context.get('form'), CreationForm)
