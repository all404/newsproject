from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config

# 初始化数据库
# 在flask很多扩展里面都可以初始化扩展的对象,然后在调用init_app方法初始化
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    # 添加配置
    app.config.from_object(config[config_name])

    # 初始化数据库
    db.init_app(app)
    # 初始化redis存储对象
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST, port=config[config_name].REDIS_PORT)
    # 开启当前项目 CSRF 保护,只做服务器验证功能
    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)

    return app
