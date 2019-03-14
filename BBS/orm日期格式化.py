import os

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BBS.settings")
    import django

    django.setup()

    from blog import models

    # ret = models.Article.objects.values("create_time").annotate()  # 按照年月日时分秒分组
    ret = models.Article.objects.extra(
        # 在原来查询的基础上额外再执行sql语句
        select={"create_ym": "DATE_FORMAT(create_time, '%%Y-%%m')"}  # %%为转义
        # 查询的每一个对象都多了一个create_ym
    )
    for article in ret:
        print(article.create_time, "|", article.create_ym)

    # 更高灵活的方式执行原生sql语句
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute("""SELECT DATE_FORMAT(create_time,'%Y-%m') FROM blog_article;""")
    ret = cursor.fetchall()
    print(ret)
