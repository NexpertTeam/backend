from claude import Claude
import json

def expand(orig_description, paper):
    expander = Claude()
    expanded = expander(
        f"""
            My user wants to learn about a key concept from a paper. In order to do this, I am going to give you a description of a key concept from a paper. I am also going to give you the text of the paper.
            I want you to return an expanded (8-9 sentence) description of the key concept. This description should be informative and educational, and teach the user about the key concept as well as how it is applied in the given paper.
            I also want you to return a 3-5 word name for the key concept.

            You will return this result in the following format:
            <long_description> (THIS IS THE 8-9 SENTENCE INFORMATIVE DESCRIPTION) </long_description>
            <name> (A 3-5 word name for the key concept) </name>

            The key concept short description is: {
                orig_description
            }

            The paper text is:
            <text>
            {paper}
            </text>

            Please surround your response in <response></response> tags.
        """
    )
    response = expanded
    return response

