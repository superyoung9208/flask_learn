from flask import Flask, url_for, render_template

app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template("index.html",name=name,movies=movies)


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
