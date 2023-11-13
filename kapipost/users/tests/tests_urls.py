from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class UserURLTest(TestCase):
    '''User URLs testing'''
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # test user (author)
        cls.test_user = User.objects.create_user(  # type: ignore
            username='test_user'
        )

    def setUp(self) -> None:
        # unauthorized client
        self.guest_client = Client()
        # authorized as test_user client
        self.auth_client = Client()
        self.auth_client.force_login(user=self.test_user)
        # list of clients
        self.clients: list[Client] = [
            self.guest_client,
            self.auth_client,
        ]

    def test_page_response_for_unauth_users(self) -> None:
        '''Test: access to pages for an unauthorized user.'''
        url_adress_and_templates: dict[str, str] = {
            reverse(viewname='users:signup'): 'users/signup.html',
            reverse(viewname='users:login'): 'users/login.html',
            reverse(viewname='users:password_reset'):
            'users/password_reset_form.html',
            reverse(viewname='users:password_reset_done'):
            'users/password_reset_done.html',
            reverse(viewname='users:password_reset_complete'):
            'users/password_reset_complete.html',
        }
        for url_adress, template in url_adress_and_templates.items():
            with self.subTest(url_adress=url_adress):
                response: HttpResponse = self.guest_client.get(path=url_adress)
                self.assertEqual(
                    first=response.status_code,
                    second=HTTPStatus.OK,
                    msg=f'{url_adress} is not available to unauthorized user'
                )
                self.assertTemplateUsed(
                    response=response,
                    template_name=template,
                    msg_prefix=f'''Template of "{url_adress}" does not match
                    the requested one "{template}"'''
                )

    def test_redirects_for_unauth_users(self) -> None:
        '''
        Test: redirects for unauthorized clients
        '''
        url_and_redirects: dict[str, str] = {
            reverse(viewname='users:password_change'):
            '/auth/login/?next=/auth/password_change/',
            reverse(viewname='users:password_change_done'):
            '/auth/login/?next=/auth/password_change/done/',
            reverse(viewname='users:logout'): '/',
        }
        for url_adress, redirect in url_and_redirects.items():
            with self.subTest(url_adress=url_adress):
                response: HttpResponse = self.guest_client.get(path=url_adress)
                self.assertEqual(
                    first=response.status_code,
                    second=HTTPStatus.FOUND,
                    msg=f'''Redirect does not works for unauthorized clients,
                    url "{url_adress}"'''
                )
                self.assertRedirects(
                    response=response,
                    expected_url=redirect,
                    msg_prefix=f'''Redirect does not works for unauthorized
                    clients, url "{url_adress}"'''
                )

    def test_page_response_for_auth_users(self) -> None:
        '''
        Test: page access and template matches for authorized client
        '''
        template_url_names: dict[str, str] = {
            reverse(viewname='users:signup'): 'users/signup.html',
            reverse(viewname='users:login'): 'users/login.html',
            reverse(viewname='users:password_reset'):
            'users/password_reset_form.html',
            reverse(viewname='users:password_reset_done'):
            'users/password_reset_done.html',
            reverse(viewname='users:password_change'):
            'users/password_change_form.html',
            reverse(viewname='users:password_change_done'):
            'users/password_change_done.html',
            reverse(viewname='users:password_reset_complete'):
            'users/password_reset_complete.html',
        }
        for url_adress, template in template_url_names.items():
            with self.subTest(url_adress=url_adress):
                response = self.auth_client.get(path=url_adress)
                self.assertEqual(
                    first=response.status_code,
                    second=HTTPStatus.OK,
                    msg=f'Status code of url "{url_adress}" is not 200')
                self.assertTemplateUsed(
                    response=response,
                    template_name=template,
                    msg_prefix=f'''Template of "{url_adress}" does not match
                    the requested one "{template}"'''
                    )
        # and logout
        response: HttpResponse = self.auth_client.get(
            path=reverse(viewname='users:logout'))
        self.assertEqual(first=response.status_code, second=HTTPStatus.FOUND)
