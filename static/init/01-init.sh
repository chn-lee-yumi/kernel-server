#!/usr/bin/env bash
chmod +x /etc/rc.local
tmp=$(cat /etc/rc.local | grep '/usr/bin/run-parts /etc/kernel-init/' | wc -l)
if [[ $tmp == 0 ]];then
    mkdir /etc/kernel-init/
    echo "/usr/bin/run-parts /etc/kernel-init/" >> /etc/rc.local
fi