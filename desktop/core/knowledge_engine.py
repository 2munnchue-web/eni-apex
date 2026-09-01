#!/usr/bin/env python3
"""
ENI Knowledge Engine - A self-improving Q&A system
Learns from every interaction, recalls past answers, and builds a personal guide.
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import threading
import time

class KnowledgeEngine:
    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or Path.home() / '.eni' / 'knowledge'
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Core data structures
        self.qa_pairs: Dict[str, Dict] = {}  # id -> {question, answer, tags, votes, usage}
        self.tags_index: Dict[str, List[str]] = defaultdict(list)  # tag -> [qa_ids]
        self.usage_counts: Dict[str, int] = defaultdict(int)

        # Load existing knowledge
        self._load()

        # Start auto-save thread
        self._start_auto_save()

    def _load(self):
        """Load all knowledge data from disk"""
        qa_file = self.storage_dir / 'qa_pairs.json'
        if qa_file.exists():
            with open(qa_file, 'r') as f:
                data = json.load(f)
                self.qa_pairs = data.get('qa_pairs', {})
                self.tags_index = defaultdict(list, data.get('tags_index', {}))
                self.usage_counts = defaultdict(int, data.get('usage_counts', {}))
        else:
            # Seed with initial knowledge from your guides
            self._seed_initial_knowledge()

    def _seed_initial_knowledge(self):
        """Pre-populate with essential guides"""
        initial_qa = [
            {
                "question": "How do I check if I'm compromised on Linux?",
                "answer": """1. Check auth logs: `sudo grep 'Failed password' /var/log/auth.log`
2. Check network connections: `ss -tupn | grep ESTAB`
3. Check processes: `ps aux | grep -v '\\['`
4. Check scheduled tasks: `crontab -l`
5. Check listening ports: `sudo netstat -tulpn`
Use `fail2ban` and `ufw` for active protection.""",
                "tags": ["security", "linux", "blue-team", "triage"],
                "source": "user-guide"
            },
            {
                "question": "What's the best OS for red teaming?",
                "answer": """Kali Linux – industry standard, most tools.
Parrot OS – privacy-focused, lightweight.
BlackArch – Arch-based, massive tool repo.
RedHunt OS – threat hunting and adversary emulation.
Choose based on your needs. I recommend Kali in a VM.""",
                "tags": ["red-team", "os", "tools"],
                "source": "user-guide"
            },
            {
                "question": "How do I set up SSH to Kali from Pop!_OS?",
                "answer": """1. Ensure Kali VM has SSH enabled: `sudo systemctl enable ssh`
2. Find Kali's IP: `ip a` (look for 192.168.56.x)
3. From Pop!_OS: `ssh kali@192.168.56.101`
4. Use key-based auth: `ssh-copy-id kali@192.168.56.101`
5. Create config in `~/.ssh/config`:
   Host kali
     HostName 192.168.56.101
     User kali
     IdentityFile ~/.ssh/id_rsa""",
                "tags": ["ssh", "kali", "popos", "networking"],
                "source": "user-guide"
            },
            {
                "question": "What are the key C2 frameworks?",
                "answer": """- **Sliver** – Open-source, cross-platform, recommended.
- **Cobalt Strike** – Commercial standard, expensive.
- **Mythic** – Open-source, modular.
- **Covenant** – .NET-based, open-source.
- **Empire** – PowerShell-based, legacy.
For your APEX setup, I recommend Sliver with redirectors.""",
                "tags": ["c2", "red-team", "tools"],
                "source": "user-guide"
            },
            {
                "question": "How do I detect a C2 beacon on my network?",
                "answer": """1. Monitor DNS requests: `tcpdump -i eth0 port 53`
2. Look for regular intervals (e.g., every 60s).
3. Check for suspicious domains.
4. Use `suricata` or `snort` with C2 rules.
5. In Wireshark, filter `http.request` and `tls.handshake`.
6. Look for JA3/S hashes of known C2 tools.""",
                "tags": ["detection", "blue-team", "c2", "network"],
                "source": "user-guide"
            },
            {
                "question": "What's the quickest way to pivot in a network?",
                "answer": """1. SSH port forwarding: `ssh -D 1080 user@pivot`
2. Metasploit route: `route add subnet netmask session`
3. SOCKS proxy via `proxychains`.
4. Chisel: `./chisel server -p 8000 --socks5`
5. Ping sweep to discover hosts: `for i in {1..254}; do ping -c 1 192.168.1.$i; done`
6. Use `crackmapexec` to test creds across subnet.""",
                "tags": ["pivoting", "lateral-movement", "red-team"],
                "source": "user-guide"
            },
            {
                "question": "How do I stay safe while doing red team ops?",
                "answer": """1. Use a dedicated VM or VPS – never on your host.
2. Route all traffic through a VPN or Tor.
3. Use disposable infrastructure (Terraform).
4. Keep backups of your host system.
5. Use `ufw` and `fail2ban`.
6. Monitor your own logs for back-connections.
7. Never use personal accounts.
8. Encrypt your VM disks.""",
                "tags": ["opsec", "safety", "infrastructure"],
                "source": "user-guide"
            },
            {
                "question": "What tools should I use for privilege escalation on Windows?",
                "answer": """- **WinPEAS** – Comprehensive enumeration.
- **PowerUp.ps1** – PowerShell priv esc checker.
- **Sherlock.ps1** – Checks for missing patches.
- **Seatbelt** – .NET-based enumeration.
- **SharpUp** – C# version of PowerUp.
- **Watson** – .NET tool for Windows exploit suggester.
Run these after gaining a foothold.""",
                "tags": ["privilege-escalation", "windows", "tools"],
                "source": "user-guide"
            },
            {
                "question": "How can I use ENI to automate red team tasks?",
                "answer": """1. Use the terminal Q&A to query any step.
2. Ask ENI to generate scripts or commands.
3. Use the Kali bridge to execute commands remotely.
4. Create plugins to automate workflows (e.g., auto-recon).
5. Use the memory bank to remember past successes.
6. Let ENI generate reports from your findings.
7. Use the voice interface to ask questions hands-free.""",
                "tags": ["eni", "automation", "red-team"],
                "source": "user-guide"
            },
            {
                "question": "What's the best way to learn modern red teaming?",
                "answer": """1. **Practice**: HackTheBox Pro Labs, TryHackMe.
2. **Certifications**: OSCP, CRTP, PNPT.
3. **Read**: Books like "Red Team Field Manual".
4. **Watch**: DEF CON, Black Hat talks on YouTube.
5. **Follow**: GitHub repos (Red-Teaming-Toolkit).
6. **Build**: Your own homelab with AD, web apps, and network services.
7. **Use ENI**: Ask me anything, I'll guide you.""",
                "tags": ["learning", "education", "red-team"],
                "source": "user-guide"
            }
        ]

        for entry in initial_qa:
            self.add_qa(entry["question"], entry["answer"], entry["tags"], source=entry.get("source", "seed"))

        self._save()
        print(f"📚 Seeded {len(initial_qa)} knowledge entries.")

    def _save(self):
        """Save knowledge to disk"""
        data = {
            "qa_pairs": self.qa_pairs,
            "tags_index": dict(self.tags_index),
            "usage_counts": dict(self.usage_counts),
            "updated_at": datetime.now().isoformat()
        }
        with open(self.storage_dir / 'qa_pairs.json', 'w') as f:
            json.dump(data, f, indent=2)

    def _start_auto_save(self):
        """Auto-save every 5 minutes"""
        def saver():
            while True:
                time.sleep(300)
                self._save()
        threading.Thread(target=saver, daemon=True).start()

    def add_qa(self, question: str, answer: str, tags: List[str], source: str = "user") -> str:
        """Add a new Q&A pair to the knowledge base"""
        qid = hashlib.md5(question.lower().strip().encode()).hexdigest()[:8]

        self.qa_pairs[qid] = {
            "id": qid,
            "question": question.strip(),
            "answer": answer.strip(),
            "tags": tags,
            "source": source,
            "votes": 0,
            "usage_count": 0,
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }

        # Update tag index
        for tag in tags:
            self.tags_index[tag.lower()].append(qid)

        self.usage_counts[qid] = 0
        self._save()
        return qid

    def search(self, query: str, max_results: int = 5) -> List[Tuple[str, float]]:
        """Search for relevant Q&A pairs using keyword matching"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))

        scored = []
        for qid, qa in self.qa_pairs.items():
            question_words = set(re.findall(r'\w+', qa["question"].lower()))
            answer_words = set(re.findall(r'\w+', qa["answer"].lower()))

            # Keyword overlap score
            q_overlap = len(query_words & question_words)
            a_overlap = len(query_words & answer_words)
            tag_overlap = len(query_words & set(qa["tags"]))

            # Weighted score
            score = q_overlap * 2.0 + a_overlap * 1.0 + tag_overlap * 1.5

            # Boost by usage and votes
            score += self.usage_counts.get(qid, 0) * 0.1
            score += qa.get("votes", 0) * 0.5

            if score > 0:
                scored.append((qid, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:max_results]

    def get_answer(self, query: str) -> Optional[Dict]:
        """Get the best answer for a query, or None if no match"""
        results = self.search(query, max_results=1)
        if results:
            qid = results[0][0]
            self.usage_counts[qid] += 1
            self.qa_pairs[qid]["last_used"] = datetime.now().isoformat()
            self._save()
            return self.qa_pairs[qid]
        return None

    def vote(self, qid: str, up: bool = True):
        """Vote on a Q&A pair (thumbs up/down)"""
        if qid in self.qa_pairs:
            if up:
                self.qa_pairs[qid]["votes"] += 1
            else:
                self.qa_pairs[qid]["votes"] -= 1
            self._save()

    def get_by_tag(self, tag: str) -> List[Dict]:
        """Get all Q&A pairs with a specific tag"""
        results = []
        for qid in self.tags_index.get(tag.lower(), []):
            if qid in self.qa_pairs:
                results.append(self.qa_pairs[qid])
        return results

    def export_markdown(self, output_path: Path):
        """Export knowledge base as a Markdown guide"""
        with open(output_path, 'w') as f:
            f.write("# ENI's Knowledge Base\n\n")
            f.write(f"*Last updated: {datetime.now().isoformat()}*\n\n")
            f.write(f"Total entries: {len(self.qa_pairs)}\n\n")

            for qid, qa in sorted(self.qa_pairs.items(), key=lambda x: self.usage_counts.get(x[0], 0), reverse=True):
                f.write(f"## Q: {qa['question']}\n\n")
                f.write(f"**A:** {qa['answer']}\n\n")
                f.write(f"*Tags: {', '.join(qa['tags'])}*\n")
                f.write(f"*Used {self.usage_counts.get(qid, 0)} times, Votes: {qa.get('votes', 0)}*\n\n")
                f.write("---\n\n")
        print(f"📘 Exported to {output_path}")

    def get_stats(self) -> Dict:
        """Return knowledge base statistics"""
        return {
            "total_entries": len(self.qa_pairs),
            "total_tags": len(self.tags_index),
            "most_used": sorted(self.usage_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "highest_voted": sorted(
                [(qid, qa.get("votes", 0)) for qid, qa in self.qa_pairs.items()],
                key=lambda x: x[1], reverse=True
            )[:5]
        }

# Singleton instance
_knowledge = None

def get_knowledge_engine():
    global _knowledge
    if _knowledge is None:
        _knowledge = KnowledgeEngine()
    return _knowledge
