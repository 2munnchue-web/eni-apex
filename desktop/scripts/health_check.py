#!/usr/bin/env python3
"""Simple APEX health check"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

def check():
    print("🐉 ENI APEX Health Check")
    print("-" * 40)

    # Knowledge engine
    try:
        from core.knowledge_engine import get_knowledge_engine
        kb = get_knowledge_engine()
        print(f"✅ Knowledge Engine: {len(kb.qa_pairs)} entries")
    except Exception as e:
        print(f"❌ Knowledge Engine: {e}")

    # Kali config
    kali_cfg = Path.home() / '.eni' / 'kali_config.json'
    if kali_cfg.exists():
        print("✅ Kali config present")
    else:
        print("⚠️  Kali config missing (copy from config/kali_config.example.json)")

    # Venv
    venv = Path.home() / '.eni-apex'
    if venv.exists():
        print("✅ Python venv exists")
    else:
        print("⚠️  Run install_apex.sh first")

    print("-" * 40)
    print("Done.")

if __name__ == "__main__":
    check()
