import requests

DOWNLOAD_URL = "https://kernel.gdutnic.com/static"  # 注：末尾不能有斜杠


class Machine:
    """
    执行命令：exec_cmd(cmd)
    控制服务：service_ctl(service_name, cmd)  # cmd: start stop restart enable disable
    查询服务运行状态：service_is_active(service_name)  # 返回：active inactive unknown
    查询服务自启状态：service_is_enabled(service_name)  # 返回：enabled disabled unknown
    部署服务：service_deploy(service_name)
    移除服务：service_remove(service_name)
    """

    def __init__(self, url):  # 后面这两个不加会报object has no attribute的错，神奇
        self.url = url
        self.service_active = dict()  # 服务是否运行
        self.service_enabled = dict()  # 服务是否自启动
        self.online = False

    def exec_cmd(self, cmd):
        try:
            a = requests.get(self.url + "/api/ExecCmd", data={"cmd": cmd})
            self.online = True
            if a.status_code == 200:
                if a.json()['code'] != 0:
                    return {'code': a.json()['code'], 'err': a.json()['err'], 'msg': a.json()['msg']}
                else:
                    return a.json()
            else:
                return {'code': -100, 'err': a.status_code}
        except requests.exceptions.ConnectionError:
            self.online = False
            return {'code': -101, 'err': "主机连接失败"}
        except requests.exceptions.MissingSchema:
            self.online = False
            return {'code': -102, 'err': "主机的URL错误"}

    def systemctl(self, service_name, cmd):
        # cmd: start stop restart enable disable
        result = self.exec_cmd("systemctl %s %s" % (cmd, service_name))
        return result  # code: <0 agent error; =0 OK; >0 command error

    def service_is_active(self, service_name):
        # active inactive unknown
        result = self.systemctl(service_name, "is-active")
        if result['code'] == 0:
            self.service_active[service_name] = result["msg"]
        elif result['code'] == 1:
            if self.service_enabled[service_name] != "unknown":
                self.service_active[service_name] = "inactive"
            else:
                self.service_active[service_name] = "unknown"
        else:
            self.service_active[service_name] = "error"
        return self.service_active[service_name]

    def service_is_enabled(self, service_name):
        # enabled disabled unknown
        result = self.systemctl(service_name, "is-enabled")
        if result['code'] == 0:
            self.service_enabled[service_name] = result["msg"]
        elif result['code'] == 1:
            # 如果enabled!=unknown and active!=active, 就是inactive
            if result['msg'].strip() == "disabled":
                self.service_enabled[service_name] = "disabled"
            else:
                self.service_enabled[service_name] = "unknown"
        else:
            self.service_enabled[service_name] = "error"
        return self.service_enabled[service_name]

    def service_deploy(self, service_name):
        result = self.exec_cmd("curl -sL %s/service/%s/deploy.sh | bash" % (DOWNLOAD_URL, service_name))
        # wget -q -O - %s/%s/deploy.sh | bash
        return result

    def service_remove(self, service_name):
        result = self.exec_cmd("curl -sL %s/service/%s/remove.sh | bash" % (DOWNLOAD_URL, service_name))
        return result

    def run_init_script(self, script_name):
        result = self.exec_cmd("curl -sL %s/init/%s.sh | bash" % (DOWNLOAD_URL, script_name))
        return result


if __name__ == '__main__':
    nic_tech = Machine('https://kernel-agent.gdutnic.com')
    print(nic_tech.exec_cmd("cat /proc/cpuinfo | egrep '^model name' | uniq | awk '{print substr($0, index($0,$4))}'"))
