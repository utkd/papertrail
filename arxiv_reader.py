import os
import time
import arxiv

class ArxivReader(object):
    def __init__(self, local_basepath):
        if not os.path.exists(local_basepath):
            os.mkdir(local_basepath)
        self._local_basepath = local_basepath
        self._client = arxiv.Client()

    def _extract_paper_id_from_string(self, input:str) -> str:
        if input[-4:] == ".pdf":
            input = input[:-4]
        paper_id = input
        if "http" in input:
            num_c = len(input)
            ridx = input.rindex("/")
            if ridx+1 == num_c:
                input = input[:-1]
                ridx = input.rindex("/")
            paper_id = input[ridx+1:]
        return paper_id
    
    def _get_paper_by_title(self, title:str) -> arxiv.Result:
        search = arxiv.Search(
            query = title,
            max_results = 1,
            sort_by = arxiv.SortCriterion.Relevance
        )

        result = next(self._client.results(search))
        return result
    
    def _get_paper_by_url_or_id(self, input:str) -> arxiv.Result:
        paper_id = self._extract_paper_id_from_string(input)
        if paper_id == input:
            return None
        
        search_by_id = arxiv.Search(id_list=[paper_id])
        result = next(self._client.results(search_by_id))
        return result
    
    def _download_paper(self, result:arxiv.Result, output_path:str) -> str:
        try:
            paper_id = result.get_short_id()
            paper_id = paper_id[:10]
            filename = paper_id + ".pdf"
            result.download_pdf(dirpath=output_path, filename=filename)
            return os.path.join(output_path, filename)
        except Exception as e:
            print(e)
            return None
    
    def bulk_fetch(self, papers: list[str], base_output_path:str) -> list[str]:
        saved_locations = []
        for paper in papers:
            paper_result = self._get_paper_by_url_or_id(paper)
            if paper_result is None:
                paper_result = self._get_paper_by_title(paper)
            if paper_result is not None:
                saved_loc = self._download_paper(paper_result, output_path=self._local_basepath)
                saved_locations.append(saved_loc)
            time.sleep(3.0)
        return saved_locations


if __name__ == "__main__":
    reader = ArxivReader()

    result = reader._get_paper_by_url_or_id("https://arxiv.org/abs/2305.02749/")
    print(result.get_short_id())