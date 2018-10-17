from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    """工程配置信息"""
    DEBUG = True

    # 为mysql数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:123456@127.0.0.1:3306/news_information"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
# 添加配置
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)


@app.route('/')
def index():
    return "index"

if __name__ == '__main__':
    app.run(debug=True)
