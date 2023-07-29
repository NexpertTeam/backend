import arxiv

def search_arxiv(query, numRecentPapers=5, numMostCitedPapers=5):
    searchRelevance = arxiv.Search(query = query, max_results = 5, sort_by = arxiv.SortCriterion.Relevance, sort_order = arxiv.SortOrder.Descending)
    searchDate = arxiv.Search(query = query, max_results = 5, sort_by = arxiv.SortCriterion.SubmittedDate, sort_order = arxiv.SortOrder.Descending)

    papers = []

    for result in searchRelevance.results:  
        papers.append({"title": result.title, "summary": result.summary, "url": result.url, "publishedDate": result.published})
    for result in searchDate.results:  
        papers.append({"title": result.title, "summary": result.summary, "url": result.url, "publishedDate": result.published})

    return papers