from django import forms
from newspaper.models import Post
from django_summernote.widgets import SummernoteWidget


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude=("author", "views_count", "published_at")
        
        widgets={
            "title": forms.TextInput(
                attrs={
                    "class":"form-control",
                    "placeholder":"Enter the title of post...",
                    "required": True,
                    
                }
            ),
            'content': SummernoteWidget(),
            "status":forms.Select(attrs={"class": "form-control"}),
            "category":forms.Select(attrs={"class": "form-control"}),
            "tag":forms.Select(attrs={"class": "form-control"}),
                
        }
