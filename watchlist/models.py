from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from watchlist import db

class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(32))  # 名字
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        """不能直接访问密码"""
        raise AttributeError("不允许读取当前属性")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_password(self, password) -> bool:
        """校验密码"""
        return check_password_hash(self.password_hash, password)


class Movie(db.Model):
    """电影模型"""
    id = db.Column(db.INTEGER, primary_key=True)  # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份