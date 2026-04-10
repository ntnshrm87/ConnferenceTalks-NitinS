#!/bin/bash
echo "--- 🕵️ Starting the 2-Minute Forensic Sprint ---"
echo "------------------------------------------------"

triage_container() {
    NAME=$1
    DESC=$2
    echo -e "\n\033[1;33mCASE: $NAME ($DESC)\033[0m"
    
    # 0-30s: Metadata
    ID=$(docker ps -aqf "name=$NAME")
    IP=$(docker inspect $NAME --format '{{.NetworkSettings.IPAddress}}')
    echo "[0-30s] ID: ${ID:0:12} | IP: $IP"

    # 30-60s: Process Tree (The 'Who')
    echo "[30-60s] Process Hierarchy (docker top):"
    docker top $NAME auxf | tail -n +2 | sed 's/^/  /'

    # 60-90s: Filesystem Diff (The 'What')
    echo "[60-90s] Filesystem Changes (docker diff):"
    docker diff $NAME | grep -E "A |C " | head -n 5 | sed 's/^/  /'

    # 90-120s: Preservation
    echo "[90-120s] Preserving State..."
    docker commit $NAME forensic-snap-$NAME:latest > /dev/null
    echo "  -> Snapshot saved: forensic-snap-$NAME:latest"
}

# Run the Triage for each staged case
triage_container "web-app" "Suspicious Shell"
triage_container "node-server" "Web Anomaly"
triage_container "database-pod" "Persistence/Crontab"
triage_container "escape-pod" "Host Escape Attempt"

echo -e "\n------------------------------------------------"
echo "--- ✅ Triage Complete. Check Falco UI for Alerts! ---"