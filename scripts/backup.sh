#!/usr/bin/env bash
#
# Репликация профиля игрока на GitHub.
# Запускается по расписанию (systemd-таймер hcenc-backup).
#

set -e

cd /opt/hcenc

./venv/bin/hcenc backup export

if [ ! -f backup/profile.json ]; then
    exit 1
fi

git add backup/profile.json

if git diff --cached --quiet -- backup/profile.json; then
    # изменений нет
    exit 0
fi

git -c user.name="hcenc-backup" \
    -c user.email="almobil2006@gmail.com" \
    commit -m "backup: профиль $(date +'%Y-%m-%d %H:%M')"

GIT_SSH_COMMAND='ssh -o BatchMode=yes' git push origin main
