from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import sys, os

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path), os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dev'
login_manager = LoginManager(app)


@login_manager.user_loader
def user_loader(user_id):
    """创建用户加载回调函数，接受用户 ID 作为参数"""
    from watchlist.models import User
    user = User.query.get(user_id)
    return user


# 未通过的路由保护的用户重定向到登录页面
login_manager.login_view = 'login'


@app.context_processor
def inject_user():
    """模板通用变量"""
    from watchlist.models import User
    user = User.query.first()
    return dict(user=user)


from watchlist import views, commands, errors
