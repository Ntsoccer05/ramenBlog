from django import forms
from .models import Post, Comment, Reply
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse
from django.conf import settings
from django.forms import ModelForm, TextInput, Textarea


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'category', 'content', 'thumbnail', 'star')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SearchForm(forms.Form):
    freeword = forms.CharField(
        min_length=1, max_length=30, label="", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ContactForm(forms.Form):
    name = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'お名前'
        })
    )
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'メールアドレス',
        })
    )
    subject = forms.CharField(
        label='',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '件名',
        })
    )
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'お問い合わせ'
        })
    )

    def send_email(self):
        message = self.cleaned_data['message']
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        subject = self.cleaned_data['subject']
        from_email = '{name} <{email}> ({subject})'.format(
            name=name, email=email, subject=subject)
        recipient_list = [settings.EMAIL_HOST_USER]
        try:
            send_mail(subject, message, from_email, recipient_list)
        except BadHeaderError:
            return HttpResponse('無効なヘッダが検出されました。')


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'text')
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '名前'
            }),
            'text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'コメント内容'
            }),
        }
        labels = {
            'author': '',
            'text': '',
        }


class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ('author', 'text')
        widgets = {
            'author': TextInput(attrs={
                'class': 'form-control',
                'placeholder': '名前',
            }),
            'text': Textarea(attrs={
                'class': 'form-control',
                'placeholder': '返信内容',
            }),
        }
        labels = {
            'author': '',
            'text': '',
        }
