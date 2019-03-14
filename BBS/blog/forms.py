from django import forms
from django.core.validators import RegexValidator  # 正则表达式
from django.core.exceptions import ValidationError
from blog import models


# 登录
class LoginForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        min_length=4,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户名不能少于4位"
        },
        widget=forms.widgets.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        label="密码",
        min_length=6,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码不能少于6位"
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


# 注册
class RegisterForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        min_length=4,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户名不能少于4位"
        },
        widget=forms.widgets.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        label="密码",
        min_length=6,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码不能少于6位"
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    re_password = forms.CharField(
        label="确认密码",
        min_length=6,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码不能少于6位"
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    phone = forms.CharField(
        label="手机号",
        min_length=6,
        error_messages={
            "required": "手机号码不能为空",
        },
        validators=[RegexValidator(r'1[3-9]\d{9}', "手机号码格式不正确")],
        widget=forms.widgets.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    email = forms.CharField(
        label="邮箱",
        min_length=6,
        error_messages={
            "required": "邮箱不能为空",
        },
        validators=[RegexValidator(r'^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$', "手机号码格式不正确")],
        widget=forms.widgets.EmailInput(
            attrs={
                "class": "form-control"
            }
        )
    )

    # 校验密码的全局钩子
    def clean(self):
        pwd = self.cleaned_data.get("password")
        re_pwd = self.cleaned_data.get("re_password")
        if re_pwd and re_pwd == pwd:
            return self.cleaned_data
        else:
            self.add_error('re_password', "两次密码不一致")
            raise ValidationError("两次密码不一致")
