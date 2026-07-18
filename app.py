# streamlit_app.py

import streamlit as st
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Multi-Agent Research System")
st.markdown("Enter a topic and watch the agents collaborate to produce a researched report.")

# --- Sidebar ---
with st.sidebar:
    st.header("How it works")
    st.markdown("""
    1. **Search Agent** — finds recent, reliable info  
    2. **Reader Agent** — scrapes the most relevant source  
    3. **Writer Agent** — drafts a structured report  
    4. **Critic Agent** — reviews and provides feedback  
    """)
    st.divider()
    st.caption("Powered by LangChain ")

# --- Main Input ---
topic = st.text_input("Enter a research topic", placeholder="e.g., Latest advancements in quantum computing")

if st.button("Run Research Pipeline", type="primary", disabled=not topic):

    state = {}

    # Step 1: Search Agent
    with st.status("🔍 Step 1 — Search Agent is working...", expanded=True) as status:
        search_agent = build_search_agent()
        search_results = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })

        tool_output = ""
        for msg in search_results["messages"]:
            if msg.__class__.__name__ == "ToolMessage":
                tool_output = msg.content
                break

        state["search_results"] = tool_output
        status.update(label="✅ Step 1 — Search complete", state="complete", expanded=False)

    with st.expander("📄 Search Results"):
        st.text(state["search_results"][:2000] if state["search_results"] else "No results found.")

    # Step 2: Reader Agent
    with st.status("📖 Step 2 — Reader Agent is scraping top resources...", expanded=True) as status:
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}"
            )]
        })

        state["scraped_content"] = reader_result["messages"][-1].content
        status.update(label="✅ Step 2 — Scraping complete", state="complete", expanded=False)

    with st.expander("📄 Scraped Content"):
        st.text(state["scraped_content"][:3000] if state["scraped_content"] else "No content scraped.")

    # Step 3: Writer Agent
    with st.status("✍️ Step 3 — Writer is drafting the report...", expanded=True) as status:
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
        status.update(label="✅ Step 3 — Report drafted", state="complete", expanded=False)

    # Step 4: Critic Agent
    with st.status("🧐 Step 4 — Critic is reviewing the report...", expanded=True) as status:
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })
        status.update(label="✅ Step 4 — Review complete", state="complete", expanded=False)

    # --- Final Output ---
    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("📝 Final Report")
        st.markdown(state["report"])

    with col2:
        st.subheader("💬 Critic Feedback")
        st.markdown(state["feedback"])

    # Success banner
    st.success("Pipeline complete! All 4 agents have finished their work.")
