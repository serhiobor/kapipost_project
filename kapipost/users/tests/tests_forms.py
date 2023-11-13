from django.http import HttpResponse
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUsersForm(TestCase):
    '''User-app forms testing'''

    def setUp(self) -> None:
        # test client
        self.client = Client()
        # signup url
        self.url_name: str = reverse(viewname='users:signup')

    def test_signup_form_has_correct_field_values(self) -> None:
        '''
        Template formed with correct context
        '''
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        response: HttpResponse = self.client.get(path=self.url_name)
        for field_value, expected in form_fields.items():
            with self.subTest(value=field_value):
                form_field = response.context.get(
                    key='form').fields.get(field_value)
                self.assertIsInstance(
                    obj=form_field,
                    cls=expected,
                    msg=f'''field type {field_value} at the
                    {self.url_name} does not match the expected'''
                )

    def test_for_signup_form_create_new_user(self) -> None:
        '''Test: filled form let create a new user'''
        form_data: dict[str, str] = {
            'first_name': 'TestUser',
            'last_name': 'TestUser',
            'username': 'TestUser',
            'email': 'test@gmail.com',
            'password1': '123456_qwerty',
            'password2': '123456_qwerty',
        }
        self.client.post(
            path=self.url_name,
            data=form_data,
            follow=True)
        self.assertTrue(
            expr=User.objects.filter(username='TestUser').exists(),
            msg="Signup form don't create user"
            )
