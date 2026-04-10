#!/bin/bash

echo "--- 🛡️ Starting CNCF Demo Cleanup ---"

# 1. Stop the Colima VM
# This gracefully shuts down the VM and all running containers (Falco, Redis, Sidekick)
echo "[1/3] Stopping Colima VM..."
colima stop

# 2. Remove the temporary SSH configuration
# This ensures you don't have stale connection files sitting in your folder
if [ -f "colima-ssh.config" ]; then
    echo "[2/3] Removing temporary SSH config..."
    rm colima-ssh.config
else
    echo "[2/3] colima-ssh.config already gone. Skipping."
fi

# 3. Optional: Clean up Docker contexts
# This ensures your Docker CLI points back to your default (e.g., Docker Desktop) if you use it
echo "[3/3] Resetting Docker context..."
docker context use default > /dev/null 2>&1

echo "--- ✅ Cleanup Complete. Your Mac is back to its pristine state! ---"