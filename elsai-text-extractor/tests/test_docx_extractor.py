from elsai_text_extractors.docx_extractor import DocxTextExtractor
import os

def test_docx_text_extractor():
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files", "globalwarming.docx")
    docx_text_extractor = DocxTextExtractor(file_name)
    document = docx_text_extractor.extract_text_from_docx() 
    expected_text = "Global warming\n\nGlobal warming is the long-term rise in Earth's average temperature, primarily driven by human activities like burning fossil fuels, leading to climate change and environmental impacts."
    
    extracted_text = document[0].page_content
    assert extracted_text == expected_text