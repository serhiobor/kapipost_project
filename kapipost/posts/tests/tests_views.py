import tempfile
import shutil

from time import sleep

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from ..models import User, Group, Post, Comment, Follow
from ..forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostViewTemplatesTests(TestCase):
    """Tests Post-app view-functions return corresponding templates"""
    url_names_and_templates: dict[str, str] = {
        reverse(viewname='posts:index'): 'posts/index.html',
        reverse(viewname='posts:group_list', kwargs={
            'slug': 'test_group'}): 'posts/group_list.html',
        reverse(viewname='posts:groups'): 'posts/groups.html',
        reverse(viewname='posts:profile', kwargs={
            'username': 'test_author'}): 'posts/profile.html',
        reverse(viewname='posts:post_detail', kwargs={
            'post_id': '1'}): 'posts/post_detail.html',
        reverse(viewname='posts:post_create'): 'posts/create_post.html',
        reverse(viewname='posts:post_edit', kwargs={
            'pk': '1'}): 'posts/create_post.html',
        reverse(viewname='posts:follow_index'): 'posts/follow.html',
    }

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # test user (author)
        cls.test_author = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # test group
        cls.test_group: Group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test group description'
        )
        # test post of author
        cls.test_post: Post = Post.objects.create(
            text='Test post',
            author=cls.test_author,
            group=cls.test_group
        )

    def setUp(self) -> None:
        # authorized client as post author
        self.author_client = Client()
        self.author_client.force_login(user=self.test_author)

    def test_views_shows_correct_templates_for_auth_user(self) -> None:
        """Test: view-functions of post-app return corresponding templates"""
        for url_name, template in self.url_names_and_templates.items():
            cache.clear()
            with self.subTest(reverse_name=url_name):
                response: HttpResponse = self.author_client.get(path=url_name)
                self.assertTemplateUsed(
                    response=response,
                    template_name=template,
                    msg_prefix=f'''
                    View-function at "{url_name}" return incorrect template
                    '''
                )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostContextTemplatesTests(TestCase):
    '''Test for Post-app templates with correct context'''
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # test author
        cls.test_author = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # test group
        cls.test_group: Group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Test group description'
        )
        # second test group
        cls.another_test_group: Group = Group.objects.create(
            title='Another test group',
            slug='another_test_group',
            description='Another test group description'
        )
        # binary gif
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        another_small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_gif = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.another_uploaded_gif = SimpleUploadedFile(
            name='another_small.gif',
            content=another_small_gif,
            content_type='image/gif'
        )
        # test post without group to check context on a main page
        cls.test_post: Post = Post.objects.create(
            text='Test post',
            author=cls.test_author,
            image=cls.uploaded_gif
        )
        # sleep for a sec to make sure, that output order will be correct
        sleep(0.01)
        # another post with group
        cls.another_test_post: Post = Post.objects.create(
            text='Another test post',
            author=cls.test_author,
            group=cls.test_group,
            image=cls.another_uploaded_gif,
        )
        # test comment to test_post
        cls.test_comment: Comment = Comment.objects.create(
            text='Test comment',
            post=cls.test_post,
            author=cls.test_author,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        # authorized client as author
        self.author_client = Client()
        self.author_client.force_login(user=self.test_author)

    def test_main_page_context(self) -> None:
        """Test: main page template formed with correct context."""
        cache.clear()
        response: HttpResponse = self.author_client.get(
            path=reverse(viewname='posts:index'))
        first_object: Post = response.context.get(key='page_obj')[0]
        post_text: str = first_object.text
        second_object: Post = response.context.get(key='page_obj')[1]
        post_image = second_object.image
        self.assertIsInstance(
            obj=first_object,
            cls=Post,
            msg='Context of main page contains not Post-object'
        )
        self.assertEqual(
            first=post_text,
            second=self.another_test_post.text,
            msg='Order of posts on the main page is not as was expected')
        self.assertEqual(
            first=post_image,
            second=PostContextTemplatesTests.test_post.image,
            msg='Post on a main page without uploaded image')

    def test_group_list_context(self) -> None:
        """Test: group-list template formed with correct context."""
        response: HttpResponse = self.author_client.get(
            path=reverse(viewname='posts:group_list',
                         kwargs={
                             'slug': PostContextTemplatesTests.test_group.slug
                         })
        )
        page_obj = response.context.get(key='page_obj')
        first_object: Post = page_obj[0]
        post_text: str = first_object.text
        post_image = first_object.image
        self.assertIsInstance(
            obj=first_object,
            cls=Post,
            msg='Context of group-list page contains not Post-object'
        )
        self.assertEqual(
            first=post_text,
            second=PostContextTemplatesTests.another_test_post.text,
            msg='Wrong post on a group-list page'
        )
        self.assertEqual(
            first=post_image,
            second=PostContextTemplatesTests.another_test_post.image,
            msg='Post on a group-list page without uploaded image'
        )
        self.assertTrue(expr=len(page_obj) == 1,
                        msg='There should be only one post in group_list in testcase')

    def test_groups_context(self) -> None:
        """Test: page with list of groups formed with correct context."""
        response: HttpResponse = self.author_client.get(
            path=reverse(viewname='posts:groups')
        )
        first_object: Group = response.context.get(key='page_obj')[0]
        group_title: str = first_object.title
        self.assertIsInstance(
            obj=first_object,
            cls=Group,
            msg='Context of list of groups contains not Group-object'
        )
        self.assertEqual(
            first=group_title,
            second=self.another_test_group.title,
            msg='Order of groups on the group-list page is not as was expected'
        )

    def test_profile_context(self) -> None:
        """Test: profile template contains autor's posts and personal data."""
        response: HttpResponse = self.author_client.get(
            path=reverse(
                viewname='posts:profile',
                kwargs={
                    'username': PostContextTemplatesTests.test_author.username
                })
        )
        first_object: Post = response.context.get(key='page_obj')[0]
        second_object: Post = response.context.get(key='page_obj')[1]
        post_author = first_object.author
        self.assertIsInstance(
            obj=first_object,
            cls=Post,
            msg='Context of profile page contains not Post-object'
        )
        self.assertEqual(
            first=first_object.text,
            second=self.another_test_post.text,
            msg='Order of posts on the profile page is not as was expected'
        )
        self.assertEqual(
            first=second_object.text,
            second=self.test_post.text,
            msg='Order of posts on the profile page is not as was expected'
        )
        self.assertEqual(
            first=first_object.image,
            second=self.another_test_post.image,
            msg='Post on a profile page without uploaded image'
        )
        self.assertEqual(
            first=second_object.image,
            second=self.test_post.image,
            msg='Post on a profile page without uploaded image'
        )
        self.assertEqual(
            first=first_object.author,
            second=post_author,
            msg='Profile page contains post from another author'
        )

    def test_post_detail_context(self) -> None:
        """Test: post-detail page formed with correct context."""
        response: HttpResponse = self.author_client.get(
            path=reverse(viewname='posts:post_detail',
                         kwargs={
                             'post_id': PostContextTemplatesTests.test_post.pk
                         })
        )
        # check post of test_author
        post_from_context: Post = response.context.get(key='post')
        # check comment to test_post
        comment_from_context: Post = response.context.get(key='comments')[0]
        self.assertIsInstance(
            obj=post_from_context,
            cls=Post,
            msg='''Test_post detail page is without post in context'''
        )
        self.assertIsInstance(
            obj=comment_from_context,
            cls=Comment,
            msg='''Test_post detail page is without comment in context'''
        )
        self.assertEqual(
            first=post_from_context.text,
            second=self.test_post.text,
            msg='Test_post detail page get incorrect post'
        )
        self.assertEqual(
            first=post_from_context.image,
            second=self.test_post.image,
            msg='Post on a test_post profile page without uploaded image'
        )
        # check post of another_test_author
        response: HttpResponse = self.author_client.get(
            path=reverse(viewname='posts:post_detail',
                         kwargs={
                             'post_id':
                             PostContextTemplatesTests.another_test_post.pk
                         })
        )
        another_object_from_context: Post = response.context.get(key='post')
        self.assertIsInstance(
            obj=another_object_from_context,
            cls=Post,
            msg='Another_test_post detail page contains not post in context'
        )
        self.assertEqual(
            first=another_object_from_context.text,
            second=self.another_test_post.text,
            msg='Another_test_post detail page get incorrect post'
        )

    def test_post_edit_context(self) -> None:
        """Test: post edit template get the requested post."""
        response: HttpResponse = self.author_client.get(
            path=reverse(viewname='posts:post_edit', kwargs={
                'pk': PostContextTemplatesTests.test_post.pk})
        )
        object_from_context: Post = response.context.get(key='post')
        self.assertEqual(
            first=object_from_context,
            second=self.test_post,
            msg='Post-edit page get incorrect post'
        )

    def test_post_create_context(self) -> None:
        """Test: post create page contains the post creation form."""
        response: HttpResponse = self.author_client.get(
            path=reverse(viewname='posts:post_create')
        )
        page_context: PostForm = response.context.get(key='form')
        self.assertIsInstance(
            obj=page_context,
            cls=PostForm,
            msg='Post creation page can not get PostForm'
        )


class PaginatorViewsTest(TestCase):
    """Paginator testing"""
    pages_with_paginators: list[str] = [
        reverse(viewname='posts:index'),
        reverse(viewname='posts:groups'),
        reverse(viewname='posts:group_list', kwargs={'slug': 'test_group_1'}),
        reverse(viewname='posts:profile', kwargs={'username': 'test_author'}),
    ]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # test_author
        cls.test_author: User = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # a lot of groups
        for i in range(1, 14):
            Group.objects.create(
                title=f'Test group {i}',
                slug=f'test_group_{i}',
                description=f'Description of test group {i}'
            )
        # a lot of posts
        for i in range(1, 14):
            Post.objects.create(
                text=f'Test post {i}',
                author=cls.test_author,
                group=Group.objects.get(slug='test_group_1')
            )

    def setUp(self) -> None:
        self.author_client = Client()
        self.author_client.force_login(user=self.test_author)

    def test_paginator_on_pages(self) -> None:
        '''
        Test: number of posts on the first page ==10 and ==3 on the second.
        '''
        for reverse_url in self.pages_with_paginators:
            cache.clear()
            with self.subTest(revers_url=reverse_url):
                response: HttpResponse = self.author_client.get(
                    path=reverse_url
                )
                self.assertEqual(
                    first=len(response.context['page_obj']),
                    second=10,
                    msg=f'''Something wrong with paginator (url: {reverse_url})
                    on a first page'''
                )
                second_page_response: HttpResponse = self.author_client.get(
                    path=reverse_url + '?page=2')
                self.assertEqual(
                    first=len(second_page_response.context['page_obj']),
                    second=3,
                    msg=f'''Something wrong with paginator (url: {reverse_url})
                    on a second page'''
                )


class FollowingViewsTest(TestCase):
    '''Full test of follow-functions.'''
    """reverse_urls_and_templates = {
        reverse(viewname='posts:follow'): 'posts/follow.html',
        reverse(viewname='posts:profile_follow',
                kwargs={'username': 'test_user'}): 'posts/profile_follow.html',
        reverse(viewname='posts:profile_unfollow'):
        'posts/profile_follow.html',
    }"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # test user
        cls.test_user: User = User.objects.create_user(  # type: ignore
            username='test_user'
        )
        # test author to follow
        cls.test_author: User = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # a lot of posts
        for i in range(1, 14):
            Post.objects.create(
                text=f'Test_post_{i}',
                author=cls.test_author,
            )

    def setUp(self) -> None:
        self.user_client = Client()
        self.user_client.force_login(user=self.test_user)

    def test_of_follow_unfollow(self):
        author_to_follow = FollowingViewsTest.test_author.username
        initial_follows = Follow.objects.all().count()
        self.user_client.get(path=reverse(
            viewname='posts:profile_follow',
            kwargs={'username': author_to_follow})
        )
        after_following = Follow.objects.all().count()
        self.assertNotEqual(
            first=initial_follows,
            second=after_following,
            msg="Profile_follow don't create follow-object"
        )
        self.user_client.get(path=reverse(
            viewname='posts:profile_unfollow',
            kwargs={'username': author_to_follow})
        )
        final_follows = Follow.objects.all().count()
        self.assertTrue(
            expr=final_follows == 0,
            msg='Profile_unfollow do not work'
        )

    def test_of_follow_index_context(self):
        '''Test: follow_index page contains correct number of posts'''
        reverse_url = reverse(viewname='posts:follow_index')
        author_to_follow = FollowingViewsTest.test_author.username
        self.user_client.get(path=reverse(
            viewname='posts:profile_follow',
            kwargs={'username': author_to_follow})
        )
        first_page_response = self.user_client.get(path=reverse_url)
        self.assertEqual(
            first=len(first_page_response.context['page_obj']),
            second=10,
            msg='''Something wrong with paginator (follow_index) on a first page'''
        )
        second_page_response = self.user_client.get(
            path=reverse_url + '?page=2')
        self.assertEqual(
            first=len(second_page_response.context['page_obj']),
            second=3,
            msg='''Something wrong with paginator (follow_index) on a second page'''
        )


class CacheTest(TestCase):
    """Cache testing"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # test_author
        cls.test_author: User = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # a lot of posts
        for i in range(1, 4):
            Post.objects.create(
                text='Test_post',
                author=cls.test_author,
            )

    def setUp(self) -> None:
        self.author_client = Client()
        self.author_client.force_login(user=self.test_author)

    def test_cache_on_main_page(self) -> None:
        '''
        Test: posts on a main page holds in cache.
        '''
        # One Day there will be better way of testing this
        # clear cache before anything
        cache.clear()
        # first request to the page to find 3 posts on it
        response_initial = self.author_client.get('/')
        # count it
        post_count_initial = len(response_initial.context['page_obj'])
        # delete all posts
        Post.objects.all().delete()
        # second request to the page shows that there still 3 posts on it
        response_cached = self.author_client.get('/')
        # count 'Test_post' in cached content
        post_count_cached = str(response_cached.content).count('Test_post')
        self.assertEqual(
            first=post_count_initial,
            second=post_count_cached,
            msg="Cache don't work on a main page (caching)"
        )
        # remove posts from cache and repete request
        cache.clear()
        response_cleared = self.author_client.get('/')
        post_count_clear = len(response_cleared.context['page_obj'])
        self.assertTrue(
            expr=post_count_clear == 0,
            msg="Cache don't work on a main page (clear)"
        )
        # upd: it could be like this
        self.assertEqual(
            response_initial.content,
            response_cached.content
        )
