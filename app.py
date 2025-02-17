import os
import streamlit as st
from llm_service import OpenAILLM, OllamaLLM
from pdf_summarizer import PdfSummarizer
from arxiv_reader import ArxivReader
from exporter import Exporter

local_pdf_store = "pdfs"
reader = ArxivReader(local_pdf_store)
exporter = Exporter("exports/")

st.set_page_config(page_title='PaperTrail 🔗 Research Assistant', layout="wide")
st.title('PaperTrail')

openai_api_key = st.text_input('OpenAI API Key', type = 'password')

tab1, tab2, tab3 = st.tabs(["Summarize", "Browse Latest Result", "Browse all Summaries"])

with tab1:
    c1, c2 = st.columns(2)

    with c1:
        with st.form('summarize_form', clear_on_submit=True):
            uploaded_file = st.file_uploader("Upload a paper (pdf)")
            submitted = st.form_submit_button('Submit')
            if submitted and uploaded_file is not None:
                if openai_api_key is not None and len(openai_api_key) > 50:
                    llm = OpenAILLM({'openai_key': openai_api_key})
                    summarizer = PdfSummarizer(llm=llm)

                    filename = uploaded_file.name
                    with st.spinner('Processing...'):
                        bytes_data = uploaded_file.getvalue()
                        output_path = os.path.join(local_pdf_store, filename)
                        with open(output_path, 'wb') as f: 
                            f.write(bytes_data)
                        
                        outputs = summarizer.process_pdf(output_path)
                        exporter.update_data(exporter.create_df(outputs))
                        exporter.save_data()
                    
                        st.text("New data available for viewing under the 'Browse Latest Result' tab")
                else:
                    st.text("Provide a valid OpenAI API key")

        
    with c2:
        with st.form('bulk_papers_form', clear_on_submit=True):
            paper_list_str = st.text_area(label="Enter List of papers (Titles or Arxiv URLs only)", value="Papers (one per line)")
            submitted = st.form_submit_button('Submit')
            if submitted and len(paper_list_str) > 0:
                if openai_api_key is not None and len(openai_api_key) > 50:
                    llm = OpenAILLM({'openai_key': openai_api_key})

                    summarizer = PdfSummarizer(llm=llm)                
                    paper_list = paper_list_str.split('\n')

                    with st.spinner('Fetching papers (3-5 secs per paper)...'):
                        saved_papers = reader.bulk_fetch(paper_list, "pdfs")
                    with st.spinner('Processing papers (this may take a while)...'):
                        outputs = summarizer.bulk_summarize(saved_papers)
                    exporter.update_data(exporter.create_df(outputs))
                    exporter.save_data()

                    st.text("New data available for viewing under the 'Browse Latest Result' tab")
                else:
                        st.text("Provide a valid OpenAI API key")


with tab2:
    latest_data, saved_data = exporter.get_saved_data()
    if latest_data is None:
        st.text("No data available yet. Use the Summarize tab to generate some paper summaries.")
    else:
        st.markdown(latest_data[exporter.get_column_names()].to_html(escape=False), unsafe_allow_html=True)

with tab3:
    latest_data, saved_data = exporter.get_saved_data()
    if latest_data is None:
        st.text("No data available yet. Use the Summarize tab to generate some paper summaries.")
    else:
        st.markdown(saved_data[exporter.get_column_names()].to_html(escape=False), unsafe_allow_html=True)
