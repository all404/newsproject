from flask import request, current_app, abort, make_response, jsonify

from info import redis_store, constants
from info.utils.captcha.captcha import captcha
from info.utils.captcha.fonts.response_code import RET
from . import passport_blu


# 注册蓝图路由
@passport_blu.route("/image_code")
def get_image_code():
    """
    1. 取到参数
    2. 判断参数是否有值
    3. 生成图片验证码
    4. 保存图片验证码文字内容到redis
    5. 返回验证码图片
    """
    # 1.取到参数
    image_code_id = request.args.get('imageCodeId')
    # 2.判断参数是否有值
    if not image_code_id:
        return
    # 3.生成图片验证码
    name, text, image = captcha.generate_captcha()
    # 4.保存图片验证码文字内容到redis
    try:
        redis_store.set("ImageCodeId_" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
        return make_response(jsonify(error=RET.DATAERR, errmsg="保存图片验证码失败"))

    # 5.返回验证码图片
    response = make_response(image)
    # 设置返回的内容类型,以便浏览器能更加智能地识别其是什么类型
    response.headers["Content-Type"] = "image/jpg"
    return response
