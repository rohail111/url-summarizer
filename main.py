import argparse
import json
import sys

from url_summarizer.exceptions import UrlSummarizerError
from url_summarizer.fetch import fetch_url_text
from url_summarizer.logging_config import setup_logging
from url_summarizer.summarizer import format_summary_markdown, summarize_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a public webpage with LangChain + Groq.")
    parser.add_argument("url", nargs="?", help="Public http(s) URL to summarize")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output")
    args = parser.parse_args()

    setup_logging()
    url = (args.url or input("Paste URL: ")).strip()
    if not url:
        print("No URL provided.", file=sys.stderr)
        return 1

    try:
        print("Fetching...", file=sys.stderr)
        content = fetch_url_text(url)
        print("Summarizing...", file=sys.stderr)
        result = summarize_text(content)
    except UrlSummarizerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result.model_dump(), indent=2))
    else:
        print("\nSummary:\n")
        print(format_summary_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
