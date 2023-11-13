from django.core.cache import cache
from django.http import HttpResponse
from django.test import TestCase, Client, override_settings
from ..models import Post, Group, User
from http import HTTPStatus

TEMP_CACHES = {}


class PostURLTest(TestCase):
    '''Tests for URLs of Post-app.'''
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create user (author)
        cls.test_user_author = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # create user (non-author)
        cls.test_user_non_author = User.objects.create_user(  # type: ignore
            username='test_non_author'
        )
        # create group
        cls.test_group: Group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test group description'
        )
        # create test-post
        cls.test_post: Post = Post.objects.create(
            text='Test post',
            author=cls.test_user_author
        )
        # dictionary: URLs and templates
        cls.url_adress_and_templates: dict[str, str] = {
            '/group/test_group/': 'posts/group_list.html',
            '/posts/test_author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

    def setUp(self) -> None:
        # unauthorized client
        self.guest_client = Client()
        # authorized client (non author)
        self.auth_client = Client()
        self.auth_client.force_login(user=self.test_user_non_author)
        # author-client
        self.author_client = Client()
        self.author_client.force_login(user=PostURLTest.test_user_author)
        # list of users
        self.clients: list[Client] = [
            self.guest_client,
            self.auth_client,
            self.author_client
        ]

    def test_homepage_is_available_and_return_correct_template(self) -> None:
        '''Test: homepage is available'''
        template = 'posts/index.html'
        index_url = '/'
        for client in self.clients:
            cache.clear()
            with self.subTest(client=client):
                response: HttpResponse = client.get(path=index_url)
                self.assertEqual(
                    first=response.status_code,
                    second=HTTPStatus.OK,
                    msg='Homepage HTTP-status is not 200'
                )
                self.assertTemplateUsed(
                    response=response,
                    template_name=template,
                    msg_prefix='Homepage use incorrect template.')

    def test_unexisting_page(self) -> None:
        '''Test: response of unexisting page.'''
        template = 'core/404.html'
        unexisting_url = '/fck'
        for client in self.clients:
            response: HttpResponse = client.get(path=unexisting_url)
            self.assertEqual(
                first=response.status_code,
                second=HTTPStatus.NOT_FOUND,
                msg='Something wrong with response of unexisting page.'
            )
            self.assertTemplateUsed(
                response=response,
                template_name=template,
                msg_prefix='The 404-page use the wrong template'
            )

    def test_page_response_for_unauth_users(self) -> None:
        '''Test: access to pages for an unauthorized user.'''
        for url_adress in self.url_adress_and_templates.keys():
            with self.subTest(url_adress=url_adress):
                response: HttpResponse = self.guest_client.get(path=url_adress)
                if url_adress == '/posts/1/edit/':
                    self.assertEqual(first=response.status_code, second=404)
                else:
                    self.assertRedirects(
                        response=response,
                        expected_url='/auth/login/?next=' + url_adress,
                        msg_prefix="""
                        Unauthorized user wasn't redirected to login page.
                        """
                    )

    def test_page_response_for_auth_user(self) -> None:
        '''Test: access to pages and templates usage for an authorized user.'''
        for url_adress, template in self.url_adress_and_templates.items():
            with self.subTest(url_adress=url_adress):
                response: HttpResponse = self.author_client.get(
                    path=url_adress)
                self.assertEqual(
                    first=response.status_code,
                    second=HTTPStatus.OK,
                    msg=f'''
                    Page with url "{url_adress}" is not available to
                    authorized user.
                    ''')
                self.assertTemplateUsed(
                    response=response,
                    template_name=template,
                    msg_prefix=f'''
                    Page with url "{url_adress}" use incorrect template
                    ''')

    def test_page_response_for_author(self):
        '''Test: access to pages and templates usage for an author-user.'''
        for url_adress, template in self.url_adress_and_templates.items():
            with self.subTest(url_adress=url_adress):
                response: HttpResponse = self.author_client.get(
                    path=url_adress)
                self.assertEqual(
                    first=response.status_code,
                    second=HTTPStatus.OK,
                    msg=f'''
                    Page with url "{url_adress}" is not available to
                    author user.
                    ''')
                self.assertTemplateUsed(
                    response=response,
                    template_name=template,
                    msg_prefix=f'''
                    Page with url "{url_adress}" use incorrect template
                    ''')

    def test_edit_page_access_for_another_user(self):
        '''Test: access to pages for nonauthor of post.'''
        response: HttpResponse = self.auth_client.get(
            path='/posts/1/edit')
        self.assertFalse(expr=response.status_code == 200,
                         msg='''
                          Page of post-edit form is available to author user.
                          ''')
