from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

import arxiv_script
from pdf_parser import pdf_url_to_text
from functions.insight_extraction import extract_key_insights


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
def send_query(query: QuerySchema) -> None:
    return retrieve_arxiv_search(query.query)


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
