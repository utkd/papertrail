import json
from pypdf import PdfReader
import pdf_prompts as pmpts
from llm_service import LLMService

class PdfSummarizer(object):
    """
    Class that reads a pdf and generates summaaries and insights using an LLM
    """

    def __init__(self, llm: LLMService) -> None:
        self._llm = llm

    def process_pdf(self, pdf_file:str) -> dict[str, str]:
        # read the pdf
        reader = PdfReader(pdf_file)
        print("Read %d pages from %s" % (len(reader.pages), pdf_file))
        content = []
        for page in reader.pages:
            content.append(page.extract_text())
        all_content = " ".join(content)
        all_content = self._remove_references(all_content)

        print("Content lenght: %d" % (len(all_content)))

        messages = [{
            "role": "system",
            "content": pmpts.p_system_summarize
        }, {
            "role": "user",
            "content": all_content
        }]

        # call llm
        response = None
        response = self._llm.call(messages=messages)
        return json.loads(response['output'])

    def bulk_summarize(self, papers: list[str]) -> list[dict[str, str]]:
        outputs = []
        for paper_path in papers:
            output = self.process_pdf(paper_path)
            outputs.append(output)
        return outputs
    
    def _remove_references(self, content):
        try:
            references_idx = content.rindex("References")
            print("Content length from %d -> %d, after removing references" % (len(content), references_idx))
            return content[:references_idx]
        except Exception as e:
            print(e)
            return content