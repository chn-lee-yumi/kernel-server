#!/usr/bin/env bash
systemctl disable kernel-agent
systemctl stop kernel-agent
rm -f /usr/lib/systemd/system/kernel-agent.service
systemctl daemon-reload
rm -f /usr/sbin/kernel