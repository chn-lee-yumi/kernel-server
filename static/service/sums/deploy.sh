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