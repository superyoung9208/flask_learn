from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
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

class User(db.Model):
    """用户模型"""
    id = db.Column(db.INTEGER,primary_key=True)
    name = db.Column(db.String(32)) #名字

class Movie(db.Model):
    """电影模型"""
    id = db.Column(db.INTEGER, primary_key=True) # 主键
    title = db.Column(db.String(60))  # 电影标题
    year = db.Column(db.String(4))  # 电影年份




@app.cli.command() # 注册为命令
@click.option('--drop',is_flag = True,help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized database.") #输出提示信息

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
        movie = Movie(title=m['title'],year=m['year'])
        db.session.add(movie)
    db.session.add(user)
    db.session.commit()
    click.echo('Done')

@app.context_processor
def inject_user():
    """模板通用变量"""
    user = User.query.first()
    return dict(user=user)

@app.errorhandler(404)
def page_not_found(e): # e异常对象
    """404页面"""
    user = User.query.first()
    return render_template("404.html"),404

@app.route("/")
def index():
    user = User.query.first()
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


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
    app.run()
