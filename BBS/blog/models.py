from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

__all__ = ["UserInfo", "Blog", "Category", "Tag", "Article", "ArticleDetail",
           "Article2Tag", "ArticleUpDown", "Comment"]


class UserInfo(AbstractUser):
    """
    用户信息表
    """
    phone = models.CharField(max_length=11, null=True, unique=True, verbose_name="手机号")  # 手机号
    avatar = models.FileField(upload_to="avatars/", default="avatars/default.png", verbose_name="头像")  # 头像

    blog = models.OneToOneField(to="Blog", null=True, verbose_name="博客")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name


class Blog(models.Model):
    """
    博客信息
    """
    title = models.CharField(max_length=64, verbose_name="个人博客标题")  # 个人博客标题
    theme = models.CharField(max_length=32, verbose_name="博客主题")  # 博客主题

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "博客"
        verbose_name_plural = verbose_name


class Category(models.Model):
    """
    个人博客文章分类
    """
    title = models.CharField(max_length=32, verbose_name="分类标题")  # 分类标题
    blog = models.ForeignKey(to="Blog", verbose_name="外键关联博客")  # 外键关联博客，一个博客站点可以有多个分类

    def __str__(self):
        return "{}-{}".format(self.blog.title, self.title)

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = verbose_name


class Tag(models.Model):
    """
    标签
    """
    title = models.CharField(max_length=32, verbose_name='标签名')  # 标签名
    blog = models.ForeignKey(to="Blog", verbose_name="所属博客")  # 所属博客
    # 同一篇博客可以有多个标签

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name


class Article(models.Model):
    """
    文章
    """
    title = models.CharField(max_length=50, verbose_name="文章标题")  # 文章标题
    desc = models.CharField(max_length=255, verbose_name="文章描述")  # 文章描述
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 创建时间
    category = models.ForeignKey(to="Category", null=True, blank=True,
                                 verbose_name="文章分类")  # 文章分类,blank=True,专门约束admin里面的是否必填选项
    user = models.ForeignKey(to="UserInfo", verbose_name="作者")  # 作者
    tags = models.ManyToManyField(  # 文章的标签
        to="Tag",
        through="Article2Tag",
        through_fields=("article", "tag"),
        verbose_name="文章标签"
    )

    # 为了前端拿数据尽量减少跨表查询,所以把评论跟点赞写在文章表中
    # 当有人评论的时候,这几个字段加1,运用事务操作,要么都成功,要么都失败
    comment_count = models.IntegerField(default=0, verbose_name="评论数")
    # 点赞数
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    def __str__(self):
        return "{}--{}".format(self.user.username, self.title)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name


class ArticleDetail(models.Model):
    """
    文章详情表
    """
    content = models.TextField(verbose_name="文章内容")  # 文章内容
    article = models.OneToOneField(to="Article", verbose_name="外检关联文章")

    class Meta:
        verbose_name = "文章详情"
        verbose_name_plural = verbose_name


class Article2Tag(models.Model):
    """
    文章和标签的多对多关系表
    """
    article = models.ForeignKey(to="Article")
    tag = models.ForeignKey(to="Tag")

    def __str__(self):
        return "{}-{}".format(self.article, self.tag)

    class Meta:
        unique_together = (("article", "tag"),)
        verbose_name = "文章-标签"
        verbose_name_plural = verbose_name


class ArticleUpDown(models.Model):
    """
    点赞表
    """
    user = models.ForeignKey(to="UserInfo", null=True)
    article = models.ForeignKey(to="Article", null=True)
    is_up = models.BooleanField(default=True, verbose_name="点赞还是踩")  # 点赞还是踩灭

    def __str__(self):
        return "{}-{}".format(self.user_id, self.article_id)

    class Meta:
        unique_together = (("article", "user"),)  # 同一个人只能给一篇文章点一次赞
        verbose_name = "点赞"
        verbose_name_plural = verbose_name


class Comment(models.Model):
    """
    评论表
    """
    article = models.ForeignKey(to="Article")
    user = models.ForeignKey(to="UserInfo")
    content = models.CharField(max_length=255, verbose_name="评论内容")  # 评论内容
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    parent_comment = models.ForeignKey("self", null=True, blank=True)  # 自己关联自己



    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
