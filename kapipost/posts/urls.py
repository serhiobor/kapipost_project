from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path(route='', view=views.index, name='index'),
    path(route='groups/', view=views.groups, name='groups'),
    path(route='group/<slug:slug>/', view=views.group_list, name='group_list'),
    path(route='posts/<int:post_id>/',
         view=views.post_detail, name='post_detail'),
    path(route='posts/<str:username>/', view=views.profile, name='profile'),
    path(route='posts/<pk>/edit/', view=views.PostEditView.as_view(),
         name='post_edit'),
    path(route='create/', view=views.post_create, name='post_create'),
    path(route='posts/<int:post_id>/comment/',
         view=views.add_comment,
         name='add_comment'),
    path(route='follow/', view=views.follow_index, name='follow_index'),
    path(
        route='profile/<str:username>/follow/',
        view=views.profile_follow,
        name='profile_follow'
    ),
    path(
        route='profile/<str:username>/unfollow/',
        view=views.profile_unfollow,
        name='profile_unfollow'
    ),
]
