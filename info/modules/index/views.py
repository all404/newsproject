from flask import render_template, current_app

from info import redis_store
from . import index_blu


@index_blu.route('/')
def index():
    redis_store.set("name", "zhangsan")
    return render_template("news/index.html")


@index_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('news/favicon.ico')
