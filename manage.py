from flask import Flask, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


class Config(object):
    """工程配置信息"""
    DEBUG = True

    SECRET_KEY = "E8Koa9m4xNQSAngJeNMqI7gKpMVFQoFLgETau0PXAiKl+kliEkZuF7qOJ5HUk98J"

    # 为mysql数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/news_information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis的配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # Session的保存位置
    SESSION_TYPE = "redis"
    # 开启session签名
    SESSION_USE_SIGNER = True
    # 指定Session保存的redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间(2天)
    PERMANENT_SESSION_LIFETIME = 86400 * 2

app = Flask(__name__)
# 添加配置
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)
# 初始化redis存储对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目 CSRF 保护,只做服务器验证功能
CSRFProtect(app)
# 设置session保存指定位置
Session(app)

manager = Manager(app)
# 将app与db关联
Migrate(app, db)
# 将迁移命令迁移到manager中
manager.add_command("db", MigrateCommand)


@app.route('/')
def index():
    session["name"] = "zhangsan"
    return "index"

if __name__ == '__main__':
    manager.run()
