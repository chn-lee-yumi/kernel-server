#!/usr/bin/env bash
# 禁用密码登录，只允许公钥登录
sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config
# 禁用root用户登录
sed -i "s/PermitRootLogin yes/PermitRootLogin no/g" /etc/ssh/sshd_config
sed -i "s/#PermitRootLogin.*/PermitRootLogin no/g" /etc/ssh/sshd_config