from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from ramenapp.models import Post


class BlogPostSitemap(Sitemap):
    """
    ブログ記事のサイトマップ
    """
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Post.objects.all()

    # モデルに get_absolute_url() が定義されている場合は不要
    def location(self, obj):
        return reverse('ramenapp:post_detail', kwargs={'pk':obj.id})

    def lastmod(self, obj):
        if obj.updated_at:
          return obj.updated_at
        else:
          return obj.created_at


class StaticViewSitemap(Sitemap):
    """
    静的ページのサイトマップ
    """
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return ['ramenapp:index', 'ramenapp:category_list', 'ramenapp:post_list']

    def location(self, item):
        return reverse(item)
