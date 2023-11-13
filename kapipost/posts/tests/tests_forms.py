import tempfile
import shutil
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.http import HttpResponse
from django.urls import reverse
from django import forms
from ..forms import PostForm, CommentForm
from ..models import Post, User, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    '''Tests for forms of Post-app.'''
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create user (author)
        cls.test_user = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # create group
        cls.test_group: Group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Group for testing'
        )
        # image to test the form
        small_gif = (
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
        # create post
        cls.test_post: Post = Post.objects.create(
            text='Test post',
            author=cls.test_user
        )
        cls.post_form = PostForm
        cls.reverse_urls: list[str] = [
            reverse(viewname='posts:post_create'),
            reverse(viewname='posts:post_edit',
                    kwargs={'pk': cls.test_post.pk})
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        # authorise client as test_user
        self.client = Client()
        self.client.force_login(user=self.test_user)

    def test_post_creation_and_edit_forms_with_correct_context(self) -> None:
        '''
        Test: if post-creation and post-edition forms get correct context.
        '''
        for url_name in PostFormTests.reverse_urls:
            form_fields: dict = {  # form fields and values
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }
            response: HttpResponse = self.client.get(path=url_name)
            for field, expectation in form_fields.items():
                with self.subTest(value=field):
                    form_field = response.context.get(
                        key='form').fields.get(field)  # type: ignore
                    self.assertIsInstance(
                        obj=form_field, cls=expectation,
                        msg=f'Field "{field}" at "{url_name}" get wrong value'
                    )

    def test_for_post_creation_if_form_is_valid(self) -> None:
        '''Test: if validly completed form creates post.'''
        form_data: dict = {
            'text': 'Test post 2',
            'image': PostFormTests.uploaded_gif,
        }
        self.client.post(
            path=self.reverse_urls[0],
            data=form_data,
            follow=True
        )
        self.assertEqual(
            first=Post.objects.count(),
            second=2,
            msg="Post-creation form don't create post."
        )

    def test_for_post_edit_form_get_correct_obgect(self) -> None:
        '''
        Test: if post-edition form filled up with post instanse data.
        '''
        response: HttpResponse = self.client.get(path=self.reverse_urls[1])
        post_text: str = PostFormTests.test_post.text
        form_text = response.context.get(key='form')['text'].value()
        self.assertEqual(
            first=post_text,
            second=form_text,
            msg='Test edition form filled up with uncorrect data.'
        )

    def test_for_post_edit_form_changes_the_obgect(self) -> None:
        '''Test: if post-edition form changes the object.'''
        post: Post = Post.objects.get(pk=1)

        changed_data: dict[str, Any] = {
            'text': 'Changed text',
            'group': 1,
        }
        response: HttpResponse = self.client.post(
            path=PostFormTests.reverse_urls[1],
            data=changed_data,
        )
        post.refresh_from_db()
        self.assertEqual(
            first=post.text,
            second=changed_data['text'],
            msg="Post content didn't change after using edit form")
        self.assertEqual(
            first=response.status_code,
            second=302,
            msg='Status code after using post-edit for != 302'
        )


class CommentFormTests(TestCase):
    '''Tests for forms of post comments.'''
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create user (author)
        cls.test_user = User.objects.create_user(  # type: ignore
            username='test_author'
        )
        # create post
        cls.test_post: Post = Post.objects.create(
            text='Test post',
            author=cls.test_user
        )
        cls.comment_form = CommentForm()

    def setUp(self) -> None:
        # authorise client as test_user
        self.client = Client()
        self.client.force_login(user=self.test_user)

    def test_comment_form_is_working(self) -> None:
        '''
        Test: if comment form is working
        '''
        post_url = reverse(viewname='posts:add_comment',
                           kwargs={
                               'post_id': CommentFormTests.test_post.pk
                           })
        response: HttpResponse = self.client.post(
            path=post_url,
            data={'text': 'test comment'},
            follow=True
        )
        self.assertTrue(response.status_code == 200)
        self.assertTrue(
            expr=Comment.objects.count() == 1,
            msg="Comment-form don't create comment")
