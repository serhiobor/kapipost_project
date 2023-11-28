from .models import Post
from .serializers import PostSerializer
from rest_framework import viewsets


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

# from django.http import Http404, HttpResponse
# from django.shortcuts import render, get_object_or_404, redirect
# from .models import Post, Group, User, Follow
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.paginator import Paginator
# from django.views.decorators.cache import cache_page
# from .forms import PostForm, CommentForm
# from django.views.generic import UpdateView
# from django.urls import reverse
# from rest_framework import viewsets
# from .serializers import PostSerializer


# class PostViewSet(viewsets.ModelViewSet):
#     queryset = Post.objects.all()
#     serializer_class = PostSerializer

#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)


# @cache_page(timeout=30, key_prefix='index_page')
# def index(request) -> HttpResponse:
#     '''Main page of the project'''
#     template = 'posts/index.html'
#     title = 'Main page'
#     posts = Post.objects.order_by('-pub_date')
#     paginator = Paginator(object_list=posts, per_page=10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(number=page_number)
#     context = {
#         'title': title,
#         'page_obj': page_obj,
#     }
#     return render(request=request, template_name=template, context=context)


# @login_required
# def group_list(request, slug) -> HttpResponse:
#     '''Posts by a specific group'''
#     template = 'posts/group_list.html'
#     group = get_object_or_404(klass=Group, slug=slug)
#     title = f'''Group: "{group.__str__()}"'''
#     posts = Post.objects.filter(group=group).order_by('-pub_date')
#     paginator = Paginator(object_list=posts, per_page=10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(number=page_number)
#     context = {
#         'title': title,
#         'group': group,
#         'page_obj': page_obj,
#     }
#     return render(request=request, template_name=template, context=context)


# @login_required
# def groups(request) -> HttpResponse:
#     """List of groups"""
#     template = 'posts/groups.html'
#     title = 'Groups'
#     groups = Group.objects.order_by('title')
#     paginator = Paginator(object_list=groups, per_page=10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(number=page_number)
#     context = {
#         'title': title,
#         'page_obj': page_obj
#     }
#     return render(request=request, template_name=template, context=context)


# @login_required
# def profile(request, username) -> HttpResponse:
#     '''User profile and posts'''
#     template = 'posts/profile.html'
#     author = get_object_or_404(klass=User, username=username)
#     posts = Post.objects.filter(author=author).order_by('-pub_date')
#     paginator = Paginator(object_list=posts, per_page=10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(number=page_number)
#     following = Follow.objects.filter(user__username=request.user,
#                                       author=author).exists()
#     context = {
#         'title': 'Profile of user: ',
#         'author': author,
#         'posts': posts,
#         'page_obj': page_obj,
#         'following': following,
#     }
#     return render(request=request, template_name=template, context=context)


# @login_required
# def post_detail(request, post_id) -> HttpResponse:
#     '''Details of specific post'''
#     template = 'posts/post_detail.html'
#     post = get_object_or_404(klass=Post, pk=post_id)
#     title = 'Post '
#     comments = post.comments.all()  # type: ignore
#     comment_form = CommentForm
#     context = {
#         'title': title,
#         'post': post,
#         'comments': comments,
#         'form': comment_form,
#     }
#     return render(request=request, template_name=template, context=context)


# @login_required
# def post_create(request):
#     '''Create a new post'''
#     template = "posts/create_post.html"
#     form = PostForm(
#         request.POST or None,
#         files=request.FILES or None
#     )
#     if form.is_valid():
#         post = form.save(commit=False)
#         username = request.user
#         post.author = username
#         form.save()
#         return redirect('posts:profile', username.username)
#     context = {
#         'form': form,
#         'is_edit': False,
#         'title': "New post"
#     }
#     return render(request=request, template_name=template, context=context)


# @login_required
# def add_comment(request, post_id):
#     '''Add a comment to the post.'''
#     form = CommentForm(data=request.POST or None)
#     post = Post.objects.get(pk=post_id)
#     if form.is_valid():
#         comment = form.save(commit=False)
#         comment.author = request.user
#         comment.post = post
#         comment.save()
#     return redirect(to='posts:post_detail', post_id=post_id)


# class PostEditView(LoginRequiredMixin, UpdateView):
#     '''Edit an existing post.'''
#     model = Post
#     fields = ['text', 'group', 'image']
#     template_name = 'posts/create_post.html'

#     def get_success_url(self) -> str:
#         pk = self.kwargs["pk"]
#         return reverse(viewname="posts:post_detail", kwargs={"post_id": pk})

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Change post'
#         context['is_edit'] = True
#         return context

#     def dispatch(self, request, *args, **kwargs):
#         post = self.get_object()
#         if post.author != self.request.user:  # type: ignore
#             raise Http404("You are not allowed to edit this Post")
#         return super(PostEditView, self).dispatch(request, *args, **kwargs)


# @login_required
# def follow_index(request):
#     '''Posts of users followed.'''
#     template = 'posts/follow.html'
#     title = 'Posts of users followed'
#     current_user = request.user
#     posts = Post.objects.filter(author__following__user=current_user)
#     paginator = Paginator(object_list=posts, per_page=10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(number=page_number)
#     posts_count = posts.count()
#     context = {
#         'title': title,
#         'page_obj': page_obj,
#         'posts_count': posts_count,
#     }
#     return render(request=request, template_name=template, context=context)


# @login_required
# def profile_follow(request, username):
#     '''Follow author'''
#     user = get_object_or_404(klass=User, username=username)
#     Follow.objects.get_or_create(user=request.user, author=user)
#     return redirect('posts:profile', username)


# @login_required
# def profile_unfollow(request, username):
#     '''Unfollow author'''
#     user = get_object_or_404(klass=User, username=username)
#     follow, is_created = Follow.objects.get_or_create(
#         user=request.user,
#         author=user
#     )
#     follow.delete()
#     return redirect('posts:profile', username)
