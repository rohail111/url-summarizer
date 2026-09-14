import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tenacity import retry, stop_after_attempt, wait_exponential

from url_summarizer.config import get_settings
from url_summarizer.exceptions import SummarizationError
from url_summarizer.schemas import SummaryResult

logger = logging.getLogger(__name__)

_MAP_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Summarize this webpage section in 2-3 concise bullet points. "
        "Focus on facts and key ideas only.",
    ),
    ("human", "Section:\n\n{content}"),
])

_REDUCE_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You combine partial webpage summaries into one final summary. "
        "Return a one-line title and exactly five bullet points.",
    ),
    ("human", "Partial summaries:\n\n{content}"),
])

_DIRECT_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Summarize the webpage. Return a one-line title and exactly five bullet points.",
    ),
    ("human", "URL content:\n\n{content}"),
])


def _build_llm() -> ChatGroq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise SummarizationError("GROQ_API_KEY is not set.")
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.2,
    )


def _split_content(content: str) -> list[str]:
    settings = get_settings()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_text(content)


@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=1, max=4), reraise=True)
def _invoke_structured(chain, payload: dict) -> SummaryResult:
    return chain.invoke(payload)


def _summarize_direct(structured_llm, content: str) -> SummaryResult:
    chain = _DIRECT_PROMPT | structured_llm
    logger.info("Using direct summarization chain")
    return _invoke_structured(chain, {"content": content})


def _summarize_map_reduce(llm, structured_llm, content: str) -> SummaryResult:
    map_chain = _MAP_PROMPT | llm | StrOutputParser()
    chunks = _split_content(content)
    partials = map_chain.batch(
        [{"content": chunk} for chunk in chunks],
        config={"max_concurrency": 3},
    )
    combined = "\n\n".join(partials)
    reduce_chain = _REDUCE_PROMPT | structured_llm
    logger.info("Using map-reduce summarization chain (%d chunks)", len(partials))
    return _invoke_structured(reduce_chain, {"content": combined})


def summarize_text(content: str) -> SummaryResult:
    """Summarize page text using LangChain map-reduce with structured output."""
    settings = get_settings()
    llm = _build_llm()
    structured_llm = llm.with_structured_output(SummaryResult)

    try:
        if len(content) <= settings.map_reduce_threshold:
            return _summarize_direct(structured_llm, content)
        return _summarize_map_reduce(llm, structured_llm, content)
    except Exception as exc:
        logger.exception("Summarization failed")
        raise SummarizationError(f"Summarization failed: {exc}") from exc


def format_summary_markdown(result: SummaryResult) -> str:
    bullets = "\n".join(f"- {point}" for point in result.bullet_points)
    return f"**{result.title}**\n\n{bullets}"
