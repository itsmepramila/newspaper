from typing import Any, Dict
from django.shortcuts import render, redirect
from newspaper.models import Post, Category, Tag
from django.views.generic import ListView, TemplateView, View, DetailView
from datetime import timedelta
from django.utils import timezone
from newspaper.forms import ContactForm, NewsletterForm
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger


# Create your views here.
class NavigationMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()[:5]
        context["tags"] = Tag.objects.all()[:10]
        context["recent_posts"] = Post.objects.filter(
            status="active", published_at__isnull=False
        ).order_by("-published_at", "-views_count")[:6]

        return context


class HomeView(NavigationMixin, ListView):
    model = Post
    template_name = "aznews/main/home/home.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(status="active", published_at__isnull=False)[:5]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_post"] = (
            Post.objects.filter(status="active", published_at__isnull=False)
            .order_by("-views_count")
            .first()
        )

        context["featured_posts"] = Post.objects.filter(
            status="active", published_at__isnull=False
        ).order_by("-views_count")[1:4]

        one_week_ago = timezone.now() - timedelta(days=7)
        context["weekly_top_posts"] = Post.objects.filter(
            status="active",
            published_at__isnull=False,
            published_at__gte=one_week_ago,
        ).order_by("-published_at", "-views_count")[:7]

        return context


class AboutView(NavigationMixin, TemplateView):
    template_name = "aznews/about.html"


from django.contrib import messages


class ContactView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "aznews/contact.html")

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Successfulley submitted your query. WE will contact you soon. ",
            )
            return redirect("contact")
        else:
            messages.error(
                request,
                "Cannot submit your query. Please make sure all fields are valid",
            )
            return render(
                request,
                "aznews/contact.html",
                {"form": form},
            )


class PostListView(ListView):
    model = Post
    template_name = "aznews/main/list/list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(
        status="active", published_at__isnull=False
    ).order_by("-published_at")
    paginate_by = 1


class PostByCategoryView(ListView):
    model = Post
    template_name = "aznews/main/list/list.html"
    context_object_name = "posts"

    paginate_by = 1

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(
            status="active",
            published_at__isnull=False,
            category=self.kwargs["category_id"],
        ).order_by("-published_at")
        return query


class PostByTagView(ListView):
    model = Post
    template_name = "aznews/main/list/list.html"
    context_object_name = "posts"

    paginate_by = 1

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(
            status="active",
            published_at__isnull=False,
            category=self.kwargs["tag_id"],
        ).order_by("-published_at")
        return query


class PostDetailView(DetailView):
    model = Post
    template_name = "aznews/main/detail/detail.html"
    context_object_name = "post"
    queryset = Post.objects.filter(status="active", published_at__isnull=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        obj = self.get_object()
        obj.views_count += 1
        obj.save()

        context["previous_post"] = (
            Post.objects.filter(
                status="active", published_at__isnull=False, id__lt=obj.id
            )
            .order_by("-id")
            .first()
        )

        context["next_post"] = (
            Post.objects.filter(
                status="active", published_at__isnull=False, id__gt=obj.id
            )
            .order_by("id")
            .first()
        )
        return context


from newspaper.forms import CommentForm


class CommentView(View):
    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        post_id = request.POST["post"]
        if form.is_valid():
            form.save()
            return redirect("post-detail", post_id)
        else:
            post = Post.objects.get(id=post_id)
            return render(
                request,
                "aznews/main/detail/detail.html",
                {"post": post, "form": form},
            )


class NewsletterView(View):
    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get("x-requested-with")
        if is_ajax == "XMLHttpRequest":
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Successfulley subscribe to our newsletter.",
                    },
                    status=201,
                )

            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Cannot process request. Must be an AJAX XMLHttpRequest",
                    },
                    status=400,
                )

        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Cannot process request. Must be an AJAX XMLHttpRequest",
                },
                status=400,
            )


class PostSearchView(View):
    template_name = "aznews/main/list/search.html"

    def get(self, request, *args, **kwargs):
        query = request.GET["query"]
        post_list = Post.objects.filter(
            (Q(title__icontains=query) | Q(content__icontains=query))
            & (
                Q(
                    status="active",
                    published_at__isnull=False,
                )
            )
        ).order_by("-published_at")
        # print(post_list)

        # pagintation start
        page = request.GET.get("page", 1)
        paginate_by = 1
        paginator = Paginator(post_list, paginate_by)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)

        return render(
            request,
            self.template_name,
            {"page_obj": posts, "query": query},
        )

