from django.shortcuts import render, resolve_url, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView, DeleteView, ListView
from .models import Post, Like, Category, Comment, Reply, Author
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import PostForm, LoginForm, SignUpForm, SearchForm, ContactForm, CommentForm, ReplyForm, UserUpdateForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.views.generic.edit import FormView
from django.contrib.sitemaps import ping_google
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .mixins import SuperuserRequiredMixin
from django.contrib.auth.models import User

@login_required
def ping(request):
  try:
    if request.user.is_admin:
      ping_google()  
  except:
    pass
  return redirect('/')


class OnlyMyPostMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        post = Post.objects.get(id=self.kwargs['pk'])
        return post.author == self.request.user

class OnlyMyCommentMixin(UserPassesTestMixin):
    raise_exception=True

    def test_func(self):
        comment=Comment.objects.get(id=self.kwargs['pk'])
        return comment.author==self.request.user

class OnlyMyReplyMixin(UserPassesTestMixin):
    raise_exception=True

    def test_func(self):
        reply=Reply.objects.get(id=self.kwargs['pk'])
        return reply.author==self.request.user

class OnlyYouMixin(UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser

class AuthorCreate(LoginRequiredMixin, CreateView):
    model = Author
    fields = ['name']

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class UserDetail(OnlyYouMixin, DetailView):
    """ユーザーの詳細ページ"""
    model = User
    # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く
    template_name = 'ramenapp/user_detail.html'

class UserUpdate(OnlyYouMixin, UpdateView):
    """ユーザー情報更新ページ"""
    model = User
    form_class = UserUpdateForm
    template_name = 'ramenapp/user_form.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く

    def get_success_url(self):
        return resolve_url('ramenapp:user_detail', pk=self.kwargs['pk'])

class Index(TemplateView):
    template_name = 'ramenapp/index.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        if Post.updated_at:
            post_list = Post.objects.all().order_by('-updated_at')[:6]
        else:
            post_list = Post.objects.all().order_by('-created_at')[:6]
        context = {
            'post_list': post_list,
        }
        return context


class PostCreate(SuperuserRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('ramenapp:index')

    def form_valid(self, form):
        form.instance.author_id = self.request.user.id
        return super(PostCreate, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, '記事を登録しました。')
        return resolve_url('ramenapp:index')


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *args, **kwargs):
        detail_data = Post.objects.get(id=self.kwargs['pk'])
        category_posts = Post.objects.filter(
            category=detail_data.category).order_by('-created_at')[:5]
        params = {
            'object': detail_data,
            'category_posts': category_posts,
        }
        return params


class PostUpdate(SuperuserRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm

    def get_success_url(self):
        messages.info(self.request, '記事を更新しました。')
        return resolve_url('ramenapp:post_detail', pk=self.kwargs['pk'])


class PostDelete(SuperuserRequiredMixin, DeleteView):
    model = Post

    def get_success_url(self):
        messages.info(self.request, '記事を削除しました。')
        return resolve_url('ramenapp:index')


class PostList(ListView):
    model = Post
    paginate_by = 5

    def get_queryset(self):
        if Post.updated_at:
            return Post.objects.all().order_by('-updated_at')
        else:
            return Post.objects.all().order_by('-created_at')


class Login(LoginView):
    form_class = LoginForm
    template_name = 'ramenapp/login.html'


class Logout(LogoutView):
    template_name = 'ramenapp/logout.html'


class SignUp(CreateView):
    form_class = SignUpForm
    template_name = 'ramenapp/signup.html'
    success_url = reverse_lazy('ramenapp:index')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        self.object = user
        messages.info(self.request, 'ユーザー登録をしました。')
        return HttpResponseRedirect(self.get_success_url())


@login_required
def Like_add(request, *args, **kwargs):
    post = Post.objects.get(id=kwargs['post_id'])
    is_liked = Like.objects.filter(user=request.user, post=post).count()
    if is_liked > 0:
        liking = Like.objects.get(
            post_id=kwargs['post_id'], user=request.user)
        liking.delete()
        post.like_num -= 1
        # post.save()
        messages.info(request, 'お気に入りを削除しました。')
        return redirect('ramenapp:index')
    post.like_num += 1
    # post.save()
    like = Like()
    like.user = request.user
    like.post = post
    like.save()

    messages.success(request, 'お気に入りに追加しました。')
    return redirect('ramenapp:index')

class CategoryList(ListView):
    model = Category


class CategoryDetail(DetailView):
    model = Category
    slug_field = 'name_en'
    slug_url_kwarg = 'name_en'

    def get_context_data(self, *args, **kwargs):
        detail_data = Category.objects.get(name_en=self.kwargs['name_en'])
        category_posts = Post.objects.filter(
            category=detail_data.id).order_by('-created_at')

        params = {
            'object': detail_data,
            'category_posts': category_posts,
        }

        return params


def Search(request):
    if request.method == 'POST':
        searchform = SearchForm(request.POST)

        if searchform.is_valid():
            freeword = searchform.cleaned_data['freeword']
            search_list = Post.objects.filter(
                Q(title__icontains=freeword) | Q(content__icontains=freeword))

        params = {
            'search_list': search_list,
        }

        return render(request, 'ramenapp/search.html', params)


class LikeDetail(ListView):
    model = Like

    paginate_by = 5

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)


class ContactFormView(FormView):
    template_name = 'ramenapp/contact_form.html'
    form_class = ContactForm

    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)

    def get_success_url(self):
        messages.info(self.request, 'お問い合わせは正常に送信されました。')
        return resolve_url('ramenapp:index')


class CommentFormView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        comment = form.save(commit=False)
        post_pk = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_pk)
        # form.instance.author = self.request.user
        # form.instance.author_id = self.request.user.id
        comment.useremail = self.request.user.email
        comment.post = post
        comment.request = self.request
        comment.save()
        return redirect('ramenapp:post_detail', pk=post_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_pk = self.kwargs['pk']
        # post = get_object_or_404(Post, pk=post_pk)
        # context = {
        #     'post': post
        # }
        context['post'] = get_object_or_404(Post, pk=post_pk)
        context['form'] = CommentForm(initial = { 
                'author': self.request.user, 
                'mailadress' : self.request.user.email,
            }) 
        return context

# def comment_initail(request):
#     queryset = User.objects.get(id=request.user.id)
   
#     initial_data = {
#         'author': queryset.username,
#     }
 
#     form = CommentForm(
#         initial=initial_data
#     )
 
#     context = {
#         'form': form
#     }
#     return render(request, 'ramenapp/comment_form.html', context)
# @login_required
# def comment_remove(request, pk):
#     comment = get_object_or_404(Comment, pk=pk)
#     comment.delete()
#     return redirect('ramenapp;post_detail', pk=comment.post.pk)
class CommentDelete(OnlyMyCommentMixin, DeleteView):
    model = Comment

    def get_success_url(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        pk = comment.post.id
        messages.info(self.request, 'コメントを削除しました。')
        return resolve_url('ramenapp:post_detail', pk=pk)


class ReplyFormView(LoginRequiredMixin, CreateView):
    model = Reply
    form_class = ReplyForm

    def form_valid(self, form):
        reply = form.save(commit=False)
        comment_pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=comment_pk)
        reply.comment = comment
        reply.authority = self.request.user.email
        # form.instance.author = self.request.user
        # form.instance.author_id = self.request.user.id
        reply.request = self.request
        reply.save()
        return redirect('ramenapp:post_detail', pk=reply.comment.post.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        comment = get_object_or_404(Comment, pk=pk)
        context['comment'] = comment
        context['post'] = comment.post 
        context['form'] = ReplyForm( initial = { 'author': self.request.user } ) 
        return context


# class ReplyToReplyFormView(LoginRequiredMixin, CreateView):
#     model = Reply
#     form_class = ReplyForm

#     def form_valid(self, form):
#         reply = form.save(commit=False)
#         comment_id = self.kwargs['comment_id']
#         comment = Comment.objects.get(pk=comment_id)
#         reply.comment = comment
#         form.instance.author = self.request.user
#         reply.request = self.request
#         reply.save()

#         return redirect('ramenapp:post_detail', pk=reply.comment.post.pk)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         pk = self.kwargs['pk']
#         reply = Reply.objects.get(pk=pk)
#         context['reply'] = reply 
#         return context



# @login_required
# def reply_remove(request, pk):
#     reply = get_object_or_404(Reply, pk=pk)
#     reply.delete()
#     return redirect('ramenapp:post_detail', pk=reply.comment.post.pk)
class ReplyDelete(OnlyMyReplyMixin, DeleteView):
    model = Reply

    def get_success_url(self):
        reply = get_object_or_404(Reply, pk=self.kwargs['pk'])
        pk = reply.comment.post.id
        messages.info(self.request, '返信コメントを削除しました。')
        return resolve_url('ramenapp:post_detail', pk=pk)


def google(request):
    return render(request, 'ramenapp/google285b2115e8e0c8a6.html')

 
