from flask import Flask, request, redirect
import json
import time
import logging
from datetime import timedelta
import os
import pickle
import mod_kernel as kernel
import glob
import flask_login

# logging.basicConfig(level=logging.WARNING, filename='/var/log/kernel.log', filemode='a',
#                     format='%(levelname)s: %(message)s')
# TODO：美化登陆界面

# PATH = ""
PATH = "/root/kernel-server/"  # 使用systemd部署时需要绝对路径
MACHINE_DB = PATH + "machine_list.txt"

# 初始化Flask
app = Flask(__name__)
app.send_file_max_age_default = timedelta(seconds=30)
app.secret_key = "s1f3ha9q3oyi4r89pt0ua"
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

######################以下是登录部分代码######################

users = {'admin': {'password': 'gdutnic-Kernel'}}


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(req):
    username = req.form.get('username')
    if username not in users:
        return
    user = User()
    user.id = username
    user.is_authenticated = req.form['password'] == users[username]['password']
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return app.send_static_file("login.html")
    username = request.form['username']
    try:
        if request.form['password'] == users[username]['password']:
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect("https://kernel.gdutnic.com/")
    except:
        pass
    return app.send_static_file("login.html")


# @app.route('/api/login_user_id')
# @flask_login.login_required
# def api_login_user_id():
#     return flask_login.current_user.id


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return app.send_static_file("login.html")


@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect("https://kernel.gdutnic.com/login")


######################以上是登录部分代码######################

@app.route("/")
@flask_login.login_required
def index():
    return app.send_static_file("index.html")


@app.route("/api/machine_list")
@flask_login.login_required
def api_machine_list():
    global machine_list, service_update_time, service_cache_time
    # 检查是否需要刷新缓存
    if time.time() - service_update_time > service_cache_time:
        scan_service()
    # 返回机器数据
    datas = {}
    for name, machine in machine_list.items():
        #     print(name)
        #     print(machine.service_enabled)
        #     print(machine.service_active)
        datas[name] = {
            "online": machine.online,
            "active": machine.service_active,
            "enabled": machine.service_enabled
        }
    return json.dumps(datas)


@app.route("/api/service_list")
@flask_login.login_required
def api_service_list():
    global service_list
    return json.dumps(service_list)


@app.route("/api/init_script_list")
@flask_login.login_required
def api_init_script_list():
    global init_script_list
    return json.dumps(init_script_list)


@app.route("/api/add_machine", methods=['POST'])
@flask_login.login_required
def api_add_machine():
    # 格式:{"name":"nic-tech","url":"https://kernel-agent.gdutnic.com"}
    # try:
    data = json.loads(request.get_data(as_text=True))
    if data["name"] not in machine_list:
        machine_list[data["name"]] = kernel.Machine(data["url"])
        update_service_status(data["name"])
        write_db()
    else:
        return '{"code":-1,"err":"已存在同名机器"}'
    # except Exception as e:
    #     return '{"code":-1,"msg":"%s: %s"}' % (type(e), e)
    return '{"code":0}'


@app.route("/api/del_machine", methods=['POST'])
@flask_login.login_required
def api_del_machine():
    # 格式:{"name":"nic-tech"}
    # try:
    data = json.loads(request.get_data(as_text=True))
    if data["name"] in machine_list:
        machine_list.pop(data["name"])
        write_db()
    # except Exception as e:
    #     return '{"code":-1,"msg":"%s: %s"}' % (type(e), e)
    return '{"code":0}'


@app.route("/api/systemctl", methods=['POST'])
@flask_login.login_required
def api_systemctl():
    # 格式:{"name":"nic-tech","service":"sums","cmd":"start"}
    data = json.loads(request.get_data(as_text=True))
    # print(data)
    if data["name"] in machine_list:
        machine_list[data["name"]].systemctl(data["service"], data["cmd"])
        update_service_status(data["name"])
    return '{"code":0}'


@app.route("/api/deploy_service", methods=['POST'])
@flask_login.login_required
def api_deploy_service():
    # 格式:{"name":"nic-tech","service":"sums"}
    data = json.loads(request.get_data(as_text=True))
    if data["name"] in machine_list:
        exist_service = machine_list[data["name"]].service_enabled[data["service"]]
        if exist_service == "unknown":  # 防止重复部署
            ret_data = machine_list[data["name"]].service_deploy(data["service"])
            update_service_status(data["name"])
            return json.dumps(ret_data)
        else:
            return '{"code":-1,"err":"服务已存在或主机不在线"}'
    else:
        return '{"code":-1,"err":"主机不存在"}'


@app.route("/api/remove_service", methods=['POST'])
@flask_login.login_required
def api_remove_service():
    # 格式:{"name":"nic-tech","service":"sums"}
    data = json.loads(request.get_data(as_text=True))
    if data["name"] in machine_list:
        ret_data = machine_list[data["name"]].service_remove(data["service"])
        update_service_status(data["name"])
        return json.dumps(ret_data)
    else:
        return '{"code":-1,"err":"主机不存在"}'


@app.route("/api/update_all", methods=['GET'])
@flask_login.login_required
def api_update_all():
    scan_service()
    return '{"code":0}'


@app.route("/api/update_machine", methods=['POST'])
@flask_login.login_required
def api_update_machine():
    # 格式:{"name":"nic-tech"}
    data = json.loads(request.get_data(as_text=True))
    if data["name"] in machine_list:
        update_service_status(data["name"])
    return '{"code":0}'


@app.route("/api/run_init_script", methods=['POST'])
@flask_login.login_required
def api_run_init_script():
    # 格式:{"name":"nic-tech","script":"01-ssh"}
    data = json.loads(request.get_data(as_text=True))
    if data["name"] in machine_list:
        ret_data = machine_list[data["name"]].run_init_script(data["script"])
        return json.dumps(ret_data)
    else:
        return '{"code":-1,"err":"主机不存在"}'


def scan_service():
    global service_list, machine_list, service_update_time, init_script_list
    service_update_time = time.time()

    # 扫描服务文件
    for filename in glob.glob(PATH + 'static/service/*/info.json'):
        service_name = filename.split("/")[-2]
        with open(filename) as file:
            service_list[service_name] = json.load(file)

    # 扫描主机上的服务（更新服务状态） 注：如果服务器太多，这里可以改成多线程
    for name in machine_list:
        update_service_status(name)

    # 扫描初始化脚本
    init_script_list = []
    for filename in glob.glob(PATH + 'static/init/*.sh'):
        script_name = filename.split("/")[-1][:-3]
        init_script_list.append(script_name)


def update_service_status(name):
    # 更新单台服务器️的服务状态
    global service_list, machine_list, service_update_time
    service_update_time = time.time()
    for service in service_list:
        machine_list[name].service_is_enabled(service)
        machine_list[name].service_is_active(service)


def read_db():
    global machine_list
    if os.path.exists(MACHINE_DB):
        with open(MACHINE_DB, 'rb') as f:
            machine_list = pickle.load(f)


def write_db():
    global machine_list
    with open(MACHINE_DB, 'wb') as f:
        pickle.dump(machine_list, f)


# 初始化机器列表
machine_list = {}
if os.path.exists(MACHINE_DB):
    read_db()
else:
    write_db()
# print(machine_list)

# 初始化服务列表
service_list = {}
service_update_time = 0
service_cache_time = 60

# 初始化初始化脚本列表
init_script_list = []

# 扫描文件
scan_service()

if __name__ == '__main__':
    # pass
    app.run('0.0.0.0', port=8002)
    # https://kernel-agent.gdutnic.com
