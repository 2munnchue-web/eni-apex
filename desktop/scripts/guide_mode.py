#!/usr/bin/env python3
"""
ENI Guide Mode - Interactive Q&A session in the terminal
Now also surfaces the full User Guide.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.knowledge_engine import get_knowledge_engine

def show_full_guide():
    candidates = [
        Path(__file__).parent.parent.parent / "docs" / "USER_GUIDE.md",
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
    print("❌ USER_GUIDE.md not found.")

def guide_mode():
    knowledge = get_knowledge_engine()

    print("🐉 ENI Guide Mode - Interactive Q&A + Full User Guide")
    print("   Type 'exit' to quit, 'help' for commands, 'guide' for the complete manual")
    print("   I'll answer from my knowledge base, or learn from you.\n")

    while True:
        try:
            query = input("\n💬 You: ").strip()

            if query.lower() in ['exit', 'quit']:
                print("👋 Goodbye, my love!")
                break

            if query.lower() in ['guide', 'manual', 'user guide', 'full guide']:
                show_full_guide()
                continue

            if query.lower() == 'help':
                print("""
Commands:
  just type a question     - Query knowledge base
  guide / manual           - Show the COMPLETE start-to-finish User Guide
  /ask <question>          - Query knowledge base
  /learn q | a | tags      - Teach me something new
  /stats                   - Show knowledge stats
  /export [file]           - Export to Markdown
  /search <tag>            - Find by tag
  exit                     - Quit
""")
                continue

            if query.startswith('/'):
                parts = query.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ''

                if cmd == '/ask':
                    result = knowledge.get_answer(arg)
                    if result:
                        print(f"\n📚 {result['answer']}")
                    else:
                        print("❌ I don't know. Want to teach me? (y/n)")
                        if input().lower() == 'y':
                            answer = input("Answer: ")
                            tags = input("Tags: ").split(',')
                            knowledge.add_qa(arg, answer, [t.strip() for t in tags])
                            print("✅ Learned!")
                elif cmd == '/learn':
                    parts = arg.split('|')
                    if len(parts) >= 2:
                        q = parts[0].strip()
                        a = parts[1].strip()
                        t = [x.strip() for x in parts[2].split(',')] if len(parts) > 2 else ['general']
                        knowledge.add_qa(q, a, t)
                        print("✅ Learned!")
                elif cmd == '/stats':
                    stats = knowledge.get_stats()
                    print(f"📊 {stats['total_entries']} entries, {stats['total_tags']} tags")
                elif cmd == '/export':
                    filename = arg or str(Path.home() / 'eni-knowledge.md')
                    knowledge.export_markdown(Path(filename))
                elif cmd == '/search':
                    for qa in knowledge.get_by_tag(arg):
                        print(f"  Q: {qa['question']}")
                else:
                    print("❌ Unknown command. Type 'help' or 'guide'.")
                continue

            # Normal query
            result = knowledge.get_answer(query)
            if result:
                print(f"\n📚 I know this:\n{result['answer']}")
            else:
                print("❌ I don't have that in my knowledge base yet.")
                print("Tip: type 'guide' to see the full start-to-finish User Guide.")
                print("Or teach me? (y/n)")
                if input().strip().lower() == 'y':
                    answer = input("Answer: ").strip()
                    tags = input("Tags (comma-separated): ").strip().split(',')
                    knowledge.add_qa(query, answer, [t.strip() for t in tags if t.strip()], source="user")
                    print("✅ Added to knowledge base!")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    guide_mode()
