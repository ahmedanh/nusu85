#!/bin/bash
set -e

echo "=== SHAMEL Deploy ==="

cd /home/ubuntu/nusu85_new
source /home/ubuntu/venv/bin/activate

pip install -r requirements.txt -q

# Apply database migrations
python manage.py migrate --no-input

# Create the DB cache table (safe to run repeatedly — skips if already exists)
# Without this, cache.get/set silently fails and the context processor makes
# 3 extra DB queries on EVERY page load.
python manage.py createcachetable --no-input 2>/dev/null || true

# Collect static files (WhiteNoise serves them, so nginx /static/ alias optional)
python manage.py collectstatic --no-input

# Reload systemd and restart the app
sudo systemctl daemon-reload
sudo systemctl restart shamel
sudo systemctl restart nginx

echo "=== Deploy Complete ==="
sudo systemctl status shamel --no-pager
