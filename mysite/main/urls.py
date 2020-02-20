from django.urls import path
from .views import (
    PostListView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    PostExploreView,
    UserPostListView,
    CommentCreateView,
    CommentDeleteView
)
from . import views
import sys
from django.contrib.auth.models import User

urlpatterns = [
    path('', PostListView.as_view(), name='index'),
    path('explore/', PostExploreView.as_view(), name='explore'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:pk>/comment-create/', CommentCreateView.as_view(), name='comment-create'),
    path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:pk>/like/', views.like, name='like'),
    path('follow/<str:username>', views.follow, name='follow'),
    path('unfollow/<str:username>', views.unfollow, name='unfollow'),
]
