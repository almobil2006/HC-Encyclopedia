#!/usr/bin/env bash
#
# Установка HC Encyclopedia на сервере (Ubuntu/Debian).
#
# Запуск:  bash scripts/deploy.sh
# Обновление: повторный запуск подтянет свежий код из GitHub.
#
# После установки:
#   - сайт:      http://<адрес-сервера>:8000
#   - данные:    sudo -u hcenc ... или см. подсказку в конце
#

set -e

REPO_URL="https://github.com/almobil2006/HC-Encyclopedia"
INSTALL_DIR="/opt/hcenc"
SERVICE="hcenc"

#
# 1. Системные пакеты
#

sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-venv python3-pip git

#
# 2. Код
#

if [ -d "$INSTALL_DIR/.git" ]; then

    git -C "$INSTALL_DIR" pull --ff-only

else

    sudo mkdir -p "$INSTALL_DIR"
    sudo chown "$USER" "$INSTALL_DIR"

    git clone "$REPO_URL" "$INSTALL_DIR"

fi

cd "$INSTALL_DIR"

#
# 3. Окружение
#

python3 -m venv venv

./venv/bin/pip install -U -q pip
./venv/bin/pip install -q -e .

./venv/bin/hcenc db init

#
# 4. Служба systemd
#

sudo tee "/etc/systemd/system/${SERVICE}.service" > /dev/null <<EOF
[Unit]
Description=HC Encyclopedia
After=network.target

[Service]
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/uvicorn hcenc.api.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE"
sudo systemctl restart "$SERVICE"

#
# 5. Брандмауэр (если активен ufw)
#

if sudo ufw status 2>/dev/null | grep -q "Status: active"; then

    sudo ufw allow 8000/tcp

fi

IP=$(hostname -I | awk '{print $1}')

echo
echo "=============================================="
echo " Сайт:       http://${IP}:8000"
echo " Служба:     sudo systemctl status ${SERVICE}"
echo " Логи:       sudo journalctl -u ${SERVICE} -f"
echo "=============================================="
echo
echo "Первое наполнение базы (займёт 10–30 минут):"
echo
echo "  cd $INSTALL_DIR"
echo "  nohup ./venv/bin/hcenc sync all > sync.log 2>&1 &"
echo "  tail -f sync.log"
