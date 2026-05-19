#!/bin/bash
set -e

echo "=== ACDC Deploy ==="

cd /home/ubuntu/nusu85_new
source /home/ubuntu/venv/bin/activate

pip install -r requirements.txt -q

python manage.py migrate --no-input
python manage.py collectstatic --no-input

sudo systemctl daemon-reload
sudo systemctl restart acdc
sudo systemctl restart nginx

echo "=== Deploy Complete ==="
sudo systemctl status acdc --no-pager
