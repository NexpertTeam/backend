import time
from typing import List, Optional
import uuid

from fastapi import FastAPI
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

class PaperInsights(BaseModel):
    url: str
    concepts: List[ConceptNode]

class QuerySchema(BaseModel):
    query: str


class TopPaperQuerySchema(BaseModel):
    query: str
    papers: RetrieveArxivSearchOutput

class ExpandGraphWithNewInsightsSchema(BaseModel):
    query: str
    concept: ConceptNode

class idGraphSchema(BaseModel):
    query: str
    id: str

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# public-facing endpoint
@app.post("/query")
def send_query(query: Query):
    firestore_client = get_firestore_client()
    retrieve_arxiv_search(query)
    papers = firestore_client.read_from_document(
        collection_name="retrieval", document_name=query.query
    )
    getTopPaperInput = TopPaperQuerySchema(query=query.query, papers=papers)
    try:
        topPaper = get_top_paper(getTopPaperInput)
    except:
        topPaper = get_top_paper(getTopPaperInput)
    error = 0
    result = {"-1": {}}
    try:
        insights = generate_insights(paper=Paper(url=topPaper["url"]))
    except:
        insights = []
        print("something went wrong")
        error += 1
    for child_concept in insights.concepts:
        child_concept.parent = "-1"
        try:
            child_insights = generate_insights(paper=Paper(url=child_concept.referenceUrl))
            for grandchild_concept in child_insights.concepts:
                grandchild_concept.parent = child_concept.id
                child_concept.children.append(grandchild_concept.id)
                firestore_client.write_data_to_collection(collection_name="graph", document_name=query.query, data={grandchild_concept.id: dict(grandchild_concept)})
                result["-1"][child_concept.id][grandchild_concept.id] = {}
        except:
            error += 1
            print("something went wrong")
            child_insights = []
        
        firestore_client.write_data_to_collection(collection_name="graph", document_name=query.query, data={child_concept.id: dict(child_concept)})
        result["-1"][child_concept.id] = {}
    return result

@app.get("/hydrate-node")
def hydrate_node(input: idGraphSchema):
    firestore_client = get_firestore_client()
    result = {}

    def helper(cur_id, id_map, result_map):
        result_map[cur_id] = firestore_client.read_from_document(collection_name="graph", document_name=input.query)[cur_id]
        result_map[id]["children"] = []
        for id in id_map.keys():
            new_id_map = id_map[id]
            result_map[id]["children"].append(helper(id, new_id_map, result_map[cur_id]))
        return result_map[cur_id]
    
    return helper(input.id, input.id_map, result)

@app.get("/retrieve-arxiv-search")
def retrieve_arxiv_search(input: RetrieveArxivSearchInput) -> str:
    firestore_client = get_firestore_client()
    papers = arxiv_script.search_arxiv(input.query)
    firestore_client.write_data_to_collection(
        collection_name="retrieval", document_name=input.query, data={"papers": papers}
    )
    return "Success"

@app.get("/top-paper")
def get_top_paper(input: TopPaperQuerySchema):
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
    return topPaper


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
                    url = top_results[0]["url"]
                else:
                    print("Skip: ", reference_text)
        else:
            url = pdf_url
        concepts.append(
            ConceptNode(
                referenceUrl=url,
                name=idea["idea_name"],
                description=idea["description"],
                id=str(uuid.uuid4())
            )
        )
    paper_insights = PaperInsights(url=pdf_url, concepts=concepts)
    return paper_insights

@app.post("/expand-graph-with-new-nodes")
def expand_graph_with_new_nodes(input: ExpandGraphWithNewInsightsSchema) -> PaperInsights:
    firestore_client = get_firestore_client()
    insights = generate_insights(paper=Paper(url=input.concept.referenceUrl))
    for child_concept in insights.concepts:
        child_concept.parent = input.concept.id
        firestore_client.write_data_to_collection(collection_name="graph", document_name=input.query, data={child_concept.id: dict(child_concept)})
    return insights


@app.post("/more-info")
def more_information(concept: ConceptNode) -> str:
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
