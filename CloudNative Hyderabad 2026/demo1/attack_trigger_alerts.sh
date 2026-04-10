#!/bin/bash
echo "--- Triggering CNCF Demo Alerts ---"

# 1. Standard Shell Alert
echo "[1/4] Triggering Shell Alert..."
docker run --rm --name demo_shell alpine sh -c "ls /"

# 2. Behavioral Anomaly (Simulating Node.js spawning a shell)
# We use 'node' as the name to trick the rule into firing
echo "[2/4] Triggering Anomaly Alert (Web Server Shell)..."
docker run --rm --name web_server --entrypoint "/bin/sh" alpine -c "exec -a node sh -c 'whoami'"

# 3. Sensitive File Read
echo "[3/4] Triggering Sensitive File Alert..."
docker run --rm --name data_thief alpine cat /etc/shadow > /dev/null

# 4. Persistence (Crontab Write)
echo "[4/4] Triggering Persistence Alert..."
docker run --rm --name hacker_persistence alpine touch /etc/crontab

echo "--- All alerts triggered. Check the Dashboard! ---"