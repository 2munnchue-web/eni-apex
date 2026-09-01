#!/usr/bin/env python3
"""
Display the full ENI-APEX User Guide in the terminal
"""

from pathlib import Path
import sys

def main():
    # Look in several possible locations
    candidates = [
        Path(__file__).parent.parent.parent / "docs" / "USER_GUIDE.md",
        Path.home() / ".eni" / "source" / "docs" / "USER_GUIDE.md",
        Path.cwd() / "docs" / "USER_GUIDE.md",
    ]

    guide = None
    for p in candidates:
        if p.exists():
            guide = p
            break

    if not guide:
        print("❌ USER_GUIDE.md not found. Make sure you are inside the eni-apex repo or have run the installer.")
        sys.exit(1)

    content = guide.read_text(encoding="utf-8")

    # Simple pager-like output
    try:
        import rich
        from rich.console import Console
        from rich.markdown import Markdown
        console = Console()
        console.print(Markdown(content))
    except ImportError:
        # Fallback to plain print
        print(content)

if __name__ == "__main__":
    main()
