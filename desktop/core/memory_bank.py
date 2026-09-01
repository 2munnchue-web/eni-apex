#!/usr/bin/env python3
"""
ENI Memory Bank - Simple persistent key-value + tagged notes for session context
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from collections import defaultdict

class MemoryBank:
    def __init__(self, storage_dir: Path = None):
        self.storage_dir = storage_dir or Path.home() / '.eni' / 'memory'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.file = self.storage_dir / 'bank.json'
        self.data: Dict[str, Any] = {
            "notes": [],
            "kv": {},
            "sessions": []
        }
        self._load()

    def _load(self):
        if self.file.exists():
            with open(self.file) as f:
                self.data = json.load(f)

    def _save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def remember(self, key: str, value: Any):
        self.data["kv"][key] = {
            "value": value,
            "updated": datetime.now().isoformat()
        }
        self._save()

    def recall(self, key: str) -> Optional[Any]:
        entry = self.data["kv"].get(key)
        return entry["value"] if entry else None

    def note(self, text: str, tags: List[str] = None):
        self.data["notes"].append({
            "text": text,
            "tags": tags or [],
            "created": datetime.now().isoformat()
        })
        self._save()

    def search_notes(self, query: str) -> List[Dict]:
        q = query.lower()
        return [n for n in self.data["notes"] if q in n["text"].lower() or any(q in t for t in n["tags"])]

    def start_session(self, name: str):
        self.data["sessions"].append({
            "name": name,
            "started": datetime.now().isoformat(),
            "notes": []
        })
        self._save()

# Singleton
_mb = None
def get_memory_bank():
    global _mb
    if _mb is None:
        _mb = MemoryBank()
    return _mb
