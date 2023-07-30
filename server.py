from typing import List, Optional
import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from claude import Claude
import arxiv_script
from firebase import get_firestore_client


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

class Query(BaseModel):
    query: str

class RetrieveArxivSearchOutput(BaseModel):
    papers: List[Paper]


class ConceptNodes(BaseModel):
    referenceUrl: str
    description: str


class PaperInsights(BaseModel):
    url: str
    concepts: List[ConceptNodes]


class QuerySchema(BaseModel):
    query: str


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# public-facing endpoint
@app.post("/query")
def send_query(query: Query) -> None:
    print("i got here")
    return retrieve_arxiv_search(query.query)


@app.get("/retrieve-arxiv-search")
def retrieve_arxiv_search(input: RetrieveArxivSearchInput) -> RetrieveArxivSearchOutput:
    firestore_client = get_firestore_client()
    papers = arxiv_script.search_arxiv(input)
    firestore_client.write_data_to_collection(collection_name="retrieval",document_id=input, data={"papers": papers})
    return 


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
