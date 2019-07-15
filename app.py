from flask import Flask, url_for, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os, sys
import click

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dev'
login_manager = LoginManager(app)


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


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized database.")  # 输出提示信息


@app.cli.command()
def forge():
    db.create_all()
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
    ]
    user = User(name=name)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.add(user)
    db.session.commit()
    click.echo('Done')


# confirmation_prompt=True 会要求二次确认输入
# hide_input=True 会让密码输入隐藏
@app.cli.command()
@click.option('--username', prompt=True, help="The username used login")
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help="The password used login")
def admin(username, password):
    """create_user"""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo("updating user")
        user.name = username
        user.password = password
    else:
        click.echo("create user")
        user.name = username
        user.password = password
        db.session.add(user)

    db.session.commit()
    click.echo("Done.")


@app.context_processor
def inject_user():
    """模板通用变量"""
    user = User.query.first()
    return dict(user=user)


@app.errorhandler(404)
def page_not_found(e):  # e异常对象
    """404页面"""
    user = User.query.first()
    return render_template("404.html"), 404


@login_manager.user_loader
def user_loader(user_id):
    """创建用户加载回调函数，接受用户 ID 作为参数"""
    user = User.query.get(user_id)
    return user


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if not current_user.is_authenticated:
            return redirect(url_for("index"))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 50:
            flash("Invalid input")
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash("Item created.")
        return redirect(url_for("index"))

    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


login_manager.login_view = 'login'


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username and password:
            flash("Invalid input")
            return redirect(url_for("login"))
        user = User.query.first()
        if user.name == username and user.check_password(password):
            login_user(user)
            flash("Login success")
            return redirect(url_for("index"))

        flash("Invalid username or password")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """退出登陆"""
    logout_user()
    flash("Good bye")
    return redirect(url_for("index"))


@app.route("/settings",methods=['GET', 'POST'])
@login_required
def settings():
    """设置用户名字"""
    if request.method == "POST":
        username = request.form.get("name")
        if not username or len(username) > 20:
            flash("Invalid input")
        current_user.name = username
        db.session.commit()
        flash("setting updated")
        return redirect(url_for('index'))
    return render_template("settings.html")


@app.route("/movies/<int:movie_id>", methods=["GET", "POST", "DELETE"])
def update_movie(movie_id):
    """更新或者是获取一个movie"""
    if request.method == "GET":
        movie = Movie.query.get_or_404(movie_id)
        return render_template("edit.html", movie=movie)
    elif request.method == "POST":
        title = request.form.get("title")
        year = request.form.get("year")
        if not title or not year or len(year) > 4 or len(title) > 50:
            flash("Invalid input")
            return redirect(url_for("update_movie", movie_id=movie_id))
        movie = Movie.query.get_or_404(movie_id)
        movie.title = title
        movie.year = year
        db.session.commit()
        flash("Item updated.")
        return redirect(url_for("index"))
    elif request.method == "DELETE":
        movie = Movie.query.get_or_404(movie_id)
        db.session.remove(movie)
        db.session.commit()


@app.route("/user/<name>")
def user_page(name):
    return "User %s" % name


@app.route("/test")
def test():
    print(url_for("index"))
    print(url_for("user_page", name="laoyang"))
    print(url_for("user_page", name="lili"))
    print(url_for("test"))
    print(url_for("test", num=2))
    return 'Test page'


if __name__ == '__main__':
    app.run(debug=True)
