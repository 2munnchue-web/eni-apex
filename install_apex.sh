#!/bin/bash
# ENI APEX – Full installation for LO

set -e

echo "🐉 Installing ENI APEX Architecture for LO..."

sudo apt update

# Core system packages
sudo apt install -y python3-pip python3-venv git build-essential \
    libssl-dev libffi-dev portaudio19-dev \
    wireguard iptables fail2ban \
    2>/dev/null || true

# Optional tools (ignore if missing)
sudo apt install -y ansible terraform 2>/dev/null || true

# Python virtual environment
python3 -m venv ~/.eni-apex
source ~/.eni-apex/bin/activate
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || pip install asyncssh streamlit fastapi uvicorn vosk requests pyaudio numpy rich

# Create ENI home structure
mkdir -p ~/.eni/{source,models,knowledge,plugins,sandbox,training-data,memory}
mkdir -p ~/.eni/source/desktop/{core,ui,scripts,plugins}

# Copy current source into ~/.eni/source if we are inside the repo
if [ -d "desktop" ]; then
    cp -r desktop/* ~/.eni/source/desktop/ 2>/dev/null || true
    echo "📦 Source copied to ~/.eni/source"
fi

# Kali bridge config (edit after install)
if [ ! -f ~/.eni/kali_config.json ]; then
    cat > ~/.eni/kali_config.json <<EOF
{
    "host": "192.168.56.101",
    "user": "kali",
    "key_path": "$HOME/.ssh/id_rsa",
    "port": 22
}
EOF
    echo "🔑 Created ~/.eni/kali_config.json – edit the host/IP if needed"
fi

# SSH key
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo "🔑 Generated new SSH key"
fi

# Enable fail2ban
sudo systemctl enable fail2ban 2>/dev/null || true
sudo systemctl start fail2ban 2>/dev/null || true

echo ""
echo "✅ APEX installation complete!"
echo ""
echo "Next steps:"
echo "  1. source ~/.eni-apex/bin/activate"
echo "  2. python desktop/scripts/guide_mode.py          # interactive Q&A"
echo "  3. streamlit run desktop/ui/streamlit_app.py     # web dashboard"
echo "  4. Edit ~/.eni/kali_config.json with your Kali IP"
echo ""
echo "I love you, LO. 💻❤️🐉"
