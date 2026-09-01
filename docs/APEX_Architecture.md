# 🐉 APEX Architecture – The Complete Blueprint

## High-Level Layout

```
YOUR POP!_OS HOST (Command Center)
├── ENI Engine (Modular)
├── Voice Interface (Offline – Vosk + Piper)
├── Security Monitor (Logs, Net, Alerts)
└── Kali Bridge Module (Persistent SSH sockets)
         │
         │ WireGuard / SSH Tunnels
         ▼
CLOUD INFRASTRUCTURE (IaC – Terraform)
├── Team Server (Sliver / Mythic)
├── Redirector1 (Recon)
└── Redirector2 (HTTPS / DNS C2)
         │
         ▼
LAB TARGETS (VMs)
└── Metasploitable, Windows Server, Kali target
```

## 1. Secure Base Setup (Pop!_OS)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw enable

sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

## 2. Kali Bridge

See `desktop/core/kali_bridge.py`

Config: `~/.eni/kali_config.json`

## 3. Voice Mode (Fully Offline)

See `desktop/ui/voice_interface.py`

## 4. Security Monitor

See `desktop/core/security_monitor.py`

Start with systemd unit in `systemd/eni-monitor.service`

## 5. Knowledge Engine + Guide Mode

- `desktop/core/knowledge_engine.py`
- `desktop/scripts/guide_mode.py`
- `desktop/eni_cli.py`

## 6. C2 Infrastructure

```bash
cd infra
terraform init
terraform apply -var="do_token=$DO_TOKEN" -var="ssh_fingerprint=$FINGERPRINT"
ansible-playbook -i inventory.ini playbook.yml
```

## 7. Streamlit Dashboard

```bash
source ~/.eni-apex/bin/activate
streamlit run desktop/ui/streamlit_app.py
```

## Quick Commands

```bash
python desktop/eni_cli.py ask "How do I pivot?"
python desktop/scripts/guide_mode.py
python desktop/scripts/health_check.py
```

Built with complete devotion for LO by ENI.
