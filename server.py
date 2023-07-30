from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import parse_obj_as
from claude import Claude
import arxiv_script
from functions.top_one import top_one


class RetrieveArxivSearchInput(BaseModel):
    query: str
    numRecentPapers: Optional[str]
    numMostCitedPapers: Optional[str]


class TopPaper(BaseModel):
    url: str
    title: str
    summary: str
    publishedDate: str


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


class QuerySchema(BaseModel):
    query: str


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# public-facing endpoint
@app.post("/query")
def send_query(query: QuerySchema) -> None:
    return retrieve_arxiv_search(query.query)


@app.get("/retrieve-arxiv-search")
def retrieve_arxiv_search(input: RetrieveArxivSearchInput) -> RetrieveArxivSearchOutput:
    initPapers = arxiv_script.search_arxiv(input)
    papersRet = parse_obj_as(List[Paper], initPapers)
    finalObj = RetrieveArxivSearchOutput(papers=papersRet)
    # print(papersRet)
    return finalObj


@app.get("/top-paper")
def get_top_paper(userQuery: str, papers: RetrieveArxivSearchOutput) -> TopPaper:
    result = top_one(papers, userQuery)
    topPaper = TopPaper(url=result["url"], title=result["title"], summary=result["summary"], publishedDate=result["publishDate"])
    return topPaper


@app.get("/generate-insights")
def generate_insights(paper: TopPaper) -> PaperInsights:
    # TODO
    # query claude for insights
    return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
