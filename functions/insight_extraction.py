from claude import Claude

from anthropic import HUMAN_PROMPT, AI_PROMPT


def extract_key_insights(paper_text: str) -> list[dict]:
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
    return insights
