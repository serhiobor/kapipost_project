from django.http import HttpResponse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from http import HTTPStatus

User = get_user_model()


class AboutURLTest(TestCase):
    '''About-app testing.'''
    # URLs for about-app pages: template
    template_url_names: dict[str, str] = {
        reverse(viewname='about:author'): 'about/author.html',
        reverse(viewname='about:tech'): 'about/tech.html',
    }

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create test-user
        cls.test_user = User.objects.create_user(  # type: ignore
            username='test_user'
        )

    def setUp(self) -> None:
        # unauthorised client
        self.guest_client = Client()
        # client unauthorised as test_user
        self.auth_client = Client()
        self.auth_client.force_login(user=AboutURLTest.test_user)
        # list of clients
        self.clients: list[Client] = [
            self.guest_client,
            self.auth_client,
        ]

    def test_about_pages_response(self) -> None:
        '''
        Test: if About-app pages are available.
        '''
        for reverse_url, template in self.template_url_names.items():
            with self.subTest(url_adress=reverse_url):
                for client in self.clients:
                    response: HttpResponse = client.get(path=reverse_url)
                    self.assertEqual(
                        first=response.status_code, second=HTTPStatus.OK,
                        msg=f'{reverse_url} is unavailable')
                    self.assertTemplateUsed(
                        response=response, template_name=template,
                        msg_prefix=f'{reverse_url} returns incorrect template')
