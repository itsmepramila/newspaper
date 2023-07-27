from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from newspaper.models import Post
from django.utils import timezone
from blog_app.forms import PostForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

# CRUD => Class based views => 80-90


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    queryset = Post.objects.filter(published_at__isnull=False)
    context_object_name = "posts"


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=False)
        return queryset


class DraftListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "blog/draft_list.html"
    queryset = Post.objects.filter(published_at__isnull=True)
    context_object_name = "posts"


class DraftDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "blog/draft_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(pk=self.kwargs["pk"], published_at__isnull=True)
        return queryset


class DraftPublishView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk, published_at__isnull=True)
        post.published_at = timezone.now()
        post.save()
        return redirect("blog:draft-list")


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        post.delete()
        return redirect("blog:post-list")


class PostCreateView(CreateView):
    model = Post
    template_name = "blog/post_create.html"
    form_class = PostForm
    success_url = reverse_lazy("blog:draft-list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "blog/post_create.html"
    form_class = PostForm

    def get_success_url(self):
        post = self.get_object()  # jun post maile update garna khojdai xu
        if post.published_at:
            return reverse_lazy("blog:post-detail", kwargs={"pk": post.pk})
        else:
            return reverse_lazy("blog:draft-detail", kwargs={"pk": post.pk})
        
        
        
import csv

from django.contrib.auth import get_user_model
from django.http import FileResponse, HttpResponse
from django.views.generic import View

from newspaper.models import Post


User=get_user_model()

COLUMNS=[
    "first_name",
    "last_name",
    "username",
    "email",
    "is_staff",
    "is_active",
    "is_superuser",
    "last_login",
    "date_joined",
]

class UserReportView(View):
    def get(self, request):
        response=HttpResponse(content_type="text/csv")
        response["Content-Disposition"]="attachment; filename=users.csv"
        
        users=User.objects.all().only(*COLUMNS).values(*COLUMNS)
        print(users)
        
        
        writer=csv.DictWriter(response, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)
        
        return response