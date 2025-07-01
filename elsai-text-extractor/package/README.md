# elsai-text-extractors

**elsai-text-extractors** is a Python package that provides simple, structured interfaces to extract text and data from various document formats (CSV, DOCX, PDF, Excel) using LangChain-compatible loaders, with robust logging and error handling.

---

## 📦 Features

### CSV File Extraction
Extracts rows from structured CSV files with automatic handling of file reading. Logs operations and manages failures gracefully.

### DOCX File Text Extraction
Extracts plain text from Word documents with ease. Captures errors like missing files or unsupported formats.

### PDF File Text Extraction
Reads and returns text from the first page of PDF files. Includes logging for start, success, and error scenarios.

### Excel File Data Extraction
Loads data from unstructured Excel files in element-wise format. Helpful for parsing non-tabular or free-form spreadsheet content.

