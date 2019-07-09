#!/usr/bin/env bash
systemctl disable walker
systemctl stop walker
rm -f /usr/lib/systemd/system/walker.service
systemctl daemon-reload
rm -f /usr/bin/walker
userdel -r walker