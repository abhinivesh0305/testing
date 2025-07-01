from elsai_text_extractors.csv_extractor import CSVFileExtractor
import os

def test_csv_file_extractor():
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files", "weatherdata.csv")
    csv_file_extractor = CSVFileExtractor(file_name)
    expected_text = 'date: 2013-01-01\ntemperature: 10'
    
    documents = csv_file_extractor.load_from_csv()
    extracted_text = documents[0].page_content
    assert len(documents) == 10
    assert extracted_text == expected_text