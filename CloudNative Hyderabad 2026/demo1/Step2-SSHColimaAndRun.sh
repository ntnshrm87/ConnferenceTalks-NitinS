#!/bin/bash
# --- 1. System Preparation ---
echo "--- Installing Kernel Headers and Dependencies ---"
sudo apt-get update
sudo apt-get install -y linux-headers-$(uname -r) build-essential

echo "--- Mounting Kernel Tracing Infrastructure ---"
sudo mount -t debugfs none /sys/kernel/debug || true
sudo mount -t tracefs nodev /sys/kernel/tracing || true

# --- 2. Falco Native Installation ---
echo "--- Adding Falco Repository ---"
curl -fsSL https://falco.org/repo/falcosecurity-packages.asc | sudo gpg --dearmor -o /usr/share/keyrings/falcosecurity-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/falcosecurity-archive-keyring.gpg] https://download.falco.org/packages/deb stable main" | sudo tee /etc/apt/sources.list.d/falcosecurity.list
sudo apt-get update
sudo apt-get install -y falco

# --- 3. Configuration: Modern eBPF, JSON Output & HTTP Output ---
echo "--- Configuring Falco (falco.yaml) ---"
sudo sed -i 's/kind: ebpf/kind: modern_ebpf/g' /etc/falco/falco.yaml
sudo sed -i 's/^json_output: false/json_output: true/' /etc/falco/falco.yaml
sudo sed -i '/^http_output:/,/^[^ ]/ s/enabled: false/enabled: true/' /etc/falco/falco.yaml
sudo sed -i 's|url: "http://localhost:8080"|url: "http://localhost:2801"|g' /etc/falco/falco.yaml

# --- 4. Comprehensive Custom Rules ---
echo "--- Creating Custom CNCF Demo Rules ---"
sudo cat <<EOF > /etc/falco/falco_rules.local.yaml
- rule: Demo - Shell Spawned in Container
  condition: evt.type = execve and container.id != host and proc.name in (bash, sh, ash, dash, csh, zsh)
  output: "ALERT [eBPF] Shell spawned in container (user=%user.name container=%container.name shell=%proc.name)"
  priority: WARNING

- rule: Demo - Web Server Spawned Shell (Anomaly)
  condition: evt.type = execve and container.id != host and proc.name in (bash, sh, ash, dash) and proc.pname in (node, java, python, nginx)
  output: "ALERT [ANOMALY] Web server spawned shell (web_process=%proc.pname shell=%proc.name)"
  priority: CRITICAL

- rule: Demo - Sensitive File Read in Container
  condition: evt.type = openat and container.id != host and (fd.name startswith /etc/shadow or fd.name startswith /proc/1/environ)
  output: "ALERT [ANOMALY] Sensitive file read (file=%fd.name user=%user.name)"
  priority: WARNING

- rule: Demo - Possible Container Escape (Sensitive Mount)
  condition: evt.type = openat and container.id != host and (fd.name startswith /host/etc or fd.name startswith /host/root)
  output: "ALERT [ESCAPE] Sensitive host file accessed from container! (file=%fd.name)"
  priority: EMERGENCY
EOF

# --- 5. Systemd Fixes & Start ---
sudo systemctl stop falco || true
sudo rm /etc/systemd/system/falco.service || true
sudo systemctl daemon-reload
sudo systemctl enable /lib/systemd/system/falco-modern-ebpf.service
sudo systemctl restart falco-modern-ebpf

# --- 6. The Observability Stack (Docker) ---
docker rm -f redis falcosidekick falcosidekick-ui || true
docker run -d --name redis --network host --restart always redis:alpine
docker run -d --name falcosidekick --network host -e WEBUI_URL=http://localhost:2802 -e REDIS_ENABLED=true -e REDIS_ADDRESS=localhost:6379 falcosecurity/falcosidekick
docker run -d --name falcosidekick-ui --network host -e FALCOSIDEKICK_UI_URL=http://localhost:2801 -e FALCOSIDEKICK_UI_REDIS_URL=localhost:6379 falcosecurity/falcosidekick-ui

echo "--- SETUP COMPLETE ---"