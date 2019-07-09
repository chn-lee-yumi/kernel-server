#!/usr/bin/env bash
yum -y install nano python36 python36-pip
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install flask requests