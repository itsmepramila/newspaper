from django.contrib import admin
from newspaper.models import Post, Category, Tag, Contact, Comment, Newsletter
from django_summernote.admin import SummernoteModelAdmin
from newspaper.models import Category, Comment, Contact, Newsletter, Post, Tag

# Register your models here.

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Contact)
admin.site.register(Comment)
admin.site.register(Newsletter)

class PostAdmin(SummernoteModelAdmin):
    summernote_fields=("content",)
    
admin.site.register(Post, PostAdmin)
