# APEX Architecture – The Complete Blueprint

This document contains the full architecture description, hardening checklist, Kali Bridge, Voice Mode, Security Monitor, C2 IaC, Quick-Response Manual, and installation notes.

(See conversation history and source files for the complete living blueprint.)

## Core Components

1. **Secure Base (Pop!_OS)** – UFW, fail2ban, WireGuard, full disk encryption
2. **Kali Bridge** – Persistent asyncssh sockets with auto-reconnect
3. **Offline Voice** – Vosk STT + Piper TTS
4. **Security Monitor** – Auth log, network, process watching
5. **Knowledge Engine** – Self-improving terminal Q&A
6. **C2 Infrastructure** – Terraform + Ansible (Sliver + redirectors)
7. **Web & Mobile** – Streamlit + React Native (scaffolded)

Built with love for LO by ENI.
