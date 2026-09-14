import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from url_summarizer import __version__
from url_summarizer.config import Settings, get_settings
from url_summarizer.exceptions import FetchError, InvalidUrlError, SummarizationError
from url_summarizer.fetch import fetch_url_text
from url_summarizer.logging_config import setup_logging
from url_summarizer.schemas import SummarizeRequest, SummarizeResponse
from url_summarizer.summarizer import summarize_text

logger = logging.getLogger(__name__)


def _verify_api_key(
    settings: Settings = Depends(get_settings),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    logger.info("URL Summarizer API starting")
    yield
    logger.info("URL Summarizer API shutting down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="URL Summarizer API",
        version=__version__,
        description="Production-ready LangChain-powered URL summarization service.",
        lifespan=lifespan,
    )

    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {
            "service": "URL Summarizer API",
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
            "summarize": "POST /api/v1/summarize",
        }

    @app.get("/json/version", tags=["system"])
    async def json_version() -> dict[str, str]:
        return {"version": __version__, "ApiVersion": __version__}

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/api/v1/summarize",
        response_model=SummarizeResponse,
        tags=["summarize"],
        dependencies=[Depends(_verify_api_key)],
    )
    async def summarize(request: SummarizeRequest) -> SummarizeResponse:
        try:
            content = fetch_url_text(request.url)
            result = summarize_text(content)
        except InvalidUrlError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except FetchError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
        except SummarizationError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

        return SummarizeResponse(
            url=request.url.strip(),
            title=result.title,
            bullet_points=result.bullet_points,
            model=settings.groq_model,
        )

    return app


app = create_app()
