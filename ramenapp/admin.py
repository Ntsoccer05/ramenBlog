from django.contrib import admin
from .models import Post, Like, Category, Comment, Reply


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_filter = ['updated_at','created_at']
    search_fields = ['title']
    list_display = ('id', 'title', 'created_at')
    list_display_links = ('title',)
    ordering = ('-updated_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post')
    list_display_links = ('post',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    def post_title(self, obj):
        return obj.post.title

    list_filter = ['created_at']
    list_display = ('id', 'author', 'post_title', 'text', 'useremail', 'mailadress', 'created_at',)
    list_display_links = ('text',)
    search_fields = ['text',]
    ordering = ('-created_at',)



@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):

    list_filter = ['created_at']
    list_display = ('id', 'author', 'text', 'created_at',)
    list_display_links = ('text',)
    search_fields = ['text']
    ordering = ('-created_at',)

    
