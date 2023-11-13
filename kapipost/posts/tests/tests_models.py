from django.test import TestCase
from ..models import Group, Post, User


class PostModelTests(TestCase):
    '''Tests for models of Post-app.'''
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # create user (author)
        cls.test_user = User.objects.create_user(  # type: ignore
            username='test_user')
        # create group
        cls.test_group: Group = Group.objects.create(
            title='Test group',
            slug='test_slug',
            description='Test group description',
        )
        # create test-post
        cls.test_post: Post = Post.objects.create(
            author=cls.test_user,
            text='Test post',
        )

    def test_models_have_correct_object_names(self) -> None:
        """Test: models has correct __str__."""
        post: Post = PostModelTests.test_post
        post_str: str = post.text[:15]
        post_str_method: str = post.__str__()
        self.assertEqual(first=post_str, second=post_str_method,
                         msg="Post.__str__ doesn't work")
        group: Group = PostModelTests.test_group
        group_str: str = group.title
        group_str_method: str = group.__str__()
        self.assertEqual(first=group_str, second=group_str_method,
                         msg="Group.__str__ doesn't work")

    def test_post_model_verbose_name_and_help_text(self) -> None:
        '''Test: post-model has correct verbose name and help-text.'''
        post: Post = PostModelTests.test_post
        verbose_name: str = post._meta.get_field(
            field_name='text').verbose_name
        help_text: str = post._meta.get_field(field_name='text').help_text
        self.assertEqual(first=verbose_name, second='Post text',
                         msg="verbose_name of Post-model doesn't work")
        self.assertEqual(first=help_text, second='Enter the text',
                         msg="help_text of Post-model doesn't work")
