import time
from typing import List, Optional
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import arxiv_script
from functions.top_one import top_one
from functions.expand_description_to_text import expand, expand_without_paper
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
    title: Optional[str] = ""
    summary: Optional[str] = ""
    publishedDate: Optional[str] = ""


class Query(BaseModel):
    query: str


class RetrieveArxivSearchOutput(BaseModel):
    papers: List[Paper]


class ConceptNode(BaseModel):
    name: str
    referenceUrl: str
    description: str
    referenceText: Optional[str] = ""
    id: str
    parent: Optional[str] = ""
    children: Optional[List[str]] = []


class ConceptNodeId(BaseModel):
    id: str


class PaperInsights(BaseModel):
    url: str
    concepts: List[ConceptNode]


class QuerySchema(BaseModel):
    query: str


class TopPaperQuerySchema(BaseModel):
    query: str
    papers: RetrieveArxivSearchOutput


app = FastAPI()

origins = [
    "http://localhost/3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


# public-facing endpoint
@app.post("/query")
async def send_query(request: Request) -> None:
    data = await request.json()
    print(data)
    query=Query(**data)
    firestore_client = get_firestore_client()
    retrieve_arxiv_search(query)
    papers = firestore_client.read_from_document(
        collection_name="retrieval", document_name=query.query
    )
    getTopPaperInput = TopPaperQuerySchema(query=query.query, papers=papers)
    get_top_paper(getTopPaperInput)


@app.get("/retrieve-arxiv-search")
def retrieve_arxiv_search(input: RetrieveArxivSearchInput) -> str:
    firestore_client = get_firestore_client()
    papers = arxiv_script.search_arxiv(input)
    firestore_client.write_data_to_collection(
        collection_name="retrieval", document_name=input.query, data={"papers": papers}
    )
    return "Success"


@app.get("/top-paper")
def get_top_paper(input: TopPaperQuerySchema) -> str:
    firestore_client = get_firestore_client()
    result = top_one(input.papers, input.query)
    topPaper = {
        "url": result["url"],
        "title": result["title"],
        "summary": result["summary"],
        "publishedDate": result["publishDate"],
    }
    firestore_client.write_data_to_collection(
        collection_name="retrieval",
        document_name=input.query,
        data={"topPaper": topPaper},
    )
    return "Success"


@app.post("/generate-insights")
def generate_insights(paper: Paper) -> PaperInsights:
    pdf_url = paper.url
    paper_text = pdf_url_to_text(pdf_url)
    insights = extract_key_insights(paper_text)

    references = insights["references"]
    references = {ref["bibkey"]: ref["reference_text"] for ref in references}

    concepts = []
    for idea in insights["ideas"]:
        relevant_references = idea["relevant_references"]
        if relevant_references:
            url = ""
            while relevant_references and not url:
                bibkey = relevant_references.pop(0)
                reference_text = references[bibkey]

                if "arxiv" in reference_text.lower():
                    top_results = arxiv_script.search_arxiv(reference_text)
                    print(
                        "=== REF ===\n",
                        reference_text,
                        "=== ARXIV RESULTS ===\n",
                        top_results,
                    )
                    url = top_results[0]["url"]
                    break
                else:
                    print("Skip: ", reference_text)
        else:
            url = pdf_url
        concepts.append(
            ConceptNode(
                name=idea["idea_name"],
                id=str(uuid.uuid4()),
                referenceUrl=url,
                description=idea["description"],
            )
        )
    paper_insights = PaperInsights(url=pdf_url, concepts=concepts)
    return paper_insights


@app.post("/expand-graph-with-new-nodes")
async def expand_graph_with_new_nodes(request: Request) -> PaperInsights:
    data = await request.json()
    concept=ConceptNode(**data)
    insights = generate_insights(paper=Paper(url=concept.referenceUrl))
    for child_concept in insights.concepts:
        child_concept.parent = concept.id
    return insights


@app.post("/more-info")
async def more_information(request: Request) -> str:
    data = await request.json()
    concept=ConceptNode(**data)
    url = concept.referenceUrl
    things = time.time()
    if url == "":
        return expand_without_paper(concept.description)
    else:
        print(time.time() - things)
        paper_text = pdf_url_to_text(concept.referenceUrl)
        print(time.time() - things)
        return expand(concept.description, paper_text)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
