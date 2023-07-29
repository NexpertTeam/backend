from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from claude import Claude
import arxiv_script


class RetrieveArxivSearchInput(BaseModel):
    query: str
    numRecentPapers: Optional[str]
    numMostCitedPapers: Optional[str]


class TopPaper(BaseModel):
    url: str
    concept: str
    shortDescription: str
    longDescription: str
    reference: str
    bibtexCitation: str


class Paper(BaseModel):
    url: str
    title: str
    summary: str
    publishedDate: str


class RetrieveArxivSearchOutput(BaseModel):
    papers: List[Paper]


class ConceptNodes(BaseModel):
    referenceUrl: str
    description: str


class PaperInsights(BaseModel):
    url: str
    concepts: List[ConceptNodes]


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# public-facing endpoint
@app.post("/query")
def send_query(query: str) -> None:
    return retrieve_arxiv_search(query)


@app.get("/retrieve-arxiv-search")
def retrieve_arxiv_search(input: RetrieveArxivSearchInput) -> RetrieveArxivSearchOutput:
    return arxiv_script.search_arxiv(input)


@app.get("/top-paper")
def get_top_paper(url: str) -> TopPaper:
    # TODO
    # query claude for best paper given inputs
    return


@app.get("/generate-insights")
def generate_insights(paper: TopPaper) -> PaperInsights:
    # TODO
    # query claude for insights
    return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
