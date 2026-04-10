#!/bin/bash
echo "--- 🏗️ Staging the CNCF Forensic Lab ---"

# Cleanup old containers
docker rm -f web-app node-server database-pod escape-pod miner-victim 2>/dev/null

# 1. Base Scenario: Suspicious Shell in Nginx
echo "[1/5] Staging: Suspicious Shell (web-app)..."
docker run -d --name web-app nginx:alpine
# Trigger the artifact
docker exec web-app sh -c "echo 'exploit success' > /tmp/payload.log"

# 2. Anomaly: Node.js spawning a shell
echo "[2/5] Staging: Behavioral Anomaly (node-server)..."
# Using exec -a to trick the process name to 'node'
docker run -d --name node-server --entrypoint "/bin/sh" alpine -c "exec -a node sh -c 'sleep 3600'"

# 3. Persistence: Crontab modification
echo "[3/5] Staging: Persistence (database-pod)..."
docker run -d --name database-pod alpine sh -c "touch /etc/crontab; sleep 3600"

# 4. The Escape: Host Mount Access
echo "[4/5] Staging: Container Escape (escape-pod)..."
docker run -d --name escape-pod -v /etc:/host/etc alpine sh -c "cat /host/etc/shadow > /dev/null; sleep 3600"

# 5. The Miner: Dropped binary
echo "[5/5] Staging: Miner Drop (miner-victim)..."
# Changed sleep 2 to sleep 3600 so it doesn't stop!
docker run -d --name miner-victim alpine sh -c "echo 'mine_bits' > /tmp/miner.sh; chmod +x /tmp/miner.sh; sleep 3600"

echo "--- ✅ All Crime Scenes Staged & Running! ---"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"