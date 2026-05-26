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

# ── Notify all connected browsers to reload (Live Reload) ──
# Wait a moment for the server to come back up, then push the signal
echo "Waiting for server to start..."
sleep 3
DEPLOY_SECRET="${DEPLOY_SECRET:-}"
if [ -n "$DEPLOY_SECRET" ]; then
  curl -sf "http://localhost/api/live-reload/?secret=${DEPLOY_SECRET}" \
    -o /dev/null && echo "Live reload signal sent." || echo "Live reload: server not ready yet (harmless)."
else
  echo "Tip: set DEPLOY_SECRET in environment to enable live-reload push."
fi

echo "=== Deploy Complete ==="
sudo systemctl status shamel --no-pager
