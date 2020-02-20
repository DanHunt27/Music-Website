from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import PostCreateForm
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.models import User
from .models import Post, Comment
from django.db.models import Q
import requests
from bs4 import BeautifulSoup
import re


def scrape(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html5lib')
    song_id = re.search('soundcloud://sounds:\d+', soup.prettify())
    if song_id is None:
        return "invalid"
    song_id = re.search('\d+', song_id.group())
    return song_id.group()

@login_required
def follow(request, username):
    if request.user.is_authenticated:
        user = get_object_or_404(User, username=username)
        if request.user != user:
            request.user.profile.follows.add(user.profile)
    return redirect('index')

@login_required
def unfollow(request, username):
    if request.user.is_authenticated:
        user = get_object_or_404(User, username=username)
        request.user.profile.follows.remove(user.profile)
    return redirect('index')

@login_required
def like(request, pk):
    page = request.GET.get('next')
    post = Post.objects.get(pk=pk)
    if request.user.profile.likes.filter(pk=post.pk).exists():
        post.user.profile.total_likes -= 1
        post.user.profile.save()
        request.user.profile.likes.remove(post)
    else:
        post.user.profile.total_likes += 1
        post.user.profile.save()
        request.user.profile.likes.add(post)
    return redirect(page)



class PostListView(ListView):
    model = Post
    template_name = 'main/index.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
            return Post.objects.filter(Q(user__profile__in=user.profile.follows.all())|Q(user=user)).order_by('-date_posted')
        else:
            return Post.objects.all().order_by('-date_posted')


class PostExploreView(ListView):
    model = Post
    template_name = 'main/explore.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


#USER PROFILE
class UserPostListView(ListView):
    model = Post
    template_name = 'main/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        context['prof_user'] = user
        if self.request.user.is_authenticated:
            context['is_follower'] =  self.request.user.profile.follows.filter(user=user).exists()
        else:
            context['is_follower'] = False
        return context

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(user=user).order_by('-date_posted')


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm

    def form_valid(self, form):
        id = scrape(form.instance.link)
        if id == "invalid":
            form.instance.link = ''
        else:
            form.instance.link = "https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/" + id + "&color=%23ff5500&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false"
        form.instance.user = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['artist_name', 'song_name', 'description']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            return True
        return False


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['text']

    def get_success_url(self):
        return self.request.GET.get('next')

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    success_url = '/'

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False
