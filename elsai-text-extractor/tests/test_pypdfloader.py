from elsai_text_extractors.pypdfloader import PyPDFTextExtractor
import os

def test_pypdfloader_service():
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files", "globalwarming.pdf")
    pypdfloader_service = PyPDFTextExtractor(file_name)
    expected_text = "Global warming \nGlobal warming is the long-term rise in Earth's average temperature, primarily driven by \nhuman activities like burning fossil fuels, leading to climate change and environmental \nimpacts. "
    extracted_text = pypdfloader_service.extract_text_from_pdf()
    assert extracted_text == expected_text