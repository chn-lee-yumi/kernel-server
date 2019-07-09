#!/usr/bin/env bash
# 开机更新时间
cat>/etc/kernel-init/ntp.sh<<EOF
# 每次重启之后时间都不对，所以要先更新时间
/usr/sbin/ntpdate ntp.ntsc.ac.cn > /tmp/ntp.log
EOF
chmod +x /etc/kernel-init/ntp.sh
# 每小时校对一次时间
cat>/etc/cron.hourly/ntp.sh<<EOF
/usr/sbin/ntpdate ntp.ntsc.ac.cn >> /tmp/ntp.log
EOF
chmod +x /etc/cron.hourly/ntp.sh