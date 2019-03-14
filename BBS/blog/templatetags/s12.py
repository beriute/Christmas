from django import template
from django.shortcuts import get_object_or_404
from django.db.models import Count
from blog import models

# 必须叫这个名字
register = template.Library()


@register.inclusion_tag(filename='left_menu.html')  # 这些数据是要填充哪个页面需要声明
def left_menu(username):
    user_obj = get_object_or_404(models.UserInfo, username=username)  # 如果能找到这个对象的话,就把对象赋值给user_obj,如果没有则显示404页面
    # 根据用户寻找博客标题
    blog = user_obj.blog
    # 查找当前blog对应的博客分类
    category_list = models.Category.objects.filter(blog=blog)
    # 查找当前blog对应的文章标签有哪些
    tag_list = models.Tag.objects.filter(blog=blog)
    # 对当前blog的所有文章按照年月分组 查询
    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={"y_m": "DATE_FORMAT(create_time, '%%Y-%%m')"}
    ).values("y_m").annotate(c=Count("id")).values("y_m", "c")
    # 以"y_m"进行分组annotate    --->  把页面需要的日期归档和文章数字段取出来

    return {
            "category_list": category_list,
            "tag_list": tag_list,
            "archive_list": archive_list,
            "username": username
            }
