from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    '''Group model'''
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=False)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    '''Post model'''
    id = models.AutoField(primary_key=True)
    text = models.TextField(blank=True,
                            verbose_name='Post text',
                            help_text='Enter the text')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts')
    group = models.ForeignKey(
        Group,
        verbose_name='Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name: str = 'Post'
        verbose_name_plural: str = 'Posts'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    '''Comment model'''
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Post to comment',
        help_text='Post to comment',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Author'
    )
    text = models.TextField(
        max_length=400,
        verbose_name='Comment',
        help_text='Enter the comment'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date of comment'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name: str = 'Comment'
        verbose_name_plural: str = 'Comments'


class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Following'
    )
