import base64

with open("./superconductor.pdf", "rb") as f:
    bytesA = f.read()

# bytesA = base64.b64encode(bytesA).decode()

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT


anthropic = Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="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",
)

completion = anthropic.completions.create(
    model="claude-2",
    max_tokens_to_sample=300,
    prompt=f"{HUMAN_PROMPT} What is this document?\n" + bytesA + f"{AI_PROMPT}",
)
print(completion.completion)