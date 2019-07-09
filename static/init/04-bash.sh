#!/usr/bin/env bash
sed -i "s/HISTSIZE=.*/HISTSIZE=10000/g" /etc/profile  # 修改历史记录长度

cat>/etc/profile.d/server_status.sh<<EOF
uptime
free -h
EOF

cat>/etc/profile.d/ps_color.sh<<EOF
if [ "\$PS1" ]; then
    PS1="\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;33m\]\w\[\033[00m\]\\\\$ "
fi
EOF