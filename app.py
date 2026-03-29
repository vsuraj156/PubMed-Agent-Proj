import streamlit as st
from dotenv import load_dotenv
from agent import clinical_research_agent

load_dotenv()

st.set_page_config(page_title="PubMed Research Agent", page_icon="", layout="wide")

st.title("PubMed Research Agent")
st.caption("Ask a clinical question and get an evidence-based summary from PubMed literature.")

question = st.text_area(
    "Clinical Question",
    placeholder="e.g. What are the current treatment recommendations for type 2 diabetes in adults?",
    height=100,
)

col1, col2 = st.columns([1, 4])
with col1:
    max_turns = st.number_input("Max search turns", min_value=1, max_value=20, value=10)

if st.button("Search", type="primary", disabled=not question.strip()):
    with st.spinner("Searching PubMed..."):
        log_placeholder = st.empty()
        log_lines = []

        # Capture print output for live progress display
        import sys
        from io import StringIO

        class StreamCapture:
            def write(self, text):
                if text.strip():
                    log_lines.append(text.strip())
                    log_placeholder.code("\n".join(log_lines[-20:]))
            def flush(self):
                pass

        old_stdout = sys.stdout
        sys.stdout = StreamCapture()

        try:
            result = clinical_research_agent(question.strip(), max_turns=max_turns)
        finally:
            sys.stdout = old_stdout

        log_placeholder.empty()

    st.markdown("---")
    st.markdown(result)
