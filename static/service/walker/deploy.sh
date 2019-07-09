#!/usr/bin/env bash
useradd walker
curl -sL https://kernel.gdutnic.com/static/service/walker/walker_linux_amd64 -o /usr/bin/walker
chmod +x /usr/bin/walker
cat>/usr/lib/systemd/system/walker.service<<EOF
[Unit]
Description=sw
After=network.target

[Service]
ExecStart=/usr/bin/walker -r -s 172.18.0.3:8500
User=walker

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable walker
systemctl start walker