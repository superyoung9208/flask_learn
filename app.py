from flask import Flask, url_for

app = Flask(__name__)


@app.route("/")
def index():
    return '<h1>Hello Totoro!</h1><img src="http://helloflask.com/totoro.gif">'

@app.route("/user/<name>")
def user_page(name):
    return "User %s" %name

@app.route("/test")
def test():
    print(url_for("index"))
    print(url_for("user_page",name="laoyang"))
    print(url_for("user_page",name="lili"))
    print(url_for("test"))
    print(url_for("test",num=2))
    return 'Test page'