from flask import request, flash, redirect, url_for, render_template
from flask_login import login_user, login_required, logout_user, current_user

from watchlist import app, db
from watchlist.models import Movie, User

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


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
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
            return redirect(url_for('index'))
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
        db.session.delete(movie)
        db.session.commit()
        flash("Item deleted.")
        return redirect(url_for("index"))

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