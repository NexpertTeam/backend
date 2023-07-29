from claude import Claude


def extract_key_insights(paper_text: str) -> list[dict]:
    insight_extractor = Claude()
    insights = insight_extractor(
        f"""List the main ideas of the paper that reference previous work, for each idea add the APA format related references in the format:

        <idea> <description>

        # Description of the idea

        </description> <references> <bibitem>

        <bibkey>#Bibtext friendly ID</bibkey>

        <reference_text>#APA formatted reference</reference_text>
        </bibitem>

        ...
        <bibitem>

        ...

        </bibitem> </references> </idea>

        ...
        <idea>

        ...
        </idea>)

        === Paper text ===
        {paper_text}
        """
    )
    return insights
