from pydantic import BaseModel, Field


class SummaryResult(BaseModel):
    title: str = Field(description="One-line title for the page")
    bullet_points: list[str] = Field(
        description="Five concise bullet points summarizing the page",
        min_length=1,
        max_length=8,
    )


class SummarizeRequest(BaseModel):
    url: str = Field(min_length=1, description="Public http(s) URL to summarize")


class SummarizeResponse(BaseModel):
    url: str
    title: str
    bullet_points: list[str]
    model: str
