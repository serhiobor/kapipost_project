from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    '''Form of post creation and changing'''

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['group'].required = False
        self.fields['group'].empty_label = 'Group is not chosen'
        self.fields['text'].required = True
        self.fields['image'].required = False

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(ModelForm):
    '''Comment form'''
    class Meta:
        model = Comment
        fields = ('text',)
