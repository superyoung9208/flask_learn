from flask import render_template
from watchlist import app


@app.errorhandler(404)
def page_not_found(e):  # e异常对象
    """404页面"""
    return render_template("errors/404.html"), 404
