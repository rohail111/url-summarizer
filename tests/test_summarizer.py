from unittest.mock import MagicMock, patch

from url_summarizer.schemas import SummaryResult
from url_summarizer.summarizer import _summarize_direct, _summarize_map_reduce, summarize_text

_SAMPLE = SummaryResult(
    title="Example Article",
    bullet_points=["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
)


@patch("url_summarizer.summarizer._invoke_structured", return_value=_SAMPLE)
def test_summarize_direct(mock_invoke):
    structured_llm = MagicMock()
    result = _summarize_direct(structured_llm, "Short page content.")
    assert result.title == "Example Article"
    mock_invoke.assert_called_once()


@patch("url_summarizer.summarizer._invoke_structured", return_value=_SAMPLE)
@patch("url_summarizer.summarizer._split_content", return_value=["chunk-a", "chunk-b"])
@patch("url_summarizer.summarizer._MAP_PROMPT")
def test_summarize_map_reduce(mock_map_prompt, mock_split, mock_invoke):
    map_chain = MagicMock()
    map_chain.batch.return_value = ["Summary A", "Summary B"]
    map_step = MagicMock()
    map_step.__or__ = MagicMock(return_value=map_chain)
    mock_map_prompt.__or__ = MagicMock(return_value=map_step)

    result = _summarize_map_reduce(MagicMock(), MagicMock(), "x" * 10_000)
    assert result.title == "Example Article"
    mock_split.assert_called_once()
    map_chain.batch.assert_called_once()
    mock_invoke.assert_called_once()


@patch("url_summarizer.summarizer._summarize_map_reduce", return_value=_SAMPLE)
@patch("url_summarizer.summarizer._build_llm")
def test_summarize_text_uses_map_reduce_for_long_content(mock_build, mock_map_reduce):
    mock_build.return_value.with_structured_output.return_value = MagicMock()
    summarize_text("x" * 10_000)
    mock_map_reduce.assert_called_once()


@patch("url_summarizer.summarizer._summarize_direct", return_value=_SAMPLE)
@patch("url_summarizer.summarizer._build_llm")
def test_summarize_text_uses_direct_for_short_content(mock_build, mock_direct):
    mock_build.return_value.with_structured_output.return_value = MagicMock()
    summarize_text("Short content.")
    mock_direct.assert_called_once()
