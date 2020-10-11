from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField('カテゴリ名', max_length=50)
    name_en = models.CharField('カテゴリ名英語', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def post_count(self):
        n = Post.objects.filter(category=self).count()
        return n

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    title = models.CharField('タイトル', max_length=100)
    content = models.TextField('内容')
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    star = models.IntegerField('評価', blank=False, default=3, validators=[
                               MaxValueValidator(5), MinValueValidator(1)])
    thumbnail = models.ImageField(upload_to='images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    like_num = models.IntegerField(default=0)

    def like_count(self):
        n = Like.objects.filter(post=self).count()
        return n

    def __str__(self):
        return self.title


class Like(models.Model):
    post = models.ForeignKey(Post, verbose_name="投稿", on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name="Likeしたユーザー", on_delete=models.PROTECT)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.CharField(max_length=50)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.text


class Reply(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name='replies')
    author = models.CharField(max_length=50)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
