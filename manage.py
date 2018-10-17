from flask import session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from info import creat_app, db

# 通过指定的配置名字创建对应配置的app
# creat_app 就类似于工厂方法
app = creat_app("development")

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
