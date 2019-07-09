# kernel-server

项目代号：Kernel。服务器集群管理系统。

前排提醒：下面会看到一堆“Kernel”，不要误以为是Linux Kernel，而是集群管理系统的代号。

# Kernel的组成

Kernel由Agent和Server两部分组成。

Agent运行在各个服务器上，可以执行Server发来的各种命令（~~看成是个后门也行~~自己人做的~~后门~~，能叫后门吗？那叫桥梁！）

Server能汇总各个服务器的状态以及其上运行的服务，并且能一键部署服务和执行其它命令等。

# Agent的实现

采用Go开发，静态编译，单文件，部署非常方便。同时轻量设计，几乎不需要更新，所有操作都从由Server下发。Agent和Server采用HTTP进行通信。

## 交互流程

1. Agent启动后，监听端口，等待Server的请求。
2. Server连接时Agent对Server身份进行验证。（目前是验证ip）
3. Agent执行Server的命令。

## API接口

`/api/ExecCmd`：执行shell命令并返回结果

```json
GET：{"cmd": "命令"}
返回：{"code": 0, "msg": "命令执行结果"}
```

# Server的实现

采用Python+Flask开发。

因为我们有很多的服务，因此我们不打算将特定服务的逻辑写入源码，而是采取插件化的方式去实现。

对于单个服务，我们实现的功能包括服务状态查询、启停、部署、卸载等操作。由于部署和卸载等操作比较复杂，目前打算由运维人员手动编写shell脚本进行安装/卸载，点击部署/卸载后，脚本会在目标服务器上执行。

关于数据库，从最简的原则看，我们只需要记录集群的服务器，以及一些手工记录的服务器描述信息，其余都可以从服务器上实时获取并缓存。因此我们直接将服务器列表序列化后存储到txt文件中。

添加服务器后会检查服务器环境并执行初始化脚本。

## 服务部署移除工作流程

服务安装和卸载的脚本文件存放在源代码目录的`static`中，目录结构形如：

```
$ tree ~/PycharmProjects/Kernel/static
/Users/liyumin/PycharmProjects/Kernel/static
├── index.html
├── init
│   ├── 01-ssh.sh
│   └── 02-zram.sh
└── service
    ├── gitlab
    │   ├── deploy.sh
    │   ├── info.json
    │   └── remove.sh
    └── sums
        ├── deploy.sh
        ├── info.json
        ├── remove.sh
        └── sums.tgz
```

其中`service`目录内存放各个服务的安装卸载脚本，`init`目录存放服务器初始化脚本（仅在服务器加入集群时运行一次，按编号顺序执行）。如果需要编译文件，可以登录cloud.gdutnic.com进行编辑。

当调用部署和卸载的API时，服务器会自动下载对应的脚本执行。

## 如何添加服务

1. 在`static`目录下新建文件夹，名字为服务名
2. 新建`info.json`，内容模板如下：
```json
{
  "description": "这是xxxxx服务，干嘛用的"
}
```
3. 新建部署脚本`deploy.sh`和卸载脚本`remove.sh`，内容按需编写。
4. 在Web界面中点击“刷新服务”

## 服务编写示例

这里以`Sums`项目的服务编写为例子。

在`static/service`目录下新建名为`sums`的服务。

编写`info.json`：

```json
{
  "description": "Sums - 服务器用户管理系统（公钥自助登记）"
}
```

编写`deploy.sh`：（其中`sums.tgz`是项目打包好的压缩文件）

```shell
#!/usr/bin/env bash
cd /tmp
wget https://kernel.gdutnic.com/static/service/sums/sums.tgz
tar xzf sums.tgz
rm -rf sums.tgz
cd sums_pack
mkdir /root/sums
cp sums /root/sums
cp index.html /root/sums
cp sums.service /usr/lib/systemd/system/
systemctl daemon-reload
systemctl enable sums
systemctl start sums
rm -rf /tmp/sums_pack
```

编写`remove.sh`：

```shell
#!/usr/bin/env bash
systemctl disable sums
systemctl stop sums
rm -rf /usr/lib/systemd/system/sums.service
systemctl daemon-reload
rm -rf /root/sums
```

打包项目文件：（有些服务可能不需要额外的文件，可以忽略这步）

首先把`Sums`的项目文件放到一个名为`sums_pack`的文件夹（名字当然可以自己起，脚本文件里面用），其结构如下：

```
$ tree sums_pack 
sums_pack
├── index.html
├── sums
└── sums.service
```

然后我们将这个文件夹打包：`tar czf sums.tgz sums_pack`

注意事项：所有服务部署完之后必须可以用`systemctl status 服务名`来看到服务状态。（即`/usr/lib/systemd/system/`目录下要有`服务名.service`的文件存在）

## TODO

- 增加修改机器功能（名字、URL）
- 美化登录界面

# Kernel Server 部署

## 安装

以root用户执行。

```shell
cd /root
git clone https://github.com/chn-lee-yumi/kernel-server.git
cp /root/kernel-server/kernel-server.service /usr/lib/systemd/system/
systemctl daemon-reload
systemctl enable kernel-server
systemctl start kernel-server
```

## 更新

以root用户执行。

```shell
cd /root/kernel-server
git pull
systemctl restart kernel-server
```

# Kernel Agent 部署

一键安装脚本：(请用root用户执行)

`curl -sL https://kernel.gdutnic.com/static/agent/install.sh | bash`

一键卸载脚本：(请用root用户执行)

`curl -sL https://kernel.gdutnic.com/static/agent/uninstall.sh | bash`

# 注意

域名没有做单独配置，请自行修改代码和脚本中的所有相关域名。代码中，`https://kernel.gdutnic.com/`是Server的地址。

Server默认使用8002端口，Agent默认使用8001端口。

Agent项目地址：https://github.com/chn-lee-yumi/kernel-agent

Agent编译好之后放在了`static/agent/kernel`
