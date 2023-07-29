from anthropic import AI_PROMPT

from claude import Claude
from xml_parser import extract_tag_content


def parse_insights(insights_text: str) -> dict:
    output = {}
    references = extract_tag_content(insights_text, tag="references")
    reference_list = []
    for ref in references:
        bibkey = extract_tag_content(ref, tag="bibkey")
        reference_text = extract_tag_content(ref, tag="reference_text")
        reference_list.append({"bibkey": bibkey, "reference_text": reference_text})
    output["references"] = reference_list
    ideas = extract_tag_content(insights_text, tag="ideas")
    idea_list = []
    for idea in ideas:
        description = extract_tag_content(idea, tag="description")
        relevant_references = extract_tag_content(idea, tag="relevant_references")
        relevant_references = [
            extract_tag_content(ref, tag="bibkey") for ref in relevant_references
        ]
        idea_list.append(
            {"description": description, "relevant_references": relevant_references}
        )
    output["ideas"] = idea_list
    return output


def extract_key_insights(paper_text: str) -> dict:
    prompt = f"""List the most important ideas in the paper that build
    upon previous work (avoid referencing the paper itself) and then output the list of ideas in the following format:
    <references>
        <bibitem>
            <bibkey>
                # Bibtext friendly ID
            </bibkey>
            <reference_text>
                # APA formatted reference
            </reference_text>
        </bibitem>
    </references>
    <idea>
        <description>
            # Description of the idea
        </description>
        <relevant_references>
            <bibkey>
                # Bibkey ID of relevant reference
            </bibkey>
            ...
            <bibkey>
            ...
            </bibkey>
        </relevant_references>
    </idea>
    ...
    <idea>
    ...
    </idea>
    === Paper text ===
    {paper_text}

    {AI_PROMPT} I have identified the paper's title and authors and will ignore it, beyond that, these are the most important references from previous work:
    """
    insights = Claude()(prompt, output_role_or_suffix="")
    insights = parse_insights(insights)
    return insights
