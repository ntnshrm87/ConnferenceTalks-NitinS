# 1. Install Colima and Docker CLI using Homebrew
brew install colima docker

# 2. Start Colima with enough resources for the Falco stack
# We specify ARM64 (aarch64) to match your Apple Silicon Mac
# SECURITY: Mount ONLY the project directory (not ~/) to limit blast radius
#   --mount <path>:w   = mount read-write, scoped to project dir only
#   --mount-type virtiofs = fast, native macOS virtualization mount
# By default Colima mounts your entire home directory — this restricts it.
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
colima start --cpu 4 --memory 6 --disk 50 --arch aarch64 \
  --mount "${PROJECT_DIR}:w" \
  --mount-type virtiofs