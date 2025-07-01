# Elsai Utilities

The **Elsai Utilities** package provides helper classes for **chunking** and **converting documents** as part of retrieval-augmented generation (RAG) and vector database ingestion workflows.

---

## Prerequisites

* Python 3.13

---

## Installation

To install the `elsai-utilities` package:

Use the following command:
`pip install --index-url https://elsai-core-package.optisolbusiness.com/root/elsai-utilities/ elsai-utilities==0.1.0`

---

## Components

### 1. DocumentChunker

The `DocumentChunker` class offers multiple methods to split large text content into manageable and structured chunks. It supports:

* **Page-wise chunking** based on page breaks or custom delimiters
* **Markdown header-wise chunking** using header levels to split content hierarchically
* **Recursive character-wise chunking** for fine-grained splitting based on character limits and overlaps

These methods are useful when preparing documents for vector embedding and storage in databases like ChromaDB or Pinecone.

---

### 2. DocumentConverter

The `DocumentConverter` class enables conversion from **LlamaIndex** document format into **LangChain-compatible** `Document` objects. This helps maintain compatibility across different libraries when processing and ingesting documents for LLM-based systems.


