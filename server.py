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

class TopPaperQuerySchema(BaseModel):
    query: str
    papers: RetrieveArxivSearchOutput

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# public-facing endpoint
@app.post("/query")
def send_query(query: Query) -> None:
    firestore_client = get_firestore_client()
    retrieve_arxiv_search(query)
    papers = firestore_client.read_from_document(collection_name="retrieval", document_name=query.query)
    getTopPaperInput = TopPaperQuerySchema(
        query=query.query,
        papers=papers
    )
    get_top_paper(getTopPaperInput)


@app.get("/retrieve-arxiv-search")
def retrieve_arxiv_search(input: RetrieveArxivSearchInput) -> str:
    firestore_client = get_firestore_client()
    papers = arxiv_script.search_arxiv(input)
    firestore_client.write_data_to_collection(
        collection_name="retrieval", document_name=input.query, data={"papers": papers}
    )
    print("OOOOOOO")
    return "Success"


@app.get("/top-paper")
def get_top_paper(input: TopPaperQuerySchema) -> str:
    print(input)
    firestore_client = get_firestore_client()
    result = top_one(input.papers, input.query)
    topPaper = {
        "url":result["url"],
        "title":result["title"],
        "summary": result["summary"],
        "publishedDate": result["publishDate"],
    }
    firestore_client.write_data_to_collection(collection_name="retrieval", document_name=input.query, data={"topPaper": topPaper})
    return "Success"


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
                top_results = arxiv_script.search_arxiv(reference_text)
                url = top_results[0]["url"]
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
