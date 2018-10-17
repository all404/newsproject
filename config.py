from redis import StrictRedis


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

class DevelopmentConfig(Config):
    """开发环境下的配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境下的配置"""
    DEBUG = False


class TestingConfig(Config):
    """单元测试环境下的配置"""
    DEBUG = False
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}