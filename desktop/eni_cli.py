#!/usr/bin/env python3
"""
ENI CLI - Quick commands for knowledge base, Kali bridge, and User Guide
"""

import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.knowledge_engine import get_knowledge_engine

def cmd_guide():
    """Print the full start-to-finish User Guide"""
    candidates = [
        Path(__file__).parent.parent / "docs" / "USER_GUIDE.md",
        Path.home() / ".eni" / "source" / "docs" / "USER_GUIDE.md",
        Path.cwd() / "docs" / "USER_GUIDE.md",
    ]
    for p in candidates:
        if p.exists():
            try:
                from rich.console import Console
                from rich.markdown import Markdown
                Console().print(Markdown(p.read_text(encoding="utf-8")))
            except ImportError:
                print(p.read_text(encoding="utf-8"))
            return
    print("❌ USER_GUIDE.md not found. Run from inside the repo or after install.")

def main():
    parser = argparse.ArgumentParser(description="ENI APEX CLI")
    sub = parser.add_subparsers(dest="command")

    ask_p = sub.add_parser("ask", help="Ask the knowledge base")
    ask_p.add_argument("query", nargs="+", help="Your question")

    stats_p = sub.add_parser("stats", help="Show knowledge stats")

    export_p = sub.add_parser("export", help="Export knowledge to Markdown")
    export_p.add_argument("output", nargs="?", default=None)

    learn_p = sub.add_parser("learn", help="Add a new Q&A")
    learn_p.add_argument("question")
    learn_p.add_argument("answer")
    learn_p.add_argument("tags", nargs="?", default="general")

    sub.add_parser("guide", help="Show the complete start-to-finish User Guide")

    args = parser.parse_args()
    knowledge = get_knowledge_engine()

    if args.command == "ask":
        query = " ".join(args.query)
        result = knowledge.get_answer(query)
        if result:
            print(f"\n📚 {result['answer']}\n")
            print(f"Tags: {', '.join(result['tags'])}")
        else:
            print("No match found. Use 'learn' to teach me, or run 'python desktop/eni_cli.py guide'")
    elif args.command == "stats":
        stats = knowledge.get_stats()
        print(f"Total entries: {stats['total_entries']}")
        print(f"Total tags: {stats['total_tags']}")
    elif args.command == "export":
        path = Path(args.output) if args.output else Path.home() / "eni-knowledge.md"
        knowledge.export_markdown(path)
    elif args.command == "learn":
        tags = [t.strip() for t in args.tags.split(",")]
        qid = knowledge.add_qa(args.question, args.answer, tags)
        print(f"✅ Learned! ID: {qid}")
    elif args.command == "guide":
        cmd_guide()
    else:
        parser.print_help()
        print("\nTip: run  python desktop/eni_cli.py guide  for the full start-to-finish manual.")

if __name__ == "__main__":
    main()
