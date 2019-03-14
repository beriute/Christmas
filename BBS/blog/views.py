from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views import View
from blog.forms import LoginForm, RegisterForm
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.cache import never_cache  # 永不缓存
from PIL import Image, ImageDraw, ImageFont  # ImageDraw是在图片写东西的,ImageFont是写的字体
from django.db.models import Count
from io import BytesIO
from blog import models
from utils.geetest import GeetestLib
from utils.mypage import MyPage
import random

# Create your views here.
CODE_NUM = ""

#  滑动验证码第一步的API,初始化一些参数,用来校验
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


# 滑动验证码的登录
def login2(request):
    res = {"code": 0}
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        # 最终会有一个result结果
        if result:

            # 滑动验证码校验通过
            username = request.POST.get('username')
            pwd = request.POST.get('password')
            code_num = request.POST.get('code_num')
            user = authenticate(username=username, password=pwd)
            if user:
                # 用户名和密码正确
                pass
            else:
                # 用户名或密码错误
                res["code"] = 1
                res["msg"] = "用户名或密码错误"
            # return JsonResponse(res)
        else:
            # 滑动验证码校验失败
            res["code"] = 1
            res["msg"] = "验证码错误"
        return JsonResponse(res)
    form_obj = LoginForm()
    return render(request, "login2.html", {"form_obj": form_obj})


# 登录
class Login(View):

    def get(self, request):
        form_obj = LoginForm()
        return render(request, "login.html", {"form_obj": form_obj})

    def post(self, request):
        res = {
            "code": 0
        }
        print(request.POST)
        # 校验用户密码是否正确
        username = request.POST.get('username')
        pwd = request.POST.get('password')
        code_num = request.POST.get('code_num')
        # 判断验证码是否正确
        if code_num.upper() != request.session.get('code_num'):
            res["code"] = 1
            res["msg"] = "验证码错误"

        user = authenticate(username=username, password=pwd)
        if user:
            # 用户名和密码正确
            login(request, user)
        else:
            # 用户名或密码错误
            res["code"] = 1
            res["msg"] = "用户名或密码错误"

        return JsonResponse(res)


# 注销
class Logout(View):
    def get(self, request):
        logout(request)
        return redirect("/login/")


# 首页
class Index(View):
    def get(self, request):
        print(request)
        # 查询一篇文章作为测试
        # article_obj = models.Article.objects.first()
        # 查询拿出所有的博客文章
        article_list = models.Article.objects.all()
        # 文章的总条数,分页使用
        all_data_amount = article_list.count()
        # 分页的页数
        page_num = request.GET.get("page", 1)
        page_obj = MyPage(page_num, all_data_amount, per_page_data=1, url_prefix='index')
        # 按照分页的设置对总数据进行切片
        date = article_list[page_obj.start:page_obj.end]
        # 显示分页的HTML
        page_html = page_obj.ret_html()

        return render(request, "index.html", {"article_list": date, "page_html": page_html})


# 仅返回验证码图片的视图
@never_cache  # 返回响应的时候告诉浏览器不需要缓存
def v_code(request):
    # 封装一个随机颜色的函数
    def random_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    # 图片不是固定生成的,而是随机生成的图片,所以需要Pillow模块
    # 生成图片对象
    image_obj = Image.new(
        "RGB",  # 生成图片颜色类型
        (250, 35),  # 图片大小像素
        # (0, 0, 0),  # 图片的颜色
        # 随机生成图片颜色的数字,实现背景色的变换
        (random_color())

    )
    # # 将上一步生成的图片保存在本地static下面
    # with open('static/xx.png', 'wb') as f:
    #     image_obj.save(f)
    #
    # # 打开验证码图片
    # with open("static/xx.png", "rb") as f:
    #     data = f.read()

    # 生成一个准备写字的画笔
    draw_obj = ImageDraw.Draw(image_obj)  # 在这个图片上画
    font_obj = ImageFont.truetype('static/font/kumo.ttf', size=30)  # 加载本地的字体文件

    # 生成随机验证码
    tmp = []
    for i in range(5):
        n = str(random.randint(0, 9))  # 数字
        l = chr(random.randint(65, 90))  # 小写字母
        u = chr(random.randint(97, 122))  # 大写字母
        r = random.choice([n, l, u])  # 从三个里面随机选择一个数字填入tmp中
        tmp.append(r)
        # 每次取到的值都写在图片上,每取一个,写一个
        draw_obj.text(
            (i * 45 + 25, 0),  # 坐标  (x,y)
            r,  # 内容
            fill=random_color(),  # 颜色
            font=font_obj  # 字体
        )
    code_num = "".join(tmp)  # 把列表里面的内容拼接在一起
    # global CODE_NUM  # 全局变量在函数里面引用需要声明一下
    # CODE_NUM = code_num  # 给全局编码赋值

    # 将该次请求生成的验证码保存在该请求对应的session数据中
    request.session["code_num"] = code_num.upper()

    # 直接生成个图片保存在内存中
    f = BytesIO()
    image_obj.save(f, "png")
    # 从内存中读取图片
    data = f.getvalue()

    # content_type返回的数据类型
    return HttpResponse(data, content_type="image/png")


# 注册
class Register(View):
    def get(self, request):
        form_obj = RegisterForm()
        return render(request, "reg.html", {"form_obj": form_obj})

    def post(self, request):
        res = {"code": 0}
        # print(request.POST)
        # 先从验证码校验
        v_code = request.POST.get("v_code", "")
        print(v_code)
        # re_session = request.session.get("code_num")
        # print(re_session)
        if v_code.upper() == request.session.get("code_num", ""):
            # 因为在获取v_code这个视图函数的时候,本身就存储在request.session中了
            # 验证码正确
            print("通过验证码验证")
            form_obj = RegisterForm(request.POST)
            # 使用form做校验
            if form_obj.is_valid():
                # 数据有效,注册用户
                # 注意移除不需要的re_password
                form_obj.cleaned_data.pop("re_password")
                # 再创建用户之前,拿到用户上传的头像文件
                avatar_file = request.FILES.get('avatar')
                # 创建用户,因为在UserInfo这个库中有avatar这个字段
                # 并且是models.FileField类型的
                # 里面upload_to是直接保存的路径,
                # 所以不需要再单独打开文件,因为FileField会找到那个路径直接打开文件

                models.UserInfo.objects.create_user(**form_obj.cleaned_data, avatar=avatar_file)
                # 跳转到登录页面
                res["url"] = '/login/'
            else:
                # 用户输入错误
                res["code"] = 1
                res["error_msg"] = form_obj.errors
        else:
            res["code"] = 2
            res["msg"] = "验证码错误"
        return JsonResponse(res)


# 每个用户自己的博客站点
def home2(request, username, *args):  # url里面的\w+就是用户的username
    print(args)
    # 先找寻用户
    # user_obj = models.UserInfo.objects.filter(username=username).first()
    # if not user_obj:
    #     return HttpResponse("404页面,找不到该网页")
    user_obj = get_object_or_404(models.UserInfo, username=username)  # 如果能找到这个对象的话,就把对象赋值给user_obj,如果没有则显示404页面
    # 根据用户寻找博客标题
    blog = user_obj.blog
    # 查询当前用户写的所有的博客
    article_list = models.Article.objects.filter(user=user_obj)
    # 查找当前blog对应的博客分类
    category_list = models.Category.objects.filter(blog=blog)
    # 查找当前blog对应的文章标签有哪些
    tag_list = models.Tag.objects.filter(blog=blog)
    # 如果有args,说明URL有除了用户名之外的参数
    if args:
        if args[0] == "category":
            # 按照文章章节分类查询
            article_list = article_list.filter(category__title=args[1])
            print(article_list)
        elif args[0] == "tag":
            # 按照文章章节分类查询
            article_list = article_list.filter(tags__title=args[1])
            print(article_list)
        else:
            # 因为url中的正则是.*?匹配任意字符,所以防止有人不输入"-"报错,提前try一下
            # 按照文章的日期归档分类

            try:
                # 先根据url获取的日期进行年月的分割
                year, month = args[1].split("-")
                print(year)
                print(month)
                article_list = article_list.filter(create_time__year=year, create_time__month=month)
                print(article_list)
                # 这里注意时区问题,需要在settings.py文件中USE_TZ = False
            except Exception as e:
                article_list = []  # 如果没有按照规定的字符输入"-",就查询不到任何数据

    # 对当前blog的所有文章按照年月分组 查询
    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={"y_m": "DATE_FORMAT(create_time, '%%Y-%%m')"}
    ).values("y_m").annotate(c=Count("id")).values("y_m", "c")  # 以"y_m"进行分组annotate
    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓上面一段代码块的分析注释↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    # models.Article.objects.filter(user=user_obj)                   --->  查询出当前作者写的所有文章
    # extra(select={"y_m": "DATE_FORMAT(create_time, '%%Y-%%m')"})   --->  将所有文章的创建时间格式化成年-月的格式,方便后续分组查询
    # .values("y_m").annotate(c=Count("id"))                         --->  用上一步时间格式化得到的y_m字段做分组查询,同时统计出来每个分组对应的文章数
    # values("y_m", "c")                                             --->  把页面需要的日期归档和文章数字段取出来

    return render(request, 'home.html',
                  {"blog": blog,
                   "article_list": article_list,
                   "category_list": category_list,
                   "tag_list": tag_list,
                   "archive_list": archive_list,
                   "user": user_obj
                   })


# 根据inclusion_tag修改的home函数,home2函数是没修改之前的
def home(request, username, *args):  # url里面的\w+就是用户的username
    user_obj = get_object_or_404(models.UserInfo, username=username)  # 如果能找到这个对象的话,就把对象赋值给user_obj,如果没有则显示404页面
    # 根据用户寻找博客标题
    blog = user_obj.blog
    # 查询当前用户写的所有的博客
    article_list = models.Article.objects.filter(user=user_obj)
    if args:
        if args[0] == "category":
            # 按照文章章节分类查询
            article_list = article_list.filter(category__title=args[1])
            print(article_list)
        elif args[0] == "tag":
            # 按照文章章节分类查询
            article_list = article_list.filter(tags__title=args[1])
            print(article_list)
        else:
            # 因为url中的正则是.*?匹配任意字符,所以防止有人不输入"-"报错,提前try一下
            # 按照文章的日期归档分类

            try:
                # 先根据url获取的日期进行年月的分割
                year, month = args[1].split("-")
                print(year)
                print(month)
                article_list = article_list.filter(create_time__year=year, create_time__month=month)
                print(article_list)
                # 这里注意时区问题,需要在settings.py文件中USE_TZ = False
            except Exception as e:
                article_list = []  # 如果没有按照规定的字符输入"-",就查询不到任何数据

    return render(request, 'home.html',
                  {"blog": blog,
                   "article_list": article_list,
                   "username": username
                   })


# 文章详情
def article(request, username, id):
    """

    :param request:   请求对象
    :param username: 用户名
    :param id: 文章id
    :return:
    """
    user_obj = get_object_or_404(models.UserInfo, username=username)  # 用户对象
    blog = user_obj.blog  # 博客对象
    article_obj = models.Article.objects.filter(id=id).first()  # 根据id找到文章
    return render(request, "article.html", {
        "blog": blog,
        "username": username,
        "article": article_obj,
    })

