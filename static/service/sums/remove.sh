#!/usr/bin/env bash
systemctl disable sums
systemctl stop sums
rm -f /usr/lib/systemd/system/sums.service
systemctl daemon-reload
rm -rf /root/sums