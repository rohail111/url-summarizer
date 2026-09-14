import os

import streamlit as st


def _load_secrets_into_env() -> None:
    """Map Streamlit Cloud secrets to env vars used by Settings."""
    try:
        secrets = st.secrets
    except Exception:
        return
    for key in ("GROQ_API_KEY", "GROQ_MODEL"):
        if key in secrets:
            os.environ[key] = str(secrets[key])


_load_secrets_into_env()

from url_summarizer.config import get_settings
from url_summarizer.exceptions import FetchError, InvalidUrlError, SummarizationError
from url_summarizer.fetch import fetch_url_text
from url_summarizer.summarizer import format_summary_markdown, summarize_text

get_settings.cache_clear()

st.set_page_config(page_title="URL Summarizer", page_icon="🔗", layout="centered")
st.title("URL Summarizer")
st.caption("Production-ready LangChain + Groq summarization")

url = st.text_input("Paste a public URL", placeholder="https://example.com/article")

if st.button("Summarize", type="primary") and url:
    try:
        with st.spinner("Fetching page..."):
            content = fetch_url_text(url)
        with st.spinner("Summarizing with LangChain..."):
            result = summarize_text(content)
        st.markdown(format_summary_markdown(result))
        with st.expander("Structured output"):
            st.json(result.model_dump())
    except InvalidUrlError as exc:
        st.error(str(exc))
    except FetchError as exc:
        st.error(str(exc))
    except SummarizationError as exc:
        st.error(str(exc))
