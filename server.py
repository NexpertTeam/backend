from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import parse_obj_as
from claude import Claude
import arxiv_script
from functions.top_one import top_one
from pdf_parser import pdf_url_to_text
from functions.insight_extraction import extract_key_insights
from firebase import get_firestore_client


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


class Query(BaseModel):
    query: str


class RetrieveArxivSearchOutput(BaseModel):
    papers: List[Paper]


class ConceptNodes(BaseModel):
    name: str
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
    firestore_client.write_data_to_collection(
        collection_name="retrieval", document_id=input, data={"papers": papers}
    )
    return


@app.get("/top-paper")
def get_top_paper(userQuery: str, papers: RetrieveArxivSearchOutput) -> TopPaper:
    result = top_one(papers, userQuery)
    topPaper = TopPaper(
        url=result["url"],
        title=result["title"],
        summary=result["summary"],
        publishedDate=result["publishDate"],
    )
    return topPaper


@app.post("/generate-insights")
def generate_insights(paper: TopPaper) -> PaperInsights:
    pdf_url = paper.url
    paper_text = pdf_url_to_text(pdf_url)
    insights = extract_key_insights(paper_text)

    references = insights["references"]
    references = {ref["bibkey"]: ref["reference_text"] for ref in references}

    concepts = []
    for idea in insights["ideas"]:
        relevant_references = idea["relevant_references"]
        if relevant_references:
            first_bibkey = relevant_references[0]
            reference_text = references[first_bibkey]

            if "arxiv" in reference_text.lower():
                # Search paper in arxiv
                print(f"Searching arxiv for {reference_text}")
                top_results = arxiv_script.search_arxiv(reference_text)
                url = top_results[0]["url"]
                print(f"Paper url: {url}")
            else:
                url = ""
        else:
            url = ""
        concepts.append(
            ConceptNodes(
                referenceUrl=url,
                name=idea["idea_name"],
                description=idea["description"],
            )
        )

    paper_insights = PaperInsights(url=pdf_url, concepts=concepts)

    return paper_insights


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
