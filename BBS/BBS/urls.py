"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from django.conf import settings
from blog import views
from blog import urls as blog_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', views.Login.as_view()),
    url(r'^logout/$', views.Logout.as_view()),

    url(r'^login2/$', views.login2),  # 极验验证滑动验证码的登录
    url(r'^pcgetcaptcha/$', views.pcgetcaptcha),  # 极验验证滑动验证码初始化变量的相关函数

    url(r'^index/$', views.Index.as_view()),  # 首页
    url(r'^register/$', views.Register.as_view()),  # 注册

    # 给用户上传文件,配置一个处理的路由
    url(r'^media/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),

    url(r'^v-code/$', views.v_code),  # 自己写的验证码

    # 二级路由
    url(r'blog/', include(blog_urls)),

]
