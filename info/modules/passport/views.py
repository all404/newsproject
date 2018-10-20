import random
import re

from flask import request, current_app, abort, make_response, jsonify, session

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.captcha.fonts.response_code import RET
from . import passport_blu


@passport_blu.route('/register', methods=['POST'])
def register():
    """
    注册
    1.获取参数
    2.校验参数(是否为空,参数规则)
    3.从redis中取出真实短信验证码
    4.与用户输入的短信验证码对比,若不一致,返回验证码错误
    5.如果一致,初始化User模型,并且赋值
    6.将User模型添加到数据库
    7.返回响应
    :return:
    """
    # 1.获取参数
    params_dict = request.json
    mobile = params_dict['mobile']
    sms_code = params_dict['smsCode']
    password = params_dict['password']

    # 2.校验参数(是否为空, 参数规则)
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")
    # 3.从redis中取出真实短信验证码
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")

    # 4.与用户输入的短信验证码对比, 若不一致, 返回验证码错误
    if real_sms_code != sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg="验证码错误")

    # 5.如果一致,初始化User模型,并且赋值
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    user.password = password

    # 6.将User模型添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 往session中保存数据表示当前已经登录
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name

    # 7.响应
    return jsonify(errno=RET.OK, errmsg="注册成功")


@passport_blu.route('/sms_code', methods=['POST'])
def get_sms_code():
    """
    短信验证码
    1.获取参数: 手机号,图片验证码内容,图片验证码编号(随机值)
    2.校验参数(是否有值,参数是否符合规则)
    3.先从redis取出真实图片验证码内容
    4.与用户验证码内容进行对比,若不一致,返回错误信息
    5.如果一致,生成短信验证码内容
    6.发送短信验证码&保存短信验证码到redis
    7.告知发送结果
    :return:
    """
    # 1.获取参数: 手机号,图片验证码内容,图片验证码编号(随机值)
    params_dict = request.json  # 或者json.loads(requset.data)
    mobile = params_dict['mobile']
    image_code = params_dict['imageCode']
    image_code_id = params_dict['imageCodeId']

    # 2.校验参数(是否有值,参数是否符合规则)
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if not re.match('1[35678]\\d{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式错误")

    # 3.先从redis取出真实图片验证码内容
    try:  # 默认从redis中取出的验证码时字节型,要取出字符串型,需要在redis中配置 decode_responses=True
        real_image_code = redis_store.get("ImageCodeId_" + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码过期")

    # 4.与用户验证码内容进行对比,若不一致,返回错误信息
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码输入错误")

    # 5.如果一致,生成短信验证码内容
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信验证码内容: %s" % sms_code_str)

    # 6.发送短信验证码
    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 5], 1)
    # if result != 0:
    #     return jsonify(errno=RET.DATAERR, errmsg="短信发送失败")
    # 保存短信验证码到redis
    try:
        redis_store.set("SMS_" + mobile, sms_code_str, ex=constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 7.告知发送结果
    return jsonify(errno=RET.OK, errmsg="发送成功")






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
