from claude import Claude
import json

def top_one(list_of_jsons, user_query):
    top_one = Claude()
    topPaper = top_one(f"""I have a set of papers. I also have a query string from a user trying to figure out which paper is most relevant for them. The papers are in the following format:

    {{

    title: "Title"

    summary: "Summary"

    url: "url"

    publishDate: "date"

    }}

    Please return the paper that is the most relevant to the users query. Return the entire JSON of the paper. Wrap the returned JSON in <response></response> tags. Prioritize papers that are more relevant, more informative, and more recent.

    The list of papers is:
    {
        str(list_of_jsons)
    }
    
    The user query string is:
    {
        user_query
    }
    """)
    # print(topPaper)
    response = topPaper.split("<response>")[1].split("</response>")[0].replace("'", "\"")
    return json.loads(response)

