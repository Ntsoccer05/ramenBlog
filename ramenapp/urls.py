from django.urls import path, include
from . import views

app_name = 'ramenapp'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('post_create', views.PostCreate.as_view(), name='post_create'),
    path('post_detail/<int:pk>', views.PostDetail.as_view(), name='post_detail'),
    path('post_update/<int:pk>', views.PostUpdate.as_view(), name='post_update'),
    path('post_delete/<int:pk>', views.PostDelete.as_view(), name='post_delete'),
    path('post_list', views.PostList.as_view(), name='post_list'),
    path('login', views.Login.as_view(), name='login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('signup', views.SignUp.as_view(), name='signup'),
    path('like/<int:post_id>', views.Like_add, name='like_add'),
    path('category_list', views.CategoryList.as_view(), name='category_list'),
    path('category_detail/<str:name_en>',
         views.CategoryDetail.as_view(), name='category_detail'),
    path('search', views.Search, name='search'),
    path('like_list', views.LikeDetail.as_view(), name='like_list'),
    path('contact_form', views.ContactFormView.as_view(), name='contact_form'),
    path('comment/<int:pk>',
         views.CommentFormView.as_view(), name='comment_form'),
    path('comment_delete/<int:pk>',
         views.CommentDelete.as_view(), name='comment_delete'),
    path('reply/<int:pk>', views.ReplyFormView.as_view(), name='reply_form'),
    path('reply_delete/<int:pk>', views.ReplyDelete.as_view(), name='reply_delete'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('google285b2115e8e0c8a6.html', views.google, name='google'),
]
