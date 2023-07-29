from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

class RetrieveArxivSearchInput(BaseModel):
    query: str
    numRecentPapers: str | 5
    numMostCitedPapers: str | 5

class TopPaper(BaseModel):
    url: str
    concept: str
    shortDescription: str
    longDescription: str
    reference: str
    bibtexCitation: str

class RetrieveArxivSearchOutput(BaseModel):
    url: str

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

@app.post("/query")
def send_query(query: str) -> None:
    # TODO
    return

@app.get("/retrieve-arxiv-search")
def retrieve_arxiv_search(input: RetrieveArxivSearchInput) -> RetrieveArxivSearchOutput:
    # TODO
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
