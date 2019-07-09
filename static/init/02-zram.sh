#!/usr/bin/env bash
cat>/etc/kernel-init/zram.sh<<EOF
# 开启zram+swap，减少swap时磁盘IO，其中一个设备作为swap，留下一个设备备用。
# zram的swap设置为6.2G，磁盘swap2G，总swap为8.2G，加上内存7.8G，共16G。（为了好看凑个数）
modprobe zram num_devices=2
#echo 4 > /sys/block/zram0/max_comp_streams # 这个参数好像没什么用，cpu最高还是单核100%
echo lz4 > /sys/block/zram0/comp_algorithm
echo 6348M > /sys/block/zram0/disksize
mkswap /dev/zram0
swapon -p 100 /dev/zram0
EOF
chmod +x /etc/kernel-init/zram.sh