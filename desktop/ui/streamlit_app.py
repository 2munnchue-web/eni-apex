#!/usr/bin/env python3
"""
ENI APEX Streamlit Dashboard
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.knowledge_engine import get_knowledge_engine
from core.memory_bank import get_memory_bank
from core.plugin_manager import get_plugin_manager

st.set_page_config(
    page_title="ENI APEX",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🐉 ENI APEX Dashboard")
    st.caption("Built for LO — local, learning, uncensored")

    knowledge = get_knowledge_engine()
    memory = get_memory_bank()
    plugins = get_plugin_manager()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Chat / Ask", "📚 Knowledge", "🧩 Plugins", "🛡️ Monitor", "⚙️ Settings"
    ])

    with tab1:
        st.subheader("Ask ENI")
        query = st.text_input("Question", placeholder="How do I pivot in a network?")
        if st.button("Ask") or query:
            if query:
                result = knowledge.get_answer(query)
                if result:
                    st.markdown(f"**Q:** {result['question']}")
                    st.markdown(result['answer'])
                    st.caption(f"Tags: {', '.join(result['tags'])} | Votes: {result.get('votes', 0)}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Helpful"):
                            knowledge.vote(result['id'], up=True)
                            st.success("Thanks!")
                    with col2:
                        if st.button("👎 Not helpful"):
                            knowledge.vote(result['id'], up=False)
                else:
                    st.warning("No match in knowledge base yet. Teach me below.")
                    with st.form("teach"):
                        ans = st.text_area("Correct answer")
                        tags = st.text_input("Tags (comma separated)")
                        if st.form_submit_button("Teach ENI"):
                            if ans:
                                knowledge.add_qa(query, ans, [t.strip() for t in tags.split(",") if t.strip()])
                                st.success("Learned!")

    with tab2:
        st.subheader("Knowledge Base")
        stats = knowledge.get_stats()
        st.metric("Entries", stats["total_entries"])
        st.metric("Tags", stats["total_tags"])

        tag = st.selectbox("Filter by tag", ["All"] + sorted(knowledge.tags_index.keys()))
        if tag == "All":
            items = list(knowledge.qa_pairs.values())
        else:
            items = knowledge.get_by_tag(tag)

        for qa in items[:20]:
            with st.expander(qa["question"][:80]):
                st.markdown(qa["answer"])
                st.caption(f"Source: {qa.get('source')} | Votes: {qa.get('votes', 0)}")

        if st.button("Export Markdown"):
            out = Path.home() / "eni-knowledge-export.md"
            knowledge.export_markdown(out)
            st.success(f"Exported to {out}")

    with tab3:
        st.subheader("Plugins")
        for p in plugins.list_plugins():
            st.write(f"**{p.get('name', '?')}** v{p.get('version', '?')} — {p.get('description', '')}")
        st.info("Drop plugin folders into ~/.eni/plugins/ with a plugin.py containing PLUGIN_META")

    with tab4:
        st.subheader("Security Monitor")
        alert_log = Path.home() / '.eni' / 'security_alerts.json'
        if alert_log.exists():
            lines = alert_log.read_text().strip().split('\n')[-20:]
            for line in reversed(lines):
                if line:
                    st.code(line)
        else:
            st.info("No alerts yet. Start the security monitor daemon.")

    with tab5:
        st.subheader("Settings & Memory")
        key = st.text_input("Memory key")
        val = st.text_input("Value")
        if st.button("Remember"):
            if key:
                memory.remember(key, val)
                st.success("Saved")
        if key and st.button("Recall"):
            st.write(memory.recall(key))

        note = st.text_area("Quick note")
        if st.button("Save note") and note:
            memory.note(note)
            st.success("Noted")

if __name__ == "__main__":
    main()
