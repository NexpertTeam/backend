from claude import Claude
from functions.expandDescriptionToText import expand
from pdf_parser import pdf_url_to_text
attention_url = "https://arxiv.org/pdf/1706.03762.pdf"
paper_text = pdf_url_to_text(attention_url)
orig = "The Transformer achieves state-of-the-art results on machine translation using significantly less training time compared to previous models."
print(expand(orig, paper_text))

