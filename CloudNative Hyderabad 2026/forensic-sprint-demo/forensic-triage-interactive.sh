#!/bin/bash

# --- Color Palette ---
BOLD='\033[1m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; GREEN='\033[0;32m'; WHITE='\033[1;37m'; NC='\033[0m'

# The Core Triage Logic
# We use _TARGET_ instead of NAME to avoid any global conflicts
run_triage_session() {
    local _TARGET_=$1
    local _DESC_=$2
    local _COLOR_=$3

    echo -e "\n${BOLD}${_COLOR_}🔎 CASE STUDY: ${_TARGET_} (${_DESC_})${NC}"
    echo -e "${BOLD}----------------------------------------------------------${NC}"

    # Verify container exists before doing anything
    ID=$(docker ps -aqf "name=^/${_TARGET_}$")
    if [ -z "$ID" ]; then
        echo -e "${RED}❌ ERROR: Container '${_TARGET_}' is not running!${NC}"
        echo -e "   Please run ./forensic-setup.sh again."
        return
    fi

    # STEP 1: METADATA
    echo -e "${CYAN}[STEP 1: METADATA]${NC} Extracting network footprint..."
    echo -e "${WHITE}COMMAND > ${GREEN}docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${_TARGET_}${NC}"
    read -p "   (Enter to Execute)"
    
    IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${_TARGET_} 2>/dev/null)
    [ -z "$IP" ] && IP="N/A (Host Network)"
    echo -e "   ${BOLD}RESULT:${NC} ID: ${ID:0:12} | IP: $IP"

    # STEP 2: PROCESS TREE
    echo -e "\n${CYAN}[STEP 2: PROCESS HIERARCHY]${NC} Analyzing process ancestry..."
    echo -e "${WHITE}COMMAND > ${GREEN}docker top ${_TARGET_} auxf${NC}"
    read -p "   (Enter to Execute)"
    
    echo -e "${BOLD}------------------ LIVE PROCESS TREE ---------------------${NC}"
    docker top ${_TARGET_} auxf | tail -n +2 | sed 's/^/  /'
    echo -e "${BOLD}----------------------------------------------------------${NC}"

    # STEP 3: FILESYSTEM DIFF
    echo -e "\n${CYAN}[STEP 3: FILESYSTEM DIFF]${NC} Checking for runtime modifications..."
    echo -e "${WHITE}COMMAND > ${GREEN}docker diff ${_TARGET_}${NC}"
    read -p "   (Enter to Execute)"
    
    DIFF=$(docker diff ${_TARGET_} 2>/dev/null | grep -E "^A |^C ")
    if [ -z "$DIFF" ]; then
        echo -e "   ${YELLOW}RESULT:${NC} No filesystem changes detected."
    else
        echo -e "${RED}   DETECTED CHANGES:${NC}"
        echo "$DIFF" | sed 's/^/      /'
    fi

    # STEP 4: PRESERVATION
    echo -e "\n${CYAN}[STEP 4: PRESERVATION]${NC} Committing forensic snapshot..."
    echo -e "${WHITE}COMMAND > ${GREEN}docker commit ${_TARGET_} forensic-snap-${_TARGET_}${NC}"
    read -p "   (Enter to Execute)"
    
    docker commit ${_TARGET_} "forensic-snap-${_TARGET_}" > /dev/null
    echo -e "   ${GREEN}✓ SUCCESS:${NC} Forensic snapshot 'forensic-snap-${_TARGET_}' created."
}

# --- MASTER SPRINT EXECUTION ---
# This section calls the function with DIFFERENT names each time

clear
echo -e "${BOLD}${YELLOW}=========================================================="
echo -e "       CNCF MASTERCLASS: LIVE CONTAINER FORENSICS"
echo -e "==========================================================${NC}"

# Case 1: web-app
run_triage_session "web-app" "Suspicious Shell" $YELLOW
read -p "Move to Case 2: node-server? (Enter)"
clear

# Case 2: node-server
run_triage_session "node-server" "Web Anomaly" $RED
read -p "Move to Case 3: database-pod? (Enter)"
clear

# Case 3: database-pod
run_triage_session "database-pod" "Persistence Hack" $CYAN
read -p "Move to Case 4: escape-pod? (Enter)"
clear

# Case 4: escape-pod
run_triage_session "escape-pod" "Container Escape" $RED
read -p "Move to Final Case: miner-victim? (Enter)"
clear

# Case 5: miner-victim
run_triage_session "miner-victim" "Cryptominer Discovery" $YELLOW

echo -e "\n${BOLD}${GREEN}=========================================================="
echo -e "          FORENSIC SPRINT COMPLETE"
echo -e "==========================================================${NC}"
exit 0