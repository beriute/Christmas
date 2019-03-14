from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^(\w+)/$', views.home),  # 访问的是某个点击的用户的博客站点

    # url(r'^(\w+)/category/(\w+)$', views.category),  # 章节
    # url(r'^(\w+)/tag/(\w+)$', views.tag),  # 标签
    # url(r'^(\w+)/archive/(\w+)$', views.archive),  # 日期归档

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓上面三个URL可以合成一个↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    # url(r'^(\w+)/(category|tag|archive)/(.*?)$', views.threeinone),  # 三合一

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓上面的函数可以直接使用home这个视图函数↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    url(r'^(\w+)/(category|tag|archive)/(.*?)$', views.home),  # 四合一  (category|tag|archive) 表示这三个任意一个有就可以

    # 点击文章,根据文章id值进入文章详情页面
    url(r'^(\w+)/p/(\d+)/$', views.article),
]