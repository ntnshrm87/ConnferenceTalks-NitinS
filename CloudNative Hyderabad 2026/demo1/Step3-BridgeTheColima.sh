# 1. Get the SSH config
colima ssh-config > colima-ssh.config

# 2. Open the Tunnel (Keep this window open during your demo!)
ssh -F colima-ssh.config -L 2802:localhost:2802 -L 2801:localhost:2801 -N colima