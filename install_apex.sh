#!/bin/bash
# ENI APEX – Full installation

set -e

echo "🐉 Installing ENI APEX Architecture for LO..."
sudo apt update

# Core dependencies
sudo apt install -y python3-pip python3-venv git build-essential \
    libssl-dev libffi-dev portaudio19-dev \
    wireguard iptables fail2ban \
    ansible terraform 2>/dev/null || true

# Python environment
python3 -m venv ~/.eni-apex
source ~/.eni-apex/bin/activate
pip install --upgrade pip
pip install asyncssh streamlit fastapi uvicorn vosk requests pyaudio numpy

# Create directories
mkdir -p ~/.eni/{source,models,knowledge,plugins,sandbox,training-data}
mkdir -p ~/.eni/source/desktop/{core,ui,scripts,plugins}

# Copy source if running from repo
if [ -d "desktop" ]; then
    cp -r desktop/* ~/.eni/source/desktop/ 2>/dev/null || true
fi

# Install Kali bridge config
cat > ~/.eni/kali_config.json <<EOF
{
    "host": "192.168.56.101",
    "user": "kali",
    "key_path": "$HOME/.ssh/id_rsa",
    "port": 22
}
EOF

# Set up SSH key if not exists
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

# Enable and start services
sudo systemctl enable fail2ban 2>/dev/null || true
sudo systemctl start fail2ban 2>/dev/null || true

echo "✅ APEX installation complete!"
echo "To start: source ~/.eni-apex/bin/activate && python ~/.eni/source/desktop/scripts/guide_mode.py"
