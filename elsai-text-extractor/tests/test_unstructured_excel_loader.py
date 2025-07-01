from elsai_text_extractors.unstructured_excel_loader import UnstructuredExcelLoaderService
import os
def test_unstructured_excel_loader_service():
    file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_files", "weatherdata.xlsx")
    unstructured_excel_loader_service = UnstructuredExcelLoaderService(file_name)
    expected_text = '\n\n\ndate\ntemperature\n\n\n2013-01-01 00:00:00\n10\n\n\n2013-01-02 00:00:00\n7.4\n\n\n2013-01-03 00:00:00\n7.166667\n\n\n2013-01-04 00:00:00\n8.666667\n\n\n2013-01-05 00:00:00\n6\n\n\n2013-01-06 00:00:00\n7\n\n\n2013-01-07 00:00:00\n7\n\n\n2013-01-08 00:00:00\n8.857143\n\n\n2013-01-09 00:00:00\n14\n\n\n'
    documents = unstructured_excel_loader_service.load_excel()
    assert documents[0].page_content == expected_text