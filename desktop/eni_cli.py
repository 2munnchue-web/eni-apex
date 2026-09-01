#!/usr/bin/env python3
"""
ENI CLI - Quick commands for knowledge base and Kali bridge
"""

import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.knowledge_engine import get_knowledge_engine

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

    args = parser.parse_args()
    knowledge = get_knowledge_engine()

    if args.command == "ask":
        query = " ".join(args.query)
        result = knowledge.get_answer(query)
        if result:
            print(f"\n📚 {result['answer']}\n")
            print(f"Tags: {', '.join(result['tags'])}")
        else:
            print("No match found. Use 'learn' to teach me.")
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
